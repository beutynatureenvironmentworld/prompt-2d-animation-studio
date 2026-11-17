"""All sounds synthesized in CPU code, no external clips or copyrighted music."""
from pathlib import Path
import math,random,numpy as np,wave
SR=22050

def create_sound(path,duration=11.4):
 n=round(duration*SR);a=np.zeros(n,np.float32)
 rng=np.random.default_rng(17)
 events=[(.20,.18,'bling'),(1.78,.24,'whoosh'),(2.22,.15,'crunch'),(2.65,.13,'gulp'),
         (3.20,.75,'rising'),(4.24,.31,'boing'),(5.17,.25,'boom'),(5.48,2.27,'flame'),
         (7.73,.6,'steam'),(8.30,.28,'cough'),(9.90,.18,'pop'),(10.55,.47,'bling')]
 for when,length,typ in events:
  start=int(when*SR);total=min(round(length*SR),n-start)
  if total<=0:continue
  sec=np.arange(total,dtype=np.float32)/SR;z=sec/length
  envelope=np.minimum(1,np.minimum(sec*42,(length-sec)*17).clip(0,1))
  if typ=='bling':v=np.sin(2*np.pi*(790*sec+230*sec*sec))*.65+np.sin(2*np.pi*1200*sec)*.22
  elif typ=='whoosh':v=rng.normal(size=total).astype(np.float32)*.36*np.sin(z*np.pi)
  elif typ=='crunch':v=(rng.normal(size=total).astype(np.float32)*.5+np.sin(2*np.pi*175*sec)*.4)*(1-z)**1.8
  elif typ=='gulp':v=np.sin(2*np.pi*(190-100*z)*sec)*.6
  elif typ=='rising':v=np.sin(2*np.pi*(180*sec+560*sec*sec))*np.sin(np.pi*z)*.7
  elif typ=='boing':v=np.sin(2*np.pi*(180+90*np.sin(2*np.pi*2*sec))*sec)*.75
  elif typ=='boom':v=(np.sin(2*np.pi*(90-38*z)*sec)+rng.normal(size=total).astype(np.float32)*.2)*(1-z)**3
  elif typ=='flame':v=(rng.normal(size=total).astype(np.float32)*.31+np.sin(2*np.pi*76*sec)*.16)*(np.minimum(1,z*9))
  elif typ=='steam':v=(rng.normal(size=total).astype(np.float32)*.24+np.sin(2*np.pi*465*sec)*.2)*(1-z)
  elif typ=='cough':v=rng.normal(size=total).astype(np.float32)*.39*(1-z)**3
  else:v=np.sin(2*np.pi*350*sec)*(1-z)
  a[start:start+total]+=v*envelope*.75
 a=np.tanh(a*1.2)
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(path),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((a*28000).astype('<i2').tobytes())
 return {'event_count':len(events),'sample_rate':SR}
