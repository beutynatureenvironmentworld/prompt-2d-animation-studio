#!/usr/bin/env python3
"""FTE sound director: deterministic original SFX + frame-accurate FFmpeg mixing.

Uses only stdlib and FFmpeg (fits 1GB Oracle VPS for normal short-form clips).
Optional pre-produced voice WAV clips can be passed as normal cue files.
No dependency on ComfyUI, MoviePy, browser/React, CUDA or HF authentication.
"""
import argparse,json,math,random,shutil,subprocess,struct,wave
from pathlib import Path

SAMPLE_RATE=48000
def synth(tone, dest, seconds=1):
    """Generate one original public-domain-like effect algorithmically, not an external sample."""
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    n=int(SAMPLE_RATE*seconds)
    rng=random.Random(len(tone)+41)
    samples=[]
    phase=0.
    for i in range(n):
        t=i/SAMPLE_RATE
        if tone=="boing":
            freq=900-700*min(t/.52,1)
            value=math.sin(phase)*math.exp(-5*t)
        elif tone=="spray":
            freq=450+150*math.sin(t*9)
            value=(rng.uniform(-1,1)*.65+math.sin(phase)*.12)*(1-math.exp(-t*15))*math.exp(-.7*t)
        elif tone=="sneaky":
            freq=650+300*math.sin(t*9)
            value=math.sin(phase)*math.exp(-2*t)*(.6+.4*math.sin(t*17)**2)
        elif tone=="click":
            freq=1000-300*min(t/.1,1)
            value=(math.sin(phase)*.6+rng.uniform(-1,1)*.12)*math.exp(-45*t)
        elif tone=="laugh":
            freq=280+75*math.sin(t*25)
            value=(math.sin(phase)+.17*math.sin(2*phase)+rng.uniform(-1,1)*.09)*math.exp(-2*t)
            value*=.5+.5*(math.sin(t*23)**2)
        elif tone=="boom":
            freq=100-55*min(t/.6,1)
            value=math.sin(phase)*math.exp(-5*t)
        else:
            freq=420
            value=math.sin(phase)*math.exp(-4*t)
        phase+=2*math.pi*freq/SAMPLE_RATE
        env=min(1.,t/.008)*min(1.,max(0,seconds-t)/.04)
        samples.append(int(max(-1.,min(1.,value*.68*env))*32767))
    with wave.open(str(dest),"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(SAMPLE_RATE)
        out.writeframes(struct.pack("<"+"h"*len(samples),*samples))
    return dest

def probe(path):
    d=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)],text=True))
    return d

def render(video,output,config,work):
    for exe in ("ffmpeg","ffprobe"):
        if not shutil.which(exe):raise RuntimeError("Missing executable: "+exe)
    video=Path(video).resolve();output=Path(output).resolve();work=Path(work).resolve()
    if not video.is_file() or video.stat().st_size==0:raise FileNotFoundError(video)
    if video==output:raise RuntimeError("Refusing in-place overwrite of source video")
    work.mkdir(parents=True,exist_ok=True);output.parent.mkdir(parents=True,exist_ok=True)
    source=probe(video)
    duration=float(source["format"]["duration"])
    src_audio=any(s.get("codec_type")=="audio" for s in source["streams"])
    spec=json.loads(Path(config).read_text())
    cues=spec.get("cues",[])
    if not isinstance(cues,list) or len(cues)>32:raise ValueError("Supported cues: 0..32")
    cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(video)]
    fc=[]
    if src_audio:
        fc.append("[0:a:0]aresample=48000,aformat=channel_layouts=stereo,volume=0.75[base]")
    else:
        fc.append("anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration="+str(duration)+",asetpts=PTS-STARTPTS[base]")
    tracks=["[base]"]
    rec=[]
    for idx,item in enumerate(cues,1):
        if not isinstance(item,dict):raise ValueError("cue must be object")
        start=float(item.get("at_seconds",duration*float(item.get("at_fraction",0))))
        if not (0<=start<duration):continue
        volume=float(item.get("volume",.65))
        if volume<0 or volume>2:raise ValueError("Invalid volume")
        if "file" in item:
            audio=Path(item["file"]).resolve()
            if not audio.is_file():raise FileNotFoundError(audio)
        else:
            kind=str(item.get("sfx","boing"))
            if kind not in ("boing","spray","sneaky","click","laugh","boom"):
                raise ValueError("Unknown procedural SFX: "+kind)
            audio=synth(kind,work/f"cue_{idx:02}_{kind}.wav",min(2.3,float(item.get("seconds",.6))))
        cmd+=["-i",str(audio)]
        delay=int(round(start*1000))
        fc.append(f"[{idx}:a:0]aresample=48000,aformat=channel_layouts=stereo,volume={volume:.3f},adelay={delay}|{delay}[cue{idx}]")
        tracks.append(f"[cue{idx}]")
        rec.append({"at":round(start,3),"volume":volume,"cue":str(audio.name)})
    fc.append("".join(tracks)+f"amix=inputs={len(tracks)}:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.85:level=disabled,aresample=48000[mixed]")
    cmd+=["-filter_complex",";".join(fc),"-map","0:v:0","-map","[mixed]",
          "-c:v","copy","-c:a","aac","-b:a","192k",
          "-movflags","+faststart","-t",str(duration),str(output)]
    subprocess.run(cmd,check=True,timeout=170)
    new=probe(output)
    stream=next(s for s in new["streams"] if s["codec_type"]=="video")
    audio_stream=next((s for s in new["streams"] if s["codec_type"]=="audio"),None)
    seconds=float(new["format"]["duration"])
    verified=bool(audio_stream) and abs(seconds-duration)<.3 and output.stat().st_size>2000
    report={"verified":verified,"mode":"FFmpeg-only SFX mixing, no neural voice claimed",
       "source":str(video),"output":str(output),"source_has_audio":src_audio,
       "duration":seconds,"size_bytes":output.stat().st_size,
       "codec_video":stream["codec_name"],"codec_audio":audio_stream["codec_name"] if audio_stream else None,
       "events":rec}
    (work/"AUDIO_QA.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if not verified:raise RuntimeError("Output QA failed")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--video",required=True);p.add_argument("--output",required=True)
    p.add_argument("--cues",required=True);p.add_argument("--work",default="audio-director/output")
    a=p.parse_args()
    render(a.video,a.output,a.cues,a.work)
