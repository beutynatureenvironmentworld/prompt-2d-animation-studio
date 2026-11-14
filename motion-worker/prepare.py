"""Generate reusable motion independently of art, lighting and camera work."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("prompt")
parser.add_argument("directory", type=Path)
args = parser.parse_args()
if not args.prompt.strip():
    parser.error("Supply a character movement prompt")
dest = args.directory.resolve()
dest.parent.mkdir(parents=True, exist_ok=True)
if dest.exists():
    parser.error("Choose a new clip directory")
runtime = Path(os.environ.get("SPRONG_HOME", here)).resolve()
with tempfile.TemporaryDirectory(dir=dest.parent) as staging:
    clip = Path(staging) / "clip"
    clip.mkdir()
    bvh = clip / "motion.bvh"
    subprocess.run([runtime / "runtime/build/examples/01_hello", runtime / "model.gguf",
                    args.prompt, bvh], check=True)
    subprocess.run(["blender", "-b", "--factory-startup", "-t", "1",
                    "--python-exit-code", "1", "-P", here / "export_pose.py",
                    "--", bvh, clip / "pose.json"], check=True)
    (clip / "prompt.txt").write_text(args.prompt)
    clip.rename(dest)
