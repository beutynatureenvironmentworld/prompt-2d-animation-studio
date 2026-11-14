# Snap2D — rapid original cartoon, CPU-only

## සිංහල

ඇමුණුම් reference video එකේ **animation techniques** (pose-to-pose, reaction zoom, camera shake, squash/stretch, hand-inked bold faces and quick camera cuts) අධ්‍යයනය කළා. මෙම demo එකේ කතාව/චරිත/දර්ශන ස්වාධීනව නිර්මාණය කර ඇත: **The Last Cookie**. Reference video එකේ frames/audio/characters පිටපත් කරලා නැහැ.

**සැබෑ ප්‍රතිඵලය:** 13.6 seconds, 9:16, 540×960, 30 fps, sound නැති H.264 MP4. කිසිම GPU, AI subscription හෝ API key එකක් අවශ්‍ය නැහැ.

**Install** (Ubuntu 22.04+, Debian; system Python, Cairo, FFmpeg):

    sudo apt-get update
    sudo apt-get install -y python3-cairo ffmpeg
    /usr/bin/python3 snap2d/rapid_cartoon.py --output snap2d/output/last-cookie.mp4

For other Linux/Python builds, use `python -m pip install -r snap2d/requirements.txt` (may require `pkg-config libcairo2-dev python3-dev`). x86_64 and ARM64 CPU architectures supported in principle if packages are available; benchmark your host for render speeds. Windows/macOS may install PyCairo through appropriate package managers and FFmpeg separately.

**Editable JSON:**

    /usr/bin/python3 snap2d/rapid_cartoon.py --save-storyboard snap2d/output/storyboard.json --output snap2d/output/new-video.mp4
    /usr/bin/python3 snap2d/rapid_cartoon.py --storyboard snap2d/output/storyboard.json --output snap2d/output/another.mp4

**Prompt-to-shot editing:** `--prompt "A silly chase sequence: sneak, glare, chase, trip, shock"` creates a specific validated beat list. Available beats: `setup, sneak, grab, glare, chase, trip, shock, catch, stare, button`. This is a **bounded offline prompt parser**, NOT a general open-ended AI director. To construct genuinely arbitrary movement, author new pose handlers and reusable rigs. Time offsets/durations can be modified in the JSON; no generated code is executed. Files are not overwritten.

## English architecture

- Entire render engine: **Python 3 + PyCairo + FFmpeg** (free/open-source components, GPU not needed).
- Characters are reusable authored vector rigs with separate head/eyes/eyebrows/mouth/limbs; matching character look across shots.
- Camera is handled through geometric transforms. Rapid cuts, expression swaps, arm/leg keyframes, overshoot, squash/stretch, chase speed lines, and procedural shakes are all drawn for real.
- **Rhubarb Lip Sync** is not used for this *silent* demo. It only analyzes **existing audio**; it does not create voice or cinematic motion. If added later, check supported language, platform builds, and licensing. In particular, don't assume an official Linux ARM64 executable exists.
- Blender, Synfig, OpenToonz, Remotion, Revideo, Motion Canvas are **not required/installed by this module**. Existing repository modules may use them independently. A CPU video renderer is the quickest reliable baseline here.
- Prompt input does not execute shell commands, code or download media. Runtime storyboard is data-only and validated; optional `--storyboard` reads local JSON. No original user media is committed.
- If you run on Oracle, use a dedicated project directory; do not modify running unrelated services. With 1 GB RAM, avoid large LLM and video diffusion weights. GitHub Actions is ephemeral and runner resources and policies apply; **public Actions is not a promise of unlimited compute**.

### Test locally / via Actions

    /usr/bin/python3 -m unittest discover -s snap2d/tests -v
    /usr/bin/python3 snap2d/rapid_cartoon.py --width 360 --fps 24 --output snap2d/output/ci-demo.mp4
    ffprobe -v error -show_entries stream=codec_name,codec_type,width,height -of json snap2d/output/ci-demo.mp4

A workflow under `.github/workflows/snap2d.yml` automatically checks the code, runs a smoke test, renders an actual MP4 and uploads an artifact.

### Rights

New original Snap2D code/drawings are MIT-licensed (see snap2d/LICENSE). PyCairo/Python Cairo and FFmpeg carry their own licenses depending on distribution and linked codecs. Do not import copyrighted video frames, audio, characters, unlicensed sound or voices without permission. The supplied reference was inspected in this conversation for timing/animation techniques, not embedded or redistributed.

### Limitations / next work

Fast, strong but still hand-authored clip-based animation—not 60fps 3D, natural motion capture, generalized prompt-to-video AI, lip-sync without voice input or arbitrary photo/video-to-rig. For improved quality: expand a reusable SVG face/pose library, hand-tuned transitions, multi-actor choreography, and optional voice-to-viseme Rhubarb automation.
