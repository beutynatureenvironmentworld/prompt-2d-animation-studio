"""Submit three aligned tracks to a local ComfyUI instance and copy its mixed FLAC."""
import argparse
import json
import shutil
import time
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

here = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("comfy",type=Path)
parser.add_argument("output",type=Path)
for track in ("voice","music","effects"):
    parser.add_argument(track,type=Path)
args = parser.parse_args()
graph = json.loads((here/"comfy-audio-api.json").read_text())
ticket = uuid.uuid4().hex
root = args.comfy.resolve()
job = root / "input"
job.mkdir(parents=True,exist_ok=True)
staged=[]
def call(route, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = Request("http://127.0.0.1:8188/" + route, data,
                  headers={"Content-Type":"application/json"})
    with urlopen(req,timeout=20) as response:
        return json.load(response)
try:
    for node,source in enumerate((args.voice,args.music,args.effects),1):
        name = f"{ticket}-{node}{source.suffix}"
        staged.append(job/name)
        shutil.copyfile(source,job/name)
        graph[str(node)]["inputs"]["audio"] = name
    result=call("prompt",{"prompt":graph,"client_id":ticket})
    pid=result["prompt_id"]
    for _ in range(300):
        history=call("history/"+pid)
        if pid in history:
            record=history[pid]
            if record["status"]["status_str"] != "success":
                raise RuntimeError(record["status"])
            saved=record["outputs"]["6"]["audio"][0]
            src=root/"output"/saved["subfolder"]/saved["filename"]
            args.output.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,args.output)
            break
        time.sleep(2)
    else:
        raise TimeoutError("Local ComfyUI audio job exceeded ten minutes")
finally:
    for item in staged:
        item.unlink(missing_ok=True)
