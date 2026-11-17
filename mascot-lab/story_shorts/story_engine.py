"""Offline prompt -> constrained story -> real MP4 using the owner's original six-pose mascot.

This is pose-to-pose compositing, not neural inbetweening nor anatomical rigging.
"""
from __future__ import annotations
import argparse, json, io, math, random, subprocess, wave, struct, hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parent
W,H,FPS=360,640,24
PALETTE={'bg':'#f7f7f4','ink':'#151515','floor':'#e7e6e2'}
PROMPT_DEFAULT=('Use the permanent Funny Toon Ever black and white mascot. '
 'He spots a toilet door, crouches, sprints there, knocks three times, '
 'pushes the door, gets shocked when it swings open, slips, then recovers. '
 'The door says PULL. One consistent character; fast readable comedy, '
 'squash-and-stretch, speed lines, impact and reaction hold.')

BEATS=[
 ('anticipate',0.0,.85,1),
 ('sprint',.85,2.65,2),
 ('knock',2.65,4.12,0),
 ('push',4.12,4.70,1),
 ('shock',4.70,5.35,4),
 ('slip',5.35,7.15,3),
 ('recover',7.15,8.85,5),
]

def parse_prompt(prompt):
    """Constrained planner: chooses one verified comedic gag from user text, not general LLM."""
    text=prompt.lower()
    markers={'run':['run','sprint','rush','දුව'], 'door':['door','toilet','bathroom','දොර','වැසිකිළි'],
             'knock':['knock','tap','තට්ටු'],'shock':['shock','scare','surprise','බය','පුදුම'],
             'slip':['slip','fall','ලිස්','වැට']}
    found={k:any(s in text for s in group) for k,group in markers.items()}
    # Use a single creative template so motion is reproducible and safe.
    if not any(found.values()): raise ValueError('Prompt lacks recognizable action words')
    return {'compiler':'offline bounded keyword/storyboard rules, NOT LLM',
            'title':'Wrong Door — Funny Toon Ever','prompt':prompt,'matched_keywords':found,
            'total_duration':BEATS[-1][2],'fps':FPS,'scene':'restroom hall',
            'character_source':'source/permanent_mascot_original_sheet.png',
            'beats':[{'action':a,'start':start,'end':end,'pose':pose} for a,start,end,pose in BEATS]}

def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def load_poses(p):
    sheet=Image.open(p).convert('RGB');iw,ih=sheet.size
    result=[]
    for i in range(6):
        col,row=i%3,i//3
        a=(iw*col//3,ih*row//2,iw*(col+1)//3,ih*(row+1)//2)
        rgb=np.asarray(sheet.crop(a));gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        # Largest original silhouette. All facial ink remains unchanged.
        ink=(gray<123).astype(np.uint8)*255
        joined=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
        contours,_=cv2.findContours(joined,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours=[c for c in contours if cv2.contourArea(c)>1000]
        if not contours:raise ValueError('Source pose sheet segmentation failed '+str(i))
        c=max(contours,key=cv2.contourArea)
        mask=np.zeros_like(gray);cv2.drawContours(mask,[c],-1,255,-1)
        mask=cv2.GaussianBlur(mask,(3,3),.7)
        ys,xs=np.where(mask>24)
        margin=5
        x0=max(0,int(xs.min())-margin);y0=max(0,int(ys.min())-margin)
        x1=min(rgb.shape[1],int(xs.max())+margin+1);y1=min(rgb.shape[0],int(ys.max())+margin+1)
        rgba=np.concatenate([rgb,mask[:,:,None]],axis=2)
        result.append(Image.fromarray(rgba,'RGBA').crop((x0,y0,x1,y1)))
    return result

def font(size,bold=False):
    base='/usr/share/fonts/truetype/dejavu/'
    name='DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    path=Path(base)/name
    return ImageFont.truetype(str(path),size) if path.exists() else ImageFont.load_default()

def render_backdrop():
    img=Image.new('RGBA',(W,H),PALETTE['bg']);d=ImageDraw.Draw(img)
    for y in range(45,490,55):d.line((0,y,W,y),fill='#eaeae6',width=1)
    d.rectangle((0,505,W,H),fill=PALETTE['floor']);d.line((0,505,W,505),fill='#333333',width=3)
    # Door frame is drawn consistently throughout all scenes.
    d.rounded_rectangle((232,174,348,508),radius=7,fill='#eeeeea',outline='#191919',width=7)
    d.rectangle((237,179,343,501),fill='#faf9f3',outline='#4c4c4c',width=2)
    d.rounded_rectangle((240,136,341,168),radius=3,fill='#171717')
    d.text((261,145),'WC',font=font(18,True),fill='white')
    return img

def door_layer(t):
    # The left-hinged door opens outwards via perspective width.
    s=ease((t-4.40)/.65)
    img=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(img)
    doorwidth=max(11,round(104*(1-.77*s)));left=240
    right=left+doorwidth
    d.polygon([(left,182),(right,182+int(6*s)),(right,502-int(7*s)),(left,502)],
              fill='#fffefa',outline='#171717',width=5)
    d.line((left+9,205,right-8,210+int(6*s)),fill='#9a9a9a',width=2)
    d.line((left+9,480,right-8,480),fill='#9a9a9a',width=2)
    d.ellipse((right-14,330,right-5,339),fill='#202020')
    if t>5.85:
        d.rounded_rectangle((left+2,245,right-2,280),radius=2,fill='#222222')
        if doorwidth>65:d.text((left+doorwidth//2-18,250),'PULL',font=font(13,True),fill='white')
        else:d.text((260,255),'PULL!',font=font(15,True),fill='#181818')
    return img

def state(t):
    beat=BEATS[-1]
    for x in BEATS:
        if x[1]<=t<x[2]:beat=x;break
    a,start,end,pose=beat;u=(t-start)/max(.01,end-start)
    center=100;rise=0;rot=0;xs=1;ys=1
    if a=='anticipate':
        center=113;pose=1;xs=1+.12*math.sin(math.pi*u);ys=1-.12*math.sin(math.pi*u)
    elif a=='sprint':
        center=113+84*ease(u);pose=2 if int((t-start)*11)%2==0 else 3
        rise=11*abs(math.sin(2*math.pi*5.5*(t-start)));rot=2.7*math.sin(2*math.pi*5.5*(t-start))
    elif a=='knock':
        center=201+4*math.sin(math.pi*u)**2;pose=0
        rot=4*math.sin(2*math.pi*3*u)
    elif a=='push':
        center=208+9*ease(u);pose=1;rot=-14*ease(u);xs=1+.11*u;ys=1-.07*u
    elif a=='shock':
        center=204-15*ease(u);pose=4;rise=39*math.sin(math.pi*u)
        rot=-15*math.sin(math.pi*u);xs=1+.13*math.sin(math.pi*u);ys=1+.12*math.sin(math.pi*u)
    elif a=='slip':
        center=190-67*ease(u);pose=3 if u<.22 else 4
        rise=24*math.sin(math.pi*u)
        rot=-77*ease(u)
        xs=1+.17*math.sin(math.pi*u);ys=1-.13*math.sin(math.pi*u)
    elif a=='recover':
        center=121;pose=5
        rot=-10*math.exp(-6*u)*math.sin(13*u)
        xs=1+.13*math.exp(-7*u);ys=1-.10*math.exp(-7*u)
    return {'action':a,'u':u,'x':center,'rise':rise,'rot':rot,'xs':xs,'ys':ys,'pose':pose}

def frame_at(t,poses,base):
    a=state(t);img=base.copy();door=door_layer(t);img.alpha_composite(door)
    source=poses[a['pose']]
    ratio=215/source.height
    width=max(5,round(source.width*ratio*a['xs']));height=max(5,round(source.height*ratio*a['ys']))
    actor=source.resize((width,height),Image.Resampling.LANCZOS)
    if abs(a['rot'])>.001:actor=actor.rotate(a['rot'],Image.Resampling.BICUBIC,expand=True)
    x=round(a['x']-actor.width/2);y=round(503-a['rise']-actor.height)
    d=ImageDraw.Draw(img,'RGBA')
    shadow_scale=max(.5,1-a['rise']/175)
    d.ellipse((a['x']-38*shadow_scale,500,a['x']+38*shadow_scale,509),fill=(25,25,25,43))
    img.alpha_composite(actor,(x,y))
    d=ImageDraw.Draw(img,'RGBA')
    if a['action']=='sprint':
        for i in range(5):
            xx=int(a['x']-90-i*11);yy=395+i*18
            d.line((xx-24,yy,xx,yy-3),fill=(20,20,20,160),width=3)
    if a['action']=='knock' and any(abs(t-hit)<.13 for hit in (3.04,3.51,3.88)):
        for rad in (9,17):d.arc((235-rad,350-rad,235+rad,350+rad),-90,75,fill='#191919',width=3)
    if a['action']=='shock' and a['u']<.75:
        d.text((70,222),'?!',font=font(50,True),fill='#191919')
    if a['action']=='slip':
        for k in range(2):
            xx=int(a['x']+58+k*16);yy=488-k*9
            d.arc((xx-30,yy-19,xx+30,yy+16),-110,55,fill='#222222',width=3)
    if a['action']=='recover' and a['u']>.25:
        d.text((90,72),'PULL?!',font=font(29,True),fill='#171717')
        d.text((78,108),'OOPS!',font=font(26,True),fill='#555555')
    d.text((12,20),'FUNNY TOON EVER',font=font(17,True),fill='#222222')
    return img.convert('RGB'),a

def make_audio(path,length):
    sr=22050
    events=[(.92,420,.10), (1.32,390,.10),(1.73,430,.10),(2.12,390,.10),
            (3.04,185,.12),(3.51,170,.12),(3.88,190,.12),(4.52,170,.23),
            (4.86,650,.29),(5.92,140,.45),(7.35,450,.24),(8.20,600,.16)]
    payload=bytearray()
    for i in range(round(length*sr)):
        t=i/sr;v=0.0
        for start,f,d in events:
            dt=t-start
            if 0<=dt<d:
                envelope=(1-dt/d)**2
                fnow=f*(1-.38*dt/max(.01,d))
                v+=math.sin(2*math.pi*fnow*dt)*envelope*.23
                v+=math.sin(4*math.pi*fnow*dt)*envelope*.045
        payload.extend(struct.pack('<h',int(max(-1,min(1,v))*29000)))
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(payload)

def render(out:Path, prompt,source):
    plan=parse_prompt(prompt)
    out.parent.mkdir(parents=True,exist_ok=True)
    poses=load_poses(source);base=render_backdrop()
    n=round(plan['total_duration']*FPS)
    raw_mp4=out.with_suffix('.video-only.mp4');audio=out.with_suffix('.wav')
    cmd=['ffmpeg','-nostdin','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','360x640',
         '-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(raw_mp4)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(n):
            img,_=frame_at(i/FPS,poses,base)
            proc.stdin.write(img.tobytes())
        proc.stdin.close()
    except Exception:proc.kill();proc.wait();raise
    if proc.wait()!=0:raise RuntimeError('ffmpeg video encoding failed')
    make_audio(audio,plan['total_duration'])
    subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(raw_mp4),'-i',str(audio),
                    '-c:v','copy','-c:a','aac','-b:a','64k','-movflags','+faststart','-shortest',str(out)],check=True)
    raw_mp4.unlink(missing_ok=True);audio.unlink(missing_ok=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries',
                      'format=duration:stream=codec_name,width,height,r_frame_rate','-of','json',str(out)]))
    assert {'h264','aac'} <= {s['codec_name'] for s in probe['streams']}
    assert float(probe['format']['duration'])>8
    cap=cv2.VideoCapture(str(out));count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));frames=[]
    for j in range(9):
        cap.set(cv2.CAP_PROP_POS_FRAMES,min(count-1,round((j+.5)*count/9)))
        ok,frame=cap.read()
        if ok:
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            im=Image.fromarray(frame);im.thumbnail((240,425))
            frames.append(im)
    cap.release()
    contact=Image.new('RGB',(240*3,425*3),'white')
    for j,im in enumerate(frames):contact.paste(im,((j%3)*240,(j//3)*425))
    contact_path=out.with_name(out.stem+'_actual_frames.jpg');contact.save(contact_path,quality=84)
    plan.update({'video_path':str(out),'video_duration':float(probe['format']['duration']),
                 'video_size_bytes':out.stat().st_size,'decoded_frames':count,
                 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'artistic_limitations':['Six original poses retain the original always-grinning face',
                 'Door/hand contact is staged, not skeletal inverse kinematics',
                 'No real LLM inference, action planning uses offline keyword rules']})
    out.with_suffix('.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
    return plan,contact_path

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--prompt',default=PROMPT_DEFAULT)
    ap.add_argument('--output',type=Path,default=ROOT/'output/Funny_Toon_Wrong_Door_Prompt_Short.mp4')
    ap.add_argument('--source',type=Path,default=(ROOT/'source/permanent_mascot_original_sheet.png' if (ROOT/'source/permanent_mascot_original_sheet.png').exists() else ROOT.parent/'config/permanent_mascot.webp'))
    opt=ap.parse_args()
    plan,contact=render(opt.output,opt.prompt,opt.source)
    print('RENDERED',opt.output,plan['video_duration'],plan['decoded_frames'],plan['video_size_bytes'],'frames',contact)