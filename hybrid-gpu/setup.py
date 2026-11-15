"""Install one selected ComfyUI video backend into a notebook or Linux runner."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

COMFY = "eee59185ff4f43ae2d9ad122b245619d27d9daad"
TOON = "d312c62982f1582b7955444d3a22ac948fb9c603"
WAN = "Comfy-Org/Wan_2.1_ComfyUI_repackaged"
WAN_REV = "123acf1cc74bccbb9bfff8ac1ee72edc08c2341d"
FILES = {
    "ltx": [
        ("Lightricks/LTX-Video","8984fa25007f376c1a299016d0957a37a2f797bb","ltx-video-2b-v0.9.5.safetensors","checkpoints"),
        ("Comfy-Org/mochi_preview_repackaged","ed4b8585dc4d3204397291c35e100884686178d6","split_files/text_encoders/t5xxl_fp16.safetensors","text_encoders")],
    "wan": [(WAN,WAN_REV,"split_files/"+item,item.split("/")[0]) for item in (
        "diffusion_models/wan2.1_i2v_480p_14B_fp8_scaled.safetensors","vae/wan_2.1_vae.safetensors",
        "text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors","clip_vision/clip_vision_h.safetensors")],
    "toon": [
        ("Kijai/DynamiCrafter_pruned","1a427ad0865b5447f93bb8e32cd703f45ea1fcb0","tooncrafter_512_interp-pruned-fp16.safetensors","checkpoints/dynamicrafter"),
        ("Kijai/CLIPVisionModelWithProjection_fp16","d7daa6e96bf11fc2ed6f0a12ca58fbdb8dfa9ebb","CLIP-ViT-H-fp16.safetensors","clip_vision"),
        ("stabilityai/sd-vae-ft-mse-original","629b3ad3030ce36e15e70c5db7d91df0d60c627f","vae-ft-mse-840000-ema-pruned.safetensors","vae"),
        ("Manojb/stable-diffusion-2-1-base","0094d483a120f3f33dafbd187ea4aa60d10de75c","text_encoder/model.fp16.safetensors","clip/stable-diffusion-2-1-clip-fp16.safetensors")],
}

def checkout(path, repo, revision):
    if not (path/".git").exists():
        path.mkdir(parents=True,exist_ok=True)
        subprocess.run(["git","init","-q",path],check=True)
    args=["git","-C",path]
    current=subprocess.run(args+["rev-parse","HEAD"],capture_output=True,text=True)
    if current.stdout.strip()!=revision:
        subprocess.run(args+["fetch","--depth=1","https://github.com/"+repo+".git",revision],check=True)
        subprocess.run(args+["checkout","--detach","FETCH_HEAD"],check=True)

def install(root, model, sources_only=False):
    checkout(root,"Comfy-Org/ComfyUI",COMFY)
    requirements=[root/"requirements.txt"]
    if model=="toon":
        addon=root/"custom_nodes"/"DynamiCrafterWrapper"
        checkout(addon,"kijai/ComfyUI-DynamiCrafterWrapper",TOON)
        requirements.append(addon/"requirements.txt")
    if sources_only:
        return
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError("Select an available NVIDIA GPU runtime first.")
    pip=[sys.executable,"-m","pip","install"]
    for req in requirements:
        subprocess.run(pip+["-r",str(req)],check=True)
    from huggingface_hub import hf_hub_download
    for repo,rev,file,folder in FILES[model]:
        target=root/"models"/folder
        if not folder.endswith(".safetensors"):
            target=target/Path(file).name
        target.parent.mkdir(parents=True,exist_ok=True)
        cached=os.getenv("VIDBEST_MODEL_CACHE")
        mounted=Path(cached)/target.relative_to(root/"models") if cached else None
        source=mounted if mounted and mounted.is_file() else Path(hf_hub_download(repo_id=repo,revision=rev,filename=file))
        if target.is_symlink():
            target.unlink()
        if not target.exists():
            target.symlink_to(source.resolve())

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("model",choices=FILES)
    p.add_argument("--root",type=Path,default=Path("VidBestComfy"))
    p.add_argument("--sources-only",action="store_true")
    a=p.parse_args()
    install(a.root.resolve(),a.model,a.sources_only)
