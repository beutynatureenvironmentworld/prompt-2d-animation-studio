# Original Fast Action CPU Cartoon — Donut Chase

A fully reproducible **12-second, 24fps, 720x720 H.264 MP4** with two original cartoon characters, exaggerated facial expressions, running, jumping, catch, collision, and final reaction.

- Reference analysis: general rapid 2D stick-figure comedy, not a copy of the uploaded work.
- **No AI model / no sound / no paid API / no GPU / no Kaggle** needed.
- Only Python Pillow (drawn characters and scenes) and FFmpeg (MP4 encoding).
- This is a hand-coded procedural animation, **not** unrestricted AI prompt-to-video, not a preinstalled Blender/ComfyUI production pipeline.
- Kept isolated from `mascot-lab` so its permanent character reference and V6 tests remain unchanged.

## GitHub Actions

Open **Actions → Fast Action CPU — Original 2D Slapstick MP4 → Run workflow**, then download the artifact **fast-action-cpu-donut-chase** when the run succeeds. The workflow also triggers once on relevant pushes to main.

## Run on a local Linux CPU

```bash
python -m pip install -r fast-action-cpu/requirements.txt
# Install ffmpeg using the OS package manager
mkdir -p fast-action-cpu/out
python fast-action-cpu/render_fast_action.py \
  --output fast-action-cpu/out/Fast_Action_Donut_Chase_CPU.mp4 \
  --contact-sheet fast-action-cpu/out/CONTACT_SHEET.jpg
```

The animation deliberately prioritizes fast readable action and clear silhouettes over sound. Oracle 1GB RAM is *not required*; render on GitHub's hosted runner.
