"""Use Rhubarb's timed mouth cues when its CLI is installed."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import wave

SHAPES = {
    "X": (2.7,.65), "A": (3.8,.65), "B": (4.1,1.2), "C": (3.5,2.5),
    "D": (4.2,4.5), "E": (2.6,3.1), "F": (1.8,2.5), "G": (3.6,1.1), "H": (3.4,2)
}

def mouth_track(work, voice, rate, fps, duration, offset):
    root = Path(__file__).resolve().parent.parent / "motion-worker/cpu-lab"
    binary = os.getenv("RHUBARB_BIN") or shutil.which("rhubarb") or next(root.glob("Rhubarb*/rhubarb"), None)
    if not binary:
        return [None] * (duration * fps)
    wav_path = work / "dialogue.wav"
    with wave.open(str(wav_path),"wb") as wav:
        wav.setparams((1,2,rate,0,"NONE",""))
        wav.writeframes(voice.tobytes())
    cue_path=work/"mouth-cues.json"
    subprocess.run([binary,"-f","json","-o",cue_path,wav_path],check=True)
    shapes=[None]*(duration*fps)
    for cue in json.loads(cue_path.read_text())["mouthCues"]:
        start=round((offset+cue["start"])*fps)
        end=min(len(shapes),round((offset+cue["end"])*fps))
        for i in range(start,end):
            shapes[i]=SHAPES.get(cue["value"],SHAPES["X"])
    return shapes
