"""CPU-only original procedural 2D MP4 renderer. PNG not required.
Stream exactly one code-drawn Cairo image per frame to FFmpeg; mix original SFX.
"""
from __future__ import annotations
import argparse,json,math,subprocess,struct,sys,time,resource,wave
from pathlib import Path
import cairo
from story import compile_story,validate
from draw import render_frame
RES={'9:16':(432,768),'16:9':(960,540),'1:1':(640,640)}

def audio(plan,path):
    events=[]
    for b in plan['beats']:
        action,start,d=b['action'],float(b['start']),float(b['end'])-float(b['start'])
        if action=='sprint':events.extend((start+.1+i*.155,'foot') for i in range(max(1,int(d/.155))))
        if action=='jump':events.extend([(start+.12,'boing'),(start+d*.83,'land')])
        if action=='knock':events.extend([(start+.15+i*.19,'knock') for i in range(3)])
        if action=='panic':events.append((start+.1,'shock'))
        if action in ('fall','slip'):events.extend([(start+.12,'skid'),(start+d*.72,'bonk')])
        if action=='recover':events.append((start+.2,'pop'))
        if action=='laugh':events.extend([(start+.2,'pop'),(start+.43,'pop')])
        if action=='dance':events.extend([(start+i*.35,'pop') for i in range(max(1,int(d/.35)))])
    sfx={'foot':(115,.08,.13),'boing':(395,.28,.22),'land':(130,.19,.20),
         'knock':(230,.1,.24),'shock':(780,.29,.18),'skid':(570,.3,.16),
         'bonk':(98,.35,.30),'pop':(540,.12,.16)}
    sr=16000;n=round(float(plan['duration'])*sr)
    with wave.open(str(path),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(sr)
        samples=bytearray()
        for i in range(n):
            t=i/sr;v=0
            for moment,name in events:
                f,d,amp=sfx[name];dt=t-moment
                if 0<=dt<d:
                    env=(1-dt/d)**2
                    v+=env*amp*(math.sin(math.tau*(f*dt-70*dt*dt))+.13*math.sin(math.tau*f*2.4*dt))
            samples+=struct.pack('<h',int(max(-1,min(1,v))*25000))
        out.writeframes(samples)

def produce(plan,path,quality='draft',voice=None):
    validate(plan)
    w,h=RES[plan['ratio']]
    if quality=='low':w//=2;h//=2
    if quality=='hd':w=int(w*1.5);h=int(h*1.5)
    fps=int(plan['fps']);count=round(float(plan['duration'])*fps)
    path=Path(path).resolve();path.parent.mkdir(parents=True,exist_ok=True)
    silent=path.with_suffix('.silent.mp4');effects=path.with_suffix('.sfx.wav')
    encoder=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr0','-s',f'{w}x{h}','-r',str(fps),'-i','-',
      '-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(silent)]
    p=subprocess.Popen(encoder,stdin=subprocess.PIPE)
    surface=cairo.ImageSurface(cairo.FORMAT_RGB24,w,h);ctx=cairo.Context(surface)
    start=time.monotonic();used={}
    try:
        for i in range(count):
            ctx.save()
            action=render_frame(ctx,plan,i/fps,w,h)
            ctx.restore();surface.flush()
            used[action]=used.get(action,0)+1
            p.stdin.write(bytes(surface.get_data()))
        p.stdin.close()
    except BaseException:
        p.kill();p.wait();raise
    if p.wait():raise RuntimeError('FFmpeg encoder returned nonzero')
    audio(plan,effects)
    mux=['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(silent),'-i',str(effects)]
    if voice:
        v=Path(voice).resolve()
        if not v.is_file():raise FileNotFoundError('Narration file missing')
        mux+=['-i',str(v),'-filter_complex','[1:a][2:a]amix=inputs=2:duration=first:normalize=0[a]','-map','0:v:0','-map','[a]']
    else:mux+=['-map','0:v:0','-map','1:a:0']
    mux+=['-c:v','copy','-c:a','aac','-b:a','96k','-t',str(plan['duration']),'-movflags','+faststart',str(path)]
    subprocess.run(mux,check=True)
    silent.unlink(missing_ok=True);effects.unlink(missing_ok=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height','-of','json',str(path)]))
    assert {'h264','aac'}<={s['codec_name'] for s in probe['streams']}
    assert path.stat().st_size>15000
    result={'status':'verified','engine':'Python Cairo CPU IK + FFmpeg','plan':plan,'video':str(path),
      'duration':round(float(probe['format']['duration']),3),'size':[w,h],'fps':fps,
      'frames':count,'render_seconds':round(time.monotonic()-start,2),
      'rss_python_peak_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      'rss_ffmpeg_peak_kb':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
      'actions':used,'sfx':'original procedural, no commercial music',
      'notes':'Original reusable vector rigs for supported characters. Additional free-form rigs/actions require new templates or verified assets. No AI diffusion.'}
    path.with_suffix('.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PRO_SUPERTOON_VERIFIED_MP4',path,'frames',count,'render_s',result['render_seconds'],flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prompt',default='Funny boy runs to the toilet, knocks, panics, slips, recovers')
    p.add_argument('--plan',type=Path);p.add_argument('--duration',type=float,default=9)
    p.add_argument('--ratio',choices=list(RES),default='9:16');p.add_argument('--quality',choices=['low','draft','hd'],default='draft')
    p.add_argument('--style',choices=['super-test-color','ink-monochrome'],default='super-test-color')
    p.add_argument('--voice');p.add_argument('--output',default='output/funny-short.mp4')
    a=p.parse_args()
    plan=validate(json.loads(a.plan.read_text())) if a.plan else compile_story(a.prompt,a.duration,a.ratio,a.style)
    produce(plan,a.output,a.quality,a.voice)
