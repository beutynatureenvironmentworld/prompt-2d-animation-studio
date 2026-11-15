#!/usr/bin/env python3
"""Create a real silent cartoon + GPU notebook + CPU fallback without any paid API."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("ltx", "wan", "toon")

def invoke(*args, env=None):
    subprocess.run([str(a) for a in args], cwd=ROOT, env=env, check=True)

def metadata(path):
    data = subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    return json.loads(data)

def main():
    parser = argparse.ArgumentParser(description="No-GPU, no-R2 CPU animation handoff smoke test")
    parser.add_argument("--model", choices=MODELS, default="ltx")
    parser.add_argument("--output", type=Path, default=Path("handoff-test"))
    args = parser.parse_args()
    out = (ROOT / args.output).resolve()
    if not out.is_relative_to(ROOT.resolve()):
        parser.error("Output must be inside project")
    if out.exists() and any(out.iterdir()):
        parser.error("Output folder must be new or empty (no overwrite)")
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    for secret in ("R2_BUCKET", "KAGGLE_API_TOKEN", "KAGGLE_USERNAME"):
        env.pop(secret, None)
    base = out / "original-silent-cartoon.mp4"
    storyboard = out / "editable-cartoon-storyboard.json"
    invoke("/usr/bin/python3" if Path("/usr/bin/python3").exists() else sys.executable,
           "snap2d/rapid_cartoon.py", "--prompt", "shots: sneak, glare, chase, shock",
           "--width", "360", "--fps", "24", "--save-storyboard", storyboard,
           "--output", base, env=env)
    original = metadata(base)
    video = [s for s in original["streams"] if s["codec_type"]=="video"]
    assert len(video)==1 and video[0]["codec_name"]=="h264"
    assert (int(video[0]["width"]),int(video[0]["height"]))==(360,640)
    assert not any(s["codec_type"]=="audio" for s in original["streams"])
    duration = float(original["format"]["duration"])
    if duration < 3:
        raise ValueError("Cartoon is too short for trial")
    shots=[{"start_frame":24,"frames":24,"seed":24,
            "prompt":"An expressive cartoon character quickly reacts in surprise"}]
    plan=out/"gpu-shot-plan.json"
    plan.write_text(json.dumps(shots, indent=2)+"\n", encoding="utf8")
    bundle=out/"gpu-handoff-bundle.zip"
    invoke(sys.executable, "hybrid-gpu/hybrid.py", "pack", base, plan, bundle, env=env)
    invoke(sys.executable, "hybrid-gpu/orchestrator.py", bundle, out/"renders", "--model", args.model, env=env)
    hashval=hashlib.sha256(bundle.read_bytes()).hexdigest()
    folder=out/"renders"/hashval/args.model
    result=folder/"episode.mp4"
    notebook=folder/"interactive.ipynb"
    report=folder/"report.json"
    assert all(p.is_file() and p.stat().st_size>0 for p in (result, notebook, report, bundle))
    assert json.loads(report.read_text())[0]["source"]=="Oracle CPU"
    parsed=json.loads(notebook.read_text())
    assert parsed["nbformat"]==4 and len(parsed["cells"])>=4
    final=metadata(result)
    assert any(s["codec_type"]=="video" and s["codec_name"]=="h264" for s in final["streams"])
    assert abs(float(final["format"]["duration"])-duration)<0.5
    shutil.copy2(result, out/"watch-me-silent.mp4")
    shutil.copy2(notebook, out/"gpu-trial-notebook.ipynb")
    summary={"gpu_used":False,"paid_api_used":False,"r2_used":False,"model_notebook":args.model,
             "cpu_fallback_verified":True,"seconds":round(duration,2),
             "format":"H.264 360x640, silent", "r2_optional":True}
    (out/"test-result.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf8")
    print("CPU_GPU_HANDOFF_PASS",json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
