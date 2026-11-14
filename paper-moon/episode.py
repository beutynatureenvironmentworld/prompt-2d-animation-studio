"""Scene-by-scene prompt-directed animation; arbitrary episode-specific drawing code is supported."""
import argparse
import array
import fcntl
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import wave
from PIL import Image,ImageDraw
import room
import staging

FPS=24
RATE=24000
def sample(keys,t):
    if t<=keys[0][0]:return keys[0][1:]
    for left,right in zip(keys,keys[1:]):
        if t<=right[0]:
            u=(t-left[0])/(right[0]-left[0]);u=u*u*(3-2*u)
            return [a+(b-a)*u for a,b in zip(left[1:],right[1:])]
    return keys[-1][1:]

def audio(scene,folder,count):
    track=array.array('h',[0])*(count*(RATE//FPS));voices=[]
    for i,(at,who,text) in enumerate(scene['lines']):
        words=folder/f'line{i}.txt';words.write_text(text)
        voice='slt' if who=='left' else 'rms'
        raw=subprocess.check_output(['ffmpeg','-v','error','-f','lavfi','-i',f'flite=textfile={words.name}:voice={voice}','-ar',str(RATE),'-ac','1','-f','s16le','-'],cwd=folder)
        samples=array.array('h');samples.frombytes(raw);j=int(at*RATE)
        if j<0 or j+len(samples)>len(track):raise ValueError('Dialogue exceeds scene: '+text)
        for k,v in enumerate(samples):track[j+k]=max(-32767,min(32767,track[j+k]+v))
        voices.append((at,at+len(samples)/RATE,who,text,samples))
    with wave.open(str(folder/'mix.wav'),'wb') as wav:
        wav.setparams((1,2,RATE,0,'NONE',''));wav.writeframes(track.tobytes())
    return voices

def render(scene,start,folder):
    n=round(scene['seconds']*FPS);voices=audio(scene,folder,n);bg=room.night_background()
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x540','-r',str(FPS),'-i','-','-i',str(folder/'mix.wav'),'-c:v','libx264','-threads','2','-crf','19','-preset','veryfast','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(folder/'part.tmp.mp4')]
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as enc:
        for frame in range(n):
            t=frame/FPS;clock=start+t;u=t/scene['seconds']
            awake,hand,gaze=sample(scene['acting'],u)
            pose=dict(awake=awake,hand=hand,gaze=gaze);caption=''
            for a,b,who,words,samples in voices:
                if a<=t<b:
                    j=int((t-a)*RATE);chunk=samples[j:j+RATE//FPS]
                    amp=min(1,math.sqrt(sum(v*v for v in chunk)/max(1,len(chunk)))/2500)
                    pose[who+'_mouth']=amp;caption=words
            im=room.bedroom_frame(clock,bg,pose)
            x,y,scale,angle,lamp=sample(scene['flight'],u)
            staging.draw(im,t,clock,x,y,scale,angle,lamp,scene,u)
            cx,cy,zoom=sample(scene['camera'],u)
            if zoom!=1:
                w,h=960/zoom,540/zoom
                cx=min(960-w/2,max(w/2,cx));cy=min(540-h/2,max(h/2,cy))
                im=im.transform((960,540),Image.Transform.EXTENT,(cx-w/2,cy-h/2,cx+w/2,cy+h/2),Image.Resampling.BILINEAR)
            if caption:
                d=ImageDraw.Draw(im);font=room.font(22);length=d.textlength(caption,font=font)
                d.rounded_rectangle((480-length/2-12,488,480+length/2+12,525),8,fill='#181d32')
                d.text((480,505),caption,anchor='mm',font=font,fill='#fff1d8')
            enc.stdin.write(im.tobytes())
        enc.stdin.close()
        if enc.wait():raise RuntimeError('Encoding failed')
    (folder/'part.tmp.mp4').replace(folder/'part.mp4')

def main():
    p=argparse.ArgumentParser();p.add_argument('story',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    seq=json.loads(a.story.read_text());a.out.mkdir(parents=True,exist_ok=True)
    src=b''.join((Path(__file__).parent/f).read_bytes() for f in ('room.py','staging.py','episode.py'))
    with (a.out/'render.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        start=0;parts=[]
        for i,s in enumerate(seq['shots']):
            digest=hashlib.sha256(src+json.dumps([start,s],sort_keys=True).encode()).hexdigest()[:18]
            folder=a.out/f'{i:03d}-{digest}';folder.mkdir(exist_ok=True)
            if not (folder/'part.mp4').exists():render(s,start,folder)
            parts.append(folder);start+=round(s['seconds']*FPS)/FPS
        (a.out/'list.txt').write_text(''.join(f"file '{f.name}/part.mp4'\n" for f in parts))
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','1','-i',str(a.out/'list.txt'),'-c:v','copy','-c:a','aac','-movflags','+faststart',str(a.out/'episode.tmp.mp4')],check=True)
        (a.out/'episode.tmp.mp4').replace(a.out/'episode.mp4')
if __name__=='__main__':main()
