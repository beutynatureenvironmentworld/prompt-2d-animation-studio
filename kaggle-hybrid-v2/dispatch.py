"""Build a private bounded Kaggle job from the GPU manifest.

Default dry run. Submission requires Kaggle credential set in environment and
an explicit --submit. Credentials are NEVER serialized into kernel files.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
from story import validate_batch

ROOT=Path(__file__).resolve().parent
USER=re.compile(r'^[A-Za-z0-9_-]{2,64}$')


def package(username,mode,jobs,folder,minutes=20,queue_source=None,dataset_slug=None):
    if not USER.fullmatch(username):raise ValueError('Invalid Kaggle username')
    if mode not in ('probe','wan21-t2v','wangp-queue'):raise ValueError('Unsupported mode')
    if type(minutes)!=int or not 2<=minutes<=60:raise ValueError('2–60 minute hard ceiling')
    if mode!='probe':validate_batch(jobs)
    output=Path(folder).resolve();
    if output.exists() and list(output.iterdir()):raise FileExistsError('Refuse to overwrite job package')
    output.mkdir(parents=True,exist_ok=True)
    if dataset_slug and not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_-]+',dataset_slug):raise ValueError('Bad Kaggle dataset identifier')
    for f in ('gpu_worker.py','story.py','preflight.py','bootstrap_kaggle.sh'):
        shutil.copy2(ROOT/f,output/f)
    if mode!='probe':shutil.copy2(jobs,output/'gpu_jobs.json')
    if queue_source:
        if mode!='wangp-queue':raise ValueError('Queue supplied for incorrect mode')
        if Path(queue_source).suffix not in ('.json','.zip'):raise ValueError('Need exported WanGP queue .zip/.json')
        if Path(queue_source).stat().st_size>140*1024*1024:raise ValueError('Queue too large; use Kaggle Dataset mount')
        shutil.copy2(queue_source,output/'wangp_queue'+Path(queue_source).suffix)
    if mode=='wangp-queue' and not (queue_source or dataset_slug):raise ValueError('WanGP requires exported queue or user-managed dataset')
    if mode=='wangp-queue':
        qp=(f'/kaggle/input/{dataset_slug.split("/")[1]}/queue.zip' if dataset_slug else f'wangp_queue{Path(queue_source).suffix}')
        workerargs=['--mode','wangp-queue','--jobs','gpu_jobs.json','--queue',qp]
    elif mode=='wan21-t2v':workerargs=['--mode','wan21-t2v','--jobs','gpu_jobs.json']
    else:workerargs=['--mode','probe']
    payload={"mode":mode,"seconds":minutes*60,"workerargs":workerargs}
    # Write literal repr, not eval or subprocess shell interpolation.
    script='''import json,os,subprocess,sys\nfrom pathlib import Path\nC=%r\nHERE=Path(__file__).resolve().parent\nos.chdir(HERE)\nsubprocess.run(["bash",str(HERE/"bootstrap_kaggle.sh"),C["mode"]],check=True,timeout=2400)\nsubprocess.run([sys.executable,str(HERE/"gpu_worker.py"),*C["workerargs"],"--output","/kaggle/working/fte_gpu_results","--max-seconds",str(C["seconds"])],check=True,timeout=C["seconds"]+60)\n'''%payload
    (output/'gpu_job.py').write_text(script)
    digest=hashlib.sha256((mode+username+str(Path(jobs).resolve())).encode()).hexdigest()[:8]
    slug='fte-hybrid-'+mode+'-'+digest
    metadata={'id':username+'/'+slug,'title':'Funny Toon Ever Hybrid '+mode+' '+digest,
      'code_file':'gpu_job.py','language':'python','kernel_type':'script','is_private':True,
      'enable_gpu':True,'machine_shape':'NvidiaTeslaT4',
      'enable_internet':mode!='probe',
      'dataset_sources':[dataset_slug] if dataset_slug else [],
      'competition_sources':[],'kernel_sources':[],'model_sources':[]}
    (output/'kernel-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    return metadata['id']


def main():
 p=argparse.ArgumentParser();p.add_argument('--username',required=True);p.add_argument('--mode',choices=('probe','wan21-t2v','wangp-queue'),default='probe')
 p.add_argument('--jobs',default=str(ROOT/'examples/gpu_jobs.json'));p.add_argument('--folder',default='output/kaggle_job')
 p.add_argument('--minutes',type=int,default=12);p.add_argument('--queue');p.add_argument('--dataset-slug');p.add_argument('--submit',action='store_true')
 a=p.parse_args();kernel=package(a.username,a.mode,a.jobs,a.folder,a.minutes,a.queue,a.dataset_slug)
 print('PRIVATE_KAGGLE_JOB',kernel)
 if not a.submit:print('DRY_RUN_ONLY_NO_GPU_CONSUMED');return
 if not os.getenv('KAGGLE_API_TOKEN'):raise RuntimeError('KAGGLE_API_TOKEN secret missing: no submission')
 if not shutil.which('kaggle'):raise RuntimeError('Install `pip install kaggle` in GitHub runner first')
 cmd=['kaggle','kernels','push','-p',str(Path(a.folder).resolve()),'--accelerator','NvidiaTeslaT4','-t',str(a.minutes*60)]
 subprocess.run(cmd,check=True,timeout=90)
 print('SUBMISSION_ONLY_NOT_YET_VERIFIED',kernel)

if __name__=='__main__':main()
