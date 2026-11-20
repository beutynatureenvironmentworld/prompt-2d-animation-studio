#!/usr/bin/env python3
"""Text-driven sound-effects model runner: Stable Audio Open Small / Audio 3 Small.

Requires Hugging Face user acceptance of gated model license, and ideally GPU.
Does NOT run neural music/audio inference automatically in CPU CI.
"""
import argparse
from pathlib import Path
MODELS={"open-small":("stabilityai/stable-audio-open-small","generate_diffusion_cond"),
        "3-small-sfx":("stabilityai/stable-audio-3-small-sfx","generate_diffusion_cond_inpaint")}

def generate(which,prompt,out,seconds,steps,force_cpu):
    import torch,torchaudio
    from einops import rearrange
    from stable_audio_tools import get_pretrained_model
    import stable_audio_tools.inference.generation as gen
    if not torch.cuda.is_available() and not force_cpu:
        raise RuntimeError("GPU unavailable; use verified CPU Foley instead")
    device="cuda" if torch.cuda.is_available() else "cpu"
    model_id,method=MODELS[which]
    print("LOADING_LICENSED_MODEL",model_id,flush=True)
    model,config=get_pretrained_model(model_id)
    model=model.to(device).eval()
    if device=="cuda":model=model.to(torch.float16)
    sr=config["sample_rate"]
    duration=min(11.0,max(0.3,seconds))
    with torch.inference_mode():
        audio=getattr(gen,method)(
            model,steps=steps,cfg_scale=1.0,
            conditioning=[{"prompt":prompt,"seconds_total":duration}],
            sample_size=config["sample_size"],sampler_type="pingpong",device=device)
    outaudio=rearrange(audio,"b d n -> d (b n)").float()
    outaudio=(outaudio/outaudio.abs().max().clamp(min=1e-6)).clamp(-1,1)
    outaudio=outaudio[...,:round(sr*duration)].cpu()
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    torchaudio.save(str(path),outaudio,sr)
    print("LICENSED_NEURAL_SFX_GENERATED",model_id,str(path),round(outaudio.shape[-1]/sr,3))
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model",choices=list(MODELS),default="open-small")
    p.add_argument("--prompt",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--seconds",type=float,default=3)
    p.add_argument("--steps",type=int,default=8)
    p.add_argument("--force-cpu",action="store_true")
    args=p.parse_args()
    generate(args.model,args.prompt,args.out,args.seconds,args.steps,args.force_cpu)
