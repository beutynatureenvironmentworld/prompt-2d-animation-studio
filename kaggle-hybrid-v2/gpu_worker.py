"""Kaggle-only GPU worker: preflight, opt-in Wan 2.1 1.3B and WanGP saved queue.

No fictitious `--model minimax_h3_int8` flag. WanGP consumes an exported
settings JSON / queue ZIP via official `--process`. H3 is not default because
T4 memory and model licence/terms need to be tested for the exact profile.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
from preflight import probe
from story import validate_batch

ROOT=Path(__file__).resolve().parent
FPS=16
MODEL='Wan-AI/Wan2.1-T2V-1.3B-Diffusers'


def safe_queue(q):
    p=Path(q).resolve()
    if not p.is_file() or p.suffix.lower() not in ('.json','.zip'):raise ValueError('Required exported WanGP queue ZIP or settings JSON not found')
    if p.stat().st_size>180*1024*1024:raise ValueError('WanGP queue too large: mount as private Kaggle Dataset instead')
    if p.suffix.lower()=='.zip':
        import zipfile
        with zipfile.ZipFile(p) as z:
            names=z.namelist()
            if len(names)>500:raise ValueError('Too many queue entries')
            for n in names:
                pp=Path(n)
                if pp.is_absolute() or '..' in pp.parts:raise ValueError('Unsafe queue archive path')
    return p


def render_wan21_job(shot,output):
    """Executed ONLY inside actual Kaggle CUDA session; no CPU fake output."""
    import torch
    from diffusers import WanPipeline
    from diffusers.utils import export_to_video
    if not torch.cuda.is_available():raise RuntimeError('No allocated CUDA GPU')
    dev=torch.cuda.get_device_properties(0)
    if dev.total_memory<14*2**30:raise RuntimeError('Need approx T4 16GB GPU; refusing smaller card')
    # NVIDIA T4 has compute capability 7.5: float16 rather than bfloat16.
    dtype=torch.float16 if dev.major<8 else torch.bfloat16
    cache=os.getenv('HF_HOME')
    kwargs={'torch_dtype':dtype}
    if cache:kwargs['cache_dir']=cache
    pipe=WanPipeline.from_pretrained(MODEL,**kwargs)
    # CPU offload conserves the VRAM that matters (each GPU separate).
    pipe.enable_model_cpu_offload()
    generator=torch.Generator(device='cuda').manual_seed(418)
    result=pipe(prompt=shot['prompt'],negative_prompt='extra arms, duplicate eyes, additional characters, broken joints, text, watermarks',
        height=320,width=512,num_frames=49,num_inference_steps=20,guidance_scale=5.0,generator=generator)
    export_to_video(result.frames[0],str(output),fps=FPS)
    del pipe
    torch.cuda.empty_cache()


def run_wangp_queue(queue,install_dir,output_dir,max_seconds,dry_run=False):
    queue=safe_queue(queue)
    wgp=Path(install_dir).resolve()/'wgp.py'
    if not wgp.is_file():raise FileNotFoundError('WanGP not installed: run bootstrap_kaggle.sh with GPU mode wangp-queue')
    output=Path(output_dir).resolve();output.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(wgp),'--process',str(queue),'--output-dir',str(output)]
    if dry_run:command.append('--dry-run')
    proc=subprocess.run(command,cwd=wgp.parent,timeout=max_seconds,check=False)
    if proc.returncode:raise RuntimeError(f'WanGP queue failed (exit {proc.returncode})')


def media_info(p):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height','-of','json',str(p)],timeout=30))
    if not any(s.get('codec_type')=='video' for s in data['streams']):raise RuntimeError('Output does not contain video frames')
    duration=float(data.get('format',{}).get('duration',0))
    if not .35<=duration<=30:raise RuntimeError(f'Unexpected video length {duration}')
    return {'seconds':round(duration,2),'streams':[{k:v for k,v in s.items() if k in ('codec_type','codec_name','width','height')} for s in data['streams']]}


def do_batch(args):
    dest=Path(args.output).resolve();dest.mkdir(parents=True,exist_ok=True)
    status=probe(dest,require_gpu=args.mode!='probe')
    if args.mode=='probe':return {'mode':'probe','preflight':status,'model_inference_verified':False,'results':[]}
    if not args.jobs:raise ValueError('--jobs manifest is required for generation')
    jobs=validate_batch(args.jobs)['shots']
    if not jobs:raise ValueError('No selected GPU shots (safe to stop without GPU download)')
    if len(jobs)>2:raise ValueError('Max 2 shots per dispatch')
    if args.max_seconds>3600 or args.max_seconds<120:raise ValueError('Compute budget must be 120–3600s')
    start=time.monotonic();results=[]
    if args.mode=='wangp-queue':
        # Saved exported queue owns settings/model selection/embedded references.
        # Validate its structure with actual WanGP CLI before doing any inference.
        run_wangp_queue(args.queue,args.wangp_root,dest,args.max_seconds,dry_run=True)
        if args.validate_only:return {'mode':'wangp-queue','queue_validated':True,'model_inference_verified':False,'results':[]}
        before={p.resolve() for p in dest.rglob('*.mp4')}
        remaining=max(60,int(args.max_seconds-(time.monotonic()-start)))
        run_wangp_queue(args.queue,args.wangp_root,dest,remaining)
        newclips=[p for p in dest.rglob('*.mp4') if p.resolve() not in before]
        if not newclips:raise RuntimeError('WanGP reported success but no fresh MP4 created; NEVER claim GPU video')
        # Map saved queue output explicitly; cannot safely guess which result matches which scene.
        if len(jobs)!=1 or len(newclips)!=1:raise RuntimeError('WanGP queue mapping ambiguous; use 1 clip per dispatch')
        clip=dest/(jobs[0]['id']+'.mp4')
        if newclips[0].resolve()!=clip.resolve():shutil.copy2(newclips[0],clip)
        inf=media_info(clip)
        results.append({'scene_id':jobs[0]['id'],'backend':'wangp-queue','source_file':str(newclips[0].name),'output':str(clip.name),'video':inf,
                       'sha256':hashlib.sha256(clip.read_bytes()).hexdigest()})
    elif args.mode=='wan21-t2v':
        for shot in jobs:
            if time.monotonic()-start>args.max_seconds-60:raise TimeoutError('Not enough time budget for new shot; stop')
            out=dest/(shot['id']+'.mp4')
            if out.exists():raise FileExistsError('Refusing overwrite; avoid duplicate inference')
            render_wan21_job(shot,out)
            inf=media_info(out)
            results.append({'scene_id':shot['id'],'backend':MODEL,'output':out.name,'video':inf,
                'reference_conditioned':False,'requires_mascot_identity_review':True,
                'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
    else:raise ValueError('Unsupported GPU mode')
    return {'schema':'fte.gpu.results.v1','mode':args.mode,'preflight':status,'model_inference_verified':True,
            'elapsed_seconds':round(time.monotonic()-start,1),'results':results}


def main(argv=None):
    a=argparse.ArgumentParser()
    a.add_argument('--mode',choices=('probe','wan21-t2v','wangp-queue'),required=True)
    a.add_argument('--jobs');a.add_argument('--output',default='/kaggle/working/fte_gpu_results')
    a.add_argument('--queue');a.add_argument('--wangp-root',default='/kaggle/working/Wan2GP')
    a.add_argument('--max-seconds',type=int,default=900);a.add_argument('--validate-only',action='store_true')
    args=a.parse_args(argv)
    if args.mode=='wangp-queue' and not args.queue:a.error('WanGP requires a saved queue --queue file')
    result=do_batch(args)
    Path(args.output).mkdir(parents=True,exist_ok=True)
    Path(args.output,'JOB_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print('FTE_KAGGLE_RESULT',json.dumps({'mode':args.mode,'verified':result.get('model_inference_verified',False),'outputs':len(result.get('results',[]))}))
    return result

if __name__=='__main__':main()
