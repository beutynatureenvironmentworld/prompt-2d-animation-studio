"""Render original six-pose monochrome cutout scene from validated JSON timeline.

CPU-only. PIL + cv2 + numpy for effects/segmentation, streamed ffmpeg for H264,
MoviePy v2 for optional output verification. No claim of frame-by-frame AI inbetweening.
"""
import argparse,hashlib,json,math,random,resource,shutil,struct,subprocess,time,wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/poses'
NAMES=['idle_neutral','crouch_anticipation','sprint_angry','sprint_surprise','jump_shock','recover_soft_smile']
COLORS={'ink':'#202020','bg':'#f6f6f4','line':'#c5c5c5'}
FPS=24

def clamp(x,a,b):return max(a,min(b,x))
def ease(x):
    x=clamp(x,0,1)
    return x*x*(3-2*x)
def sfx(timeline,p):
    sample_rate=24000
    total=timeline['duration']
    sounds=[]
    for beat in timeline['actions']:
        t=beat['start']
        action=beat['action']
        if action=='run':sounds.extend([(t+.12,540,.11),(t+.56,475,.10),(t+1.01,520,.1),(t+1.53,490,.1)])
        elif action=='jump':sounds.extend([(t+.12,410,.17),(t+.48,830,.20)])
        elif action=='knock':sounds.extend([(t+.38,195,.12),(t+.67,175,.12)])
        elif action=='shock':sounds.append((t+.12,720,.26))
        elif action=='slip':sounds.append((t+.64,115,.31))
        elif action=='recover':sounds.append((t+.28,440,.17))
    frames=bytearray()
    for i in range(round(total*sample_rate)):
        sec=i/sample_rate;amp=0.0
        for start,frequency,duration in sounds:
            d=sec-start
            if 0<d<duration:
                env=(1-d/duration)**2
                # gentle soft SFX, not a pre-existing soundtrack
                amp+=.17*env*(math.sin(2*math.pi*(frequency*d-.2*frequency*d*d))+.2*math.sin(4*math.pi*frequency*d))
        frames.extend(struct.pack('<h',int(clamp(amp,-1,1)*25000)))
    with wave.open(str(p),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sample_rate);w.writeframes(frames)

def load_pose():
    poses=[]
    for i,name in enumerate(NAMES):
        f=ASSETS/f'{i}_{name}.png'
        im=Image.open(f).convert('RGBA')
        if im.getchannel('A').getbbox() is None:raise ValueError(f'Empty PNG {f}')
        poses.append(im)
    return poses

def background(w,h):
    im=Image.new('RGBA',(w,h),'#f9f9f7');d=ImageDraw.Draw(im)
    # monochrome minimalist room / theatre with understated line-work
    floor=int(h*.81)
    for y in range(35,floor,41):
        d.line((0,y,w,y),fill='#eeeeeb',width=1)
    d.rectangle((0,floor,w,h),fill='#eeeeeb')
    d.line((0,floor,w,floor),fill='#444444',width=3)
    for x in range(0,w,70):d.line((x,floor,x+18,h),fill='#e3e3df',width=1)
    # stage door, original art, matching action-story vocabulary
    x=int(w*.09); top=int(h*.29); doorw=int(w*.135)
    d.rounded_rectangle((x,top,x+doorw,floor),radius=5,fill='#dfdfda',outline='#333333',width=5)
    d.rectangle((x+17,top+20,x+doorw-17,floor-25),outline='#777777',width=3)
    d.ellipse((x+doorw-23,int(h*.55),x+doorw-13,int(h*.55)+10),fill='#2f2f2f')
    return im

def frame_at(t,timeline,poses,base,font,w,h):
    a=timeline['actions'][-1]
    for b in timeline['actions']:
        if b['start'] <= t < b['start']+b['duration']:
            a=b;break
    dur=a['duration']; u=clamp((t-a['start'])/dur,0,1)
    action=a['action']
    pose=a['pose']
    if action=='run':
        # Pose 2 is consistently angry, pose 3 is used as a short intentional surprise beat.
        pose=3 if .83<u<.90 else 2
    if action=='knock':pose=1 if (u<.65) else 3
    if action=='slip':pose=4 if u>.23 else 3
    if action=='jump':pose=4 if u>.22 else 1
    sprite=poses[pose]
    # Nonlinear motion: key poses, squash/stretch and hand-drawn limited-animation holds.
    xs=1.;ys=1.;rise=0.;dx=0.
    if action=='idle':
        ys=1+.012*math.sin(2*math.pi*t*.65)
    elif action=='crouch':
        xs=1+.11*math.sin(math.pi*u);ys=1-.18*math.sin(math.pi*u)
    elif action=='run':
        step=math.sin(2*math.pi*4.2*(t-a['start']))
        rise=12*abs(step)
        ys=1+.02*abs(step);xs=1-.015*abs(step)
        dx=120*(ease(u)-.5)
    elif action=='jump':
        rise=142*(math.sin(math.pi*ease(u))**.85)
        stretch=math.sin(math.pi*u)
        xs=1-.11*stretch;ys=1+.18*stretch
        if u>.85:xs=1+.12*(u-.85)/.15;ys=1-.10*(u-.85)/.15
    elif action=='shock':
        wave=math.sin(2*math.pi*12*(t-a['start']))
        xs=1.13+.03*wave;ys=1.09;rise=11+7*abs(wave)
    elif action=='knock':
        xs=1+.08*math.sin(2*math.pi*3*u);dx=35*ease(u)
    elif action=='slip':
        xs=1+.23*math.sin(math.pi*u);ys=1-.20*math.sin(math.pi*u)
        rise=38*math.sin(math.pi*u)
    elif action=='recover':
        ys=1-.16*math.sin(math.pi*u)*math.exp(-1.3*u)
    # Draw actor as ONE single facial layer. No duplicate face masks in any frames.
    body_height=clamp(h*.63,130,h*.78)
    factor=body_height/sprite.height
    sz=(max(8,round(sprite.width*factor*xs)),max(8,round(sprite.height*factor*ys)))
    # in place of MoviePy heavy frame arrays, use one streaming PIL layer
    obj=sprite.resize(sz,Image.Resampling.LANCZOS)
    im=base.copy();d=ImageDraw.Draw(im,'RGBA')
    world_mid=w*.53
    if action=='run':world_mid+=dx
    if action=='knock':world_mid=w*.37+dx
    actor_cx=int(world_mid)
    ground=int(h*.81)
    actor_bottom=int(ground-rise)
    actor_top=actor_bottom-obj.height
    # shadow independent of sprite, never a second ghost face
    sx=int(w*.13*xs*(1-rise/500));sy=int(h*.018)
    shadow=Image.new('RGBA',(max(3,sx*2),max(3,sy*2)),(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.ellipse((0,0,shadow.width-1,shadow.height-1),fill=(75,75,75,int(75*(1-rise/190))))
    shadow=shadow.filter(ImageFilter.GaussianBlur(max(2,int(h*.005))))
    im.alpha_composite(shadow,(int(actor_cx-shadow.width/2),ground-3))
    im.alpha_composite(obj,(actor_cx-obj.width//2,actor_top))
    d=ImageDraw.Draw(im,'RGBA')
    if action=='run':
        rng=random.Random(int(t*fps_global)+87)
        for _ in range(7):
            x=actor_cx-obj.width//2-rng.randrange(15,115)
            y=actor_top+rng.randrange(max(15,obj.height//4),max(30,obj.height-12))
            d.line((x,y,x+rng.randrange(12,50),y-rng.randrange(0,12)),fill=(40,40,40,150),width=3)
        for j in range(3):
            r=9+4*j; xx=actor_cx-obj.width*.26-12*j
            d.ellipse((xx-r,ground-r,xx+r,ground+2),fill=(155,155,155,max(25,70-15*j)))
    if action=='shock':
        for k in range(5):
            theta=math.pi*(k/6+.12)
            x=actor_cx+int((obj.width*.35)*math.cos(theta))
            y=actor_top+int((obj.height*.15)*math.sin(theta))
            d.line((x,y,x+int(20*math.cos(theta)),y-int(20*math.sin(theta))),fill=(15,15,15,230),width=3)
    if action=='knock' and .3<u<.8:
        xx=int(w*.225);yy=int(h*.51)
        for k in range(3):d.arc((xx-22+k*5,yy-33-k*8,xx+45+k*5,yy+30+k*8),-70,45,fill='#2f2f2f',width=3)
    if action=='slip' and .42<u<.92:
        for k in range(7):
            theta=math.pi*(k/6)
            d.line((actor_cx+int(15*math.cos(theta)),ground-9,actor_cx+int(60*math.cos(theta)),ground-int(32*math.sin(theta))),fill='#303030',width=4)
    # tiny branded caption, intentionally outside character face
    cap=f"FUNNY TOON EVER   •   {action.upper()}"
    d.rectangle((15,h-40, min(w-10,340),h-12),fill='#f5f5f3',outline='#888888',width=1)
    d.text((23,h-34),cap,fill='#292929',font=font)
    # shaky camera exactly on shock and slip impacts
    if action=='shock' and u<.66 or (action=='slip' and .6<u<.9):
        shake=int(w*.006*math.sin(2*math.pi*11*(t-a['start'])))
        # safe in-image shift, so no flickering black canvas edges
        im=im.transform((w,h),Image.Transform.AFFINE,(1,0,shake,0,1,0),resample=Image.Resampling.BILINEAR,fillcolor='#f9f9f7')
    return im.convert('RGB'),action

fps_global=24

def render(plan,output,width=960,height=540,verify=True):
    if not shutil.which('ffmpeg'):raise EnvironmentError('ffmpeg missing')
    start=time.perf_counter()
    poses=load_pose()
    base=background(width,height)
    fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font=ImageFont.truetype(fontpath,max(11,round(height*.027))) if Path(fontpath).exists() else ImageFont.load_default()
    output.parent.mkdir(parents=True,exist_ok=True)
    silent=output.parent/(output.stem+'.tmp.video.mp4')
    audio=output.parent/(output.stem+'.tmp.audio.wav')
    fps=int(plan['fps'])
    n=round(plan['duration']*fps)
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-f','rawvideo','-pixel_format','rgb24',
      '-video_size',f'{width}x{height}','-framerate',str(fps),'-i','-','-an',
      '-c:v','libx264','-preset','ultrafast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    used={}
    try:
        for i in range(n):
            frame,action=frame_at(i/fps,plan,poses,base,font,width,height)
            used[action]=used.get(action,0)+1
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
    finally:
        rc=proc.wait()
    if rc:raise RuntimeError('ffmpeg raw stream encode failed '+str(rc))
    sfx(plan,audio)
    mux=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y','-i',str(silent),'-i',str(audio),
        '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','64k','-shortest','-movflags','+faststart',str(output)],check=True)
    elapsed=time.perf_counter()-start
    silent.unlink(missing_ok=True);audio.unlink(missing_ok=True)
    probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height','-of','json',str(output)])
    pp=json.loads(probe)
    if verify:
        from moviepy import VideoFileClip
        with VideoFileClip(str(output),audio=True) as m:
            assert m.duration>0 and m.audio is not None
            assert m.size==[width,height]
    output_png=output.with_suffix('.jpg')
    thumb=frame_at(min(1.2,plan['duration']*.4),plan,poses,base,font,width,height)[0]
    thumb.thumbnail((800,450));thumb.save(output_png,quality=85)
    report={
      'clip':str(output.relative_to(ROOT)), 'producer':'CPU-only PIL/OpenCV/FFmpeg + MoviePy validation',
      'compiled_by':plan['compiler'], 'actual_render_seconds':round(elapsed,3),
      'duration_seconds':round(n/fps,3),'resolution':[width,height], 'fps':fps,'frames_written':n,
      'source_pose_images':6,'actions':used,'mp4_bytes':output.stat().st_size,
      'python_process_maxrss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'ffmpeg_child_maxrss_kb':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
      'video_verified_with_moviepy':bool(verify),
      'original_source':'six generated original black-and-white mascot poses',
      'not_a_rig':True,'not_gpu_video_generation':True,
      'no_double_face':'Each frame composites exactly one whole-body sprite containing one face',
      'license_note':'User-provided/previously generated mascot design. No source photographs redistributed.'}
    output.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('POSE_CUTOUT_REAL_MP4_PASS',report['clip'],report['duration_seconds'],
         'seconds, rendered',report['actual_render_seconds'],'sec, frames:',n,flush=True)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--timeline',type=Path,default=ROOT/'output/timeline.json')
    p.add_argument('--output',type=Path,default=ROOT/'output/demo.mp4')
    p.add_argument('--width',type=int,default=960);p.add_argument('--height',type=int,default=540)
    a=p.parse_args()
    if a.width%2 or a.height%2 or a.width>1920 or a.height>1080 or a.width<320 or a.height<240:raise ValueError('Use even dimensions: 320..1920 x 240..1080')
    plan=json.loads(a.timeline.read_text())
    from prompt_to_json import validate
    plan=validate({'actions':[{'action':x['action'],'duration':x['duration']} for x in plan['actions']],
       'input_prompt':plan.get('input_prompt',''),'compiler':plan.get('compiler','external-json')})
    render(plan,a.output,a.width,a.height)
if __name__=='__main__':main()
