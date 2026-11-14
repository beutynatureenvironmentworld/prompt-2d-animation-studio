import argparse,array,json,math,os,re,shutil,subprocess,sys,tempfile,wave
from pathlib import Path
import paint
from plan import plan,FIELDS
HERE=Path(__file__).resolve().parent
ALIASES={'night':['moonlit','midnight','nighttime'],'warm':['sunny','daylight','sunlit'],'duck':['ducks','crouches'],'jump':['jumps','leaps'],'reach':['reaches'],'drop':['falls','drops','falling'],'bounce':['bounces','bouncing'],'slide':['slides','sliding'],'close':['close-up','closeup'],'parcel':['package','box']}
def ground(p):
    text=p['prompt'].lower();result=dict(p)
    for key,values in FIELDS.items():
        hits=[v for v in values if any(re.search(r'\b'+re.escape(w)+r'\b',text) for w in [v]+ALIASES.get(v,[]))]
        if len(hits)==1:result[key]=hits[0]
    return result
def render(p,out,sim,width,character=None,plate=None):
    rate=24000;duration=10;fps=24
    line={'clock':'That alarm is getting way too personal.','ball':'Somebody signed me up for sports.','parcel':'That was express delivery.'}[p['prop']]
    with tempfile.TemporaryDirectory(dir=out.parent) as tmp:
        work=Path(tmp);(work/'line.txt').write_text(line)
        raw=subprocess.check_output(['ffmpeg','-v','error','-f','lavfi','-i','flite=textfile=line.txt:voice=slt','-ar',str(rate),'-ac','1','-f','s16le','-'],cwd=work)
        voice=array.array('h');voice.frombytes(raw);samples=array.array('h',[0])*(rate*duration)
        start=6*rate;samples[start:start+len(voice)]=voice
        amp=[min(1,math.sqrt(sum(v*v for v in samples[i:i+1000])/1000)/2200) for i in range(0,rate*duration,1000)]
        for f in sim['hits']:
            for j in range(min(4500,len(samples)-f*1000)):
                n=f*1000+j;samples[n]=max(-32767,min(32767,samples[n]+int(3400*math.exp(-j/800)*math.sin(j*(.045 if p['prop']=='ball' else .075)))))
        with wave.open(str(work/'audio.wav'),'wb') as wav:wav.setparams((1,2,rate,0,'NONE',''));wav.writeframes(samples.tobytes())
        paint.WIDTH=width
        cmd=['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr0','-s',f'{width}x{width*16//9}','-r',str(fps),'-i','-','-i',str(work/'audio.wav'),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(work/'film.mp4')]
        with subprocess.Popen(cmd,stdin=subprocess.PIPE) as enc:
            for i in range(240):enc.stdin.write(paint.frame(i/fps,i,p,sim,amp[i],character,plate))
            enc.stdin.close()
            if enc.wait():raise RuntimeError('Encoding failed')
        (work/'film.mp4').replace(out)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('prompt');parser.add_argument('directory',type=Path);parser.add_argument('--width',type=int,choices=[360,540,720],default=540);parser.add_argument('--cached-plan',type=Path)
    parser.add_argument('--motion-clip', type=Path, help='Clip directory from motion-worker/prepare.py')
    parser.add_argument('--motion-start', type=float, help='Clip start time in seconds')
    parser.add_argument('--background-plate',type=Path,help='Generated scenic PNG to use behind the actors')
    a=parser.parse_args();a.directory.mkdir(parents=True,exist_ok=False)
    raw=json.loads(a.cached_plan.read_text()) if a.cached_plan else plan(a.prompt)
    if raw['prompt']!=a.prompt:raise ValueError('Cached plan belongs to another prompt')
    p=ground(raw);(a.directory/'plan.json').write_text(json.dumps(p,indent=2));(a.directory/'inference.json').write_text(json.dumps(raw,indent=2))
    node=shutil.which('node') or str(HERE.parent/'midnight-jar/runtime/node-v22.16.0-linux-x64/bin/node')
    subprocess.run([node,str(HERE/'physics.cjs'),str(a.directory/'plan.json'),str(a.directory/'trajectory.json')],check=True)
    sim=json.loads((a.directory/'trajectory.json').read_text())
    character=None
    if a.motion_clip:
        from motion_layer import MotionLayer
        start=a.motion_start if a.motion_start is not None else max(0,sim['cue']/24-1)
        character=MotionLayer(json.loads((a.motion_clip/'pose.json').read_text()),start).draw
    plate=paint.cairo.ImageSurface.create_from_png(str(a.background_plate)) if a.background_plate else None
    render(p,a.directory/'short.mp4',sim,a.width,character,plate)
