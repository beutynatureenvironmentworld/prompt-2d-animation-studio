"""Original Funny Toon Ever: visually clear reversible milk-carton slapstick.
Rendered inside Kaggle with Pillow/numpy/FFmpeg. Not a MiniMax H3 output.
"""
import json, math, os, subprocess, sys, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path("/kaggle/working") if Path("/kaggle/working").exists() else Path.cwd()
OUT=ROOT/"FTE_Milk_Prank"; OUT.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/"Funny_Toon_Ever_Clever_Milk_Prank_KAGGLE.mp4"
MANIFEST=OUT/"RESULT.json"
W,H=720,1280
FPS=24
SECONDS=11.5
BLACK="#14171e"; CREAM="#fff8e9"; YELLOW="#fff0a1"; BLUE="#3ea6ff"; PINK="#ff5f70"
RED="#ff4b55"; FLOOR="#eccbaa"; MILK="#ffffff"; PALE="#d9f7ff"
def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]:
        if Path(p).is_file(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
FB=font(51); FM=font(28); FS=font(20)
def clamp(v,a=0.,b=1.):return max(a,min(b,v))
def ease(v):v=clamp(v);return v*v*(3-2*v)
def bez(a,b,v):return a+(b-a)*ease(v)
def line(d,p,width=11,color=BLACK):d.line(p,fill=color,width=width,joint="curve")
def ell(d,x,y,rx,ry=None,fill=MILK,outline=BLACK,width=6):
    ry=rx if ry is None else ry
    d.ellipse((int(x-rx),int(y-ry),int(x+rx),int(y+ry)),fill=fill,outline=outline,width=width)
def textcenter(d,text,x,y,f=FB,fill=BLACK):
    bbox=d.textbbox((0,0),text,font=f)
    d.text((int(x-(bbox[2]-bbox[0])/2),int(y)),text,font=f,fill=fill,stroke_width=0)

def shadow(d,x,y,rx):
    ell(d,x,y,rx,20,"#d6b99b","#d6b99b",1)

def face(d,x,y,who="girl",mood="angry",shake=0.0,splash=0.0):
    r=91 if who=="girl" else 89
    if who=="girl":
        # Twin pigtails are larger and readable even at phone size.
        line(d,[(x-62,y-42),(x-116,y-62)],12)
        line(d,[(x+62,y-42),(x+116,y-62)],12)
        ell(d,x-125,y-63,30,30,MILK,BLACK,7)
        ell(d,x+125,y-63,30,30,MILK,BLACK,7)
        for a in (-1,1):
            line(d,[(x+a*115,y-75),(x+a*139,y-87)],4)
    ell(d,x,y,r,r,MILK,BLACK,9)
    if mood in ("shocked","drenched"):
        # Pop-out eyes on bendy stalks, separated for legibility.
        for s in (-1,1):
            xx=x+s*34
            line(d,[(xx,y-30),(xx+s*5,y-100),(xx,y-134)],5)
            ell(d,xx,y-140,26,30,MILK,BLACK,6)
            ell(d,xx,y-140,6,6,BLACK,BLACK,1)
        ell(d,x,y+43,17,28,BLACK,BLACK,3)
    elif mood=="laugh":
        for s in (-1,1):
            d.arc((x+s*33-24,y-28,x+s*33+24,y+15),185,345,fill=BLACK,width=7)
        ell(d,x,y+37,45,28,BLACK,BLACK,3)
        d.arc((x-40,y+19,x+40,y+52),5,170,fill=MILK,width=7)
        for dx in (-18,0,18):line(d,[(x+dx,y+26),(x+dx,y+44)],2,MILK)
    else:
        for s in (-1,1):
            xx=x+s*33
            ell(d,xx,y-8,16,23,MILK,BLACK,5)
            ell(d,xx+s*3,y-4,6,10,BLACK,BLACK,2)
            if mood=="angry":
                line(d,[(xx-22,y-39+(11 if s==-1 else 0)),(xx+21,y-30+(0 if s==-1 else 11))],6)
        if mood=="sly":
            d.arc((x-50,y+10,x+51,y+76),0,175,fill=BLACK,width=7)
            line(d,[(x-35,y+52),(x+36,y+52)],4)
        elif mood=="angry":
            d.arc((x-32,y+44,x+30,y+65),185,350,fill=BLACK,width=7)
        else:
            d.arc((x-32,y+12,x+32,y+58),0,180,fill=BLACK,width=7)
    if splash>0.1:
        for sx,sy,r0 in [(-42,-20,17),(-18,31,13),(32,-39,20),(44,28,14)]:
            ell(d,x+sx,y+sy,r0,12,fill=MILK,outline="#a9d8f6",width=2)
        for j,dx in enumerate((-35,13,45)):
            y0=y+71+(j%2)*6
            line(d,[(x+dx,y0),(x+dx+4,y0+24+13*splash)],6,color=MILK)

def person(d,who,t,mood=None,hand=None,splash=0.0):
    girl=(who=="girl")
    x=170 if girl else 565
    y=588
    if mood is None:mood="angry" if girl else "sly"
    wobble=0
    if mood=="laugh":wobble=12*math.sin((t-8.1)*23)
    y+=wobble
    shadow(d,x,1070,82)
    # rounded shoes and legs
    for s in (-1,1):
        lx=x+s*40
        line(d,[(x+s*34,y+287),(lx+s*10,1010)],19)
        ell(d,lx+s*11,1021,31,16,BLACK,BLACK,1)
    if girl:
        d.polygon([(x-53,y+116),(x+53,y+116),(x+84,y+285),(x-84,y+285)],fill=PINK)
        d.line([(x-53,y+116),(x+53,y+116),(x+84,y+285),(x-84,y+285),(x-53,y+116)],fill=BLACK,width=9)
        line(d,[(x,y+146),(x,y+265)],5,fill if False else "#ffcfda")
    else:
        d.rounded_rectangle((x-63,y+109,x+62,y+286),radius=35,fill=BLUE,outline=BLACK,width=9)
        line(d,[(x-41,y+135),(x+39,y+135)],5,"#9fdefb")
    # arms: their action is deliberately readable
    if girl:
        left=[(x-56,y+160),(x-104,y+220)]
        right=[(x+57,y+160),(x+107,y+222)]
        if hand is not None:
            right=[(x+57,y+160),(x+140,y+168),(hand[0],hand[1])]
        line(d,left,21);line(d,right,21)
        ell(d,*left[-1],20,20,MILK,BLACK,6)
        ell(d,*right[-1],21,21,MILK,BLACK,6)
    else:
        left=[(x-56,y+158),(x-105,y+204)]
        right=[(x+58,y+158),(x+102,y+198)]
        if mood=="laugh":
            left=[(x-53,y+148),(x-115,y+108)]
            right=[(x+55,y+149),(x+110,y+108)]
        else:
            left=[(x-53,y+148),(x-102,y+135)]
            right=[(x+54,y+147),(x+94,y+130)]
        line(d,left,21);line(d,right,21)
        ell(d,*left[-1],18,18,MILK,BLACK,5)
        ell(d,*right[-1],18,18,MILK,BLACK,5)
    face(d,x,y,who,mood,shake=wobble,splash=splash)

def carton(d,compressed=0.,show_labels=False):
    # A single fixed clearly horizontal carton.
    # Straw LEFT points at the girl; SEALED BASE RIGHT touches the boy's mouth.
    x1=360; x2=511; cy=667
    # squeezed edge moves toward body center; nozzle never reverses
    a=20*compressed
    p=[(x1,cy-57),(x2-a,cy-57),(x2-a,cy+57),(x1,cy+57)]
    d.polygon(p,fill="#fffefa")
    line(d,p+[p[0]],8)
    d.polygon([(x1,cy-57),(x1+29,cy-79),(x2-a+2,cy-57)],fill="#c1e8ff")
    line(d,[(x1,cy-57),(x1+29,cy-79),(x2-a+2,cy-57)],6)
    d.polygon([(x2-a,cy-57),(x2-a+17,cy-38),(x2-a+17,cy+51),(x2-a,cy+57)],fill="#e9ecfb")
    line(d,[(x2-a,cy-57),(x2-a+17,cy-38),(x2-a+17,cy+51),(x2-a,cy+57)],7)
    textcenter(d,"MILK",(x1+x2-a)/2,cy-18,FM)
    ell(d,x1+16,cy-18,16,11,fill="#ffb457",outline=BLACK,width=4)
    # open straw sticks toward GIRL, not toward the boy.
    line(d,[(x1+15,cy-18),(x1-45,cy-35)],13,"#e4f5ff")
    line(d,[(x1-48,cy-36),(x1-63,cy-38)],13,BLACK)
    if show_labels:
        d.rounded_rectangle((28,330,370,411),radius=22,fill="#fff2ba",outline=BLACK,width=5)
        textcenter(d,"OPEN STRAW",202,348,FM)
        # arrow from label to open nozzle
        line(d,[(205,430),(274,496),(318,628)],11,RED)
        d.polygon([(313,628),(336,613),(322,659)],fill=RED)
        d.rounded_rectangle((390,337,690,415),radius=22,fill="#d6f6ff",outline=BLACK,width=5)
        textcenter(d,"SEALED END",540,356,FM)
        line(d,[(534,430),(520,530),(521,620)],9,BLUE)
        d.polygon([(505,615),(539,616),(522,657)],fill=BLUE)
    return (x1-63,cy-36)

def splash(d,level,second=False):
    if level<=0:return
    x,y=(300,631)
    tx,ty=176,590
    # Thick continuous jet makes cause/effect obvious.
    endx=bez(x,tx,level)
    endy=bez(y,ty,level)
    wave=13*math.sin(level*6)
    poly=[(x,y-12),(endx,endy-45-wave),(endx-20,endy),(endx,endy+35+wave),(x,y+12)]
    d.polygon(poly,fill=MILK)
    line(d,poly+[poly[0]],4,"#a6dffc")
    for k in range(19):
        p=(k*0.6180339887)%1
        xx=endx+(p-.5)*140
        yy=endy+math.sin(k*2.1)*77
        rr=4+(k%4)*3
        ell(d,xx,yy,rr,rr*0.8,fill=MILK,outline="#b5e4fa",width=2)

def starburst(d,cx,cy,rr=155):
    pts=[]
    for i in range(22):
        a=(i*math.pi/11)-math.pi/2
        rad=rr if i%2==0 else rr*.79
        pts.append((cx+rad*math.cos(a),cy+rad*math.sin(a)))
    d.polygon(pts,fill="#ffe386",outline=BLACK)
    line(d,pts+[pts[0]],6)

def frame_at(t):
    im=Image.new("RGB",(W,H),CREAM);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,172),fill="#ffedbd")
    d.rectangle((0,1057,W,H),fill=FLOOR)
    line(d,[(0,1057),(W,1057)],7,"#d4b38d")
    # faint minimalist decoration in the background, not clutter
    d.arc((30,255,170,400),10,145,fill="#efd9c6",width=7)
    d.arc((540,260,710,430),180,330,fill="#efd9c6",width=7)
    if t<2.2:
        # First splash: boy squeezed first carton at girl.
        alpha=ease((t-.42)/.3)
        if .42<t<1.65:
            starburst(d,170,560,116)
        person(d,"girl",t,"shocked" if alpha>.1 else "angry",splash=alpha)
        person(d,"boy",t,"sly")
        carton(d,compressed=alpha*.8)
        if .42<t<1.65:splash(d,clamp((t-.42)/.17))
        textcenter(d,"ROUND 1",W/2,52,FB)
        if t>0.75:textcenter(d,"SPLASH!",W/2,208,FB,RED)
    elif t<5.2:
        # The trick: big close-up with BOTH ends marked unmistakably.
        person(d,"girl",t,"angry",splash=1)
        person(d,"boy",t,"sly")
        carton(d,show_labels=True)
        textcenter(d,"THE SNEAKY TRICK",W/2,52,FB)
        # fake drinking: sealed end rests right beside boy's mouth.
        if t>3.1:
            d.arc((518,551,599,634),180,315,fill=BLACK,width=6)
            for i in range(3):
                ell(d,520+i*15,540-i*17,4,6,fill=YELLOW,outline=BLACK,width=2)
        # character glances toward carton
    elif t<8.45:
        # Girl presses the SAME carton; exposed straw still points left.
        a=ease((t-5.55)/.5)
        flash=ease((t-6.18)/.15)*(1-ease((t-7.66)/.5))
        person(d,"girl",t,"shocked" if flash>.1 else "angry",hand=(422-10*a,683),splash=1 if flash>.2 else .7)
        person(d,"boy",t,"sly")
        carton(d,compressed=a)
        if flash>0:splash(d,flash,second=True)
        textcenter(d,"SHE SQUEEZES...",W/2,52,FB)
        if flash>.55:
            textcenter(d,"BACKFIRE!",W/2,210,FB,RED)
        # emphasize pinch action with short speed lines
        if a>.25:
            for k in range(3):
                line(d,[(442+k*12,745),(459+k*12,765)],5,BLACK)
    else:
        person(d,"girl",t,"drenched",splash=1)
        person(d,"boy",t,"laugh")
        carton(d,compressed=1)
        textcenter(d,"GOTCHA!",W/2,50,FB,RED)
        # comic bounce text near boy
        if int((t-8.45)*5)%2==0:
            textcenter(d,"HA! HA!",535,303,FM,BLACK)
    # quality brand, consistent and nonintrusive
    d.rounded_rectangle((226,1197,494,1255),radius=20,fill="#ffffff",outline=BLACK,width=5)
    textcenter(d,"funnytoonever",W/2,1210,FM)
    return im

SR=44100
samples=np.zeros(round(SECONDS*SR),np.float32)
def tone(at,duration,f0,f1=None,amp=.17):
    f1=f0 if f1 is None else f1
    x=int(at*SR);n=min(int(duration*SR),len(samples)-x)
    if n<=0:return
    tt=np.arange(n,dtype=np.float32)/SR
    phi=2*math.pi*(f0*tt+.5*(f1-f0)*tt*tt/max(duration,1e-6))
    env=np.minimum(1,tt/.015)*(1-tt/duration)**1.5
    samples[x:x+n]+=(np.sin(phi)*env*amp).astype(np.float32)
def hiss(at,duration,amp=.18):
    x=int(at*SR);n=min(int(duration*SR),len(samples)-x)
    if n<=0:return
    rng=np.random.default_rng(139)
    v=rng.standard_normal(n).astype(np.float32)
    v[1:]-=.88*v[:-1]
    env=np.sin(np.linspace(0,math.pi,n))**.6
    samples[x:x+n]+=(v*env*amp).astype(np.float32)
# original, royalty-free procedural effects (not commercial samples)
hiss(.43,.68,.17);tone(.7,.3,128,60,.45)
tone(2.37,.15,760,1250,.23);tone(2.59,.19,1340,660,.20)
tone(5.55,.3,230,510,.15);hiss(6.22,1.15,.21)
tone(6.45,.6,135,55,.45);tone(6.48,.4,270,75,.20)
for t in (8.65,8.95,9.24,9.57,9.9,10.3):
    tone(t,.17,440,300,.20);tone(t+.07,.12,610,400,.13)
mx=max(1.0,float(np.max(abs(samples))))
samples=np.tanh(samples/mx*1.9)
wav=OUT/"original_cartoon_sfx.wav"
with wave.open(str(wav),"wb") as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((samples*28000).astype("<i2").tobytes())
cmd=["ffmpeg","-y","-hide_banner","-loglevel","error",
     "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","pipe:0",
     "-i",str(wav),"-c:v","libx264","-preset","veryfast","-crf","19",
     "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(VIDEO)]
try:
    import torch
    detected=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
except Exception: detected=[]
print("KAGGLE_ACCELERATORS",detected,flush=True)
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
    for i in range(round(SECONDS*FPS)):
        p.stdin.write(frame_at(i/FPS).tobytes())
    p.stdin.close()
    err=p.stderr.read().decode(errors="replace")
    rc=p.wait(timeout=80)
    if rc: raise RuntimeError("ffmpeg failed: "+err[-1400:])
except Exception:
    p.kill();p.wait();raise
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(VIDEO)],text=True))
vid=next(s for s in probe["streams"] if s["codec_type"]=="video")
au=any(s["codec_type"]=="audio" for s in probe["streams"])
duration=float(probe["format"]["duration"])
okay=vid["width"]==W and vid["height"]==H and duration>=11.2 and au
manifest={"status":"completed" if okay else "failed","output":str(VIDEO),
          "story":"The Clever Milk Carton Reverse Prank",
          "method":"Kaggle original vector pose-to-pose animation with synthesized sound",
          "model":"not MiniMax H3","h3_inference_verified":False,
          "width":W,"height":H,"fps":FPS,"seconds":duration,
          "has_audio":au,"gpu_devices_detected":detected,
          "visual_checks":["left-facing straw","sealed end at boy mouth","girl hand presses carton",
                           "jet travels left to girl","laugh and drips"],
          "video_valid":okay}
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n")
print("FTE_KAGGLE_RENDER_RESULT",json.dumps(manifest),flush=True)
if not okay:raise SystemExit(2)
