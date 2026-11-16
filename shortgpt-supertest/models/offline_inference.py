#!/usr/bin/env python3
"""Actual local open-weight inference; never fakes an AI-generated scene.

LLM  : Qwen3-4B-Instruct-2507 GGUF Q4_K_M with CPU llama.cpp
Image: Segmind SSD-1B (Apache-2.0) with CPU Diffusers/PyTorch

Both are separate processes to avoid combined peak memory. No API tokens are
required for public models, but model downloads need a network connection.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

DEFAULT_GGUF_REPO = "bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF"
DEFAULT_GGUF_FILE = "Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
DEFAULT_IMAGE_REPO = "segmind/SSD-1B"
ACTIONS = ["notice", "run", "knock", "jump", "shock", "slip", "recover", "dance"]
LOCATIONS = ["toilet", "school", "garden", "street", "office", "park"]


def _download_gguf() -> str:
    from huggingface_hub import hf_hub_download
    model_id = os.environ.get("GGUF_MODEL_ID", DEFAULT_GGUF_REPO)
    filename = os.environ.get("GGUF_MODEL_FILE", DEFAULT_GGUF_FILE)
    return hf_hub_download(repo_id=model_id, filename=filename,
                           cache_dir=os.environ.get("HF_HOME") or None)


def create_story(prompt: str, output: Path, max_tokens: int=450):
    from llama_cpp import Llama
    from json import loads
    t0 = time.monotonic()
    model_path = _download_gguf()
    cpu = max(1, min(4, os.cpu_count() or 2))
    engine = Llama(model_path=model_path, n_ctx=4096, n_threads=cpu,
                  n_gpu_layers=0, use_mmap=True, verbose=False)
    system = (
        "You are a witty family-friendly original short-cartoon director. "
        "Produce ONLY strict JSON, no markdown, with one key scenes: an array of 2-6 objects. "
        "Each scene has exactly action, location, duration, narration, image_prompt. "
        f"action MUST be one of {ACTIONS}. location MUST be one of {LOCATIONS}. "
        "duration numeric between 0.6 and 3.0, sum <=12. "
        "Narration English, max 80 characters. Every image_prompt is a cohesive "
        "illustrated background WITHOUT characters, text, signage, brand or watermark. "
        "Aim for strong physical gag, anticipation, payoff and recovery. "
        "Example: {\"scenes\":[{\"action\":\"notice\",\"location\":\"toilet\",\"duration\":0.8,\"narration\":\"Uh-oh!\",\"image_prompt\":\"Funny 2D cartoon bathroom hallway, clear door, no characters\"},{\"action\":\"run\",\"location\":\"toilet\",\"duration\":1.2,\"narration\":\"Gotta go!\",\"image_prompt\":\"The same bathroom hallway, no characters\"}]}"
    )
    response = engine.create_chat_completion(
        messages=[{"role":"system","content":system},
                  {"role":"user","content":prompt[:500]}],
        max_tokens=max_tokens, temperature=.17, top_p=.86,
        response_format={"type":"json_object"},
    )
    content = response["choices"][0]["message"]["content"]
    try: proposal = loads(content)
    except Exception as exc: raise RuntimeError("LLM did not produce valid JSON") from exc
    # Validate strictly in the ShortGPT adapter; DO NOT evaluate any generated code.
    parent = Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(parent))
    from shortgpt_supertest import safe_plan
    plan = safe_plan(proposal)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"engine":"Qwen3-4B-Instruct-2507-GGUF-Q4", "ai_inference":True,
        "story_path":str(output),"scenes":len(plan['scenes']),
        "seconds":round(time.monotonic()-t0,2)},ensure_ascii=False),flush=True)


def create_background(prompt: str, output: Path, steps: int=9, width: int=384, height: int=512):
    import torch
    from diffusers import StableDiffusionXLPipeline
    from huggingface_hub import snapshot_download
    t0=time.monotonic()
    repo=os.environ.get("CPU_IMAGE_MODEL",DEFAULT_IMAGE_REPO)
    if repo!=DEFAULT_IMAGE_REPO and not os.environ.get("ALLOW_UNVERIFIED_IMAGE_MODEL"):
        raise RuntimeError("Only audited Apache-2.0 Segmind SSD-1B allowed unless explicitly overridden")
    # Download only fp16 Diffusers component weights (~4.5GB), not the 26.8GB
    # aggregate of duplicate full checkpoints / fp32 copies.
    parts=["model_index.json","scheduler/*","tokenizer/*","tokenizer_2/*",
           "text_encoder/config.json","text_encoder/model.fp16.safetensors",
           "text_encoder_2/config.json","text_encoder_2/model.fp16.safetensors",
           "unet/config.json","unet/diffusion_pytorch_model.fp16.safetensors",
           "vae/config.json","vae/diffusion_pytorch_model.fp16.safetensors"]
    folder=snapshot_download(repo_id=repo,allow_patterns=parts,
                             cache_dir=os.environ.get("HF_HOME") or None)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 2)))
    with torch.inference_mode():
        pipe=StableDiffusionXLPipeline.from_pretrained(
             folder,torch_dtype=torch.float32,variant="fp16",use_safetensors=True,
             local_files_only=True)
        pipe.to('cpu')
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
        # Explicit standard-deviations and inference steps. This renders original
        # pixels with local CPU, not PIL/vector or HF paid provider.
        negative="humans, characters, letters, text, subtitles, watermark, logo, noisy, blurry"
        generator=torch.Generator(device='cpu').manual_seed(20261117)
        img=pipe(prompt=prompt,negative_prompt=negative,
                 num_inference_steps=steps,guidance_scale=7.2,
                 width=width,height=height,generator=generator).images[0]
    output.parent.mkdir(parents=True,exist_ok=True)
    img.convert('RGB').save(output)
    print(json.dumps({"engine":repo,"ai_inference":True,"image_path":str(output),
        "dimensions":[width,height],"steps":steps,
        "seconds":round(time.monotonic()-t0,2),"bytes":output.stat().st_size}),flush=True)


def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="job",required=True)
    chat=sub.add_parser("story");chat.add_argument("--prompt",required=True)
    chat.add_argument("--output",required=True);chat.add_argument("--max-tokens",type=int,default=450)
    image=sub.add_parser("image");image.add_argument("--prompt",required=True)
    image.add_argument("--output",required=True);image.add_argument("--steps",type=int,default=9)
    image.add_argument("--width",type=int,default=384);image.add_argument("--height",type=int,default=512)
    a=p.parse_args()
    if a.job=="story":create_story(a.prompt,Path(a.output),a.max_tokens)
    else:
        if a.width%8 or a.height%8 or not(256<=a.width<=1024 and 256<=a.height<=1024):
            raise ValueError("Image dimensions must be multiples of 8, 256 to 1024")
        if not 1<=a.steps<=40:raise ValueError("steps must be between 1 and 40")
        create_background(a.prompt,Path(a.output),a.steps,a.width,a.height)
if __name__=='__main__':main()