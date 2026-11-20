#!/usr/bin/env python3
"""Generate original sound effects from text with Stable Audio Open Small.

Model requires Hugging Face license acceptance. GPU strongly recommended.
Avoid uploading a model or artifacts to public repositories.
"""
import argparse
from pathlib import Path

def generate(prompt: str, out: str, seconds: float, steps: int,
             force_cpu: bool = False):
    import torch
    import torchaudio
    from einops import rearrange
    from stable_audio_tools import get_pretrained_model
    from stable_audio_tools.inference.generation import generate_diffusion_cond
    if not torch.cuda.is_available() and not force_cpu:
        raise RuntimeError("No GPU: re-run with --force-cpu only if you accept very slow CPU generation")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, config = get_pretrained_model("stabilityai/stable-audio-open-small")
    model = model.to(device).eval()
    sample_rate = config["sample_rate"]
    duration = min(11.0, max(0.3, seconds))
    with torch.inference_mode():
        audio = generate_diffusion_cond(model,
            steps=steps,
            cfg_scale=1.0,
            conditioning=[{"prompt": prompt, "seconds_total": duration}],
            sample_size=config["sample_size"],
            sampler_type="pingpong",
            device=device)
    output = rearrange(audio, "b d n -> d (b n)")
    output = output.to(torch.float32)
    output = output / output.abs().max().clamp(min=1e-6) * .90
    output = output[..., :round(duration*sample_rate)].cpu()
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(out, output, sample_rate)
    print("GENERATED_MODEL_AUDIO", out, output.shape, sample_rate)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seconds", type=float, default=3.0)
    p.add_argument("--steps", type=int, default=8)
    p.add_argument("--force-cpu", action="store_true")
    a = p.parse_args()
    generate(a.prompt, a.out, a.seconds, a.steps, a.force_cpu)
