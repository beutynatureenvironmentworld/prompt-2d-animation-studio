"""Create one PRIVATE user-owned HF dataset and upload our original small 2D demo.

This is an authorized storage setup only; no model weights, user reference media,
credentials, or copyrighted third-party files are uploaded.
"""
import json,os,sys
from pathlib import Path
from huggingface_hub import HfApi
key=os.environ.get("HF_TOKEN","").strip()
if not key:raise SystemExit("HF_TOKEN is missing; no write attempt made")
api=HfApi(token=key)
who=api.whoami(token=key)
username=who.get("name")
if not username:raise SystemExit("Cannot authenticate HF user, no write attempt made")
dataset_id=username+"/vidbest-animation-storage"
# Visibility must be private; if an existing similarly named public repo is present, refuse to upload.
api.create_repo(repo_id=dataset_id,repo_type="dataset",private=True,exist_ok=True,token=key)
info=api.repo_info(repo_id=dataset_id,repo_type="dataset",token=key)
if not bool(info.private):raise SystemExit("Refusing upload: Hugging Face dataset is not private")
output=Path("hf-storage/output")
output.mkdir(parents=True,exist_ok=True)
asset=Path("inkrig/output/original-rigged-2d-comedy.mp4")
if not asset.exists() or asset.stat().st_size<=10000 or asset.stat().st_size>8000000:
    raise SystemExit("Missing demo MP4 or out-of-bounds test asset size")
api.upload_file(
 path_or_fileobj=str(asset),path_in_repo="animation-demos/original-rigged-2d-comedy.mp4",
 repo_id=dataset_id,repo_type="dataset",token=key,
 commit_message="Original joint-animated 2D comedy test (not GPU diffusion)")
manifest={"purpose":"VidBest animation storage test",
          "artifact":"animation-demos/original-rigged-2d-comedy.mp4",
          "render_origin":"GitHub InkRig original vector skeleton renderer",
          "horde_or_video_diffusion":False,"user_reference_media_uploaded":False,
          "model_weights_uploaded":False,"dataset_visibility":"private"}
api.upload_file(
 path_or_fileobj=json.dumps(manifest,indent=2).encode("utf-8"),
 path_in_repo="animation-demos/provenance.json",
 repo_id=dataset_id,repo_type="dataset",token=key,
 commit_message="Record private animation artifact provenance")
result={"hf_storage_authenticated":True,"private_dataset_created_or_reused":True,
        "demo_mp4_uploaded":True,"dataset_private":True,
        "model_weights_uploaded":False,"test_bytes":asset.stat().st_size}
(output/"hf-private-storage-upload.json").write_text(json.dumps(result,indent=2)+"\n")
print("HF_PRIVATE_STORAGE_REAL_MP4_UPLOAD_PASS",asset.stat().st_size,"bytes")
print("NO_LARGE_MODEL_WEIGHTS_COPIED")
