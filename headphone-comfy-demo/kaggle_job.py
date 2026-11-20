#!/usr/bin/env python3
"""Real ComfyUI + Wan2.2 5B image-to-video one-shot Kaggle smoke test.

Generates a NEW short clip. It does not claim to use the attached V2 pixels:
upload them separately for identical reference art.
Runs only on a Kaggle GPU. Model checkpoints are downloaded to the Kaggle worker.
No paid APIs, no public ComfyUI tunnel, no secrets printed.
"""
import os,sys,json,time,subprocess,shutil,math,argparse
from pathlib import Path

ROOT=Path("/kaggle/working") if Path("/kaggle/working").is_dir() else Path.cwd()
OUT=ROOT/"Headphone_Comfy_Wan22_GPU_OneShot.mp4"
COMFY=ROOT/"ComfyUI"
W,H=320,576
FPS=24
FRAMES=49
MODEL="wan2.2_ti2v_5B_fp16.safetensors"
ENCODER="umt5_xxl_fp8_e4m3fn_scaled.safetensors"
VAE="wan2.2_vae.safetensors"
PROMPT=("Original colorful hand-drawn 2D slapstick cartoon. One adult woman wearing large pink headphones sings confidently "
"at the left in a cozy bright living room. A second playful woman at the right carefully reaches toward the headphone "
"cable jack connected to the music player, pinches it with fingers, and dramatically pulls it out. Real body weight shift, "
"expressive full-body movement and crisp hand-object contact. The singer jolts, stops dancing, freezes for a split second, "
"then mouths an exaggerated awful off-key note with a bulging-eyed shocked expression. Fast organic squash and stretch, "
"natural secondary hair motion, comedy anticipation and follow-through, keep identical line art and costume identity, "
"stable room layout. One continuous medium-wide shot, no cuts, no words or subtitles.")
NEG=("static puppet, still body, floating hands, disappearing headphone jack, cable glitches, extra fingers or arms, "
"swapped characters, distorted eyes, changed clothing, photorealistic, 3D, blurry, text, watermark")

def sh(*args,timeout=None):
    print("CMD", " ".join(str(x) for x in args[:5]),flush=True)
    subprocess.run(list(map(str,args)),check=True,timeout=timeout)

def reference_image(path):
    from PIL import Image,ImageDraw,ImageFilter
    im=Image.new("RGB",(W,H),(244,238,228));d=ImageDraw.Draw(im)
    # Original cartoon backdrop with visual landmarks for I2V temporal consistency.
    d.rectangle((0,0,W,400),fill="#fff0db")
    d.rectangle((0,400,W,H),fill="#d1e1cf")
    d.rectangle((0,400,W,408),fill="#665d52")
    d.rounded_rectangle((20,74,116,219),15,fill="#93cfde",outline="#242424",width=4)
    d.line((68,74,68,219),fill="#242424",width=3)
    d.line((20,147,116,147),fill="#242424",width=3)
    d.rounded_rectangle((212,290,302,406),12,fill="#e5a8a0",outline="#242424",width=4)
    d.rounded_rectangle((229,316,285,337),7,fill="#f9d7b0",outline="#242424",width=3)
    d.ellipse((244,347,272,374),fill="#e5bd43",outline="#242424",width=3)
    # Karaoke player, intentionally clear cable socket and dark wire.
    d.rounded_rectangle((126,360,204,401),7,fill="#b0a5ca",outline="#242424",width=4)
    d.rectangle((133,371,165,385),fill="#2b455e")
    d.ellipse((184,377,194,387),fill="#303030")
    # Singer body: head, expressive face and bold limb silhouettes.
    d.line([(78,376),(53,435),(58,511)],fill="#252425",width=17,joint="curve")
    d.line([(105,375),(126,436),(131,507)],fill="#252425",width=17,joint="curve")
    d.line([(78,376),(53,435),(58,511)],fill="#fff3d8",width=10,joint="curve")
    d.line([(105,375),(126,436),(131,507)],fill="#fff3d8",width=10,joint="curve")
    d.ellipse((40,499,82,519),fill="#e65a87",outline="#222222",width=4)
    d.ellipse((111,499,154,519),fill="#e65a87",outline="#222222",width=4)
    d.line([(63,283),(34,326),(18,310)],fill="#242424",width=14,joint="curve")
    d.line([(119,281),(148,322),(158,275)],fill="#242424",width=14,joint="curve")
    d.line([(63,283),(34,326),(18,310)],fill="#ffdabd",width=8,joint="curve")
    d.line([(119,281),(148,322),(158,275)],fill="#ffdabd",width=8,joint="curve")
    d.ellipse((8,296,30,318),fill="#f4b992",outline="#222222",width=3)
    d.ellipse((147,260,169,284),fill="#f4b992",outline="#222222",width=3)
    d.rounded_rectangle((58,264,126,389),16,fill="#f17b79",outline="#242424",width=5)
    d.ellipse((84,314,101,331),fill="#ffdf9a",outline="#242424",width=2)
    d.rounded_rectangle((84,236,101,279),7,fill="#ffdabd",outline="#242424",width=3)
    d.ellipse((35,143,145,263),fill="#30202e",outline="#252425",width=5)
    d.ellipse((44,149,137,250),fill="#ffd6b1",outline="#242424",width=5)
    d.pieslice((41,139,139,207),180,353,fill="#332432")
    # Pink headphones with centered arch and earcups.
    d.arc((39,145,142,248),182,354,fill="#e34688",width=13)
    d.arc((39,145,142,248),182,354,fill="#242424",width=3)
    d.rounded_rectangle((29,201,45,237),6,fill="#ee598e",outline="#242424",width=3)
    d.rounded_rectangle((134,197,150,237),6,fill="#ee598e",outline="#242424",width=3)
    d.ellipse((63,194,78,209),fill="#242424")
    d.ellipse((108,194,123,209),fill="#242424")
    d.ellipse((68,196,72,202),fill="white")
    d.ellipse((113,196,117,202),fill="white")
    d.arc((79,216,105,244),10,170,fill="#9c3d4f",width=5)
    d.line([(145,228),(168,263),(180,306),(189,381)],fill="#282528",width=3,joint="curve")
    # Second character: brown-haired prankster in mint dress with reaching arm.
    d.line([(250,373),(238,454),(230,510)],fill="#242424",width=15,joint="curve")
    d.line([(274,373),(283,455),(290,511)],fill="#242424",width=15,joint="curve")
    d.line([(250,373),(238,454),(230,510)],fill="#f1c1a3",width=9,joint="curve")
    d.line([(274,373),(283,455),(290,511)],fill="#f1c1a3",width=9,joint="curve")
    d.ellipse((207,500,245,520),fill="#5c99aa",outline="#242424",width=4)
    d.ellipse((274,500,311,520),fill="#5c99aa",outline="#242424",width=4)
    d.rounded_rectangle((232,277,287,392),17,fill="#6ccabb",outline="#242424",width=5)
    d.line([(236,304),(220,329),(197,372)],fill="#242424",width=14,joint="curve")
    d.line([(236,304),(220,329),(197,372)],fill="#f9c3a2",width=8,joint="curve")
    d.ellipse((186,363,205,379),fill="#f9c3a2",outline="#242424",width=3)
    d.line([(283,301),(300,357),(313,332)],fill="#242424",width=14,joint="curve")
    d.line([(283,301),(300,357),(313,332)],fill="#f9c3a2",width=8,joint="curve")
    d.ellipse((244,231,263,290),fill="#f8c7a8",outline="#242424",width=4)
    d.ellipse((210,159,308,266),fill="#31232a",outline="#242424",width=5)
    d.ellipse((215,170,301,259),fill="#f9c7a6",outline="#242424",width=4)
    d.ellipse((237,195,252,211),fill="#242424")
    d.ellipse((278,195,291,211),fill="#242424")
    d.arc((248,217,278,238),12,155,fill="#9a4750",width=4)
    d.ellipse((233,157,287,185),fill="#31232a")
    # Music notes are scenery, not typography.
    for x,y in [(69,91),(181,117),(106,60)]:
        d.line((x+8,y-14,x+8,y),fill="#ca6488",width=3)
        d.ellipse((x,y-2,x+12,y+7),fill="#ca6488")
    im.save(path)
    print("KEYFRAME",path,flush=True)

def graph(image):
    return {
       "37":{"class_type":"UNETLoader","inputs":{"unet_name":MODEL,"weight_dtype":"default"}},
       "38":{"class_type":"CLIPLoader","inputs":{"clip_name":ENCODER,"type":"wan","device":"default"}},
       "39":{"class_type":"VAELoader","inputs":{"vae_name":VAE}},
       "48":{"class_type":"ModelSamplingSD3","inputs":{"model":["37",0],"shift":8}},
       "56":{"class_type":"LoadImage","inputs":{"image":image}},
       "55":{"class_type":"Wan22ImageToVideoLatent","inputs":{"vae":["39",0],"start_image":["56",0],"width":W,"height":H,"length":FRAMES,"batch_size":1}},
       "6":{"class_type":"CLIPTextEncode","inputs":{"clip":["38",0],"text":PROMPT}},
       "7":{"class_type":"CLIPTextEncode","inputs":{"clip":["38",0],"text":NEG}},
       "3":{"class_type":"KSampler","inputs":{"model":["48",0],"positive":["6",0],"negative":["7",0],"latent_image":["55",0],"seed":12112026,"steps":12,"cfg":5,"sampler_name":"uni_pc","scheduler":"simple","denoise":1}},
       "8":{"class_type":"VAEDecode","inputs":{"samples":["3",0],"vae":["39",0]}},
       "57":{"class_type":"CreateVideo","inputs":{"images":["8",0],"fps":FPS}},
       "58":{"class_type":"SaveVideo","inputs":{"video":["57",0],"filename_prefix":"headphone_comfy/one_shot","format":"auto"}}
    }

def preflight():
    assert W%32==0 and H%32==0 and (FRAMES-1)%4==0
    print("PLAN",json.dumps({"size":[W,H],"frames":FRAMES,"fps":FPS,"steps":12,
          "type":"Wan2.2-5B I2V", "cuda_required":True},indent=2))
    if not os.environ.get("COMFY_DRY_RUN"):
        return
    reference_image(Path.cwd()/"headphone_start.png")
    (Path.cwd()/"headphone_comfy_api.json").write_text(json.dumps(graph("headphone_start.png"),indent=2))

def models():
    from huggingface_hub import hf_hub_download
    refs=[
      ("Comfy-Org/Wan_2.2_ComfyUI_Repackaged","split_files/diffusion_models/"+MODEL,"diffusion_models"),
      ("Comfy-Org/Wan_2.1_ComfyUI_repackaged","split_files/text_encoders/"+ENCODER,"text_encoders"),
      ("Comfy-Org/Wan_2.2_ComfyUI_Repackaged","split_files/vae/"+VAE,"vae")
    ]
    for repo,remote,folder in refs:
        target=COMFY/"models"/folder/Path(remote).name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.stat().st_size>1000000000:continue
        print("DOWNLOAD",repo,remote,flush=True)
        src=Path(hf_hub_download(repo_id=repo,filename=remote))
        if target.is_symlink():target.unlink()
        if not target.exists():target.symlink_to(src)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--preflight",action="store_true");a=ap.parse_args()
    preflight()
    if a.preflight:return
    import torch
    if not torch.cuda.is_available():raise RuntimeError("NO_CUDA_GPU: real Wan inference requires Kaggle GPU")
    print("NVIDIA_GPU",torch.cuda.get_device_name(0),torch.cuda.get_device_properties(0).total_memory,flush=True)
    print("FREE_DISK_BYTES",shutil.disk_usage(ROOT).free,flush=True)
    if shutil.disk_usage(ROOT).free < 18*10**9:raise RuntimeError("Insufficient free disk for model weights; attach private Kaggle model cache.")
    sh(sys.executable,"-m","pip","install","-q","huggingface_hub","requests","Pillow",timeout=420)
    if not (COMFY/"main.py").exists():
        sh("git","clone","--depth","1","https://github.com/Comfy-Org/ComfyUI.git",COMFY,timeout=360)
    sh(sys.executable,"-m","pip","install","-q","-r",COMFY/"requirements.txt",timeout=600)
    models()
    start=COMFY/"input"/"headphone_start.png";start.parent.mkdir(parents=True,exist_ok=True)
    reference_image(start)
    log=(ROOT/"comfy_one_shot.log").open("w")
    server=subprocess.Popen([sys.executable,"main.py","--listen","127.0.0.1","--port","8188","--lowvram","--cpu-vae"],cwd=str(COMFY),stdout=log,stderr=subprocess.STDOUT)
    import requests
    url="http://127.0.0.1:8188"
    for _ in range(90):
        if server.poll() is not None:raise RuntimeError("ComfyUI exited; inspect /kaggle/working/comfy_one_shot.log")
        try:
            if requests.get(url+"/system_stats",timeout=3).ok:break
        except requests.RequestException:pass
        time.sleep(3)
    else:raise RuntimeError("ComfyUI did not start; inspect log")
    info=requests.get(url+"/object_info",timeout=50).json()
    req=set(x["class_type"] for x in graph("headphone_start.png").values())
    if req-set(info):raise RuntimeError("Missing Comfy nodes: "+repr(sorted(req-set(info))))
    job=requests.post(url+"/prompt",json={"prompt":graph("headphone_start.png"),"client_id":"kaggle-headphone-wan22"},timeout=60)
    if not job.ok:raise RuntimeError("GRAPH_REJECTED: "+job.text[:1800])
    pid=job.json()["prompt_id"];print("COMFY_PROMPT_ID",pid,flush=True)
    t0=time.monotonic()
    while time.monotonic()-t0<2200:
        hist=requests.get(url+"/history/"+pid,timeout=30).json().get(pid)
        if hist:
            if hist.get("status",{}).get("status_str")=="error":
                raise RuntimeError("COMFY_EXECUTION_ERROR: "+repr(hist["status"])[:1500])
            files=list((COMFY/"output").rglob("one_shot*.mp4"))
            if files:
                sh("ffmpeg","-hide_banner","-loglevel","error","-y","-i",files[-1],"-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",OUT,timeout=200)
                print("ACTUAL_GPU_VIDEO",OUT,"SIZE",OUT.stat().st_size,flush=True);return
        time.sleep(12)
    raise TimeoutError("ComfyUI timed out; inspect GPU logs; no output is claimed.")

if __name__=="__main__":main()
