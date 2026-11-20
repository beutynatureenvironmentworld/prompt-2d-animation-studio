"""Small, opt-in Modal GPU image-to-video test for original 2D slapstick characters.

No API deployment, no background GPU usage, no paid model APIs.
This is a REAL LTX-Video 2B-ish diffusion model pilot, not LTX-2.3.
UNTESTED on the user's Modal workspace; GPU charges begin when you run it.
"""
from __future__ import annotations
from pathlib import Path
import modal

APP_NAME = "funny-toon-modal-credit-pilot"
MODEL_ID = "Lightricks/LTX-Video"
app = modal.App(APP_NAME)

runtime = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch==2.7.0",
        "diffusers==0.33.1",
        "transformers==4.51.3",
        "accelerate==1.6.0",
        "huggingface-hub==0.36.0",
        "sentencepiece==0.2.0",
        "Pillow>=11,<13",
        "imageio==2.37.0",
        "imageio-ffmpeg==0.5.1",
    )
    .env({"HF_HOME": "/cache/huggingface"})
)
# Keeps downloaded weights between runs; storage is metered.
cache = modal.Volume.from_name("funny-toon-ltx-weight-cache", create_if_missing=True)

NEGATIVE = (
    "static puppet, rigid motion, floating hand, incorrect plug contact, "
    "changing clothes, morphing faces, extra limbs, duplicate pupils, "
    "unwanted camera pan, photoreal, 3D rendering, text, watermarks"
)
WIDTH, HEIGHT = 384, 672
FRAMES, FPS = 49, 24
STEPS = 16

@app.cls(
    image=runtime,
    gpu="L40S",
    volumes={"/cache": cache},
    scaledown_window=0,
    max_containers=1,
    timeout=900,
)
class SlapstickVideo:
    @modal.enter()
    def setup(self):
        import torch
        from diffusers import LTXImageToVideoPipeline
        self.pipe = LTXImageToVideoPipeline.from_pretrained(
            MODEL_ID, torch_dtype=torch.bfloat16
        )
        self.pipe.to("cuda")
        cache.commit()

    @modal.method()
    def render(self, image_bytes: bytes, prompt: str, seed: int = 20261120) -> bytes:
        import io
        import torch
        from PIL import Image, ImageOps
        from diffusers.utils import export_to_video

        if not (100 <= len(image_bytes) <= 8_000_000):
            raise ValueError("Provide 100 B to 8 MB original reference PNG/JPG.")
        if not (30 <= len(prompt) <= 1600):
            raise ValueError("Prompt must be 30-1600 characters.")
        frame = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Keep the full cartoon silhouette and composition.
        frame = ImageOps.pad(frame, (WIDTH, HEIGHT), color=(245, 239, 225))
        g = torch.Generator("cuda").manual_seed(int(seed))
        output = self.pipe(
            image=frame,
            prompt=prompt,
            negative_prompt=NEGATIVE,
            width=WIDTH,
            height=HEIGHT,
            num_frames=FRAMES,
            num_inference_steps=STEPS,
            guidance_scale=4.5,
            decode_timestep=0.05,
            image_cond_noise_scale=0.025,
            generator=g,
        ).frames[0]
        path = Path("/tmp/modal_toon_pilot.mp4")
        export_to_video(output, str(path), fps=FPS)
        result = path.read_bytes()
        if len(result) < 3000:
            raise RuntimeError("Video export was empty.")
        return result

@app.local_entrypoint()
def main(image_path: str, prompt: str, output: str = "modal_toon_pilot.mp4"):
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    # Explicit invocation only. Modal billable GPU begins here.
    content = SlapstickVideo().render.remote(path.read_bytes(), prompt)
    Path(output).write_bytes(content)
    print("REAL_GPU_MP4_SAVED", output, len(content), "bytes")
