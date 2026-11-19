#!/usr/bin/env python3
"""Original 2D modular PNG cut-out animation on CPU. Pillow and FFmpeg only."""
import argparse
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageStat

ROOT=Path(__file__).resolve().parent
BASE_W,BASE_H=540,960
GROUND=780
INK=(30,30,43,255)
WHITE=(255,254,251,255)
HAIR=(55,47,65,255)
GOLD=(255,194,88,255)

def curved_line(d, a, b, c, width=17):
    pts=[]
    for i in range(31):
        t=i/30
        x=(1-t)**2*a[0]+2*(1-t)*t*b[0]+t*t*c[0]
        y=(1-t)**2*a[1]+2*(1-t)*t*b[1]+t*t*c[1]
        pts.append((round(x),round(y)))
    d.line(pts,fill=INK,width=width,joint="curve")
    r=width//2
    for x,y in (pts[0],pts[-1]):
        d.ellipse((x-r,y-r,x+r,y+r),fill=INK)

def actor(pose):
    """Create one transparent original sprite pose. The two elbows are never drawn."""
    im=Image.new("RGBA",(360,480),(0,0,0,0))
    d=ImageDraw.Draw(im)
    low=pose in ("bend","reach","crouch","landing")
    high=pose in ("jump","smear")
    shift=28 if low else (-13 if high else 0)
    hip=328+shift
    foot_y=430 if high else 450
    if pose=="kick":
        curved_line(d,(155,hip),(153,389),(129,451))
        curved_line(d,(201,hip),(258,371),(300,318))
        d.ellipse((289,302,330,329),fill=WHITE,outline=INK,width=7)
    else:
        for x0,xf in ((153,129 if not low else 110),(207,225 if not low else 242)):
            curved_line(d,(x0,hip),((x0+xf)//2,390),(xf,foot_y))
            d.ellipse((xf-20,foot_y-9,xf+17,foot_y+10),fill=WHITE,outline=INK,width=6)
    right=(228,256+shift)
    back={
      "reach":(285,400),"bend":(273,364),"jump":(287,152),
      "smear":(294,106),"wave_mid":(263,183),"wave_high":(271,120),
      "lift":(289,249),"shock":(281,177),"crouch":(246,347),
      "landing":(244,339)
    }.get(pose,(260,347))
    curved_line(d,right,(276,273+shift),back,16)
    d.ellipse((back[0]-14,back[1]-14,back[0]+14,back[1]+14),
              fill=WHITE,outline=INK,width=6)
    body=[(144,228+shift),(209,228+shift),(236,280+shift),
          (259,346+shift),(106,346+shift),(126,280+shift)]
    d.polygon(body,fill=WHITE)
    d.line(body+[body[0]],fill=INK,width=8,joint="curve")
    d.polygon([(153,257+shift),(207,257+shift),(194,286+shift),
               (164,286+shift)],fill=GOLD)
    front={
      "wave_mid":(67,173),"wave_high":(86,108),"reach":(305,395),
      "bend":(293,363),"jump":(86,167),"smear":(74,117),
      "lift":(306,264),"shock":(86,196),"crouch":(99,350),
      "landing":(99,345),"kick":(83,281)
    }.get(pose,(101,339))
    start=(131,257+shift)
    control=((front[0]+start[0])*.48+13,(front[1]+start[1])*.52+10)
    curved_line(d,start,control,front,17)
    d.ellipse((front[0]-14,front[1]-14,front[0]+14,front[1]+14),
              fill=WHITE,outline=INK,width=6)
    # Clear thick-black line art; face is complete (no duplicated overlay eyes).
    d.ellipse((82,101+shift,142,178+shift),fill=HAIR,outline=INK,width=6)
    d.ellipse((220,101+shift,280,178+shift),fill=HAIR,outline=INK,width=6)
    d.ellipse((111,56+shift,248,233+shift),fill=WHITE,outline=INK,width=9)
    d.arc((115,57+shift,247,159+shift),180,355,fill=HAIR,width=11)
    d.polygon([(180,82+shift),(153,62+shift),(158,99+shift)],fill=GOLD)
    d.polygon([(181,82+shift),(205,61+shift),(206,100+shift)],fill=GOLD)
    d.ellipse((172,76+shift,191,91+shift),fill=GOLD,outline=INK,width=3)
    for x in (154,209):
        d.ellipse((x-11,135+shift,x+11,169+shift),fill=WHITE,outline=INK,width=4)
        d.ellipse((x-4,146+shift,x+4,158+shift),fill=INK)
    if pose=="shock":
        d.ellipse((174,183+shift,198,216+shift),fill=INK)
    elif low:
        d.arc((161,179+shift,212,211+shift),0,160,fill=INK,width=5)
    else:
        d.rounded_rectangle((153,186+shift,211,216+shift),radius=13,fill=INK)
        d.rounded_rectangle((159,189+shift,205,200+shift),radius=4,fill=WHITE)
    return im

def prop(name):
    if name=="bag":
        im=Image.new("RGBA",(130,125),(0,0,0,0)); d=ImageDraw.Draw(im)
        d.rounded_rectangle((10,28,119,121),radius=14,
                            fill=(250,175,138),outline=INK,width=8)
        d.arc((36,0,92,70),180,360,fill=INK,width=8)
        d.line((17,45,111,45),fill=INK,width=6)
        d.rounded_rectangle((52,56,79,83),radius=5,fill=GOLD,outline=INK,width=3)
    elif name=="camera":
        im=Image.new("RGBA",(100,85),(0,0,0,0)); d=ImageDraw.Draw(im)
        d.rounded_rectangle((7,22,94,78),radius=10,
                            fill=(109,201,213),outline=INK,width=7)
        d.rectangle((22,9,47,28),fill=INK)
        d.ellipse((38,30,77,69),fill=WHITE,outline=INK,width=6)
        d.ellipse((50,42,67,59),fill=(95,153,192),outline=INK,width=3)
    else:
        im=Image.new("RGBA",(92,92),(0,0,0,0));d=ImageDraw.Draw(im)
        d.ellipse((5,5,87,87),fill=(135,222,126),outline=INK,width=7)
        d.arc((23,10,74,74),15,140,fill=WHITE,width=5)
    return im

POSES=("idle","wave_mid","wave_high","bend","reach","lift","crouch",
       "jump","landing","windup","kick","smear","shock")
PROPS=("bag","camera","ball")

def generate(directory):
    directory.mkdir(parents=True,exist_ok=True)
    for pose in POSES:actor(pose).save(directory/(pose+".png"))
    for name in PROPS:prop(name).save(directory/(name+".png"))
    (directory/"manifest.json").write_text(json.dumps({
        "identity":"original demo character, unrelated to Rico copyrighted artwork",
        "poses":POSES,"props":PROPS,"sprite_size":[360,480],
        "actor_feet_anchor":[180,450]},indent=2)+"\n")
    print("GENERATED",len(POSES)+len(PROPS),"transparent PNG sprites")

def landscape():
    im=Image.new("RGBA",(BASE_W,BASE_H))
    d=ImageDraw.Draw(im)
    for y in range(BASE_H):
        t=y/BASE_H
        d.line((0,y,BASE_W,y),fill=(255-int(t*14),244-int(t*21),234-int(t*5),255))
    d.ellipse((-130,603,620,1020),fill=(210,229,178,255))
    d.ellipse((-260,678,271,1060),fill=(169,210,165,255))
    d.ellipse((245,642,790,1030),fill=(183,213,167,255))
    d.rectangle((0,GROUND,BASE_W,BASE_H),fill=(213,230,185,255))
    d.line((0,GROUND,BASE_W,GROUND),fill=(94,145,112,255),width=6)
    for x,y in ((55,630),(480,623)):
        d.rounded_rectangle((x-9,y-5,x+9,GROUND-10),radius=5,
                            fill=(126,102,82,255))
        for a,b,r in ((0,0,54),(-26,13,39),(26,13,38)):
            d.ellipse((x+a-r,y+b-r,x+a+r,y+b+r),fill=(153,203,166,255))
    for x,y in ((116,181),(386,252)):
        for a,b,r in ((0,0,32),(28,-6,27),(-28,-3,27)):
            d.ellipse((x+a-r,y+b-r,x+a+r,y+b+r),fill=(255,255,255,225))
    return im

def paste(canvas,img,x,baseline,scale=1,stretch=(1,1)):
    sx,sy=stretch
    iw,ih=img.size
    size=(max(1,round(iw*scale*sx)),max(1,round(ih*scale*sy)))
    sprite=img.resize(size,Image.Resampling.LANCZOS)
    foot=(180,450) if (iw,ih)==(360,480) else (iw/2,ih)
    pos=(round(x-foot[0]*scale*sx),round(baseline-foot[1]*scale*sy))
    canvas.paste(sprite,pos,sprite)

def object_layer(canvas,img,x,y,scale=1):
    obj=img.resize((round(img.width*scale),round(img.height*scale)),
                   Image.Resampling.LANCZOS)
    canvas.paste(obj,(round(x),round(y)),obj)

def state(action,p,tick):
    s={"pose":"idle","x":215,"feet":GROUND,"stretch":(1,1),
       "camera":None,"camera_front":False,"ball":(390,GROUND-80),
       "shake":False,"speed":False}
    if action=="wave":
        s["pose"]="idle" if p<.12 else ("wave_mid" if tick%4<2 else "wave_high")
        s["x"]+=8*math.sin(2*math.pi*p)
    elif action=="pickup":
        if p<.2:s["pose"]="idle"
        elif p<.41:s["pose"]="bend"
        elif p<.63:s["pose"]="reach"
        else:
            s["pose"]="lift"
            q=min(1,(p-.63)/.17)
            s["camera"]=(369-61*q,708-181*q)
            s["camera_front"]=q>.5
    elif action=="jump":
        if p<.17:
            s["pose"]="crouch";s["stretch"]=(1.11,.88)
        elif p<.8:
            q=(p-.17)/.63
            s["pose"]="smear" if .1<q<.17 else "jump"
            s["feet"]=GROUND-250*4*q*(1-q)
            s["stretch"]=(.94,1.08)
        elif p<.92:
            s["pose"]="landing";s["stretch"]=(1.13,.88)
        else:s["pose"]="idle"
    elif action=="kick":
        s["x"]=202
        if p<.38:s["pose"]="windup"
        elif p<.55:s["pose"]="kick"
        elif p<.62:
            s["pose"]="smear";s["stretch"]=(1.16,.93)
            s["shake"]=True;s["speed"]=True
        elif p<.83:
            s["pose"]="kick";s["speed"]=True
            q=(p-.62)/.21
            s["ball"]=(390+345*q,GROUND-80-74*math.sin(math.pi*q))
        else:s["pose"]="shock";s["ball"]=(800,GROUND-80)
    return s

def render(story,assetdir,output,width,height,fps):
    beats=story["beats"]
    if not beats:raise ValueError("At least one action is required")
    for b in beats:
        if b["action"] not in ("wave","pickup","jump","kick"):
            raise ValueError("Unknown action: "+str(b["action"]))
        if not 0<float(b["duration"])<=30:
            raise ValueError("Beat duration must be >0 and <=30 seconds")
    if not (assetdir/"idle.png").is_file():generate(assetdir)
    art={name:Image.open(assetdir/(name+".png")).convert("RGBA")
         for name in POSES+PROPS}
    bg=landscape()
    output.parent.mkdir(parents=True,exist_ok=True)
    command=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo",
             "-pixel_format","rgb24","-video_size","540x960",
             "-framerate",str(fps),"-i","pipe:0","-an","-vf",
             "scale="+str(width)+":"+str(height)+":flags=lanczos,format=yuv420p",
             "-c:v","libx264","-preset","veryfast","-crf","21",
             "-movflags","+faststart",str(output)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    frames=0
    try:
        for beat in beats:
            action=beat["action"]; count=round(float(beat["duration"])*fps)
            for j in range(count):
                step=max(1,round(fps/12));tick=j//step
                p=min(1,tick*step/max(1,count-1))
                s=state(action,p,tick)
                frame=bg.copy()
                if action=="jump":
                    ImageDraw.Draw(frame).ellipse((152,764,277,779),
                                                  fill=(95,120,91,80))
                if action=="pickup":
                    if s["camera"] and not s["camera_front"]:
                        object_layer(frame,art["camera"],*s["camera"],.75)
                    object_layer(frame,art["bag"],347,GROUND-100,.85)
                if action=="kick" and s["ball"][0]<600:
                    object_layer(frame,art["ball"],*s["ball"],.95)
                paste(frame,art[s["pose"]],s["x"],s["feet"],stretch=s["stretch"])
                if action=="pickup" and s["camera_front"]:
                    object_layer(frame,art["camera"],*s["camera"],.75)
                if s["speed"]:
                    draw=ImageDraw.Draw(frame)
                    for i in range(9):
                        y=264+i*49
                        draw.line((0,y,65+(i%3)*25,y-8),
                                  fill=(88,108,119,130),width=3)
                if s["shake"]:
                    shift=6 if tick%2==0 else -6
                    shaken=bg.copy()
                    shaken.paste(frame,(shift,0),frame)
                    frame=shaken
                process.stdin.write(frame.convert("RGB").tobytes())
                frames+=1
        process.stdin.close()
    except Exception:
        process.kill()
        raise
    error=process.stderr.read().decode("utf-8","replace")
    if process.wait():raise RuntimeError("ffmpeg failed: "+error[-1200:])
    meta={"frames":frames,"fps":fps,"source_fps":12,"duration":frames/fps,
          "width":width,"height":height,"beats":beats}
    output.with_suffix(".json").write_text(json.dumps(meta,indent=2)+"\n")
    print("RENDERED",output,frames,"frames",frames/fps,"seconds")

def verify(video,contact,report):
    def cmd(parts):
        return subprocess.run(parts,check=True,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout
    probe=json.loads(cmd(["ffprobe","-v","error","-show_streams",
                          "-show_format","-of","json",str(video)]))
    stream=next(s for s in probe["streams"] if s["codec_type"]=="video")
    duration=float(probe["format"]["duration"])
    assert stream["codec_name"]=="h264" and duration>1.5
    frames=[]
    for f in (.12,.30,.52,.74,.92):
        raw=cmd(["ffmpeg","-loglevel","error","-ss",str(duration*f),
                 "-i",str(video),"-frames:v","1","-vf","scale=270:480",
                 "-f","rawvideo","-pix_fmt","rgb24","pipe:1"])
        assert len(raw)==270*480*3,"Decoded frame size mismatch"
        frames.append(Image.frombytes("RGB",(270,480),raw))
    movement=[sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
              for a,b in zip(frames,frames[1:])]
    assert max(movement)>3,"Video appears static: "+str(movement)
    montage=Image.new("RGB",(1350,480),"white")
    for idx,im in enumerate(frames):montage.paste(im,(idx*270,0))
    contact.parent.mkdir(parents=True,exist_ok=True)
    montage.save(contact,quality=90)
    quality={"pass":True,"codec":stream["codec_name"],
             "width":stream["width"],"height":stream["height"],
             "duration":duration,"sample_motion":movement}
    report.write_text(json.dumps(quality,indent=2)+"\n")
    print("QUALITY",json.dumps(quality))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["assets","render","verify"])
    p.add_argument("--story",type=Path,default=ROOT/"story.json")
    p.add_argument("--assets",type=Path,default=ROOT/"assets/poses")
    p.add_argument("--output",type=Path,default=ROOT/"out/slapstick_demo.mp4")
    p.add_argument("--contact",type=Path,default=ROOT/"out/contact.jpg")
    p.add_argument("--report",type=Path,default=ROOT/"out/quality.json")
    p.add_argument("--width",type=int,default=1080)
    p.add_argument("--height",type=int,default=1920)
    p.add_argument("--fps",type=int,default=24)
    a=p.parse_args()
    if a.mode=="assets":generate(a.assets)
    elif a.mode=="render":
        if min(a.width,a.height)<320 or not 12<=a.fps<=60:
            p.error("Min output dimension 320, FPS range 12-60")
        render(json.loads(a.story.read_text()),a.assets,a.output,
               a.width,a.height,a.fps)
    else:verify(a.output,a.contact,a.report)

if __name__=="__main__":
    main()
