"""InkRig-2D: an original *real joint-animated* 2D cartoon, not still-image zoom.

Frame-by-frame shoulder, elbow, hip, knee, head, expression and cat tail motion.
No internet or GPU required, so Kaggle/AI Horde queues cannot block this preview.
GPU diffusion should be added *as a distinct, separately validated stage*.
"""
from __future__ import annotations
import argparse, math, random, subprocess, sys, wave, struct, json
from pathlib import Path
import cairo

W,H,FPS=360,640,24
TOTAL_SECONDS=11.5
INK="#22242c"
PAPER="#b6b9a5"
WHITE="#f9f2e1"
BLUE="#647d9b"
HOOD="#e6c25b"
ORANGE="#e68d3c"

def rgb(s):
    s=s.lstrip("#")
    return tuple(int(s[i:i+2],16)/255 for i in (0,2,4))
def source(c,color,a=1):
    c.set_source_rgba(*rgb(color),a)
def shape(c,points,fill=None,stroke=INK,lw=4,close=True):
    c.move_to(*points[0])
    for x,y in points[1:]:c.line_to(x,y)
    if close:c.close_path()
    if fill:source(c,fill);c.fill_preserve()
    if stroke:source(c,stroke);c.set_line_width(lw);c.set_line_join(cairo.LINE_JOIN_ROUND);c.set_line_cap(cairo.LINE_CAP_ROUND);c.stroke()
    else:c.new_path()
def disk(c,x,y,r,fill,stroke=INK,lw=3,ry=None):
    c.save();c.translate(x,y);c.scale(r,ry if ry is not None else r)
    c.arc(0,0,1,0,math.tau);c.restore()
    if fill:source(c,fill);c.fill_preserve()
    if stroke:source(c,stroke);c.set_line_width(lw);c.stroke()
    else:c.new_path()
def curve(c,coords,color=INK,width=5):
    c.move_to(*coords[0])
    if len(coords)==4:c.curve_to(*coords[1],*coords[2],*coords[3])
    else:
        for pt in coords[1:]:c.line_to(*pt)
    source(c,color);c.set_line_width(width);c.set_line_cap(cairo.LINE_CAP_ROUND);c.set_line_join(cairo.LINE_JOIN_ROUND);c.stroke()
def smooth(a,b,t):
    x=max(0,min(1,(t-a)/(b-a)))
    return x*x*(3-2*x)
def wiggle(t,f=5):return math.sin(t*f*math.tau)
def ellipse(c,x,y,rx,ry,fill=WHITE,outline=INK,w=4):
    disk(c,x,y,rx,fill,outline,w,ry=ry)
def rotate(c,deg):
    c.rotate(math.radians(deg))
def label(c,x,y,text,scale=1):
    c.save();c.translate(x,y);c.scale(scale,scale)
    c.select_font_face("DejaVu Sans",cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(21)
    ext=c.text_extents(text);tw=ext.x_advance
    source(c,WHITE);c.rectangle(-11,-28,tw+22,39);c.fill_preserve()
    source(c,INK);c.set_line_width(3);c.stroke()
    source(c,INK);c.move_to(0,0);c.show_text(text);c.restore()
def person(c,x,y,t,mode="idle",scale=1,face="smile",tilt=0,blink=False):
    c.save();c.translate(x,y);c.scale(scale,scale);rotate(c,tilt)
    r=1 if mode=="run" else 0
    run=wiggle(t,3.0)
    hip=0 if not r else 9*abs(run)
    shoulder=-65
    # Two truly articulated legs. Knees and feet change in opposite phases.
    for side in (-1,1):
        phase=run*side
        knee_x=side*19+(33*phase if r else 0)
        knee_y=76-(20*max(phase,0) if r else 0)
        ankle_x=side*18+(65*phase if r else 0)
        ankle_y=150-(43*max(phase,0) if r else 0)
        if mode=="slip":
            knee_x=side*28+39;knee_y=35+side*19
            ankle_x=side*27+75;ankle_y=85+side*44
        curve(c,[(0,46),(knee_x*.65,58),(knee_x,knee_y),(ankle_x,ankle_y)],INK,8)
        ellipse(c,ankle_x+9,ankle_y+2,17,7,WHITE,INK,3)
    # Joint-driven arms, from shoulders through elbows to hands.
    for side in (-1,1):
        phase=side*run
        elbow=(side*45+(25*phase if r else 0),-38+(35*phase if r else 0))
        hand=(side*58+(45*phase if r else 0),3+(64*phase if r else 0))
        if mode=="panic":
            elbow=(side*85,-95);hand=(side*95,-157)
        if mode=="slip":
            elbow=(side*65,-125);hand=(side*103,-170)
        if mode=="point" and side==1:
            elbow=(73,-59);hand=(112,-75)
        curve(c,[(side*25,shoulder),(side*37,-51),elbow,hand],INK,7)
        ellipse(c,*hand,11,10,WHITE,INK,3)
    # Hoodie and dark undershirt, distinct from previous stick-only test.
    shape(c,[(-32,-68),(-13,-81),(20,-78),(35,-56),(28,50),(0,61),(-29,48)],HOOD,lw=4)
    curve(c,[(0,-76),(0,-45),(3,-20),(1,48)],INK,2)
    ellipse(c,-9,-36,4,4,INK,None)
    ellipse(c,7,-35,4,4,INK,None)
    # Neck
    curve(c,[(0,-76),(1,-83),(0,-86),(0,-96)],INK,7)
    # Head moves independently from shoulders.
    c.save();c.translate(0,-155+(-4*abs(run) if r else 0))
    rotate(c,5*wiggle(t,.7) if mode!="slip" else -7)
    ellipse(c,0,0,62,68,WHITE,INK,5)
    # A simple original five-tuft hairstyle, fixed character ID.
    shape(c,[(-56,-22),(-62,-52),(-40,-48),(-32,-80),(-9,-56),(6,-87),
             (22,-57),(53,-62),(42,-37),(58,-21),(34,-37),(4,-33),(-25,-37)],INK,None)
    # Cheeks and expressive eye ovals.
    ellipse(c,-24,-10,23,28,WHITE,INK,3)
    ellipse(c,24,-8,23,30,WHITE,INK,3)
    if not blink:
        for eye_x in (-22,27):
            disk(c,eye_x+(-7 if face=="fear" else 4),-5,6,INK,None)
            disk(c,eye_x+(-9 if face=="fear" else 2),-7,1.5,WHITE,None)
    else:
        curve(c,[(-42,-3),(-26,-9),(-12,-6),(0,-4)],INK,3)
        curve(c,[(8,-2),(22,-7),(33,-8),(44,-2)],INK,3)
    if face in ("fear","shock"):
        curve(c,[(-43,-39),(-30,-55),(-17,-52),(-8,-44)],INK,4)
        curve(c,[(9,-43),(23,-52),(35,-51),(45,-40)],INK,4)
        ellipse(c,2,41,20,24,"#492e35",INK,3)
        ellipse(c,2,57,11,7,"#f3a3a3",None)
    elif face=="angry":
        curve(c,[(-44,-43),(-28,-31),(-17,-29),(-9,-29)],INK,5)
        curve(c,[(8,-29),(23,-29),(36,-33),(46,-44)],INK,5)
        curve(c,[(-21,33),(-7,23),(18,24),(30,34)],INK,5)
    elif face=="talk":
        curve(c,[(-43,-42),(-26,-51),(-18,-50),(-9,-40)],INK,3)
        curve(c,[(9,-41),(24,-49),(34,-49),(43,-39)],INK,3)
        ellipse(c,1,39,21,12,"#492e35",INK,3)
    else:
        curve(c,[(-40,-45),(-26,-52),(-16,-48),(-11,-41)],INK,3)
        curve(c,[(12,-40),(25,-50),(40,-50),(44,-40)],INK,3)
        curve(c,[(-24,35),(-9,53),(9,55),(26,32)],INK,4)
    # little nose
    curve(c,[(0,9),(8,13),(11,18),(4,21)],INK,2.5)
    c.restore()
    c.restore()
def cat(c,x,y,t,mode="idle",scale=1,flipped=False,cookie=True):
    c.save();c.translate(x,y);c.scale((-scale if flipped else scale),scale)
    phase=wiggle(t,4.8)
    # Tail is truly deforming over time, not a zoom of an AI still.
    curve(c,[(28,-55),(51+9*phase,-66),(53-7*phase,-109),(70+16*phase,-116)],INK,11)
    curve(c,[(28,-55),(51+9*phase,-66),(53-7*phase,-109),(70+16*phase,-116)],ORANGE,7)
    # Four leg contact cycles, two on opposite beats.
    for side in (-1,1):
        for q in (0,1):
            ox=-21+q*29;yy=18
            off=(phase if (q+int(side>0))%2==0 else -phase)
            fy=yy+35-17*max(0,off) if mode=="run" else yy+30
            fx=ox+(23*off if mode=="run" else 0)+side*3
            curve(c,[(ox,yy),(ox-3,yy+16),(fx,fy-5),(fx,fy)],INK,7)
            disk(c,fx,fy,9,ORANGE,INK,2,ry=7)
    ellipse(c,0,-21,43,41,ORANGE,INK,4)
    # head + ears + eyes
    ellipse(c,-6,-81,43,42,ORANGE,INK,4)
    shape(c,[(-43,-95),(-45,-134),(-15,-117)],ORANGE,lw=4)
    shape(c,[(13,-114),(35,-139),(37,-94)],ORANGE,lw=4)
    shape(c,[(-33,-117),(-33,-125),(-24,-119)],"#eab3ae",None)
    shape(c,[(21,-115),(31,-126),(31,-112)],"#eab3ae",None)
    for ex in (-24,10):
        ellipse(c,ex,-84,14,18,WHITE,INK,2.5)
        disk(c,ex+6,-84,4.9,INK,None)
    disk(c,-7,-66,6,"#d75f69",INK,2,ry=4)
    if mode in ("laugh","smile"):
        curve(c,[(-17,-59),(-3,-45),(14,-50),(22,-61)],INK,3)
    elif mode=="run":
        ellipse(c,2,-50,10,8,"#492e35",INK,2)
    for sign in (-1,1):
        x1=-5+sign*9
        curve(c,[(x1,-62),(x1+sign*25,-64),(x1+sign*39,-58),(x1+sign*49,-54)],INK,2)
        curve(c,[(x1,-59),(x1+sign*25,-57),(x1+sign*40,-47),(x1+sign*49,-44)],INK,2)
    if cookie:
        disk(c,-9,-39,21,"#daa26c",INK,3)
        for ox,oy in [(-7,-44),(2,-32),(-23,-35)]:
            disk(c,ox,oy,3,"#54362e",None)
    c.restore()
def environment(c,t,scene):
    source(c,PAPER);c.paint()
    # Slight analog paper stipple without a downloaded image.
    random.seed(42)
    for _ in range(75):
        x=random.randrange(360);y=random.randrange(640)
        disk(c,x,y,random.choice((.8,1.2,1.8)),"#838b7d",None,ry=1)
    # floor
    curve(c,[(0,490),(110,490),(240,491),(360,490)],"#787c76",2)
    # door is original production art, comparable 2D cartoon setting
    c.save();c.translate(280,236)
    shape(c,[(-3,-3),(80,-11),(100,239),(-5,237)],BLUE,lw=5)
    shape(c,[(15,19),(64,15),(76,210),(15,213)],"#d2d6bc",lw=3)
    disk(c,66,129,5,"#c4a769",INK,2)
    c.restore()
    # recognizable on-set cookie plate
    if scene=="intro":
        ellipse(c,247,421,45,11,"#d2d4c4",INK,2)
        disk(c,245,409,22,"#d59a5a",INK,3)
        for dx,dy in [(238,407),(258,418),(243,396),(251,406)]:
            disk(c,dx,dy,3,"#4c3831",None)
def splash(c,t,scene):
    if scene in ("run","slip"):
        random.seed(int(t*FPS)+11)
        for _ in range(9):
            x=random.randrange(10,350);y=random.randrange(55,590)
            curve(c,[(x,y),(x+random.randint(25,95),y-random.randint(0,35))],
                  "#faf5df" if scene=="run" else INK,random.choice([2,3,4]))
    if scene=="slip":
        label(c,47,114,"WHOAAA!",.91)
    if scene=="react":
        label(c,24,128,"MY COOKIE!",.92)
def render(c,t):
    scene="intro" if t<2 else "snatch" if t<3.35 else "react" if t<4.7 else "run" if t<7.25 else "slip" if t<8.65 else "bonk" if t<9.6 else "final"
    c.save()
    if scene in ("react","bonk"):
        # Reaction cuts use real independently drawn facial changes.
        zoom=1.58 if scene=="react" else 1.28
        c.translate(W/2,H*.52);c.scale(zoom,zoom);c.translate(-W/2,-H*.52)
    if scene=="slip":
        c.translate(5*wiggle(t,14),3*wiggle(t,11))
    environment(c,t,scene)
    if scene=="intro":
        person(c,148,479,t,mode="point" if t>1.25 else "idle",face="talk" if 1.0<t<1.65 else "smile",blink=(1.45<t<1.51))
    elif scene=="snatch":
        progress=smooth(2,3.35,t)
        cat(c,-70+395*progress,477,t,mode="run",scale=.82,cookie=True)
        person(c,132,479,t,mode="panic" if t>2.55 else "point",face="shock" if t>2.48 else "smile")
        if progress>.65:label(c,32,95,"HEY!")
    elif scene=="react":
        person(c,173,566,t,mode="panic",face="fear",scale=1.65,tilt=-3+8*wiggle(t,2))
    elif scene=="run":
        offset=8*wiggle(t,10)
        cat(c,270+3*wiggle(t,1),474-15*abs(wiggle(t,4.8)),t,mode="run",scale=.88)
        person(c,121,476-13*abs(wiggle(t,3)),t,mode="run",face="angry",scale=.92)
        splash(c,t,scene)
        if 6.65<t<7.23:label(c,30,109,"STOP!")
    elif scene=="slip":
        p=smooth(7.25,8.55,t)
        person(c,171+30*p,476-125*math.sin(math.pi*p),t,mode="slip",face="fear",
               tilt=-110*p,scale=1+0.1*p)
        cat(c,304,480,t,mode="smile",scale=.77)
        splash(c,t,scene)
    elif scene=="bonk":
        person(c,194,514,t,mode="slip",face="fear",tilt=-75+18*wiggle(t,7),scale=1.13)
        cat(c,318,483,t,mode="laugh",scale=.75)
        if t<9.2:label(c,20,102,"BONK!")
    else:
        person(c,163,489,t,mode="idle",face="fear" if t<10.65 else "smile",
               tilt=-4+6*wiggle(t,1.1),scale=1.12)
        cat(c,281,483,t,mode="laugh",scale=.84)
        disk(c,155,252,24,"#d59a5a",INK,3)
        disk(c,160,249,6,"#f6f0df",INK,1)
        if t>10.55:label(c,17,103,"NICE HAT!")
    c.restore()
    # Vertical video designed with quiet safe-margin; no imported character art.
    c.save();source(c,INK,.32);c.set_line_width(1.5);c.rectangle(4,4,W-8,H-8);c.stroke();c.restore()
def sfx(path):
    hz=22050
    cues=[(.4,360,.08),(1.6,600,.13),(2.15,280,.15),(2.65,740,.16),
          (3.37,290,.24),(4.68,470,.09),(5.25,280,.08),
          (6.4,530,.12),(7.45,740,.23),(8.58,94,.35),
          (9.8,435,.13),(10.7,660,.16)]
    samples=bytearray()
    for i in range(int(hz*TOTAL_SECONDS)):
        t=i/hz;v=0.0
        for st,f,d in cues:
            a=t-st
            if 0<a<d:
                q=(1-a/d)**2
                v+=.22*q*(math.sin(math.tau*(f*a-90*a*a))+.3*math.sin(math.tau*2*f*a))
        value=max(-32767,min(32767,int(v*24500)))
        samples+=struct.pack("<h",value)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(hz);w.writeframes(samples)
def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path,default=Path("inkrig/output/original-rigged-2d-comedy.mp4"))
    cli.add_argument("--seconds",type=float,default=TOTAL_SECONDS)
    args=cli.parse_args()
    if not 1<=args.seconds<=TOTAL_SECONDS:raise ValueError("seconds must be in [1, 11.5]")
    output=args.output;output.parent.mkdir(parents=True,exist_ok=True)
    size=2
    surf=cairo.ImageSurface(cairo.FORMAT_RGB24,W*size,H*size)
    c=cairo.Context(surf);c.scale(size,size)
    noaudio=output.with_name("silent-rig.mp4")
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-f","rawvideo","-pix_fmt","bgr0","-s",f"{W*size}x{H*size}","-r",str(FPS),
         "-i","-","-an","-vf",f"scale={W}:{H}:flags=lanczos","-c:v","libx264",
         "-preset","veryfast","-crf","21","-pix_fmt","yuv420p",str(noaudio)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    n=round(args.seconds*FPS)
    try:
        for index in range(n):
            c.save();render(c,index/FPS);c.restore();surf.flush()
            p.stdin.write(bytes(surf.get_data()))
            c.new_path()
        p.stdin.close()
    finally:
        status=p.wait()
    if status:raise RuntimeError("FFmpeg render failed")
    audio=output.with_name("original-slapstick-sfx.wav");sfx(audio)
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i",str(noaudio),"-i",str(audio),
       "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-shortest",str(output)],check=True)
    result={"source":"original procedural vector cartoon rig","real_skeleton_motion":True,
            "gpu_video_diffusion":False,"used_ai_horde_frames":False,
            "delivered_new_mp4":str(output),"duration_seconds":args.seconds,
            "fps":FPS,"dimensions":[W,H],
            "note":"Character limbs, eyes, mouth and tail redraw on each frame; not a zoom slideshow."}
    output.with_suffix(".json").write_text(json.dumps(result,indent=2)+"\n")
    print("REAL_JOINT_2D_ANIMATION_COMPLETE",output,output.stat().st_size,flush=True)
if __name__=="__main__":main()
