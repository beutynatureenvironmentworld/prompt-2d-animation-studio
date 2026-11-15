"""Build bounded private Kaggle GPU jobs. Secret is NEVER included in notebook metadata."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
USERNAME = re.compile(r"^[a-zA-Z0-9_-]{2,64}$")
MODES = {"probe", "pose-ai"}


def create_job(output: Path, owner: str, mode: str, minutes: int, job_id: str = "trial") -> str:
    if not USERNAME.fullmatch(owner):
        raise ValueError("Invalid Kaggle username")
    if mode not in MODES or not 2 <= minutes <= 30:
        raise ValueError("Invalid mode or budget: 2-30 minutes")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,50}", job_id):
        raise ValueError("Invalid identifier")
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("Will not overwrite nonempty job folder")
    output.mkdir(parents=True, exist_ok=True)
    source = (ROOT / "gpu_worker.py").read_text(encoding="utf8")
    declaration = (
        "KAGGLE_STUDIO_MODE = " + repr(mode) + "\n" +
        "KAGGLE_STUDIO_BUDGET_SECONDS = " + str(minutes * 60) + "\n"
    )
    needle = "from __future__ import annotations\n"
    if source.count(needle) != 1:
        raise RuntimeError("Unexpected worker source header")
    code = source.replace(needle, needle + declaration, 1)
    (output / "gpu_job.py").write_text(code, encoding="utf8")
    suffix = hashlib.sha256(code.encode()).hexdigest()[:8]
    slug = "vidbest-" + mode + "-" + job_id.lower() + "-" + suffix
    slug = slug[:64].rstrip("-")
    identifier = owner + "/" + slug
    metadata = {
        "id": identifier, "title": "VidBest " + mode + " " + suffix,
        "code_file": "gpu_job.py", "language": "python", "kernel_type": "script",
        "is_private": True, "enable_gpu": True, "machine_shape": "NvidiaTeslaT4",
        "enable_internet": mode == "pose-ai",
        "dataset_sources": [], "competition_sources": [], "kernel_sources": [], "model_sources": []
    }
    (output / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return identifier


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--username", required=True)
    p.add_argument("--mode", choices=sorted(MODES), default="probe")
    p.add_argument("--minutes", type=int, default=8)
    p.add_argument("--job-id", default="trial")
    p.add_argument("--out", type=Path, default=Path("kaggle-studio/job"))
    p.add_argument("--submit", action="store_true")
    a = p.parse_args()
    kernel = create_job(a.out, a.username, a.mode, a.minutes, a.job_id)
    print("Private Kaggle kernel:", kernel, flush=True)
    if not a.submit:
        print("Dry-run: no GPU time used.")
        return
    if not os.environ.get("KAGGLE_API_TOKEN"):
        raise RuntimeError("Missing KAGGLE_API_TOKEN repository secret: not submitted")
    subprocess.run(
        ["kaggle", "kernels", "push", "-p", str(a.out.resolve()), "--accelerator",
         "NvidiaTeslaT4", "-t", str(a.minutes * 60)],
        check=True,
    )
    print("Submission accepted; completion NOT yet verified:", kernel, flush=True)
    print("Check in Kaggle or use: kaggle kernels status " + kernel)


if __name__ == "__main__":
    main()
