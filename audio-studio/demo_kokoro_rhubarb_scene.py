#!/usr/bin/env python3
"""Synthesize scene-specific FastToon dialogue with real Kokoro 82M voices.

Rhubarb CLI generates independent A-H/X cues for each original line BEFORE
mixing. One 9sec Opus track and aligned mouth timeline are committed for use
by the 2D portrait renderer. RVC and Stable Audio are separate unverified mods.
"""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

SR=24000
SEGMENTS=[
 {"start":0.69,"role":"girl","voice":"af_heart","speech":"Help! I'm falling!","speed":1.22},
 {"start":1.79,"role":"boy","voice":"am_puck","speech":"I've got you!","speed":1.22},
 {"start":4.81,"role":"girl","voice":"af_heart","speech":"You saved me!","speed":1.29},
 {"start":5.40,"role":"boy","voice":"am_puck","speech":"No problem!","speed":1.25},
 {"start":6.28,"role":"girl","voice":"af_heart","speech":"Eww! What's that smell?","speed":1.37},
 {"start":8.01,"role":"boy","voice":"am_puck","speech":"Oh, no!","speed":1.25}
]
def main(out_dir,rhubarb):
 from kokoro import KPipeline
 out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
 pipelines={"boy":KPipeline(lang_code="a"),"girl":KPipeline(lang_code="a")}
 timeline={"fps":30,"duration":9.0,
           "provenance":{"voice_model":"hexgrad/Kokoro-82M",
                         "mouth_engine":"Rhubarb Lip Sync phonetic recognizer",
                         "rvc_applied":False,"stable_audio_model_sfx_applied":False},
           "segments":[]}
 voice=np.zeros((round(9*SR),),np.float32)
 for i,s in enumerate(SEGMENTS):
  parts=[]
  for _,_,audio in pipelines[s["role"]](s["speech"],voice=s["voice"],
                                        speed=s["speed"]):
   parts.append(audio.detach().cpu().numpy() if hasattr(audio,"detach") else np.asarray(audio))
  if not parts:raise RuntimeError("Kokoro unexpectedly produced silence")
  x=np.concatenate(parts).astype(np.float32)
  maxlen=max(0,len(voice)-round(s["start"]*SR))
  x=x[:maxlen]
  if len(x)==0:raise RuntimeError("Speech starts beyond timeline")
  loud=float(np.sqrt(np.mean(x*x)))
  if loud<0.002:raise RuntimeError("Kokoro output too quiet")
  x=x*min(1.3,0.21/max(loud,1e-6))
  path=out/(f"voice_{i:02d}_{s['role']}.wav")
  sf.write(path,x,SR)
  cues_path=out/(f"voice_{i:02d}_{s['role']}.json")
  subprocess.run([rhubarb,"--recognizer","phonetic","-f","json","-o",
                  str(cues_path),str(path)],check=True,timeout=80)
  parsed=json.loads(cues_path.read_text())
  cues=[{"start":round(float(c["start"]),3),
         "end":round(float(c["end"]),3),"value":c["value"]}
        for c in parsed["mouthCues"]]
  base=round(s["start"]*SR)
  voice[base:base+len(x)]+=x
  timeline["segments"].append({**s,"duration":round(len(x)/SR,3),
                              "cues":cues})
  print("RHU_KOKORO_PASS",s["role"],len(cues),
        "seconds",round(len(x)/SR,3),"start",s["start"],flush=True)
 voice=np.tanh(voice*1.2)*0.84
 sf.write(out/"FastToon_9s_Kokoro_Dialogue_Only.wav",voice,SR)
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-i",str(out/"FastToon_9s_Kokoro_Dialogue_Only.wav"),
       "-c:a","libopus","-b:a","12k","-ac","1","-ar","24000",
       str(out/"FastToon_9s_Kokoro_Dialogue_Only.opus")],check=True,timeout=45)
 (out/"FastToon_9s_Rhubarb_Aligned.json").write_text(
      json.dumps(timeline,indent=2,ensure_ascii=False))
 total=sum(len(s["cues"]) for s in timeline["segments"])
 assert total>=15, "Unexpected low viseme cue count"
 assert len(voice)==9*SR
 print("FINAL_KOKORO_RHUBARB_DEMO_PASS","segments",len(SEGMENTS),
       "viseme_cues",total,"opus_bytes",
       (out/"FastToon_9s_Kokoro_Dialogue_Only.opus").stat().st_size,
       flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--out",default="audio-studio/outputs/kokoro_rhubarb_scene")
 p.add_argument("--rhubarb",required=True)
 args=p.parse_args()
 main(args.out,args.rhubarb)
