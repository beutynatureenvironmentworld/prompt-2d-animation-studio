"""Verify real CUDA computation; no model weights, credentials or media uploads."""
import json,time
from pathlib import Path
start=time.monotonic()
import torch
if not torch.cuda.is_available(): raise RuntimeError("T4 CUDA GPU not available")
gpu=torch.device("cuda:0")
a=torch.ones((128,128),device=gpu)
b=torch.sin(a).sum()
torch.cuda.synchronize()
assert 0<b.item()<16384
p=torch.cuda.get_device_properties(gpu)
result={"cuda_verified":True,"ai_video_generated":False,"device":p.name,
        "vram_gib":round(p.total_memory/(1024**3),2),
        "elapsed_seconds":round(time.monotonic()-start,3)}
Path("/content/vidbest_gpu_probe.json").write_text(json.dumps(result,indent=2)+"\n")
print("COLAB_GPU_TENSOR_PASS; video generated: False")
