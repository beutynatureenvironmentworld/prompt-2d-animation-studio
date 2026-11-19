# Sprite Pose Lab — original 2D slapstick animation factory

Standalone **CPU-only** project in prompt-2d-animation-studio, isolated from mascot-lab and other projects.

## What is included

- **Two original reusable characters**, Pip and Luma, each with 12 transparent 560×800 PNG poses: idle, talk, grin, blink, point, shock, run, kick, jump, crouch, fall, celebrate.
- **Four original transparent props**: ball, cup, splash, impact burst, and an original 720×1280 living-room background.
- **Editable 12-FPS storyboard JSON**, pose holds, x/y motion, squash/stretch, rotation, dynamic z-index sorting, shake, zoom, and generated illustrative sound effects.
- **24-FPS H.264/AAC vertical MP4 export** using FFmpeg without diffusion models or GPU.
- **GitHub Actions manual run** with an MP4 artifact; no automatic posting, paid APIs, or secrets.

This implements the modular-sprite animation **technique**, not any creator's protected character designs, voices, soundtrack, or video frames. Sample art is original and basic. It is a functional proof of concept, **not** a reproduction of professional animation quality.

## Run locally / Kaggle / GitHub Actions

Requires Python 3.10+ and FFmpeg in PATH. For Ubuntu, install ffmpeg and libcairo2.

1. Install Python dependencies: python -m pip install -r requirements.txt
2. Create art: python sprite_factory.py
3. Create a sample storyboard: python make_story.py
4. Render: python render.py --width 720 --height 1280 --output demo.mp4
5. For vertical Full HD: python render.py --width 1080 --height 1920 --output demo-full-hd.mp4

Generated PNG pose paths: assets/characters/pip/*.png and assets/characters/luma/*.png, plus assets/props/*.png. Assets are reproducible and excluded from Git. Replace any character or prop PNG with compatible, original transparent art and update storyboard paths.

## Storyboard editing

make_story.py creates config/demo_story.json. Each shot has frames, a layers array and optional sfx, zoom, zoom_end, shake, and impact. Each layer has sprite, start, end, scale, optionally scale_end, squash [sx,sy], rotation, rotation_end, opacity, and z. z sorts layers. All stage coordinates use an internal 720×1280 virtual canvas; output scaling does not change coordinates. The bottom-center sprite anchor can keep feet on the ground when the art has consistent padding.

Animation uses **12 distinct frames per second**, duplicated into a 24-FPS MP4. More fluid character acting requires more poses, improved rigging, and temporal spacing. A general-purpose natural-language-to-JSON LLM is **not included**; custom timelines can be generated separately. The 10–15 second render claim for 1080p is **not guaranteed**; speed depends on encoding settings and hardware.

## GitHub Actions

Under the repository Actions tab, select **Sprite Pose Lab - CPU render**, click Run workflow and choose width 720 or 1080. Download the sprite-pose-lab-demo artifact after the job completes. The workflow is manual, so it does not compete with existing scheduled rendering jobs.

## New: Milk Prank V2 (sound-synchronized original slapstick short)

`milk_prank_v2.py` renders an **11.5-second** original cartoon short at **12 pose frames/sec** (exported to **24 FPS**, H.264 video and AAC audio). It keeps the original Pip/Luma character proportions while updating wardrobe to a yellow cap and blue shirt for the boy and a coral-pink dress and brown bun for the girl. This is a dedicated procedural character animation, separate from the sprite_factory demo. No inference model or GPU is required.

Features: expressive angry eyebrows; sneaky toothy grin; a moving/rotating milk carton with a prominent straw; timed hand strike, squeeze and milk blast; face splashes and persistent dripping; eye-pop elastic springs; camera punch zoom/shake; carton drop; bouncing laugh reaction; and synthesized whoosh, pop, boing, splash and giggle effects.

```bash
# Inside sprite-pose-lab/
python -m pip install pillow numpy
python milk_prank_v2.py --resolution 1080p --output milk-prank-v2.mp4
python milk_prank_v2.py --preview --output milk-prank-v2.mp4
```

For a no-install workflow, open **Actions → Milk Prank V2 - Render with Sounds → Run workflow**, select 720p or 1080p, and retrieve the MP4 artifact. The workflow runs **only when manually dispatched**, so it does not interfere with existing scheduled projects.

All characters, code and audio are original procedural assets. This demonstrates a general 2D comedy technique; it does not reproduce other creators' protected characters or frames. This second generation is a working prototype; high-end hand-drawn acting and custom performance audio remain future improvements.
