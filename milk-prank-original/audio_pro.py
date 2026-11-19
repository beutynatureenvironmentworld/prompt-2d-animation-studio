"""High-dynamic-range stereo Foley generated from mathematics, not sample libraries.
Includes original background score, room tone, footsteps, cloth, carton, milk,
cartoon spring and laughter cues; never claims to be neural text-to-audio.
"""
import json, math, wave, sys
from pathlib import Path
import numpy as np

SR=48000; SECONDS=15.0
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path("milk-prank-original/out")
OUT.mkdir(parents=True,exist_ok=True)
N=int(SR*SECONDS)
L=np.zeros((N,2),dtype=np.float64)
events=[]
def envelope(n,attack=.01,release=.11):
    t=np.arange(n,dtype=np.float64)/SR
    return np.minimum(1,np.maximum(0,t/attack))*np.minimum(1,np.maximum(0,(n/SR-t)/release))
def put(name,at,mono,gain=.2,pan=0.0):
    at=int(round(at*SR))
    n=min(len(mono),N-at)
    if n<=0 or at<0:return
    theta=(max(-1,min(1,pan))+1)*np.pi/4
    L[at:at+n,0]+=gain*np.cos(theta)*mono[:n]
    L[at:at+n,1]+=gain*np.sin(theta)*mono[:n]
    events.append(dict(name=name,time=round(at/SR,3),seconds=round(n/SR,3),pan=pan))
def tone(name,at,length,f0,f1,amp=.3,pan=0.):
    n=int(length*SR)
    tt=np.arange(n,dtype=np.float64)/SR
    phase=2*np.pi*(f0*tt+0.5*(f1-f0)/length*tt*tt)
    signal=(np.sin(phase)+0.29*np.sin(2*phase))*.76*envelope(n,.012,min(.12,length/3))
    put(name,at,signal,amp,pan)
def spray(name,at,length,amp=.18,pan=-.85,seed=5):
    n=int(length*SR)
    rng=np.random.default_rng(seed)
    noise=rng.standard_normal(n).astype(np.float64)
    # High-pass spray + low rumble. Pure DSP, no borrowed audio.
    hi=noise-np.convolve(noise,np.ones(13)/13,'same')
    ripple=(np.sin(2*np.pi*(34+8*np.sin(np.arange(n)/SR*9))*np.arange(n)/SR))
    env=envelope(n,.02,.17)*(.7+.3*np.sin(np.linspace(0,26*np.pi,n))**2)
    put(name,at,env*(hi*.48+ripple*.13),amp,pan)
def thump(name,at,amp=.30,pan=0):
    tone(name,at,.37,132,46,amp,pan)
    spray(name+'_click',at,.063,amp*.30,pan,seed=int(at*100)+1)
# Musical motif: original very quiet pentatonic toy-marimba melody.
notes=[(0,392),(.45,494),(.85,587),(1.55,494),(2.2,392),(3.2,523),
       (3.65,659),(4.15,523),(5.4,392),(6.1,523),(6.85,659),
       (7.55,587),(8.0,494),(8.7,440),(11.6,523),(12.3,587),(13.0,659),(13.8,784)]
for i,(at,fr) in enumerate(notes):
    n=int(.29*SR);tt=np.arange(n)/SR
    wavelet=(np.sin(2*np.pi*fr*tt)+.33*np.sin(4*np.pi*fr*tt))*np.exp(-13*tt)
    put('original_music_note_'+str(i),at,wavelet,.075,(-.2 if i%2==0 else .2))
for i in range(16):
    # low, unobtrusive night ambience on both channels
    f=60+i*.3
    tone('room_bed_'+str(i),i*.94,.8,f,f,.007,(-.3 if i%2 else .3))
# Exact performance cues from storyboard:
spray('first_milk_jet',.69,1.14,.30,-.7,11)
thump('girl_first_surprise',1.24,.29,-.78)
tone('carton_tilt_squeak',3.12,.33,570,970,.22,.65)
tone('fake_drink_sly_wink',4.36,.22,1180,490,.22,.7)
spray('boy_clothes_small_swish',5.35,.20,.05,.55,99)
tone('left_foot_step',6.52,.12,220,94,.10,-.7)
tone('reach_hand_swish',6.94,.39,660,370,.11,-.4)
tone('finger_contact',8.27,.16,240,160,.09,-.06)
tone('carton_crush',8.81,.30,195,580,.22,-.05)
spray('large_reverse_milk_jet',9.14,1.58,.37,-.72,22)
thump('girl_second_surprise',9.64,.43,-.76)
tone('eye_pop',9.84,.57,220,1030,.26,-.85)
for i,at in enumerate([12.18,12.44,12.78,13.09,13.39,13.74,14.07,14.4]):
    tone('cartoon_laugh_'+str(i),at,.16,410+40*(i%2),280,.17,.75)
    spray('laugh_breath_'+str(i),at+.015,.08,.035,.72,67+i)
# Stereo limiter / soft-tanh to avoid hard peaks.
peak=float(np.max(np.abs(L)))
if peak>.80:L=L*(.80/peak)
L=np.tanh(L*1.11)
audio=np.clip(L*32767,-32767,32767).astype('<i2')
wav=OUT/'FTE_PRO_STEREO_FOLEY_48K.wav'
with wave.open(str(wav),'wb') as wf:
    wf.setnchannels(2);wf.setsampwidth(2);wf.setframerate(SR)
    wf.writeframes(audio.tobytes())
manifest={"engine":"original synthetic stereo Foley DSP","sample_rate":SR,"channels":2,
          "duration":SECONDS,"events":events,"event_count":len(events),
          "peak_after_limiting":round(float(np.max(np.abs(L))),4),
          "copyrighted_samples_used":False,"neural_sfx_inference":False}
(OUT/'AUDIO_FOLEY_QA.json').write_text(json.dumps(manifest,indent=2)+'\n')
print("FTE_STEREO_PRO_FOLEY_SUCCESS",len(events),wav.stat().st_size,flush=True)
