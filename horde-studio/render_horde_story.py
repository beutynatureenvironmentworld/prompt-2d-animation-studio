"""Edit newly generated AI Horde still frames into a short CPU-animated comedy.
Video has original AI imagery, NOT frame-to-frame GPU diffusion animation.
"""
import os,math,subprocess,json,random,struct,wave
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path("horde-studio/generated")
IMAGES=sorted(ROOT.glob("0*_*.png"))
if not IMAGES:raise RuntimeError("No new AI Horde images; refuse CPU fallback")
OUT=Path("horde-studio/output")
OUT.mkdir(parents=True,exist_ok=True)
SIZE=(360,640);FPS=16;SECONDS=9
font_name="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=ImageFont.truetype(font_name,47) if os.path.exists(font_name) else ImageFont.load_default()
sources=[Image.open(p).convert("RGB") for p in IMAGES]
def frame(t):
    index=min(len(sources)-1,int(t/3*len(sources)/3)) if len(sources)<3 else min(2,int(t/3))
    segment=(t/SECONDS)*len(sources)
    index=min(len(sources)-1,int(segment))
    local=(segment-index)*SECONDS/len(sources)
    im=sources[index]
    w,h=im.size
    scale=max(SIZE[0]/w,SIZE[1]/h)*(1.11+0.07*math.sin(t*2.1))
    if index==1 and 1<local<1.75:scale+=.15
    nw,nh=round(w*scale),round(h*scale)
    img=im.resize((nw,nh),Image.Resampling.BICUBIC)
    shake=7*math.sin(t*38) if index==1 and .9<local<2.0 else 0
    x=max(0,min(nw-SIZE[0],int((nw-SIZE[0])/2+math.sin(t*1.5)*11+shake)))
    y=max(0,min(nh-SIZE[1],int((nh-SIZE[1])/2+math.cos(t*1.8)*13)))
    img=img.crop((x,y,x+SIZE[0],y+SIZE[1]))
    draw=ImageDraw.Draw(img,"RGBA")
    if .95<local<2.15:
        if index==1:
            rng=random.Random(int(t*FPS)+2317)
            for i in range(8):
                sy=rng.randint(80,540)
                sx=rng.randint(0,300)
                draw.line((sx,sy,sx+60,sy-20),fill=(255,255,255,140),width=3)
        word=["GASP!","WHOA!","BONK!"][min(index,2)]
        bx=12;by=55+int(8*math.sin(t*8))
        draw.rounded_rectangle((bx,by,bx+310,by+66),radius=13,fill=(255,239,178,224),outline=(20,30,35,255),width=3)
        draw.text((bx+7,by+5),word,font=font,fill=(24,28,30,255))
    return img
def sfx(path):
    hz=16000
    events=[(.55,480,.11),(1.5,680,.16),(3.9,240,.19),(4.6,175,.26),(6.6,590,.12),(8.2,330,.18)]
    samples=bytearray()
    for n in range(hz*SECONDS):
        t=n/hz; val=0.0
        for st,freq,length in events:
            dt=t-st
            if 0<dt<length:
                val+=0.5*(1-dt/length)**2*math.sin(2*math.pi*freq*dt)
        samples.extend(struct.pack("<h",max(-32767,min(32767,int(val*12500)))))
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(hz);w.writeframes(samples)
def main():
    raw=OUT/"stills-motion.mp4"
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo",
         "-pix_fmt","rgb24","-s","360x640","-r",str(FPS),"-i","-",
         "-an","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(raw)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for idx in range(FPS*SECONDS):
            proc.stdin.write(frame(idx/FPS).tobytes())
        proc.stdin.close()
    finally:
        code=proc.wait()
    if code:raise RuntimeError("Video encode failed")
    sounds=OUT/"comic-original-sfx.wav";sfx(sounds)
    movie=OUT/"fresh-horde-anime-comedy-preview.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(raw),
      "-i",str(sounds),"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac",
      "-shortest",str(movie)],check=True)
    assert movie.stat().st_size>20000
    (OUT/"provenance.json").write_text(json.dumps({
     "image_provider":"AI Horde","new_ai_image_count":len(sources),
     "gpu_video_generated":False,"animated_by":"CPU camera / speed line / zoom / caption edit",
     "duration_s":SECONDS,"old_snap2d_video_reused":False},indent=2)+"\n")
    print("NEW_FRESH_HORDE_STILLS_ANIMATED_PREVIEW",movie,movie.stat().st_size,flush=True)
if __name__=="__main__":main()
