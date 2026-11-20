#!/usr/bin/env python3
"""Guarded Wan2.2 TI2V-5B runner (model download is explicitly opt-in).

Official Wan 2.2 guidance: >=24 GiB single-card GPU VRAM for TI2V-5B.
This program does NOT claim workable CPU-only high-quality Wan generation.
"""
import argparse,json,subprocess,sys
from pathlib import Path
MODEL="Wan-AI/Wan2.2-TI2V-5B"
def cards():
    try:
        p=subprocess.run(["nvidia-smi","--query-gpu=name,memory.total",
                          "--format=csv,noheader,nounits"],capture_output=True,
                         text=True,timeout=10,check=True)
        return [{"name":line.rsplit(",",1)[0].strip(),
                 "memory_mib":int(line.rsplit(",",1)[1].strip())}
                for line in p.stdout.splitlines() if line.strip()]
    except (FileNotFoundError,ValueError,subprocess.SubprocessError):
        return []
def audit():
    gpu=cards()
    eligible=any(x["memory_mib"]>=24*1024 for x in gpu)
    print(json.dumps({"detected_gpus":gpu,"official_ti2v5b_min_single_gpu_vram_gb":24,
                      "eligible_to_attempt":eligible,
                      "github_cpu_wan_video_generation_practical":False},indent=2),flush=True)
    return eligible
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--audit",action="store_true")
    p.add_argument("--run",action="store_true",
                   help="Explicitly install/download massive Wan model after GPU guard")
    p.add_argument("--prompt",default="Original fast two-dimensional cartoon rescue with stable character identity")
    p.add_argument("--image",help="existing original image for I2V")
    p.add_argument("--workspace",default="wan_workspace")
    args=p.parse_args()
    allowed=audit()
    if not args.run:return
    if not allowed:raise SystemExit("BLOCKED: full Wan2.2 5B needs NVIDIA GPU >=24 GiB")
    if args.image and not Path(args.image).is_file():raise SystemExit("Input image missing")
    root=Path(args.workspace).resolve();root.mkdir(parents=True,exist_ok=True)
    code=root/"Wan2.2"
    if not (code/"generate.py").exists():
        subprocess.run(["git","clone","--depth","1","https://github.com/Wan-Video/Wan2.2.git",str(code)],check=True)
    subprocess.run([sys.executable,"-m","pip","install","-r",str(code/"requirements.txt")],check=True)
    subprocess.run([sys.executable,"-m","pip","install","huggingface_hub[cli]"],check=True)
    ckpt=root/"Wan2.2-TI2V-5B"
    subprocess.run(["hf","download",MODEL,"--local-dir",str(ckpt)],check=True)
    cmd=[sys.executable,"generate.py","--task","ti2v-5B","--size","704*1280",
         "--ckpt_dir",str(ckpt),"--offload_model","True","--convert_model_dtype",
         "--t5_cpu","--prompt",args.prompt]
    if args.image:cmd+=["--image",str(Path(args.image).resolve())]
    subprocess.run(cmd,cwd=code,check=True)
if __name__=="__main__":main()
