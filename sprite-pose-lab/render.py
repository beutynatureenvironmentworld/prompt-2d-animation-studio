"""CPU-only pose-to-pose transparent PNG animation renderer. Outputs genuine H.264 MP4."""
import argparse
import json
import math
import shutil
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
STAGE_W,STAGE_H=720,1280
FPS=12

def smooth(t, mode='ease'):
    t=max(0.,min(1.,t))
    return t if mode=='linear' else t*t*(3-2*t)

def lerp(a,b,t): return a+(b-a)*t

def validate(timeline, root):
    if timeline.get('fps')!=12: raise ValueError('Timeline must use 12 fps')
    if not timeline.get('shots'): raise ValueError('No shots')
    for shot in timeline['shots']:
        if not 1<=shot.get('frames',0)<=240: raise ValueError('Invalid shot length')
        for layer in shot.get('layers',[]):
            rel=Path(layer['sprite'])
            if rel.is_absolute() or '..' in rel.parts: raise ValueError('Asset path escapes library')
            if not (root/rel).is_file(): raise FileNotFoundError(root/rel)
            if not all(math.isfinite(float(v)) for v in layer.get('start',[360,960])+layer.get('end',[360,960])): raise ValueError('Invalid coordinate')
    return timeline

@lru_cache(maxsize=256)
def load(path):
    return Image.open(path).convert('RGBA')

def transformed(src,scale_x,scale_y,rotation,opacity):
    w=max(1,round(src.width*scale_x));h=max(1,round(src.height*scale_y))
    im=src.resize((w,h),Image.Resampling.LANCZOS)
    if rotation: im=im.rotate(rotation,expand=True,resample=Image.Resampling.BICUBIC)
    if opacity<1:
        a=im.getchannel('A').point(lambda v: int(v*opacity));im.putalpha(a)
    return im

def frame_image(shot, frame_idx, root, width, height):
    t=0 if shot['frames']<=1 else frame_idx/(shot['frames']-1)
    eased=smooth(t,shot.get('ease','ease'))
    base=load(str(root/'backgrounds/living_room.png')).copy()
    # Persistent layer order: every shot can place a prop behind or in front of an actor.
    for l in sorted(shot.get('layers',[]),key=lambda s:s.get('z',1)):
        src=load(str(root/l['sprite']))
        p0=l.get('start',[360,1000]);p1=l.get('end',p0)
        ax,ay=lerp(p0[0],p1[0],eased),lerp(p0[1],p1[1],eased)
        scale0=l.get('scale',.45);scale1=l.get('scale_end',scale0)
        sc=lerp(scale0,scale1,eased)
        squeeze=l.get('squash',[1,1]);rotation=lerp(l.get('rotation',0),l.get('rotation_end',l.get('rotation',0)),eased)
        opacity=lerp(l.get('opacity',1),l.get('opacity_end',1),eased)
        item=transformed(src,sc*squeeze[0],sc*squeeze[1],rotation,opacity)
        # Source PNGs keep clear padding, so anchor to bottom-center consistently.
        pos=(round(ax-item.width/2),round(ay-item.height))
        base.alpha_composite(item,pos) if pos[0]>=0 and pos[1]>=0 else paste_clipped(base,item,pos)
    if shot.get('impact'):
        overlay=Image.new('RGBA',base.size,(255,255,245,0));d=ImageDraw.Draw(overlay)
        d.ellipse((170,300,570,700),outline=(255,226,77,95),width=32)
        base=Image.alpha_composite(base,overlay)
    zoom=lerp(shot.get('zoom',1),shot.get('zoom_end',shot.get('zoom',1)),eased)
    shake=int(shot.get('shake',0))
    if zoom!=1 or shake:
        dx=shake*((frame_idx%4)//2*2-1)
        dy=shake*((frame_idx%3)-1)
        cw,ch=round(STAGE_W/max(1,zoom)),round(STAGE_H/max(1,zoom))
        cx=max(0,min(STAGE_W-cw,(STAGE_W-cw)//2+dx))
        cy=max(0,min(STAGE_H-ch,(STAGE_H-ch)//2+dy))
        base=base.crop((cx,cy,cx+cw,cy+ch)).resize((STAGE_W,STAGE_H),Image.Resampling.BICUBIC)
    if (width,height)!=(STAGE_W,STAGE_H): base=base.resize((width,height),Image.Resampling.LANCZOS)
    return base.convert('RGB')

def paste_clipped(base,item,pos):
    x,y=pos; lx=max(0,-x);ly=max(0,-y);rx=min(item.width,base.width-x);ry=min(item.height,base.height-y)
    if rx>lx and ry>ly: base.alpha_composite(item.crop((lx,ly,rx,ry)),(max(0,x),max(0,y)))

def audio_sfx(events, duration, output, sample_rate=24000):
    n=round(duration*sample_rate);mix=np.zeros(n,dtype=np.float32)
    for timestamp,name in events:
        if name not in ('boing','whoosh','pop','splash','laugh'):continue
        t=np.arange(int(sample_rate*.32),dtype=np.float32)/sample_rate
        if name=='boing':sig=np.sin(2*np.pi*(300*t+230*t*t))*np.exp(-t*11)
        elif name=='whoosh': sig=np.sin(2*np.pi*(120*t+2600*t*t))*np.exp(-t*9)
        elif name=='pop': sig=np.sin(2*np.pi*(400*t+90*t*t))*np.exp(-t*23)+np.random.default_rng(2).normal(0,.14,len(t))*np.exp(-t*23)
        elif name=='splash':sig=np.random.default_rng(4).normal(0,.4,len(t))*np.exp(-t*12)
        else:sig=np.sin(2*np.pi*(400*t+40*np.sin(2*np.pi*11*t)))*np.exp(-t*7)
        begin=round(timestamp*sample_rate);end=min(n,begin+len(sig))
        if begin<n:mix[begin:end]+=.35*sig[:end-begin]
    mix=np.clip(mix,-.9,.9)
    with wave.open(str(output),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sample_rate)
        w.writeframes((mix*32767).astype('<i2').tobytes())

def render(story=ROOT/'config'/'demo_story.json',output=ROOT/'demo.mp4',width=720,height=1280):
    if width%2 or height%2:raise ValueError('MP4 requires even dimensions')
    if not shutil.which('ffmpeg'):raise RuntimeError('ffmpeg required')
    timeline=validate(json.loads(Path(story).read_text(encoding='utf-8')),ROOT/'assets')
    frames=sum(s['frames'] for s in timeline['shots']);duration=frames/FPS
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    raw_output=output.with_suffix('.silent.mp4');audio=output.with_suffix('.wav')
    ffmpeg=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}',
            '-r',str(FPS),'-i','pipe:0','-vf','fps=24','-c:v','libx264','-preset','veryfast','-crf','24',
            '-pix_fmt','yuv420p','-movflags','+faststart',str(raw_output)]
    p=subprocess.Popen(ffmpeg,stdin=subprocess.PIPE)
    events=[];current=0
    try:
        for shot in timeline['shots']:
            if shot.get('sfx'):events.append((current/FPS,shot['sfx']))
            for f in range(shot['frames']):
                p.stdin.write(frame_image(shot,f,ROOT/'assets',width,height).tobytes())
            current+=shot['frames']
    except Exception:
        p.kill();p.wait();raise
    finally:
        if p.stdin and not p.stdin.closed:p.stdin.close()
    if p.wait():raise RuntimeError('ffmpeg video encoding failed')
    audio_sfx(events,duration,audio)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw_output),'-i',str(audio),
        '-c:v','copy','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(output)],check=True)
    raw_output.unlink(missing_ok=True);audio.unlink(missing_ok=True)
    print(f'SUCCESS: {frames} animation frames, 24 FPS MP4, {width}x{height}, {duration:.2f}s: {output}')
    return output

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--story',type=Path,default=ROOT/'config'/'demo_story.json');ap.add_argument('--output',type=Path,default=ROOT/'demo.mp4')
    ap.add_argument('--width',type=int,default=720);ap.add_argument('--height',type=int,default=1280)
    a=ap.parse_args();render(a.story,a.output,a.width,a.height)
