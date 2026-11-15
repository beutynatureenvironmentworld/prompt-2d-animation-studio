"""Kaggle GPU first-run worker. This runs INSIDE the user's private Kaggle Notebook.

MODE='probe': verifies actual CUDA arithmetic, no external model download.
MODE='pose-ai': downloads one SD1.5 model and generates one original cartoon pose.
The parent dispatcher prepends the hard-coded MODE and BUDGET_SECONDS.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import time

MODE = globals().get("KAGGLE_STUDIO_MODE", "probe")
BUDGET_SECONDS = globals().get("KAGGLE_STUDIO_BUDGET_SECONDS", 720)
OUTPUT = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path.cwd()
ALLOWED = {"probe", "pose-ai"}


def run():
    if MODE not in ALLOWED or type(BUDGET_SECONDS) is not int or not 60 <= BUDGET_SECONDS <= 1800:
        raise ValueError("Unsupported mode or runtime budget")
    start = time.monotonic()
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("No CUDA device was allocated by Kaggle. Stop without downloading models.")
    device = torch.device("cuda:0")
    info = []
    for idx in range(torch.cuda.device_count()):
        dev = torch.cuda.get_device_properties(idx)
        info.append({"index": idx, "name": dev.name, "vram_gib": round(dev.total_memory / 2**30, 2)})
    # Actual GPU execution; note VRAM on separate GPUs is NOT additive for one model.
    x = torch.ones((512, 512), device=device, dtype=torch.float16)
    y = torch.cos(x * 2.5) + x
    torch.cuda.synchronize()
    assert bool(torch.isfinite(y).all().item())
    report = {"mode": MODE, "cuda_verified": True, "devices": info,
              "model_inference_verified": False, "output": [], "budget_seconds": BUDGET_SECONDS}
    OUTPUT.mkdir(parents=True, exist_ok=True)

    if MODE == "probe":
        from PIL import Image
        grid = torch.arange(256, device=device, dtype=torch.float32)
        xx, yy = torch.meshgrid(grid, grid, indexing="xy")
        r = torch.where((xx-128)**2 + (yy-121)**2 < 82**2, 250., 205.)
        eye = ((xx-98)**2+(yy-110)**2 < 7**2) | ((xx-158)**2+(yy-110)**2 < 7**2)
        r = torch.where(eye, 23., r)
        g = torch.where(eye, 25., r*.92)
        b = torch.where(eye, 33., r*.84)
        image = torch.stack([r,g,b], -1).clamp(0,255).byte().cpu().numpy()
        path = OUTPUT/"gpu-calculation-proof.png"
        Image.fromarray(image,"RGB").save(path)
        report["output"].append(path.name)
        report["notes"] = "Real GPU tensor processing; this is NOT a diffusion-generated AI image."
    elif MODE == "pose-ai":
        # Use the initial T4 GPU for a realistic single-image benchmark.
        # SD1.5 weights have CreativeML OpenRAIL-M restrictions, not a permissive MIT model license.
        remaining = BUDGET_SECONDS - (time.monotonic()-start)
        if remaining < 120:
            raise TimeoutError("Too little budget to attempt model download/inference")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                        "diffusers==0.35.2", "transformers>=4.40,<5",
                        "accelerate>=1,<2", "safetensors>=0.4"], check=True, timeout=min(int(remaining-40), 540))
        from diffusers import StableDiffusionPipeline
        model_id = "stable-diffusion-v1-5/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id, torch_dtype=torch.float16, use_safetensors=True
        )
        pipe.to(device)
        pipe.enable_attention_slicing()
        generator = torch.Generator(device="cuda").manual_seed(2317)
        prompt = (
            "Original funny 2D cartoon character design, expressive worried stick-figure boy "
            "with oversized face, thick black ink outlines, large wide surprised eyes, thin black limbs, "
            "simple muted olive background, graphic flat colors, full body, clean readable silhouette, "
            "pose sheet single character, original animation production artwork"
        )
        result = pipe(
            prompt=prompt,
            negative_prompt="text, watermark, logo, extra limbs, photorealistic, realistic skin, blurry",
            num_inference_steps=16, guidance_scale=7.0, height=512, width=512, generator=generator
        )
        path = OUTPUT/"original-cartoon-pose.png"
        result.images[0].save(path)
        report["output"].append(path.name)
        report["model_inference_verified"] = True
        report["model"] = model_id
        report["notes"] = "One generated pose; consistent character identity and full animation NOT established."
        del pipe
        torch.cuda.empty_cache()

    report["elapsed_seconds"] = round(time.monotonic()-start, 2)
    (OUTPUT/"gpu-studio-result.json").write_text(json.dumps(report, indent=2)+"\n")
    print("GPU_STUDIO_RESULT", json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    run()
