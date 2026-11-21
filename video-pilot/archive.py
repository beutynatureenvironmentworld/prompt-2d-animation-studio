"""Private Modal function for video support copies in a private Hugging Face dataset."""
import hashlib
import re
import tempfile
import urllib.request
from pathlib import Path
import modal

app = modal.App("vidbest-delivery-archive")
image = modal.Image.debian_slim(python_version="3.12").pip_install("huggingface_hub>=0.30,<2")
settings = dict(image=image, secrets=[modal.Secret.from_name("vidbest-huggingface")], retries=0, max_containers=1)


def private_dataset():
    from huggingface_hub import HfApi
    api = HfApi()
    repo = api.whoami()["name"] + "/vidbest-private-deliveries"
    api.create_repo(repo, repo_type="dataset", private=True, exist_ok=True)
    if api.repo_info(repo, repo_type="dataset").private is not True:
        raise RuntimeError("Private storage required")
    return api, repo


@app.function(**settings, timeout=90)
def prepare():
    private_dataset()
    print("Private dataset verified")


@app.function(**settings, timeout=900)
def backup(order, expiry, signature, expected_sha):
    if not re.fullmatch("[0-9a-f]{24}", order) or not re.fullmatch("[0-9a-f]{64}", signature):
        raise ValueError("Invalid order")
    api, repo = private_dataset()
    url = f"https://ai.vid.best/api/support-copy/{order}?expires={int(expiry)}&sig={signature}"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "video.mp4"
        digest = hashlib.sha256()
        request = urllib.request.Request(url, headers={"User-Agent":"vid.best delivery archive/1.0"})
        with urllib.request.urlopen(request,timeout=90) as source, path.open("wb") as out:
            while block := source.read(1024 * 1024):
                digest.update(block)
                out.write(block)
        if digest.hexdigest()!=expected_sha:
            raise ValueError("Copy checksum mismatch")
        api.upload_file(path_or_fileobj=str(path),path_in_repo=f"videos/{order}/{expected_sha}.mp4",
                        repo_id=repo,repo_type="dataset",commit_message="Save verified video copy")
        return expected_sha
