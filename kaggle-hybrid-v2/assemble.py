"""CPU-only shot assembly. GPU clips are optional and never silently substituted.

Works on a 1GB Oracle VM for *small* projects but no 50MB RAM/2sec promise.
Downloads/copy are the caller's responsibility; no public unauthenticated endpoint.
"""
from __future__ import annotations
import argparse,json,shutil,subprocess,tempfile
from pathlib import Path
from story import read_story


def call(cmd,timeout=180):subprocess.run(cmd,check=True,timeout=timeout,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)


def quote_concat(p):return "file '"+str(p.resolve()).replace("'", "'\\''")+"'\n"


def assemble(story,cpu_dir,gpu_dir,dest,allow_cpu_fallback=False,audio=None):
    data=read_story(story);cpu_dir=Path(cpu_dir);gpu_dir=Path(gpu_dir);dest=Path(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    sources=[]
    for c in data['clips']:
        path=(gpu_dir if c['kind']=='gpu_candidate' else cpu_dir)/(c['id']+'.mp4')
        from_engine='gpu' if c['kind']=='gpu_candidate' else 'cpu'
        if not path.is_file() and c['kind']=='gpu_candidate' and allow_cpu_fallback:
            path=cpu_dir/(c['id']+'.mp4');from_engine='cpu_explicit_fallback'
        if not path.is_file():raise FileNotFoundError(f'Missing {c["id"]} ({c["kind"]}). No silent CPU fallback: {path}')
        sources.append((c,path,from_engine))
    if audio and not Path(audio).is_file():raise FileNotFoundError('Missing explicitly selected final audio track')
    with tempfile.TemporaryDirectory(prefix='fte_stitch_') as temp:
        temp=Path(temp);files=[];report=[]
        for i,(scene,source,engine) in enumerate(sources):
            normalized=temp/f'{i:02d}.mp4'
            # Enforce consistent geometry/framerate/codecs, avoiding broken stream-copy from mismatched GPU outputs.
            call(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),'-t',str(scene['duration_s']),
                  '-vf',"fps=24,scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2:color=white,format=yuv420p",
                  '-r','24','-an','-c:v','libx264','-preset','veryfast','-crf','23','-movflags','+faststart',str(normalized)])
            files.append(normalized)
            report.append({'scene_id':scene['id'],'source':str(source),'used':engine,'duration_s':scene['duration_s']})
        manifest=temp/'files.txt';manifest.write_text(''.join(quote_concat(p) for p in files))
        silent=temp/'joined.mp4'
        call(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(manifest),'-c','copy','-movflags','+faststart',str(silent)])
        if audio:
            call(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(audio),
                  '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','96k','-shortest','-movflags','+faststart',str(dest)])
        else:shutil.copy2(silent,dest)
    results={'schema':'fte.hybrid.assemble.v1','output':str(dest),'gpu_generated_scenes':sum(r['used']=='gpu' for r in report),
             'cpu_scenes':sum(r['used'].startswith('cpu') for r in report),'clips':report,
             'note':'No GPU-origin assertion is made beyond the explicit supplied file paths; review every generated frame before publication'}
    dest.with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n')
    return results

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('story');p.add_argument('--cpu-dir',required=True);p.add_argument('--gpu-dir',required=True)
 p.add_argument('--out',required=True);p.add_argument('--allow-cpu-fallback',action='store_true');p.add_argument('--audio')
 a=p.parse_args();print(json.dumps(assemble(a.story,a.cpu_dir,a.gpu_dir,a.out,a.allow_cpu_fallback,a.audio),indent=2))
