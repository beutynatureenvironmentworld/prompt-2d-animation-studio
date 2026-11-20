#!/usr/bin/env python3
"""Make one small authentic Wan2.2 and/or LTX2.3 community ZeroGPU I2V trial.

No fabricated MP4 fallback. Reads generated original flat-2D PNG. Runs anonymously,
queues can be full or require sign-in. Each provider is requested at most once.
Writes explicit diagnostic JSON. Only successful, decoded MP4s count as results.
"""
import json,time,os,subprocess
from pathlib import Path
import requests
ROOT=Path("modal-toon/outputs")
ROOT.mkdir(parents=True,exist_ok=True)
IMAGE=ROOT/"flat_2d_puffgirl_start.png"
PROMPT=(
    "Original simple flat 2D cartoon on plain ivory background. Consistent two cartoon characters with VERY simple "
    "solid color shapes and thick black outlines. On LEFT brown-skinned boy with a sideways black cap blue shirt and "
    "a red microphone sings happily, excited eyes, opens mouth, bobs his head and swings an arm in vigorous FAST gestures. "
    "On RIGHT light peach skin girl with TWO large brown PUFF BUNS, large expressive one-winking eye, thin black stick "
    "legs and curved black stick arms, a simple turquoise triangular dress and teal shoes dances briskly, "
    "hops on one foot, pumps both arms and sways her torso with elastic natural movement. Fast energetic comic timing, "
    "fluid decisive 2D animated poses, natural weight shift, all character details and light peach skin preserved. "
    "Simple FlipaClip-like 2D hand drawn animation, no 3D lighting, no gradients, clean consistent flat background, no words."
)
NEG=("photorealistic, 3D, painted shading, texture, glossy, slow puppet motion, static character, "
     "stiff frozen pose, extra arms and legs, change of outfits, morphing faces, losing the buns, watermark, text")
PROVIDERS=[
 ("wan22","https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space",
   lambda ref:[ref,PROMPT,6,NEG,2.0,1,1,61124,False]),
 ("ltx23","https://lightricks-ltx-2-3.hf.space",
   lambda ref:[ref,PROMPT,2.0,False,61124,False,768,448]),
]
session=requests.Session()
session.headers["User-Agent"]="FastToonOriginal2D/1.0"
errors=[]
for name,base,build in PROVIDERS:
  try:
    print("TRYING_PROVIDER",name,flush=True)
    with IMAGE.open("rb") as file:
      response=session.post(base+"/gradio_api/upload",
          files={"files":(IMAGE.name,file,"image/png")},timeout=40)
    response.raise_for_status()
    uploaded=response.json()[0]
    file_data={"path":uploaded,"meta":{"_type":"gradio.FileData"}}
    req=session.post(base+"/gradio_api/call/generate_video",
        json={"data":build(file_data)},timeout=40)
    req.raise_for_status()
    event_id=req.json()["event_id"]
    print("PROVIDER_QUEUED",name,event_id,flush=True)
    stream=session.get(base+"/gradio_api/call/generate_video/"+event_id,
        stream=True,timeout=(20,160))
    stream.raise_for_status()
    event=""
    got_video=False
    for raw in stream.iter_lines(decode_unicode=True):
      if not raw: continue
      line=raw.decode("utf-8") if isinstance(raw,bytes) else raw
      if line.startswith("event:"):
        event=line.split(":",1)[1].strip()
        if event=="error":raise RuntimeError("Remote ZeroGPU event:error")
      elif line.startswith("data:"):
        try:data=json.loads(line.split(":",1)[1].strip())
        except Exception:continue
        if event=="complete":
          if not isinstance(data,list) or not data or not isinstance(data[0],dict) or "url" not in data[0]:
            raise RuntimeError("Complete without video output URL")
          result=session.get(data[0]["url"],timeout=70)
          result.raise_for_status()
          if len(result.content)<10000 or b"ftyp" not in result.content[:100]:
            raise RuntimeError("Result not a plausible MP4")
          dest=ROOT/("Flat2D_PuffGirl_Real_"+name.upper()+"_GPU.mp4")
          dest.write_bytes(result.content)
          # Decode at least one frame, not just detect header.
          check=subprocess.run(["ffmpeg","-v","error","-i",str(dest),"-frames:v","1","-f","null","-"],
              capture_output=True,text=True,timeout=30)
          if check.returncode:raise RuntimeError("MP4 does not decode: "+check.stderr[:300])
          print("VIDEO_VERIFIED",str(dest),len(result.content),flush=True)
          got_video=True
          break
    stream.close()
    if not got_video:raise RuntimeError("Stream closed without MP4")
  except Exception as exc:
    print("PROVIDER_FAILED",name,type(exc).__name__,str(exc)[:250],flush=True)
    errors.append({"provider":name,"error":type(exc).__name__+": "+str(exc)[:500]})
(ROOT/"zerogpu_attempts.json").write_text(json.dumps(errors,indent=2))
print("SUCCESSFUL_GPU_VIDEO_COUNT",len(list(ROOT.glob("Flat2D_PuffGirl_Real_*_GPU.mp4"))),flush=True)
