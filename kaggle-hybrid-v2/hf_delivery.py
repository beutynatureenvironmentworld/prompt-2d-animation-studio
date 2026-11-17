"""Opt-in private Hugging Face DATASET clip archival; never assume free unlimited storage."""
import argparse,os,re,json,hashlib
from pathlib import Path

def upload(clip,repo_id,confirm=False):
 if not confirm:raise PermissionError('Explicit --confirm-private-upload required')
 if not re.fullmatch('[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo_id):raise ValueError('Invalid HF repo_id')
 if not os.environ.get('HF_TOKEN'):raise PermissionError('HF_TOKEN must be Kaggle Secret or GitHub Actions Secret, not a CLI argument')
 path=Path(clip)
 if path.suffix.lower()!='.mp4' or not path.is_file():raise ValueError('Missing MP4')
 from huggingface_hub import HfApi
 api=HfApi(token=os.environ['HF_TOKEN'])
 info=api.repo_info(repo_id,repo_type='dataset')
 if not info.private:raise PermissionError('Refusing to upload clip to a PUBLIC Hugging Face dataset')
 remote='fte-clips/'+hashlib.sha256(path.read_bytes()).hexdigest()[:16]+'_'+path.name
 url=api.upload_file(path_or_fileobj=str(path),path_in_repo=remote,repo_id=repo_id,repo_type='dataset')
 return {'dataset':repo_id,'private_checked':True,'remote_path':remote,'url':str(url)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('clip');p.add_argument('dataset');p.add_argument('--confirm-private-upload',action='store_true');a=p.parse_args()
 print(json.dumps(upload(a.clip,a.dataset,a.confirm_private_upload),indent=2))
