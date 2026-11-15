"""Prioritise finished results, one private Kaggle submission, then available workers."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from notebook import build
from hybrid import digest,extract,process,valid,Storage,FPS,run

HERE=Path(__file__).resolve().parent

def hf_shots(bundle,out,model,config):
    """Call an explicitly chosen Space with a known, compatible Gradio signature."""
    from gradio_client import Client,handle_file
    cfg=json.loads(config.read_text())
    client=Client(cfg["space"],token=os.environ.get("HF_TOKEN"))
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp);m=extract(bundle,tmp)
        for i,shot in enumerate(m["shots"]):
            path=out/f"shot-{i}.mp4"
            if valid(path,shot["frames"]):continue
            values={"$first":handle_file(str(tmp/f"{i}-first.png")),"$last":handle_file(str(tmp/f"{i}-last.png")),"$prompt":shot["prompt"],"$seed":shot.get("seed",42)}
            kwargs={k:values.get(v,v) if isinstance(v,str) else v for k,v in cfg["inputs"].items()}
            result=client.predict(api_name=cfg["api_name"],**kwargs)
            for part in cfg.get("output_path",[]):result=result[part]
            src=Path(result)
            if not src.is_file():raise ValueError("Space didn't return a downloaded video file")
            temp=tmp/"normalized.mp4"
            run(["ffmpeg","-loglevel","error","-y","-i",src,"-an","-vf","fps=24,tpad=stop_mode=clone:stop_duration="+str(shot["frames"]/FPS),"-frames:v",shot["frames"],"-c:v","libx264","-pix_fmt","yuv420p",temp])
            if not valid(temp,shot["frames"]):raise ValueError("Invalid Space output")
            shutil.copyfile(temp,out/f".{i}.part");(out/f".{i}.part").replace(path)
            Storage().upload(f"vidbest/{digest(bundle)}/{model}/{path.name}",path)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("bundle",type=Path);parser.add_argument("outputs",type=Path)
    parser.add_argument("--model",choices=("ltx","wan","toon"),default="ltx")
    parser.add_argument("--kaggle-user",default=os.getenv("KAGGLE_USERNAME"))
    parser.add_argument("--hf-space-config",type=Path)
    parser.add_argument("--wait-minutes",type=float,default=0)
    a=parser.parse_args();bundle=a.bundle.resolve();out=a.outputs.resolve()
    key=digest(bundle);job=out/key/a.model;job.mkdir(parents=True,exist_ok=True)
    with (job/"route.lock").open("w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        # Finalise a CPU copy immediately; validated GPU shots replace it on subsequent passes.
        process(bundle,out,a.model,None,False)
        def complete():return all(s["source"]!="Oracle CPU" for s in json.loads((job/"report.json").read_text()))
        if complete():return
        build(job/"interactive.ipynb",bundle,a.model)
        marker=job/"kaggle-request.json"
        if a.kaggle_user and shutil.which("kaggle"):
            kid=a.kaggle_user+"/vidbest-"+a.model+"-"+key[:16]
            if not marker.exists():
                marker.write_text(json.dumps({"id":kid,"submitted_at":time.time()}))
                submitted=subprocess.run([sys.executable,HERE/"kaggle_job.py",bundle,a.kaggle_user,"--model",a.model])
                if submitted.returncode:print("Submission unconfirmed. Check the recorded private kernel ID.",flush=True)
            end=time.monotonic()+60*a.wait_minutes
            while True:
                result=subprocess.run(["kaggle","kernels","status",kid],capture_output=True,text=True)
                state=result.stdout.lower()
                if result.returncode==0 and "complete" in state:
                    with tempfile.TemporaryDirectory() as tmp:
                        run(["kaggle","kernels","output",kid,"-p",tmp])
                        for p in Path(tmp).rglob("shot-*.mp4"):
                            if p.parent.name==a.model and p.parent.parent.name==key:
                                shutil.copyfile(p,job/("."+p.name));(job/("."+p.name)).replace(job/p.name)
                    process(bundle,out,a.model,None,False)
                    if complete():return
                    break
                if "error" in state or "cancel" in state:break
                if time.monotonic()>=end:
                    print("Kaggle status pending or unknown. Run the same command again to collect; CPU episode is ready.")
                    return
                time.sleep(min(30,max(0,end-time.monotonic())))
        if a.hf_space_config:
            try:
                hf_shots(bundle,job,a.model,a.hf_space_config)
            except Exception as error:
                print("Space render incomplete:", type(error).__name__, str(error)[:400])
                print("Use the interactive handoff at",job/"interactive.ipynb",file=sys.stderr)
                process(bundle,out,a.model,None,False)
                raise SystemExit(2)
            process(bundle,out,a.model,None,False)
        else:print("GPU handoff notebook:",job/"interactive.ipynb")
if __name__=="__main__":main()
