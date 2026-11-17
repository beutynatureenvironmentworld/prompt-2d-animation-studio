"""Optional GPU-OFF model staging into a private Kaggle Dataset.

This MUST be run with Kaggle Accelerator=None. It NEVER turns on or attempts
GPU allocation and does not upload to HF/Kaggle automatically. Real model size
and license must be confirmed; partial failed downloads are not marked ready.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,time
from pathlib import Path

WAN_ID='Wan-AI/Wan2.1-T2V-1.3B-Diffusers'

def cache_manifest_path(root):return Path(root)/'FTE_CACHE_MANIFEST.json'

def validate_cache(root,expected_repo=WAN_ID):
    root=Path(root)
    f=cache_manifest_path(root)
    if not f.is_file():raise ValueError('Missing FTE_CACHE_MANIFEST.json (incomplete or unmanaged model cache)')
    data=json.loads(f.read_text())
    if data.get('repo_id')!=expected_repo or not data.get('finished'):
        raise ValueError('Wrong or incomplete model cache')
    if not (root/'model_index.json').is_file():raise ValueError('Missing Diffusers model_index.json')
    if not any(root.rglob('*.safetensors')):raise ValueError('Missing model checkpoint(s)')
    return data


def stage(root,download=False,min_disk_gb=18):
    root=Path(root).resolve()
    if os.getenv('CUDA_VISIBLE_DEVICES') not in ('','-1',None):
        raise RuntimeError('Set CUDA_VISIBLE_DEVICES=-1 and Accelerator=None for CPU-only model staging')
    if not download:return {'repo_id':WAN_ID,'destination':str(root),'downloaded':False,'gpu_used':False,
         'instruction':'Review public model LICENSE and private Kaggle dataset quota, then pass --download while GPU is OFF'}
    root.mkdir(parents=True,exist_ok=True)
    free_gb=shutil.disk_usage(root).free/1e9
    if free_gb<min_disk_gb:raise RuntimeError(f'Insufficient free disk for model staging: {free_gb:.1f}GB < {min_disk_gb}GB')
    from huggingface_hub import snapshot_download
    snapshot_download(repo_id=WAN_ID,local_dir=str(root),max_workers=3)
    # Write complete flag LAST, only after every model file is present.
    if not (root/'model_index.json').is_file() or not any(root.rglob('*.safetensors')):
        raise RuntimeError('Model download incomplete; do not publish cache as ready')
    weights=[p for p in root.rglob('*.safetensors')]
    manifest={'schema':'fte.model.cache.v1','repo_id':WAN_ID,'finished':True,'cache_root':str(root),
              'total_weight_bytes':sum(p.stat().st_size for p in weights),'checkpoint_files':len(weights),
              'gpu_used':False,'staged_unix':int(time.time()),'license':'apache-2.0 (verify upstream LICENSE)'}
    cache_manifest_path(root).write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--download',action='store_true');a=p.parse_args()
 print(json.dumps(stage(a.out,a.download),indent=2))
