"""Render verified CPU Super Test shorts using original vector art and FFmpeg.

Input can be validated JSON or an ordinary prompt; rendering is fully offline.
No third-party video download, no arbitrary code execution, no credentials.
"""
from __future__ import annotations
import argparse,io,json,math,os,struct,subprocess,sys,time,wave,random,resource
from pathlib import Path
import cairo
from plan import compile_story,validate
from draw import draw_frame

RES={'9:16':(432,768),'16:9':(960,540),'1:1':(640,640)}

def sound(plan,p):
    events=[]
    for e in plan['beats']:
        s=float(e['start']);d=float(e['end']-e['start']);a=e['action']
        if a=='sprint':
            for n in range(max(1,int(d*6))):events.append((s+n/6,'foot'))
            events.append((s+.1,'whoosh'))
        if a=='knock':
            for n in range(3):events.append((s+.1+n*.19,'knock'))
        if a=='jump':events.extend([(s+.14,'boing'),(s+d*.76,'land')])
        if a=='panic':events.append((s+.08,'shock'))
        if a=='slip':events.extend([(s+.11,'skid'),(s+d*.78,'bonk')])
        if a=='laugh':events.extend([(s+.14,'pop'),(s+.42,'pop')])
        if a=='recover':events.append((s+.2,'pop'))
    sr=16000;count=int(sr*float(plan['duration']))
    with wave.open(str(p),'wb') as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr)
        # One fast scalar arithmetic pass for short original SFX (no copyrighted music)
        wave_out=bytearray()
        typeinfo={'foot':(130,.07,.13),'whoosh':(380,.32,.1),'knock':(220,.09,.22),
                  'boing':(425,.4,.18),'land':(180,.18,.15),'shock':(740,.22,.21),
                  'skid':(630,.27,.14),'bonk':(90,.28,.25),'pop':(550,.12,.13)}
        for i in range(count):
            t=i/sr;v=0
            for moment,name in events:
                f,duration,amp=typeinfo[name];dt=t-moment
                if 0<=dt<duration:
                    env=(1-dt/duration)**1.8
                    v+=env*amp*(math.sin(math.tau*(f*dt-65*dt*dt))+.12*math.sin(math.tau*2*f*dt))
            wave_out.extend(struct.pack('<h',int(max(-1,min(1,v))*28000)))
        wf.writeframes(wave_out)

def render(plan,out,quality='draft',voice=None):
    validate(plan)
    w,h=RES[plan['ratio']];fps=int(plan['fps']);n=round(float(plan['duration'])*fps)
    if quality=='low':w//=2;h//=2
    if quality=='hd':w=int(w*1.5);h=int(h*1.5)
    out=Path(out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    tmp=out.with_suffix('.silent.mp4');wav=out.with_suffix('.sfx.wav')
    video_cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','bgr0',
         '-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-threads','2','-c:v','libx264',
         '-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(tmp)]
    p=subprocess.Popen(video_cmd,stdin=subprocess.PIPE)
    ctxsurf=cairo.ImageSurface(cairo.FORMAT_RGB24,w,h);ctx=cairo.Context(ctxsurf)
    start=time.monotonic();used={}
    try:
        for i in range(n):
            ctx.save();action=draw_frame(ctx,plan,i/fps,w,h);ctx.restore();ctxsurf.flush()
            used[action]=used.get(action,0)+1
            p.stdin.write(bytes(ctxsurf.get_data()))
        p.stdin.close()
    except BaseException:
        p.kill();p.wait();raise
    if p.wait():raise RuntimeError('FFmpeg rawvideo encoding failed')
    sound(plan,wav)
    args=['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(tmp),'-i',str(wav)]
    if voice is not None:
        v=Path(voice).resolve()
        if not v.is_file():raise FileNotFoundError('Manual narration audio not found')
        args+=['-i',str(v),'-filter_complex','[1:a][2:a]amix=inputs=2:duration=first:normalize=0[a]','-map','0:v:0','-map','[a]']
    else:args+=['-map','0:v:0','-map','1:a:0']
    args+=['-c:v','copy','-c:a','aac','-b:a','96k','-t',str(plan['duration']),'-movflags','+faststart',str(out)]
    subprocess.run(args,check=True)
    elapsed=round(time.monotonic()-start,2)
    tmp.unlink(missing_ok=True);wav.unlink(missing_ok=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height','-of','json',str(out)]))
    assert {'h264','aac'}.issubset({s['codec_name'] for s in probe['streams']})
    assert out.stat().st_size>10000 and float(probe['format']['duration'])>1.9
    report={'status':'real_verified_mp4','plan':plan,'output':str(out),'frame_count':n,'size':[w,h],
            'codec':[s['codec_name'] for s in probe['streams']], 'render_wall_seconds':elapsed,
            'rss_current_process_max_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'rss_child_process_max_kb':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'actual_ik_arms_legs':True,'unique_original_vector_head_per_frame':True,
            'limitations':'Character/environment/actions are procedurally authored and selected from built-in vocabulary; not arbitrary AI image/video generation.',
            'llm_used':False,'gpu_used':False}
    out.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('VERIFIED_SUPERTOON_ORIGINAL_MP4',out,elapsed,'sec',n,'frames',w,'x',h,flush=True)
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--prompt',default='ටොයිලට් එකට දුවගෙන ගිහින් දොරට තට්ටු කරලා බය වෙලා ලිස්සලා වැටෙන 2D විහිළුවක්')
    a.add_argument('--plan',type=Path)
    a.add_argument('--duration',type=float,default=9)
    a.add_argument('--ratio',choices=list(RES),default='9:16')
    a.add_argument('--quality',choices=['low','draft','hd'],default='draft')
    a.add_argument('--voice',type=Path,default=None)
    a.add_argument('--output',type=Path,default=Path('out/supertoon_new.mp4'))
    args=a.parse_args()
    plan=validate(json.loads(args.plan.read_text())) if args.plan else compile_story(args.prompt,args.duration,args.ratio)
    render(plan,args.output,args.quality,args.voice)