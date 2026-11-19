"""Original copyright-safe synthetic comedy sound design for midnight-jar milk prank.
Source character motion is SVG renderer, not AI diffusion. No external audio files.
"""
from pathlib import Path
import math, wave, subprocess, sys, json
import numpy as np
SR=44100; DURATION=15
y=np.zeros(SR*DURATION,dtype=np.float32)
def chirp(start,duration,f0,f1,amp=.2):
    a=int(start*SR); n=int(duration*SR)
    t=np.arange(n,dtype=np.float32)/SR
    freq=f0+(f1-f0)*(t/duration)
    phase=np.cumsum(freq)/SR*2*np.pi
    env=np.sin(np.pi*np.clip(t/duration,0,1))**1.1
    y[a:a+n]+=amp*np.sin(phase)*env
def noise(start,duration,amp=.17,seed=0):
    a=int(start*SR);n=int(duration*SR)
    rng=np.random.default_rng(seed)
    z=rng.standard_normal(n).astype(np.float32)
    z[1:]-=.94*z[:-1]
    env=np.sin(np.pi*np.linspace(0,1,n))**1.3
    y[a:a+n]+=amp*z*env
# Dimensional but gentle room-tone; silence remains in narrative holds.
for at in np.arange(0,15,1.5): chirp(float(at),.13,165,132,.015)
# First spray and her shocked reaction.
noise(.72,.87,.23,13);chirp(1.36,.42,148,55,.28)
# Sneaky twist, reveal, plastic-carton squeak.
chirp(3.17,.20,560,890,.08);chirp(3.38,.27,900,370,.11)
noise(4.2,.34,.08,61);chirp(4.24,.29,260,740,.15)
chirp(5.65,.22,700,1130,.08)
# Her reaching hand and compressing milk carton.
chirp(7.38,.42,170,450,.11);chirp(8.57,.34,210,90,.12)
# Large reverse-splash that hits girl, followed by bass comedy sting.
noise(9.13,1.25,.35,97);chirp(9.46,.49,740,190,.23)
chirp(9.83,.60,110,46,.46);chirp(9.92,.38,228,71,.16)
# Synthetic comic laughter; not human voice or TTS.
for i,at in enumerate([12.22,12.52,12.78,13.10,13.39,13.75,14.06,14.41]):
    chirp(at,.19,370+30*(i%2),280,.14)
    chirp(at+.06,.12,640,430,.06)
    noise(at,.09,.018,300+i)
peak=float(np.max(np.abs(y)))
if peak>0:y=y/peak*.86
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
wav=out/'original_comedy_sfx.wav'
with wave.open(str(wav),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR)
    f.writeframes((y*32767).astype(np.int16).tobytes())
print('SFX_TIMELINE_GENERATED',str(wav),len(y)/SR)
