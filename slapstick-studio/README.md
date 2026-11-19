# Slapstick Sprite Studio — independent CPU-based 2D workflow

A reproducible, original **modular PNG sprite** 2D cartoon workflow, isolated from earlier projects. Does not change any Funny Toon mascot file, hourly automation or other workflows.

## What works
- Generates **13 complete original transparent character poses plus 3 props** from vector-like line geometry as PNG files, once before compositing.
- Continuous curved and rounded arm/leg strokes hide elbows and knees (no visible V-shaped bone joints).
- Plays a customizable JSON storyboard: hand wave, pickup camera from bag, squash/stretch jump, fast kick with smear pose and camera shake.
- Keeps the same foot baseline as poses change; switches camera behind/in front of bag and character using layer order.
- Samples poses at **12 fps** and writes a **24 fps, 1080 x 1920 H264 MP4** using FFmpeg; holds repeated drawings on twos.
- A decoded-video QA step checks actual encoded video and generates contact sheet.
- No paid model, API, Kaggle, GPU, licensed proprietary tools, third-party Rico character artwork or audio.

This demo is **deterministic sprite animation**, not unrestricted AI text-to-video or full Blender rigging. The actions in the sample JSON are intentionally bounded to 4 known verbs. More complex scenes need additional authored poses and scene choreography.

## Run locally from repository root

    sudo apt-get update && sudo apt-get install -y ffmpeg
    python -m pip install -r slapstick-studio/requirements.txt
    python slapstick-studio/studio.py assets
    python slapstick-studio/studio.py render
    python slapstick-studio/studio.py verify

Output: slapstick-studio/out/slapstick_demo.mp4, contact.jpg, quality.json and a render metadata JSON.

To change resolution: run render with --width 1920 --height 1080 for landscape (scene choreography is optimized for portrait), or use --width 540 --height 960 for a fast preview. Replace transparent PNGs in slapstick-studio/assets/poses using the same filenames and 360x480 canvas with feet anchored at (180,450). Change action order and durations in story.json.

## GitHub Actions

Use Actions > Slapstick Studio — Original Sprite Animation Demo > Run workflow. Pushes changing only this project also render automatically. The MP4, decoded contact sheet, and all transparent PNG pose assets are stored in the workflow's downloadable artifact. The manual Optional Animation Tools Audit installs only apt-available Blender, Krita, Inkscape, Synfig, OpenToonz, Pencil2D and FFmpeg packages on a disposable Ubuntu runner, so desktop tools **do not remain installed** when a GitHub Actions job finishes.

## Tutorials informing the general technique

- Hand Movement: https://www.youtube.com/watch?v=GlGI7IgttVA
- Picking Object: https://www.youtube.com/watch?v=JAo7EGEU15M
- Jumping: https://www.youtube.com/watch?v=xymBBykaEk0

No material or character sprite from those tutorials is copied. For manual character design, use Blender Grease Pencil / OpenToonz / Krita / Inkscape. The headless render requires Pillow and FFmpeg only.
