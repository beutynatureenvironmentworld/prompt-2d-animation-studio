"""Original, offline garden ambience / object SFX and vocal-like reactions.

No pretrained voice model, no spoken story or narration, no copyrighted clips.
The 'oh/whoa/wow' signals are synthesized exclamatory formant glides, not
human voice recordings. Subtitles label the emotion beats for clarity.
"""
from pathlib import Path
import wave,math,random,struct
import numpy as np
from scipy.signal import butter, sosfilt

SR=22050

def add_at(buffer, start, signal, volume=1):
    j=max(0,round(start*SR)); n=min(len(signal),len(buffer)-j)
    if n>0:buffer[j:j+n]+=signal[:n]*volume


def taper(s,attack=.025,decay=.16):
    n=len(s); a=max(1,int(attack*SR));b=max(1,int(decay*SR));env=np.ones(n)
    env[:min(a,n)]*=np.linspace(0,1,min(a,n))
    env[max(0,n-b):]*=np.linspace(1,0,min(b,n))
    return s*env


def vocal(duration, glides, fundamental=165):
    """Original harmonic formant synthesis approximating an excited rounded vowel.
    glides is list of (time fraction, F1, F2, pitch factor). Not full TTS.
    """
    n=int(duration*SR); x=np.arange(n)/SR;u=x/duration
    points=np.array(glides,dtype=float);f1=np.interp(u,points[:,0],points[:,1]);f2=np.interp(u,points[:,0],points[:,2]);pitch=np.interp(u,points[:,0],points[:,3])*fundamental
    pitch*=1+.012*np.sin(2*np.pi*6*x)
    phase=2*np.pi*np.cumsum(pitch)/SR
    out=np.zeros(n,dtype=float)
    for h in range(1,31):
        freq=h*pitch
        amp=(np.exp(-.5*((freq-f1)/100)**2)+.68*np.exp(-.5*((freq-f2)/170)**2)+.17)*h**(-.75)
        out+=np.sin(h*phase)*amp
    out/=max(.1,np.max(abs(out)))
    return taper(out,.09,.25)


def bell(fund=392,duration=1.9):
    t=np.arange(int(SR*duration))/SR
    series=sum(np.sin(2*np.pi*fund*ratio*t+phase)*w for ratio,w,phase in [(1,1,0),(2.01,.4,.3),(2.97,.24,.9),(4.13,.13,1.7),(6.31,.07,.1)])
    s=series*np.exp(-2.1*t)
    return taper(s,.004,.03)


def chirp(freq=1100,duration=.23):
    t=np.arange(int(SR*duration))/SR
    phase=2*np.pi*(freq*t+150*t*t-100*t*t*t)
    s=np.sin(phase)+.25*np.sin(2*phase)
    return s*np.exp(-16*t)*np.sin(np.pi*np.clip(t/duration,0,1))


def make_audio(path,duration=11.5):
    n=round(duration*SR);rng=np.random.default_rng(727);b=np.zeros(n)
    # Naturalistic muted wind in treetops, intermittent bird chatter.
    noise=rng.standard_normal(n)
    low=sosfilt(butter(2,320,fs=SR,output='sos'),noise)
    b+=.014*low*(1+.36*np.sin(2*np.pi*.21*np.arange(n)/SR))
    cues=[]
    for t in (.6,1.4,2.5,3.0,4.9,8.65,10.2):
        add_at(b,t,chirp(840+(int(t*31)%6)*120),.12);cues.append((t,'garden birds'))
    for j in range(10):
        t=.99+j*.18
        tt=np.arange(int(.10*SR))/SR
        s=(rng.standard_normal(len(tt))*.24+np.sin(2*np.pi*93*tt)*.5)*np.exp(-50*tt)
        add_at(b,t,s,.16);cues.append((t,'grass step'))
    for t,p in ((3.72,420),(4.21,528),(4.71,658)):
        add_at(b,t,bell(p,1.45),.28);cues.append((t,'bell chime'))
    # Brief ORIGINAL vowel-like exclamations, not a narrative TTS track.
    add_at(b,5.26,vocal(.53,[(0,470,1050,1.08),(.40,560,1120,1.5),(1,430,970,.78)],fundamental=168),.19);cues.append((5.26,'OH! formant reaction'))
    add_at(b,5.97,vocal(.78,[(0,420,820,.78),(.25,610,1200,1.35),(.72,520,1000,1.10),(1,420,880,.63)],fundamental=163),.21);cues.append((5.97,'WOAH! formant reaction'))
    t=np.arange(int(.72*SR))/SR
    slide=np.sin(2*np.pi*(1120-720*t)*t)*np.exp(-3*t)
    add_at(b,6.72,slide,.10);cues.append((6.72,'magic slip'))
    tt=np.arange(int(.23*SR))/SR
    thud=(rng.standard_normal(len(tt))*.15+np.sin(2*np.pi*94*tt)*.7)*np.exp(-19*tt)
    add_at(b,7.48,thud,.33);cues.append((7.48,'soft grass thud'))
    for t,p in ((9.38,494),(9.54,588),(9.73,740)):
        add_at(b,t,bell(p,2.0),.22);cues.append((t,'flower sparkle'))
    add_at(b,10.28,vocal(.94,[(0,430,790,.9),(.28,520,1360,1.1),(.68,560,1550,1.32),(1,440,960,.75)],fundamental=194),.20);cues.append((10.28,'WOW! formant reaction'))
    for t,p in ((10.5,391.995),(10.52,493.88),(10.54,587.33)):
        add_at(b,t,bell(p,1),.18)
    # Saturate instead of clipping; fade gently.
    b=np.tanh(b*1.22)*.82
    b[-min(len(b),int(.3*SR)):]*=np.linspace(1,0,min(len(b),int(.3*SR)))
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    import soundfile as sf
    sf.write(path,b,SR,subtype='PCM_16')
    return {'events':[{ 'time':round(t,3),'type':name} for t,name in cues],'synthesis':'original ambience, chimes and three formant-vowel reactions; no narration','sample_rate':SR}
