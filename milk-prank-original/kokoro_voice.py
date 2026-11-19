"""Produce REAL neural speech with Apache-2.0 Kokoro-82M from Hugging Face.
Do not emit a success manifest without real waveform inference. No voice cloning.
"""
import json, sys, traceback
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

out=Path(sys.argv[1]) if len(sys.argv)>1 else Path("milk-prank-original/out/voice")
out.mkdir(parents=True,exist_ok=True)
result={"model":"hexgrad/Kokoro-82M","license":"Apache-2.0 (model card)",
        "real_hugging_face_model_inference":False,"dialogue":[]}
try:
    pipeline=KPipeline(lang_code="a")
    scenes=[
        {"name":"girl_reaction","text":"Oh! Again?!","voice":"af_heart","start_at":10.72},
        {"name":"boy_laugh","text":"Ha ha! Gotcha!","voice":"am_michael","start_at":12.42},
    ]
    for scene in scenes:
        chunks=[]
        for _,_,signal in pipeline(scene["text"],voice=scene["voice"],speed=1.08):
            audio=np.asarray(signal,dtype=np.float32)
            if audio.size:chunks.append(audio)
        if not chunks:raise RuntimeError("Kokoro returned zero samples for "+scene["name"])
        voice=np.concatenate(chunks)
        if not np.all(np.isfinite(voice)):raise RuntimeError("Invalid neural output samples")
        wav=out/(scene["name"]+".wav")
        sf.write(str(wav),voice,24000,subtype="PCM_16")
        result["dialogue"].append({
            "name":scene["name"],"text":scene["text"],"voice":scene["voice"],
            "time_seconds":scene["start_at"],"duration":round(len(voice)/24000,4),
            "sample_rate":24000,"bytes":wav.stat().st_size})
    result["real_hugging_face_model_inference"]=True
    result["status"]="completed"
except Exception as exc:
    result["status"]="failed"
    result["error"]=repr(exc)
    result["traceback_tail"]=traceback.format_exc()[-2200:]
finally:
    (out/"VOICE_QA.json").write_text(json.dumps(result,indent=2)+"\n")
    print("KOKORO_REAL_NEURAL_VOICE_RESULT",json.dumps(result),flush=True)
if not result["real_hugging_face_model_inference"]: raise SystemExit(1)
