"""Run the Oracle shared workflow from a scene prompt and optional motion direction."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
studio = here.parent / "kinetic-studio"
lab = here / "cpu-lab"
parser = argparse.ArgumentParser()
parser.add_argument("prompt")
parser.add_argument("output", type=Path)
parser.add_argument("--motion", help="Describe the actor's movement in English. Defaults to the scene prompt.")
parser.add_argument("--clip", type=Path, help="Reuse a prepared motion directory")
source = parser.add_mutually_exclusive_group()
source.add_argument("--background",help="Generate a background once with SD Turbo")
source.add_argument("--plate",type=Path,help="Reuse a PNG plate from another worker")
parser.add_argument("--width",choices=("360","540","720"),default="540")
args = parser.parse_args()
target = args.output.resolve()
target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():
    parser.error("Choose a new output directory")
with tempfile.TemporaryDirectory(dir=target.parent) as temp:
    job = Path(temp) / "episode"
    job.mkdir()
    clip = args.clip.resolve() if args.clip else job/"character"
    if not args.clip:
        subprocess.run(["python3",here/"prepare.py",args.motion or args.prompt,clip],check=True)
    plate = args.plate.resolve() if args.plate else None
    if args.background:
        plate = job/"background.png"
        env = os.environ.copy()
        env.setdefault("SD_BIN",str(studio/"diffusion-runtime/ubuntu24/sd-cli"))
        env.setdefault("SD_MODEL",str(lab/"background.gguf"))
        subprocess.run(["bash",here/"cpu-background.sh",args.background,plate],env=env,check=True)
    command=["/usr/bin/python3",studio/"film.py",args.prompt,job/"render",
             "--width",args.width,"--motion-clip",clip]
    if plate:
        command.extend(["--background-plate",plate])
    subprocess.run(command,check=True)
    (job/"settings.json").write_text(json.dumps(vars(args),default=str,indent=2))
    job.rename(target)
