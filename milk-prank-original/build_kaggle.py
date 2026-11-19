"""Build one PRIVATE Kaggle CPU kernel containing the exact Snore Collector drawing engine.
No GPU requested. No keys or weights are embedded in the job.
"""
import base64
import json
import os
import textwrap
from pathlib import Path

ARTIFACTS = {
    "art.cjs": Path("milk-prank-original/art.cjs"),
    "story.json": Path("milk-prank-original/story.json"),
    "audio.py": Path("milk-prank-original/audio.py"),
    "scene.cjs": Path("midnight-jar/scene.cjs"),
    "render.py": Path("midnight-jar/render.py"),
}
destination = Path(os.environ.get("FTE_KAGGLE_BUILD_DIR", "/tmp/fte-original-style-milk-prank"))
destination.mkdir(parents=True, exist_ok=True)
files = {name: base64.b64encode(path.read_bytes()).decode("ascii") for name, path in ARTIFACTS.items()}
slug = "fte-snore-engine-milk-prank-" + os.environ["GITHUB_RUN_ID"]
kid = os.environ["KAGGLE_USERNAME"] + "/" + slug

script = '''
import base64, json, os, shutil, subprocess, sys, traceback, ctypes.util
from pathlib import Path
WORK=Path("/kaggle/working") if Path("/kaggle/working").is_dir() else Path.cwd()
OUT=WORK/"FTE_Snore_Engine_Milk_Prank"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"RESULT.json"
files=__ASSETS__
def run(cmd,timeout=300,cwd=None):
 print("FTE_EXEC",cmd,flush=True)
 subprocess.run(cmd,check=True,timeout=timeout,cwd=cwd)
def write(x):REPORT.write_text(json.dumps(x,indent=2,default=str)+chr(10))
state={"status":"initializing","engine":"original Snore Collector SVG+librsvg+FFmpeg",
       "model":"procedural original 2D / no neural image generation",
       "gpu_requested":False,"h3_inference_verified":False,"video_verified":False}
write(state)
try:
  src=WORK/"fte_reference_original_engine"
  src.mkdir(parents=True,exist_ok=True)
  for name,blob in files.items():
   (src/name).write_bytes(base64.b64decode(blob))
  if not shutil.which("node") or not shutil.which("ffmpeg") or not ctypes.util.find_library("rsvg-2"):
   run(["apt-get","update","-qq"],200)
   run(["apt-get","install","-y","-qq","nodejs","ffmpeg","librsvg2-2","libcairo2"],400)
  run(["node","--check","art.cjs"],20,cwd=src)
  run([sys.executable,"render.py","story.json",str(OUT/"silent.mp4"),
       "--width","540","--fps","24"],1300,cwd=src)
  run([sys.executable,"audio.py",str(OUT)],70,cwd=src)
  target=OUT/"Funny_Toon_Ever_Milk_Prank_Kaggle_Original_Engine.mp4"
  run(["ffmpeg","-y","-loglevel","error","-i",str(OUT/"silent.mp4"),
       "-i",str(OUT/"original_comedy_sfx.wav"),"-map","0:v:0","-map","1:a:0",
       "-vf","scale=1080:1920:flags=lanczos,format=yuv420p",
       "-r","24","-c:v","libx264","-preset","veryfast","-crf","20",
       "-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",str(target)],500)
  p=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams",
               "-show_format","-of","json",str(target)],text=True,timeout=30))
  video=next(q for q in p["streams"] if q["codec_type"]=="video")
  audio=any(q["codec_type"]=="audio" for q in p["streams"])
  duration=float(p["format"]["duration"])
  verified=(video["width"]==1080 and video["height"]==1920 and
            duration>=14.8 and audio and video["codec_name"]=="h264")
  state.update({"status":"completed" if verified else "failed_quality",
     "video":str(target),"width":video["width"],"height":video["height"],
     "seconds":duration,"has_audio":audio,"video_verified":verified,
     "storyboard_shots":5,"reference_source":"repo midnight-jar/art.cjs"})
  write(state)
  print("KAGGLE_FTE_REFERENCE_STYLE_RESULT",json.dumps(state),flush=True)
  if not verified:raise RuntimeError("ffprobe genuine video quality gates failed")
except Exception as exc:
  state.update({"status":"error","video_verified":False,
    "error":str(exc),"traceback_tail":traceback.format_exc()[-4000:]})
  write(state)
  raise
'''.replace("__ASSETS__", repr(files))
# Keep the Python notebook's source fully standalone (Kaggle only needs runner.py).
(destination / "runner.py").write_text(script)
metadata = {
  "id":kid,"title":slug,"code_file":"runner.py",
  "language":"python","kernel_type":"script","is_private":True,
  "enable_gpu":False,"enable_internet":True,
  "dataset_sources":[],"kernel_sources":[],"competition_sources":[],"model_sources":[]
}
(destination/"kernel-metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
print("FTE_KAGGLE_ORIGINAL_ENGINE_ID",kid,flush=True)
Path("milk-prank-original/KAGGLE_KERNEL_ID.txt").write_text(kid+"\n")
