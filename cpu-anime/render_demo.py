"""Silent deterministic CPU illustration demo; not AI-generated video."""
from __future__ import annotations
import argparse
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from plan import make_plan, safe_output

W,H=640,360

def line(draw, pts, color, width=5):
    draw.line(pts, fill=color, width=width, joint="curve")

def frame_at(t:float, actions:list[str]):
    im=Image.new("RGB",(W,H),(246,211,172));d=ImageDraw.Draw(im)
    # Sunset gradients and parallax hills
    for y in range(H):
        k=y/H
        d.line((0,y,W,y), fill=(int(246-39*k),int(214-58*k),int(193-47*k)))
    d.ellipse((435,25,540,130),fill=(255,228,164))
    d.polygon([(0,230),(85,181),(178,227),(300,178),(441,227),(525,180),(640,228),(640,360),(0,360)],fill=(142,174,156))
    d.polygon([(0,275),(150,234),(260,260),(385,227),(530,251),(640,224),(640,360),(0,360)],fill=(70,131,126))
    d.rectangle((0,294,W,H),fill=(66,111,104))
    d.line((0,294,W,294),fill=(36,85,87),width=3)
    # Lantern and flicker; separate authored prop
    lx,ly=525,206
    glow=Image.new("RGBA",(W,H));g=ImageDraw.Draw(glow)
    for radius,alpha in ((72,14),(48,25),(28,33)):
        g.ellipse((lx-radius,ly-radius,lx+radius,ly+radius),fill=(255,215,122,alpha))
    im=Image.alpha_composite(im.convert("RGBA"),glow.filter(ImageFilter.GaussianBlur(14)))
    d=ImageDraw.Draw(im)
    line(d,[(lx,ly-20),(lx,ly-41)],(48,57,73),3)
    d.rounded_rectangle((lx-17,ly-20,lx+17,ly+22),radius=5,fill=(244,194,114),outline=(47,57,73),width=3)
    # Walking cycle with body weight transfer and stationary ground
    moving="walk" in actions
    phase=t*6 if moving else 0
    x=140+int(22*min(t,4)) if moving else 210
    bob=3*abs(math.sin(phase)) if moving else 0
    foot_l=math.sin(phase)*16 if moving else -6
    foot_r=-foot_l
    base=289-bob
    skirt=(x-20,base-83,x+20,base-41)
    # feet: maintain proportions; prototype uses authored joint poses
    hip=(x,base-53)
    for offset in (foot_l, foot_r):
        knee=(x+offset*.55,base-27+max(0,-offset)*.22)
        foot=(x+offset,294-max(0,offset)*.3)
        line(d,[hip,knee,foot],(42,57,76),6)
    # Body and sleeves
    d.polygon([(x-20,base-91),(x+20,base-91),(x+22,base-49),(x-23,base-49)],fill=(214,93,95))
    d.polygon([(x-17,base-77),(x+18,base-77),(x+29,base-42),(x-30,base-42)],fill=(153,67,102))
    neck=(x,base-101)
    # arms with shoulder and elbow positions
    shoulder_y=base-82
    wave="wave" in actions and t>2.2
    waving=math.sin((t-2.2)*6)
    left_elbow=(x-30,shoulder_y+16); left_hand=(x-28,shoulder_y+35)
    right_elbow=(x+29,shoulder_y+(0 if wave else 20))
    right_hand=(x+35+8*waving,shoulder_y-31+8*waving) if wave else (x+37,shoulder_y+36)
    for a,b,c in (((x-15,shoulder_y),left_elbow,left_hand),((x+15,shoulder_y),right_elbow,right_hand)):
        line(d,[a,b,c],(57,58,73),6)
        d.ellipse((c[0]-5,c[1]-5,c[0]+5,c[1]+5),fill=(245,199,162))
    # head, hairstyle and subtle secondary movement
    hx,hy=x,base-122
    hair_tilt=3*math.sin(t*3.1)
    d.ellipse((hx-24,hy-26,hx+24,hy+24),fill=(46,55,77))
    d.ellipse((hx-20,hy-18,hx+20,hy+22),fill=(255,209,169))
    d.polygon([(hx-22,hy-11),(hx+11,hy-28),(hx+20,hy-13),(hx+1,hy-10)],fill=(42,52,77))
    d.ellipse((hx+12,hy-17+hair_tilt,hx+32,hy+4+hair_tilt),fill=(45,53,76))
    blink="blink" in actions and (t%2.8)<.12
    if blink:
        line(d,[(hx-12,hy+1),(hx-3,hy+1)],(48,55,70),2)
        line(d,[(hx+5,hy+1),(hx+14,hy+1)],(48,55,70),2)
    else:
        d.ellipse((hx-12,hy-2,hx-7,hy+5),fill=(50,55,69))
        d.ellipse((hx+7,hy-2,hx+12,hy+5),fill=(50,55,69))
    d.arc((hx-6,hy+5,hx+9,hy+14),0,150,fill=(140,69,79),width=2)
    d.ellipse((x-23,291,x+23,299),fill=(37,78,76))
    return im.convert("RGB")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prompt",default="A girl walks past a lantern and waves, blinks in the wind")
    p.add_argument("--duration",type=float,default=6.)
    p.add_argument("--fps",type=int,default=15)
    p.add_argument("--output",type=Path,default=Path("cpu-anime/out/anime-demo.mp4"))
    ns=p.parse_args()
    plan=make_plan(ns.prompt,ns.duration,ns.fps)
    root=(Path(__file__).resolve().parent/"out").resolve()
    root.mkdir(parents=True,exist_ok=True)
    output=safe_output(ns.output,root)
    output.parent.mkdir(parents=True,exist_ok=True)
    working=output.with_suffix(".working.mp4")
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(ns.fps),"-i","pipe:0","-an","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-movflags","+faststart",str(working)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for index in range(round(ns.duration*ns.fps)):
            proc.stdin.write(frame_at(index/ns.fps,plan["actions"]).tobytes())
        proc.stdin.close()
        error=proc.stderr.read() if proc.stderr else b""
        code=proc.wait()
        if code!=0:raise RuntimeError("FFmpeg failed: "+error.decode(errors="replace")[:300])
        working.replace(output)
        print("RENDER_OK",output)
    finally:
        if proc.poll() is None:proc.kill();proc.wait()
        if working.exists():working.unlink()

if __name__=="__main__":main()
