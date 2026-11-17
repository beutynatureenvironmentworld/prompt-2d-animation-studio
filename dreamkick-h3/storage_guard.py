"""CPU-only preflight for the actual Singularity Ref2VA INT8 H3 cache; no inference."""
import argparse,json,os,shutil
from pathlib import Path
SHARED={
 'text_encoder':('text_encoders','qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors'),
 'video_vae':('vae','minimax_h3_video_vae_fp16.safetensors'),
 'audio_vae':('vae','minimax_h3_audio_vae_fp32.safetensors')}
SINGULARITY=('diffusion_models','Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors')
REQUIRED={**SHARED,'singularity_ref2va_int8':SINGULARITY}
DEFAULT_DATASET='/kaggle/input/fte-h3-models/models'
MIN_FILE_BYTES=1000000
def inspect(root=DEFAULT_DATASET,strict_min_bytes=MIN_FILE_BYTES):
 root=Path(root);items={}
 for role,(folder,name) in REQUIRED.items():
  path=root/folder/name
  size=path.stat().st_size if path.is_file() else 0
  items[role]={'relative_path':str(Path(folder)/name),'exists':path.is_file(),'bytes':int(size),'large_enough':size>=strict_min_bytes}
 disks={}
 for location in ('/kaggle/working','/kaggle/tmp','/kaggle/temp','/tmp'):
  p=Path(location)
  if p.exists():
   usage=shutil.disk_usage(p)
   disks[location]={'free_gib':round(usage.free/2**30,2),'total_gib':round(usage.total/2**30,2),'device':p.stat().st_dev}
 ready=all(x['large_enough'] for x in items.values())
 return {'schema':'fte_h3_disk_guard_v2','profile':'MiniMax H3 Singularity Ref2VA INT8 (not base FP8)','cache_root':str(root),'cache_complete':ready,'required_files':items,'disks':disks,'gpu_started':False,'downloads_started':False,'next_step':'May test GPU initialization with permission' if ready else 'Do not submit GPU job: model cache incomplete'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--cache-root',default=os.environ.get('FTE_H3_MODEL_DATASET',DEFAULT_DATASET));p.add_argument('--out',default='FTE_H3_STORAGE_READINESS.json');p.add_argument('--require-complete',action='store_true')
 a=p.parse_args();r=inspect(a.cache_root);q=Path(a.out);q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(r,indent=2)+'\n')
 print('STORAGE_READINESS',r['cache_complete'],q)
 if a.require_complete and not r['cache_complete']:raise SystemExit('H3_STORAGE_BLOCKED: private cache missing; no GPU used')
if __name__=='__main__':main()
