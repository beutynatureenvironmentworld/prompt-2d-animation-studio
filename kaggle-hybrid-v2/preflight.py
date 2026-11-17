"""Do a genuine CUDA arithmetic proof before consuming a model-sized GPU session."""
from __future__ import annotations
import json,os,platform,shutil,time
from pathlib import Path


def probe(output_dir,require_gpu=False):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    result={'schema':'fte.gpu.preflight.v1','utc_unix':int(time.time()),'platform':platform.system(),
      'working_free_gb':round(shutil.disk_usage(out).free/1e9,2),'device_count':0,'devices':[],
      'cuda_verified':False,'model_inference_verified':False}
    try:
        import torch
        result['torch_version']=str(torch.__version__)
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                prop=torch.cuda.get_device_properties(i)
                result['devices'].append({'index':i,'name':prop.name,'vram_gib':round(prop.total_memory/2**30,2),
                                          'compute_capability':f'{prop.major}.{prop.minor}'})
            result['device_count']=len(result['devices'])
            # Compute on cuda:0, not just nvidia-smi discovery
            x=torch.arange(256*256,device='cuda:0',dtype=torch.float32).reshape(256,256)
            y=(x/257).cos().square();torch.cuda.synchronize()
            result['cuda_verified']=bool(torch.isfinite(y).all().item())
    except ImportError:result['note']='torch not available; CPU-side dry-run only'
    (out/'GPU_PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n')
    if require_gpu and not result['cuda_verified']:raise RuntimeError('No Kaggle CUDA calculation verified; do not download model')
    return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',default='output');p.add_argument('--require-gpu',action='store_true');a=p.parse_args()
 print(json.dumps(probe(a.output,a.require_gpu),indent=2))
