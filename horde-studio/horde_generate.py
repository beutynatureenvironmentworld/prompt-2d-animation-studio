"""Generate real new anime stills using AI Horde; do not reuse any previous CPU video."""
import os,json,time,urllib.request,urllib.error,urllib.parse,base64,io
from pathlib import Path
from PIL import Image
ROOT="https://stablehorde.net/api/v2"
KEY=os.environ.get("AI_HORDE_API_KEY","").strip()
AGENT="VidBestStudio:0.1:https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio"
OUT=Path("horde-studio/generated")
OUT.mkdir(parents=True,exist_ok=True)
SCENES=[
 ("01_cat_chase","original funny 2D hand drawn anime, blue haired lanky cartoon boy in mustard hoodie is startled as an orange ginger cat runs off with an oversized pink glazed doughnut, expressive eyes wide open, running comedy pose, pastel olive green background"),
 ("02_cartoon_trip","original funny 2D hand drawn anime, blue haired lanky cartoon boy in mustard hoodie slides on a banana peel, arms flailing and mouth open in shock, orange ginger cat holds a pink glazed doughnut, playful action pose, pastel olive green background"),
 ("03_silly_end","original funny 2D hand drawn anime, blue haired lanky cartoon boy in mustard hoodie sitting with pink glazed doughnut on head like silly hat, ginger cat laughing beside him, expressive anime faces, charming comedy ending, pastel olive green background")
]
NEG="photorealism, realistic photograph, 3d render, dull colors, bad anatomy, extra limbs, watermark, text, nsfw"
def api(path, data=None,timeout=30):
    if not KEY:raise RuntimeError("Missing GitHub AI_HORDE_API_KEY secret")
    headers={"apikey":KEY,"Client-Agent":AGENT,"Accept":"application/json"}
    payload=None
    if data is not None:
        headers["Content-Type"]="application/json"
        payload=json.dumps(data).encode()
    req=urllib.request.Request(ROOT+path,headers=headers,data=payload,method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req,timeout=timeout) as resp:
            return json.loads(resp.read(1000000))
    except urllib.error.HTTPError as e:
        raise RuntimeError("Horde HTTP "+str(e.code)+" for "+path.split("/")[-2]) from None
    except (urllib.error.URLError,TimeoutError):
        raise RuntimeError("Horde connection unavailable") from None
def image_save(result,path):
    value=result.get("img") or result.get("image")
    if not isinstance(value,str):raise ValueError("No result image field")
    if value.startswith("https://"):
        with urllib.request.urlopen(urllib.request.Request(value,headers={"User-Agent":AGENT}),timeout=50) as response:
            body=response.read(12000000)
    elif value.startswith("data:image/"):
        body=base64.b64decode(value.partition(",")[2])
    else: raise ValueError("No usable image URL")
    with Image.open(io.BytesIO(body)) as im:
        im.load()
        if im.width<256 or im.height<256:raise ValueError("Image too small")
        im.convert("RGB").save(path,format="PNG")
def main():
    user=api("/find_user")
    if not user.get("username") or str(user["username"]).lower()=="anonymous":
        raise RuntimeError("Horde key did not authenticate")
    print("HORDE_AUTHENTICATED",flush=True)
    requests={}; failures={}; complete={}
    started=time.monotonic()
    for i,(slug,description) in enumerate(SCENES):
        try:
            payload={"prompt":description+", high quality cel shaded anime, bold ink outlines, vivid funny pose, full body, vertical 9:16 ### "+NEG,
              "params":{"sampler_name":"k_euler_a","steps":16,"cfg_scale":7,"width":512,"height":768,"n":1,"seed":str(72070+i)},
              "nsfw":False,"censor_nsfw":True,"shared":False,"r2":True,"models":["stable_diffusion"]}
            result=api("/generate/async",payload)
            id=result.get("id")
            if not isinstance(id,str) or len(id)<12:raise ValueError("Invalid request id")
            requests[slug]=id
            print("NEW_AI_IMAGE_SUBMITTED",slug,id,flush=True)
        except Exception as e:
            failures[slug]=str(e)
            print("HORDE_SUBMIT_ERROR",slug,type(e).__name__,flush=True)
    (OUT/"submitted-ids.json").write_text(json.dumps(requests,indent=2)+"\n")
    for round_no in range(36):
        if not requests:break
        for slug,id in list(requests.items()):
            try:
                check=api("/generate/check/"+id,timeout=20)
                if check.get("faulted"):
                    failures[slug]="faulted";del requests[slug];continue
                if check.get("done"):
                    result=api("/generate/status/"+id,timeout=30)
                    images=result.get("generations") or []
                    if not images:raise ValueError("Horde completed without images")
                    file=OUT/(slug+".png")
                    image_save(images[0],file)
                    complete[slug]={"file":file.name,"model":images[0].get("model","unknown"),"bytes":file.stat().st_size}
                    print("REAL_NEW_AI_FRAME_OK",slug,file.stat().st_size,flush=True)
                    del requests[slug]
            except Exception as e:
                print("HORDE_CHECK_WARNING",slug,type(e).__name__,flush=True)
        if requests:
            print("HORDE_WAITING",len(requests),"elapsed",int(time.monotonic()-started),flush=True)
            time.sleep(12)
    for slug,id in requests.items():failures[slug]="still_queued_timeout"
    status={"original_ai_stills_generated":len(complete),"completed":complete,"pending":requests,
            "failures":failures,"gpu_generated_motion":False,
            "note":"Each completed PNG is a new AI Horde image. No video diffusion yet."}
    (OUT/"status.json").write_text(json.dumps(status,indent=2)+"\n")
    if not complete:raise RuntimeError("No new AI frames. No old Snap2D substitution.")
    print("NEW_HORDE_FRAME_COUNT",len(complete),flush=True)
if __name__=="__main__":main()
