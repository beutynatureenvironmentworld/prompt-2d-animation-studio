"""ONE real AI Horde img2img trial on an InkRig body-motion keyframe.
Only the image inference is AI; never claim the full rig-video is diffusion video.
"""
import base64,io,json,os,time,urllib.request,urllib.error
from pathlib import Path
from PIL import Image,ImageChops
BASE="https://stablehorde.net/api/v2"
SOURCE=Path("horde-guided/pose-source.png")
OUT=Path("horde-guided/output");OUT.mkdir(parents=True,exist_ok=True)
KEY=os.environ.get("AI_HORDE_API_KEY","").strip()
AGENT="VidBestStudio:0.2:https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio"
if not KEY:raise SystemExit("Missing AI Horde GitHub Actions secret")
def request(path,payload=None):
    headers={"apikey":KEY,"Client-Agent":AGENT,"Accept":"application/json"}
    data=None
    if payload is not None:
        headers["Content-Type"]="application/json"
        data=json.dumps(payload).encode("utf8")
    req=urllib.request.Request(BASE+path,data=data,headers=headers,
        method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req,timeout=35) as r:
            return json.loads(r.read(2500000))
    except urllib.error.HTTPError as e:
        raise RuntimeError("AI Horde HTTP "+str(e.code)+" at "+path.split("/")[1]) from None
p=SOURCE.read_bytes()
with Image.open(io.BytesIO(p)) as im:
    assert im.size==(512,768)
payload={
 "prompt":("original simple hand drawn 2D animated cartoon frame, same one boy with a yellow shirt, "
           "black expressive eyes, four limbs with natural bend, surprised reaction, one orange funny cat, "
           "olive flat studio background, preserve exact character location and body pose of source, "
           "crisp black ink cel animation, hand drawn 2D cartoon, very clear face, high quality"
           " ### extra fingers, extra limbs, distorted face, photo, 3D render, watermarks, text"),
 "source_image":base64.b64encode(p).decode("ascii"),
 "source_processing":"img2img",
 "params":{"width":512,"height":768,"steps":18,"cfg_scale":6.5,"n":1,
           "sampler_name":"k_euler_a","seed":"6021","denoising_strength":0.30},
 "models":["stable_diffusion"],"nsfw":False,"censor_nsfw":True,
 "shared":False,"r2":True,
}
start=time.monotonic()
result=request("/generate/async",payload)
job=result.get("id")
if not isinstance(job,str) or len(job)<15:
    raise SystemExit("AI Horde did not accept guided generation")
print("GUIDED_HORDE_ONE_IMAGE_SUBMITTED",job,flush=True)
report={"id":job,"mode":"img2img","source":"an original InkRig animated-body PNG",
        "source_processing":"img2img","denoising_strength":0.30,
        "new_ai_frame_verified":False,"queue_seconds":None,
        "note":"No video diffusion. A single style-guided still only."}
try:
    for index in range(21):
        s=request("/generate/check/"+job)
        if s.get("faulted"):
            report["status"]="worker_faulted";break
        if s.get("done"):
            info=request("/generate/status/"+job)
            generations=info.get("generations") or []
            if not generations:
                report["status"]="completed_without_image";break
            g=generations[0]
            url=g.get("img","")
            if not isinstance(url,str) or not url.startswith("https://"):
                report["status"]="bad_generated_image_location";break
            with urllib.request.urlopen(url,timeout=40) as resp:
                content=resp.read(12_000_000)
            with Image.open(io.BytesIO(content)) as i:
                i.load()
                i.convert("RGB").save(OUT/"original-pose-guided-horde-anime.png")
                image=i.convert("RGB").resize((512,768))
            with Image.open(SOURCE) as original:
                original=original.convert("RGB")
                bbox=ImageChops.difference(original,image).getbbox()
            if bbox is None:raise RuntimeError("No pixel differences from source; not AI restyle")
            report.update(status="generated",new_ai_frame_verified=True,
                    model=g.get("model","unknown"),
                    file="original-pose-guided-horde-anime.png",
                    image_bytes=(OUT/"original-pose-guided-horde-anime.png").stat().st_size)
            print("REAL_AI_HORDE_IMG2IMG_WITH_POSE_GUIDANCE_PASS",flush=True)
            break
        print("GUIDED_WAIT",index, "queue",s.get("wait_time"),flush=True)
        time.sleep(12)
    else:
        report["status"]="time_window_elapsed_no_image"
finally:
    report["queue_seconds"]=int(time.monotonic()-start)
    (OUT/"img2img-status.json").write_text(json.dumps(report,indent=2)+"\n")
if not report["new_ai_frame_verified"]:
    raise SystemExit("No real AI img2img image, do not claim success")
