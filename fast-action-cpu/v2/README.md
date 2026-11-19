# Fast Action 2D V2 — expressive CPU demo

This is the next step after the verified V1 donut-chase. V1 stays intact.

Improvements in V2:
- **Continuous quadratic Bézier limbs** for arms and legs. Control points stay hidden; no joint circles.
- Facial eyebrows + cheek accents + secondary hair motion.
- Fast-paced streaks, airborne motion, dust and spin accents.
- Timed burst rays, catch reaction and bounded hit camera zoom.
- Pre-existing 12-second story, scene cuts and original artwork preserved.
- Silent 720×720, 24fps, H.264; no GPU, no large AI model, no third-party footage.

To render:
```bash
python -m pip install Pillow
python fast-action-cpu/v2/render_fast_action_v2.py \
  --output Fast_Action_Donut_Chase_V2_CPU.mp4 \
  --contact-sheet Contact_V2.jpg
```
Requires `ffmpeg` and `ffprobe` on PATH. V2 is **art-directed procedural animation**,
not unrestricted generative AI or proof that Blender/ComfyUI was used.
For the Gradio app files to deploy on HF, see `huggingface-space/`.
