"""Private Modal functions for one LTX-2.5 shot and CPU-only model staging."""
import functools
import tempfile
from pathlib import Path

import modal

MODEL = "Lightricks/LTX-2.5-Diffusers"
MODEL_REVISION = "426936f8b22dc28e4def61e515478b0b7e4a53cc"
DIFFUSERS_REVISION = "ed32672706fec20ddac3a090c5a8290b3fd313cb"
CACHE = Path("/weights/hub")
MODEL_PATH = CACHE / "models--Lightricks--LTX-2.5-Diffusers" / "snapshots" / MODEL_REVISION
READY = Path("/weights") / (MODEL_REVISION + ".ready")
FPS = 24
# Inference dimensions are multiples of 32; output crops preserve exact ratios.
SIZES = {
    "16:9": (960, 544, 960, 540),
    "9:16": (544, 960, 540, 960),
    "1:1": (704, 704, 704, 704),
    "4:3": (896, 672, 896, 672),
    "3:4": (672, 896, 672, 896),
}

app = modal.App("vidbest-ltx25")
volume = modal.Volume.from_name("vidbest-ltx25-weights", create_if_missing=True)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git", "ffmpeg", "libgl1", "libsndfile1")
    .pip_install(
        "torch", "torchvision", "torchaudio", "transformers", "accelerate",
        "sentencepiece", "protobuf", "av", "safetensors", "ftfy", "scipy",
        "diffusers @ git+https://github.com/huggingface/diffusers.git@" + DIFFUSERS_REVISION,
    )
    .env({"HF_HOME": "/weights", "HF_HUB_DISABLE_TELEMETRY": "1"})
)


@app.function(image=image, secrets=[modal.Secret.from_name("vidbest-huggingface")],
              volumes={"/weights": volume}, timeout=3600, retries=0, max_containers=1)
def prepare_weights():
    from diffusers import LTX2Pipeline

    # download() reads model_index.json and resolves only pipeline components.
    path = LTX2Pipeline.download(MODEL, revision=MODEL_REVISION, cache_dir=str(CACHE))
    if Path(path).resolve() != MODEL_PATH.resolve():
        raise RuntimeError("Staged snapshot does not match the pinned revision")
    READY.touch()
    volume.commit()
    return MODEL_REVISION


@functools.lru_cache(maxsize=1)
def _pipeline():
    import torch
    from diffusers import LTX2Pipeline

    if not READY.is_file():
        volume.reload()
    if not READY.is_file():
        raise RuntimeError("Stage weights first with prepare_weights")
    pipe = LTX2Pipeline.from_pretrained(str(MODEL_PATH), torch_dtype=torch.bfloat16,
                                        local_files_only=True)
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_tiling()
    return pipe


@app.function(image=image, gpu="H100", memory=98304, volumes={"/weights": volume},
              timeout=900, retries=0, max_containers=1, scaledown_window=10)
def render_shot(prompt: str, ratio: str, seconds: int, seed: int) -> bytes:
    import torch
    from diffusers.pipelines.ltx2.utils import DEFAULT_NEGATIVE_PROMPT, DISTILLED_SIGMA_VALUES
    from diffusers.utils import encode_video

    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 6000:
        raise ValueError("Supply a prompt between 1 and 6000 characters")
    if ratio not in SIZES or type(seconds) is not int or not 1 <= seconds <= 10:
        raise ValueError("Choose a supported aspect ratio and 1–10 seconds per shot")
    if type(seed) is not int or not 0 <= seed < 2**63:
        raise ValueError("Seed must be a nonnegative 63-bit integer")
    width, height, out_width, out_height = SIZES[ratio]
    pipe = _pipeline()
    frame_count = FPS * seconds
    with torch.inference_mode():
        video, audio = pipe(
            prompt=prompt, negative_prompt=DEFAULT_NEGATIVE_PROMPT,
            width=width, height=height, num_frames=frame_count + 1,
            frame_rate=float(FPS), sigmas=DISTILLED_SIGMA_VALUES,
            guidance_scale=1.0, audio_guidance_scale=1.0,
            stg_scale=0.0, audio_stg_scale=0.0,
            modality_scale=1.0, audio_modality_scale=1.0,
            generator=torch.Generator("cuda").manual_seed(seed),
            output_type="np", return_dict=False,
        )
    left, top = (width - out_width) // 2, (height - out_height) // 2
    frames = video[0][:frame_count, top:top + out_height, left:left + out_width]
    sample_rate = pipe.vocoder.config.output_sampling_rate
    waveform = audio[0][..., :sample_rate * seconds].float().cpu()
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "shot.mp4"
        encode_video(frames, fps=FPS, output_path=str(output), audio=waveform,
                     audio_sample_rate=sample_rate)
        return output.read_bytes()
