---
title: Fast Action V2 Cartoon Lab
emoji: 🎞️
colorFrom: yellow
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

# Fast Action V2 — original CPU cartoon Space

An actual callable **silent**, 720×720, 24 FPS, 12 s, 2D original cartoon demo.
Click Render to create a new H.264 MP4 and timeline contact sheet on the Space's CPU.
It uses only Pillow, FFmpeg and the local `renderer.py` implementation; no large models or GPUs are downloaded.

Important: this directory is **ready to upload but not proof of a deployed Space**.
The file can be deployed using `.github/workflows/deploy-fast-action-hf-space.yml`,
with a user-created HF Space ID and an authorized `HF_TOKEN` GitHub secret.
Do not hard-code tokens, choose paid GPUs, or request GPU billing automatically.
Hugging Face's current rules can restrict new Gradio/Docker Space creation
to eligible paid plans, with limited ZeroGPU exceptions for free accounts.
The free CPU Basic hardware is 2 vCPU and 16GB RAM **where available**.

The visible result is procedural keyframe-based 2D animation, **not** text-to-video inference.
For ComfyUI/AnimateDiff or larger GPU models use dedicated GPU hardware separately
after checking the available VRAM, license, model weights and usage fees.
