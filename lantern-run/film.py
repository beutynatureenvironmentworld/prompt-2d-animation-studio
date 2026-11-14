"""Build dialogue, timed mouth opening, full body frames and effects in one CPU job."""
import argparse,array,json,math,os,subprocess as sp,sys,tempfile,wave
from pathlib import Path
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('story',type=Path);p.add_argument('output',type=Path)
p.add_argument('--width',type=int,choices=[320,640,960,1280,1920],default=1280);a=p.parse_args()
story=json.loads(a.story.read_text());rate=24000;fps=24
if not 0<story['release']<story['catch']<story['relight']<story['seconds']<=300:raise ValueError('Invalid story timing.')
with tempfile.TemporaryDirectory(dir=a.output.resolve().parent) as tmp:
    work=Path(tmp);track=array.array('h',[0])*round(rate*story['seconds'])
    for at,text in story['dialogue']:
        (work/'line.txt').write_text(text)
        raw=sp.check_output(['ffmpeg','-v','error','-f','lavfi','-i','flite=textfile=line.txt:voice=slt','-ar',str(rate),'-ac','1','-f','s16le','-'],cwd=work)
        samples=array.array('h');samples.frombytes(raw);offset=round(at*rate)
        if offset<0 or offset+len(samples)>len(track):raise ValueError('Speech outside episode')
        for j,v in enumerate(samples):track[offset+j]=max(-32768,min(32767,track[offset+j]+v))
    env=os.environ.copy();env['LANTERN_VOICE']=str(work/'mouth.json')
    window=rate//fps
    (work/'mouth.json').write_text(json.dumps([min(1,(sum(x*x for x in track[i:i+window])/window)**.5/2300) for i in range(0,len(track),window)]))
    for j in range(len(track)):
        t=j/rate; sample=0
        for at,pitch in [(story['catch'],215),(story['relight'],660),(story['relight']+.35,825),(story['relight']+.7,990)]:
            u=t-at
            if 0<=u<1:sample+=1450*math.sin(2*math.pi*pitch*u)*math.exp(-5*u)*min(1,u*65)
        track[j]=int(max(-32768,min(32767,track[j]+sample)))
    with wave.open(str(work/'sound.wav'),'wb') as w:w.setparams((1,2,rate,0,'NONE',''));w.writeframes(track.tobytes())
    sp.run([sys.executable,str(root/'render.py'),str(a.story.resolve()),str(work/'frames.mp4'),'--width',str(a.width)],env=env,check=True)
    sp.run(['ffmpeg','-v','error','-y','-i',str(work/'frames.mp4'),'-i',str(work/'sound.wav'),'-c:v','copy','-c:a','aac','-movflags','+faststart',str(work/'final.mp4')],check=True)
    (work/'final.mp4').replace(a.output)
