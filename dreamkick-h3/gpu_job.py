"""Private Kaggle MiniMax H3 experiment for Funny Toon Ever Dream Kick.
Actual model output is recorded only after real video validation. No fake MP4.
Input: 9:16 2D pigtail-girl + white bald boy refs. Two 5-second scenes.
"""
import sys,os,subprocess,time,json,math,traceback,shutil
from pathlib import Path
WORK=Path('/kaggle/working') if Path('/kaggle/working').is_dir() else Path.cwd()
ROOT=Path('/kaggle/tmp') if Path('/kaggle/tmp').is_dir() else WORK
OUT=WORK/'fte_dreamkick_h3'; OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/'RESULT.json'
START=time.monotonic()
SCENES=[
("scene01_dream","Minimal flat 2D black-and-white hand-drawn funny cartoon, 9:16. Same white cartoon girl with black outlines, two pigtails, simple dress, wide sly grin, runs toward vivid GREEN soccer ball across clean lawn, winds her leg back with elastic stretch, kicks ball very hard to right. Natural continuous limbs, no X knees or floating shoulders, strong motion, fast comedic zoom, dramatic leg extension held at last frame. Original cartoon sounds, no captions. Frame all critical action within the central 40% width of a 4:3 image for a 9:16 vertical crop; keep both the kicking foot and ball in that safe area."),
("scene02_bedroom","Same girl with pigtails and white dress is lying asleep beside a bald white cartoon boy in a BED at NIGHT. At the start her dreaming leg extends in exactly the same motion as her soccer kick. Her foot directly hits the boy and sends him flying off mattress, eyes bulge in panic, limbs flail, then he crashes to ground and looks dizzy. Girl wakes shocked and leans over bed edge. Original expressive 2D ink line art, clear match cut staging, rubber-hose shoulders, no extra pupils, strong comedic timing, no captions. Frame both characters and all kick/contact action in the central 40% width of a 4:3 image for later portrait crop.")
]
def write(d): REPORT.write_text(json.dumps(d,indent=2,default=str)+'\n');print('FTE_RESULT',d['status'],flush=True)
def run(cmd,limit=180):subprocess.run(cmd,check=True,timeout=limit,stdout=subprocess.DEVNULL)
def reference_image(path,bed=False):
 from PIL import Image,ImageDraw
 im=Image.new('RGB',(384,672),'#fbfaf6' if not bed else '#e4e6f2');d=ImageDraw.Draw(im)
 ink='#111111'
 if bed:
  d.rectangle((16,340,368,541),fill='white',outline=ink,width=7)
  d.rectangle((28,388,359,516),fill='#f0eff7',outline=ink,width=5)
  d.rectangle((279,73,362,181),fill='#25283f',outline=ink,width=5)
  d.ellipse((309,89,350,128),fill='#fff7be')
  gx,gy=114,388;bx,by=284,394
 else:
  d.line((0,520,384,520),fill='#9acc89',width=5);gx,gy=142,375;bx,by=-300,-300
 def inkline(points,width=11):
  d.line(points,fill=ink,width=width,joint='curve')
  d.line(points,fill='white',width=max(2,width-6),joint='curve')
 def head(x,y,girl=False):
  if girl:
   for s in (-1,1):
    p=x+s*53
    d.ellipse((p-38,y-84,p+38,y-17),fill='white',outline=ink,width=5)
    d.line((x+s*41,y-44,p,y-60),fill=ink,width=5)
  d.ellipse((x-60,y-60,x+60,y+60),fill='white',outline=ink,width=7)
  for dx in (-26,26):
   if bed:
    d.arc((x+dx-17,y-12,x+dx+17,y+12),0,180,fill=ink,width=4)
   else:
    d.ellipse((x+dx-13,y-10,x+dx+13,y+18),fill='white',outline=ink,width=4)
    d.ellipse((x+dx-1,y+1,x+dx+9,y+12),fill=ink)
  if bed:d.ellipse((x-7,y+21,x+8,y+38),fill=ink)
  else:
   d.pieslice((x-41,y+13,x+43,y+56),0,180,fill='white',outline=ink,width=5)
   for n in range(-3,4):
    d.line((x+n*10,y+30,x+n*10,y+45),fill=ink,width=2)
 head(gx,gy,True)
 d.rounded_rectangle((gx-36,gy+65,gx+36,gy+147),radius=23,fill='white',outline=ink,width=6)
 for s in (-1,1):
  inkline([(gx+s*33,gy+90),(gx+s*66,gy+137)],10)
  inkline([(gx+s*26,gy+142),(gx+s*61,gy+219)],12)
 if not bed:
  d.ellipse((238,474,321,558),fill='#6efe45',outline=ink,width=6)
  d.polygon([(279,501),(299,515),(291,538),(266,537),(258,512)],fill=ink)
 if bed:
  head(bx,by,False)
  d.rounded_rectangle((bx-32,by+62,bx+32,by+132),radius=22,fill='white',outline=ink,width=6)
  for s in (-1,1):
   inkline([(bx+s*26,by+95),(bx+s*49,by+146)],10)
   inkline([(bx+s*22,by+126),(bx+s*42,by+179)],12)
 im.save(path)
def prepare_model_storage(checkout):
 """Require a complete private Kaggle Input model dataset or ample local space.

 Model files are never committed to public GitHub. Read-only mounted Kaggle
 datasets must include all shared and Ref2VA diffusion checkpoints.
 """
 from kaggle_h3.bootstrap import required_model_files
 model_dir=checkout/'ComfyUI'/'models'
 source=Path(os.environ.get('FTE_H3_MODEL_DATASET','/kaggle/input/fte-h3-models/models'))
 required=required_model_files('Ref2VA',include_diffusion=True)
 if source.is_dir():
  missing=[str(Path(directory)/filename) for directory,filename in required.values()
           if not (source/directory/filename).is_file()]
  if missing:
   raise RuntimeError('Private H3 model dataset is incomplete; missing: '+', '.join(missing))
  model_dir.mkdir(parents=True,exist_ok=True)
  for directory in sorted({v[0] for v in required.values()}):
   target=model_dir/directory
   if target.is_symlink():
    if target.resolve()!=(source/directory).resolve():
     raise RuntimeError('Unexpected existing model directory symlink: '+str(target))
   elif target.exists():
    if any(target.iterdir()):
     raise RuntimeError('Refusing to overwrite nonempty model directory: '+str(target))
    target.rmdir()
   else: pass
   if not target.is_symlink():target.symlink_to(source/directory,target_is_directory=True)
  return {'mode':'private_kaggle_dataset','source':str(source),'files':len(required)}
 free_gib=round(shutil.disk_usage(WORK).free/2**30,2)
 # Guardrail only; actual checkpoint sizes vary. No guarantee 50 GiB suffices.
 if free_gib<50:
  raise RuntimeError(
   f'Kaggle free disk {free_gib} GiB: too small for H3 checkpoints and temp files. '
   'Stage the complete licensed H3 model tree as a PRIVATE Kaggle Dataset at '
   '/kaggle/input/fte-h3-models/models (or set FTE_H3_MODEL_DATASET). '
   'Do not retry GPU download until storage is resolved.')
 return {'mode':'direct_download','free_gib':free_gib,'warning':'50 GiB is a guardrail, not a guaranteed requirement'}

def main():
 d={'status':'initialized','model':'MiniMax-H3 Singularity Ref2VA INT8','h3_inference_verified':False,'scenes':[],'device_count':0}
 write(d)
 try:
  import torch
  if not torch.cuda.is_available():raise RuntimeError('No GPU device allocated')
  d['device_count']=torch.cuda.device_count()
  d['gpu_names']=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
  a=OUT/'girl_soccer.png';b=OUT/'girl_boy_bedroom.png'
  reference_image(a,False);reference_image(b,True)
  checkout=ROOT/'kaggle_h3_github'
  run(['git','clone','--depth','1','https://github.com/celunah/kaggle_h3.git',str(checkout)],210)
  run([sys.executable,'-m','pip','install','-q','-r',str(checkout/'requirements-kaggle.txt')],490)
  sys.path.insert(0,str(checkout/'src'))
  from kaggle_h3.workflow import H3Request
  from kaggle_h3.pipeline import run_generation
  d['model_storage']=prepare_model_storage(checkout)
  write(d)
  for i,(slug,prompt) in enumerate(SCENES):
   if time.monotonic()-START>70*60:
    d['status']='budget_exhausted';break
   req=H3Request(prompt=prompt,character_references=[a],
     scene_references=[a if i==0 else b],duration_seconds=5.0,
     aspect_ratio='4:3',quality_mode='quick',seed=2417+i,
     turbo_mode=True,turbo_steps=4,mute_generated_audio=False)
   result=run_generation(req,project_root=checkout,comfy_root=checkout/'ComfyUI',
     backend='auto',allow_single_gpu_fallback=True,
     download_models=True,dry_run=False,max_attempts=1)
   paths=[Path(p) for p in result.get('outputs',[]) if Path(p).is_file()]
   item={'scene':slug,'status':result.get('status'),'verified':result.get('validation'),
         'gpu_verification':result.get('verification'),'output':None}
   if result.get('status')=='completed' and result.get('validation',{}).get('status')=='passed' and paths:
    dest=OUT/(slug+'_MiniMaxH3.mp4')
    shutil.copyfile(paths[0],dest);item['output']=str(dest)
   d['scenes'].append(item);write(d)
   if not item['output']:break
  if len(d['scenes'])==2 and all(x['output'] for x in d['scenes']):
   # Actual validated H3 scene clips normalized for vertical delivery; native H3 Ref2VA supports 4:3/16:9, not 9:16.
   normalized=[]
   for i,item in enumerate(d['scenes']):
    dst=OUT/f'normalized_{i+1}.mp4'
    run(['ffmpeg','-y','-loglevel','error','-i',item['output'],'-vf',
      'scale=540:960:force_original_aspect_ratio=increase,crop=540:960,fps=24',
      '-c:v','libx264','-preset','veryfast','-crf','21','-c:a','aac','-b:a','128k','-ar','44100',str(dst)],240)
    normalized.append(dst)
   lst=OUT/'list.txt';lst.write_text(''.join("file '"+str(x)+"'\n" for x in normalized))
   joined=OUT/'joined.mp4'
   run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(lst),
        '-c','copy',str(joined)],120)
   final=OUT/'Funny_Toon_Ever_Dream_Kick_ACTUAL_H3.mp4'
   # Original non-licensed synthesized comedy SFX and subtle room ambience.
   # Retain the native H3 audio in raw source clips for later editorial review.
   import wave,math,numpy as np
   SR=22050;N=SR*10
   y=np.zeros(N,dtype=np.float32)
   for when,freq,seconds,amp in [(0.55,92,.11,.21),(1.15,94,.11,.21),
       (3.75,230,.35,.48),(4.4,125,.42,.75),(5.0,450,.45,.35),
       (6.4,730,.55,.31),(7.0,98,.55,.65),(9.0,95,.4,.50)]:
    off=int(when*SR);n=min(round(seconds*SR),N-off)
    if n<=0:continue
    tt=np.arange(n,dtype=np.float32)/SR
    env=(1-tt/seconds).clip(0,1)**2
    y[off:off+n]+=(np.sin(2*np.pi*freq*tt)*env*amp).astype(np.float32)
   y+=.007*np.sin(2*np.pi*49*np.arange(N)/SR)
   audio=OUT/'original_comedy_sfx.wav'
   with wave.open(str(audio),'wb') as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((np.tanh(y)*29000).astype('<i2').tobytes())
   run(['ffmpeg','-y','-loglevel','error','-i',str(joined),'-i',str(audio),
     '-filter_complex','[0:a:0][1:a:0]amix=inputs=2:duration=first:weights=1 0.68:normalize=0[a]',
     '-map','0:v:0','-map','[a]','-vf',
     "drawtext=text='funnytoonever':fontsize=19:fontcolor=black:box=1:boxcolor=white@0.65:x=(w-text_w)/2:y=h-37",
     '-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',
     '-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart',str(final)],200)
   # Do not mark an MP4 production-ready without validating video, portrait ratio and audio.
   info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)],text=True))
   v=next((s for s in info.get('streams',[]) if s.get('codec_type')=='video'),None)
   audio_ok=any(s.get('codec_type')=='audio' for s in info.get('streams',[]))
   duration=float(info.get('format',{}).get('duration',0))
   if not v or int(v['width'])*16!=int(v['height'])*9 or not audio_ok or duration<8:
    raise RuntimeError('Final H3 QA failed: require 9:16 video, >=8 seconds and real audio stream')
   d['final_media_qa']={'width':v['width'],'height':v['height'],'seconds':duration,'has_audio':audio_ok}
   d['status']='completed'
   d['h3_inference_verified']=True;d['final_video']=str(final)
  else:d['status']=d['status'] if d['status']=='budget_exhausted' else 'incomplete_h3'
  d['elapsed_seconds']=round(time.monotonic()-START,2);write(d)
 except Exception as ex:
  d['status']='failed';d['error']=str(ex)[:1400]
  d['traceback_tail']=traceback.format_exc()[-2400:]
  d['elapsed_seconds']=round(time.monotonic()-START,2);write(d);raise
if __name__=='__main__':main()
