#!/usr/bin/env python3
"""Offline-only GPU/provider readiness report; never reads or prints secret values."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "hybrid-gpu/setup.py", "hybrid-gpu/hybrid.py", "hybrid-gpu/notebook.py",
    "hybrid-gpu/orchestrator.py", "hybrid-gpu/kaggle_job.py",
    "hybrid-gpu/Start_Here.ipynb", ".github/workflows/hybrid-gpu.yml",
    ".github/workflows/comfy-video-check.yml",
)


def inspect(root=ROOT, environ=None):
    root = Path(root)
    env = os.environ if environ is None else environ
    graphs = {}
    for model in ("ltx", "wan", "toon"):
        path = root / "hybrid-gpu" / (model + "-api.json")
        try:
            graph = json.loads(path.read_text(encoding="utf8"))
            valid = isinstance(graph, dict) and bool(graph) and all(
                isinstance(v, dict) and "class_type" in v and "inputs" in v
                for v in graph.values()
            )
        except (OSError, ValueError, TypeError):
            valid = False
        graphs[model] = {"exists": path.is_file(), "valid_json": valid}
    gpu = False
    try:
        if importlib.util.find_spec("torch"):
            import torch
            gpu = bool(torch.cuda.is_available())
    except Exception:
        gpu = False
    return {
        "scope": "offline checks ONLY: no provider login, GPU inference, upload, or billing",
        "repository": {
            "required_files_present": all((root / file).is_file() for file in REQUIRED),
            "comfy_graphs": graphs,
        },
        "system": {
            "python": sys.version.split()[0],
            "ffmpeg_installed": bool(shutil.which("ffmpeg")),
            "git_installed": bool(shutil.which("git")),
            "cuda_accessible": gpu,
        },
        "providers": {
            "kaggle": {
                "dispatcher_present": (root / "hybrid-gpu/kaggle_job.py").is_file(),
                "cli_available": bool(shutil.which("kaggle")),
                "account_fields_set": bool(env.get("KAGGLE_USERNAME")) and bool(
                    env.get("KAGGLE_API_TOKEN") or env.get("KAGGLE_KEY")
                ),
                "gpu_video_render_verified": False,
            },
            "colab": {
                "notebook_ready": (root / "hybrid-gpu/Start_Here.ipynb").is_file(),
                "requires_interactive_gpu_session": True,
                "gpu_video_render_verified": False,
            },
            "lightning": {
                "requires_user_studio_and_credits": True,
                "gpu_video_render_verified": False,
            },
            "hf_zerogpu": {
                "example_config_ready": (root / "hybrid-gpu/ltx-space.json").is_file(),
                "requires_live_space_api_verification": True,
                "gpu_video_render_verified": False,
            },
        },
        "r2": {
            "optional": True,
            "configuration_fields_set": all(bool(env.get(name)) for name in (
                "R2_BUCKET", "R2_ENDPOINT", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
            )),
            "connection_verified": False,
        },
        "cpu_fallback": "previously validated in separate GitHub Actions run",
        "video_output_rate_verified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = json.dumps(inspect(args.root), ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        if args.json_out.exists():
            parser.error("refusing to overwrite existing report")
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(result, encoding="utf8")
    print(result, end="")


if __name__ == "__main__":
    main()
