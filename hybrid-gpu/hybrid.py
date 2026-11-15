"""Prepare, render, resume and assemble GPU shots inside an existing CPU episode."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from urllib.request import Request,urlopen
from zipfile import ZipFile,ZIP_DEFLATED

HERE=Path(__file__).resolve().parent
MODELS=("ltx","wan","toon")
FPS=24

def run(args):
    subprocess.run([str(v) for v in args],check=True)

def probe(path):
    data=subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",path])
    meta=json.loads(data)
    video=next(s for s in meta["streams"] if s["codec_type"]=="video")
    return video,float(meta["format"]["duration"])

def digest(path):
    with Path(path).open("rb") as f:
        h=hashlib.sha256()
        while block:=f.read(1024*1024):
            h.update(block)
        return h.hexdigest()

def prepare(base,plan,bundle):
    video,duration=probe(base)
    shots=json.loads(plan.read_text())
    previous=0
    for shot in shots:
        start=shot["start_frame"]
        count=shot["frames"]
        if type(start)!=int or type(count)!=int or count<2 or start<previous or start+count>round(duration*FPS):
            raise ValueError("Use sorted, nonoverlapping shot ranges inside the CPU video at 24 fps")
        if not shot["prompt"].strip():
            raise ValueError("Empty motion prompt")
        previous=start+count
    if not shots:raise ValueError("Add at least one GPU shot")
    manifest={"fps":FPS,"base_sha256":digest(base),"width":video["width"],"height":video["height"],"shots":shots}
    bundle.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=bundle.parent) as tmp:
        tmp=Path(tmp)
        with ZipFile(tmp/"bundle.zip","w",ZIP_DEFLATED) as archive:
            archive.writestr("scene.json",json.dumps(manifest))
            archive.write(base,"base.mp4")
            for i,shot in enumerate(shots):
                for name,frame in (("first",shot["start_frame"]),("last",shot["start_frame"]+shot["frames"]-1)):
                    path=tmp/f"{i}-{name}.png"
                    run(["ffmpeg","-loglevel","error","-ss",str(frame/FPS),"-i",base,"-frames:v","1","-y",path])
                    archive.write(path,path.name)
        (tmp/"bundle.zip").replace(bundle)

def extract(bundle,work):
    with ZipFile(bundle) as z:
        m=json.loads(z.read("scene.json"))
        for name in ["base.mp4"]+[f"{i}-{k}.png" for i in range(len(m["shots"])) for k in ("first","last")]:
            with z.open(name) as src,(work/name).open("wb") as dest:shutil.copyfileobj(src,dest)
    if digest(work/"base.mp4")!=m["base_sha256"]:raise ValueError("Damaged base video")
    return m

class Storage:
    def __init__(self):
        self.bucket=os.environ.get("R2_BUCKET")
        if self.bucket:
            import boto3
            self.client=boto3.client("s3",endpoint_url=os.environ["R2_ENDPOINT"],region_name="auto")
    def download(self,key,path):
        if not self.bucket:return False
        from botocore.exceptions import ClientError
        try:self.client.download_file(self.bucket,key,str(path))
        except ClientError as err:
            if err.response["Error"]["Code"] not in ("404","NoSuchKey","NotFound"):raise
            return False
        return True
    def upload(self,key,path):
        if self.bucket:self.client.upload_file(str(path),self.bucket,key)

def rpc(url,data=None):
    req=Request(url,data=json.dumps(data).encode() if data is not None else None,headers={"Content-Type":"application/json"})
    with urlopen(req,timeout=30) as response:return json.load(response)

@contextlib.contextmanager
def server(root):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1",0)); port=sock.getsockname()[1]
    address=f"http://127.0.0.1:{port}"
    with (root/"vidbest.log").open("w") as log:
        proc=subprocess.Popen([sys.executable,"main.py","--listen","127.0.0.1","--port",str(port),"--lowvram","--disable-auto-launch"],cwd=root,stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(180):
                if proc.poll() is not None:raise RuntimeError(f"ComfyUI exited. See {log.name}")
                try:rpc(address+"/system_stats");break
                except OSError:time.sleep(2)
            else:raise TimeoutError("ComfyUI startup timed out")
            yield address
        finally:
            proc.terminate()
            try:proc.wait(timeout=12)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()

def render(model,root,address,work,manifest,i,out):
    from PIL import Image,ImageOps
    graph=json.loads((HERE/(model+"-api.json")).read_text())
    shot=manifest["shots"][i]
    tall=manifest["height"]>manifest["width"]
    w,h=(320,512) if tall else (512,320)
    token=uuid.uuid4().hex
    names={}
    for name in ("first","last") if model=="toon" else ("first",):
        names[name]=f"{token}-{name}.png"
        with Image.open(work/f"{i}-{name}.png") as im:
            ImageOps.pad(im.convert("RGB"),(w,h)).save(root/"input"/names[name])
    graph["6"]["inputs"]["text"]=shot["prompt"]
    if model=="toon":
        graph["1"]["inputs"]["image"]=names["first"]
        graph["2"]["inputs"]["image"]=names["last"]
        graph["10"]["inputs"]["seed"]=shot.get("seed",42)
    else:
        ltx=model=="ltx"
        graph["78" if ltx else "52"]["inputs"]["image"]=names["first"]
        rate=24 if ltx else 16
        stride=8 if ltx else 4
        length=stride*max(1,round((shot["frames"]*rate/FPS-1)/stride))+1
        graph["95" if ltx else "50"]["inputs"].update(width=w,height=h,length=length)
        graph["72" if ltx else "3"]["inputs"]["noise_seed" if ltx else "seed"]=shot.get("seed",42)
    graph["99"]["inputs"]["filename_prefix"]=token+"/frame"
    pid=rpc(address+"/prompt",{"prompt":graph})["prompt_id"]
    while True:
        record=rpc(address+"/history/"+pid).get(pid)
        if record:break
        time.sleep(3)
    if record["status"]["status_str"]!="success":raise RuntimeError(str(record["status"])[:1600])
    files=record["outputs"]["99"]["images"]
    if len(files)<2:raise RuntimeError("Video model returned fewer than two frames")
    with tempfile.TemporaryDirectory(dir=work) as sequence:
        sequence=Path(sequence)
        for n,info in enumerate(files):
            image=root/"output"/info["subfolder"]/info["filename"]
            os.link(image,sequence/f"{n:05d}.png") if image.stat().st_dev==sequence.stat().st_dev else shutil.copyfile(image,sequence/f"{n:05d}.png")
        run(["ffmpeg","-loglevel","error","-framerate",f'{len(files)*FPS}/{shot["frames"]}',"-i",sequence/"%05d.png","-vf",f"fps={FPS},tpad=stop_mode=clone:stop_duration=1","-frames:v",shot["frames"],"-c:v","libx264","-pix_fmt","yuv420p","-y",out])
    shutil.rmtree(root/"output"/token)
    for name in names.values():(root/"input"/name).unlink(missing_ok=True)

def valid(path,frames):
    if not path.exists():return False
    try:
        video,_=probe(path)
        return int(video.get("nb_frames",0))==frames
    except (ValueError,StopIteration,subprocess.CalledProcessError):return False

def assemble(base,manifest,clips,output):
    selected=[(i,p) for i,p in enumerate(clips) if p is not None]
    if not selected:
        shutil.copyfile(base,output);return
    args=["ffmpeg","-v","error","-i",base]
    filters=["[0:v]fps=24,setpts=PTS-STARTPTS[base0]"]
    w,h=manifest["width"],manifest["height"]
    for j,(i,p) in enumerate(selected,1):
        args+=["-i",p]
        shot=manifest["shots"][i]; start=shot["start_frame"]
        filters.append(f"[{j}:v]fps=24,scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,setpts=PTS-STARTPTS+{start}/24/TB[v{j}]")
        filters.append(f"[base{j-1}][v{j}]overlay=eof_action=pass:enable='between(n,{start},{start+shot['frames']-1})'[base{j}]")
    run(args+["-filter_complex_threads","1","-filter_complex",";".join(filters),"-map",f"[base{len(selected)}]","-map","0:a?","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-movflags","+faststart","-y",output])

def process(bundle,directory,model,root,generate):
    from contextlib import ExitStack
    import fcntl
    store=Storage(); key=digest(bundle)
    directory=directory.resolve()/key/model
    directory.mkdir(parents=True,exist_ok=True)
    with (directory/"worker.lock").open("w") as lock, tempfile.TemporaryDirectory(dir=directory) as scratch, ExitStack() as stack:
        fcntl.flock(lock,fcntl.LOCK_EX)
        work=Path(scratch);m=extract(bundle,work);clips=[];report=[];address=None
        for i,shot in enumerate(m["shots"]):
            target=directory/f"shot-{i}.mp4"; obj=f"vidbest/{key}/{model}/{target.name}"
            temp=work/f"shot-{i}.mp4"; state="cached"
            if not valid(target,shot["frames"]) and store.download(obj,temp):
                if not valid(temp,shot["frames"]):raise ValueError("Invalid remote checkpoint "+obj)
                temp.replace(target)
            if generate and not valid(target,shot["frames"]):
                before=time.monotonic()
                if address is None:address=stack.enter_context(server(root))
                render(model,root,address,work,m,i,temp)
                if not valid(temp,shot["frames"]):raise ValueError("Invalid generated clip")
                temp.replace(target);state=f"GPU {time.monotonic()-before:.1f}s"
            if valid(target,shot["frames"]):
                if generate:store.upload(obj,target)
                clips.append(target)
            else:clips.append(None);state="Oracle CPU"
            report.append({"shot":i,"source":state})
        temp=work/"episode.mp4";assemble(work/"base.mp4",m,clips,temp)
        temp.replace(directory/"episode.mp4")
        (directory/"report.json").write_text(json.dumps(report,indent=2))
        if generate:store.upload(f"vidbest/{key}/{model}/episode.mp4",directory/"episode.mp4")
        print(directory/"episode.mp4")

if __name__=="__main__":
    p=argparse.ArgumentParser(); subs=p.add_subparsers(dest="cmd",required=True)
    a=subs.add_parser("pack");a.add_argument("base",type=Path);a.add_argument("plan",type=Path);a.add_argument("bundle",type=Path)
    for mode in ("gpu","finish"):
        a=subs.add_parser(mode);a.add_argument("bundle",type=Path);a.add_argument("directory",type=Path);a.add_argument("--model",choices=MODELS,default="ltx");a.add_argument("--root",type=Path,default=Path("VidBestComfy"))
    a=p.parse_args()
    if a.cmd=="pack":prepare(a.base,a.plan,a.bundle)
    else:process(a.bundle,a.directory,a.model,a.root.resolve(),a.cmd=="gpu")
