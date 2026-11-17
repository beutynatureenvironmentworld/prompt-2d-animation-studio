"""Original synthesized percussion and comedy SFX; no copyrighted audio."""
import wave,math,struct,random
from pathlib import Path

def make_audio(path,duration=11.5,sr=22050):
    rng=random.Random(42);samples=[0.]*int(sr*duration)
    events=[]
    for j in range(9):events.append((.92+j*.205,'step',.09,.39))
    for t in (3.72,4.22,4.71):events.append((t,'knock',.15,.82))
    events += [(2.69,'brake',.21,.51),(5.35,'boing',.44,.46),(6.05,'whoosh',.55,.48),
               (7.20,'slip',.74,.52),(7.60,'thud',.25,.67),(8.45,'pop',.18,.48),
               (9.50,'ding',.58,.42),(10.70,'ding',.53,.39)]
    for start,name,dur,amp in events:
        i0=max(0,int(start*sr));i1=min(len(samples),int((start+dur)*sr));N=max(1,i1-i0)
        for i in range(i0,i1):
            z=(i-i0)/N;tt=z*dur
            fade=(1-z)**(2 if name in ('step','knock','thud') else 1.2)
            if name=='step':w=rng.uniform(-1,1)*.65+math.sin(2*math.pi*75*tt)*.35
            elif name=='knock':w=(math.sin(2*math.pi*142*tt)+.6*math.sin(2*math.pi*221*tt)+rng.uniform(-1,1)*.38)*.5
            elif name=='brake':w=math.sin(2*math.pi*(550-300*z)*tt)*(.8-z*.5)+rng.uniform(-1,1)*.2
            elif name=='boing':w=math.sin(2*math.pi*(240+180*z)*tt)
            elif name=='whoosh':w=rng.uniform(-1,1)*math.sin(math.pi*z)
            elif name=='slip':w=math.sin(2*math.pi*(790-560*z)*(tt))
            elif name=='thud':w=math.sin(2*math.pi*(116-65*z)*tt)+rng.uniform(-1,1)*.3
            elif name=='pop':w=math.sin(2*math.pi*370*tt)
            elif name=='ding':w=math.sin(2*math.pi*750*tt)+.24*math.sin(2*math.pi*1200*tt)
            samples[i]+=w*fade*amp
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes(b''.join(struct.pack('<h',round(max(-1,min(1,v))*.71*32767)) for v in samples))
    return {'events':[{'sec':e[0],'type':e[1]} for e in events],'filename':str(path),'samples':len(samples)}
