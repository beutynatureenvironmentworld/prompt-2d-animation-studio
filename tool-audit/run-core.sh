#!/usr/bin/env bash
set -Eeuo pipefail
TOOL="$1"; OUT="tool-audit/results/$TOOL"
mkdir -p "$OUT"
echo "TOOL=$TOOL" > "$OUT/report.txt"
finish(){ rc=$?; echo "RESULT=$([ "$rc" -eq 0 ] && echo PASS || echo FAIL)" >> "$OUT/report.txt"; echo "EXIT=$rc" >> "$OUT/report.txt"; }
trap finish EXIT
case "$TOOL" in
ffmpeg)
  ffmpeg -hide_banner -loglevel error -y -f lavfi -i testsrc2=s=160x90:r=12 -t 1 -an -c:v libx264 -pix_fmt yuv420p "$OUT/test.mp4"
  test -s "$OUT/test.mp4"
  echo 'SCOPE=actual MP4 render' >> "$OUT/report.txt";;
blender)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends blender
  blender -b --factory-startup --python-exit-code 1 --python cpu-anime/blender_cpu_test.py
  test -n "$(find cpu-anime/out/blender-smoke -type f -name '*.png' -size +100c -print -quit)"
  echo 'SCOPE=actual Blender CPU frame rendering' >> "$OUT/report.txt";;
synfig)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends synfig
  synfig /usr/share/synfig/plugins/add-skeleton-simple/stickman.sif -o "$OUT/frame.png" -t png -w 320 -h 180
  test -n "$(find "$OUT" -name '*.png' -type f -print -quit)"
  echo 'SCOPE=actual Synfig vector stickman rendering' >> "$OUT/report.txt";;
inkscape)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends inkscape
  echo '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="80"><circle cx="50" cy="40" r="20" fill="#98bdff"/></svg>' > "$OUT/input.svg"
  timeout 40 inkscape "$OUT/input.svg" --export-filename="$OUT/image.png"
  test -s "$OUT/image.png"
  echo 'SCOPE=actual SVG vector rasterization' >> "$OUT/report.txt";;
manim)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends ffmpeg libcairo2-dev libpango1.0-dev pkg-config
  python -m pip install --no-cache-dir manim
  echo 'from manim import *
class DotMove(Scene):
 def construct(self):
  p=Dot()
  self.add(p)
  self.play(p.animate.shift(RIGHT),run_time=.3)' > "$OUT/smoke.py"
  manim -ql --disable_caching --media_dir "$OUT/media" "$OUT/smoke.py" DotMove
  test -n "$(find "$OUT/media" -name '*.mp4' -size +100c -print -quit)"
  echo 'SCOPE=actual Manim MP4 scene rendering' >> "$OUT/report.txt";;
moviepy)
  python -m pip install --no-cache-dir moviepy
  python - "$OUT/moviepy.mp4" <<'PY'
from moviepy import ColorClip
import sys
c=ColorClip(size=(160,90),color=(20,70,180),duration=1)
c.write_videofile(sys.argv[1],fps=12,codec="libx264",audio=False,logger=None)
c.close()
PY
  test -s "$OUT/moviepy.mp4"
  echo 'SCOPE=actual MoviePy MP4 rendering' >> "$OUT/report.txt";;
rhubarb)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends unzip
  curl -fLsS --retry 2 --max-time 150 -o "$OUT/pkg.zip" https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip
  unzip -q "$OUT/pkg.zip" -d "$OUT/bin"
  CLI="$(find "$OUT/bin" -type f -name rhubarb -print -quit)"
  test -n "$CLI"; chmod +x "$CLI"
  python - "$OUT/voice.wav" <<'PY'
import sys,wave,math,struct
with wave.open(sys.argv[1],"wb") as f:
 f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000)
 f.writeframes(b"".join(struct.pack("<h",int(8000*math.sin(2*math.pi*220*i/16000))) for i in range(16000)))
PY
  "$CLI" -r phonetic -f json -o "$OUT/cues.json" "$OUT/voice.wav"
  python - "$OUT/cues.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]));assert isinstance(d["mouthCues"],list)
print("Rhubarb mouth cues",len(d["mouthCues"]))
PY
  rm "$OUT/pkg.zip"
  echo 'SCOPE=actual audio analysis and mouth-cue JSON; synthetic tone, no speech quality validation' >> "$OUT/report.txt";;
potrace)
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends potrace
  printf 'P1\n5 5\n0 0 0 0 0\n0 1 1 1 0\n0 1 1 1 0\n0 1 1 1 0\n0 0 0 0 0\n' > "$OUT/in.pbm"
  potrace -s "$OUT/in.pbm" -o "$OUT/out.svg"
  grep -q '<svg' "$OUT/out.svg"
  echo 'SCOPE=actual PBM to SVG conversion' >> "$OUT/report.txt";;
vtracer)
  python -m pip install --no-cache-dir vtracer Pillow
  python - "$OUT/in.png" <<'PY'
from PIL import Image,ImageDraw
import sys
a=Image.new("RGB",(40,40),"white");ImageDraw.Draw(a).ellipse((2,2,35,35),fill="navy");a.save(sys.argv[1])
PY
  vtracer --input "$OUT/in.png" --output "$OUT/out.svg"
  grep -q '<svg' "$OUT/out.svg"
  echo 'SCOPE=actual PNG to SVG conversion' >> "$OUT/report.txt";;
mediapipe)
  python -m pip install --no-cache-dir mediapipe
  python - <<'PY'
import numpy as np
import mediapipe as mp
i=mp.Image(image_format=mp.ImageFormat.SRGB,data=np.zeros((16,16,3),dtype=np.uint8))
assert i.width==16
print("Mediapipe import + Image API",mp.__version__)
PY
  echo 'SCOPE=import and image API only; pose estimation needs model weights' >> "$OUT/report.txt";;
piper)
  python -m pip install --no-cache-dir piper-tts
  python - <<'PY'
import piper
print("Piper import successful",piper.__file__)
PY
  echo 'SCOPE=TTS engine import only; no licensed voice model, no speech synthesis' >> "$OUT/report.txt";;
edge-tts)
  python -m pip install --no-cache-dir edge-tts
  python - <<'PY'
import edge_tts
print("Edge TTS Python client import successful",edge_tts.__file__)
PY
  echo 'SCOPE=online TTS client import only; NOT offline open-source voice backend' >> "$OUT/report.txt";;
*) echo "Unknown tool $TOOL";exit 2;;
esac
echo "SUCCESS $TOOL"
