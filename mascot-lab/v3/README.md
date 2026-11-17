# Funny Toon Ever V3 — Permanent Mascot Motion Director + Real Two-Bone IK

The canonical character is the **user's black-and-white six-pose Funny Toon Ever mascot**. This V3 experimental branch preserves the authentic original toothy grin in most beats, while changing to focus / effort / shock / worried only when acting needs it.

## Verified demonstration (local)

- **11.50-second portrait MP4**, 540×960, 24 FPS, **276 real generated frames**, H.264 and AAC with original programmatically composed sound effects (no copyrighted music).
- **CPU render:** about **6.3 seconds** on the demonstration container *with dependencies already installed*; performance depends on the host. Original reference face from source silhouette + a matching procedural white body.
- **Hand IK:** exact two-bone arm solver; actual right hand reaches authored `(406,606)` door-handle interaction, with three articulated knock/recoil gestures.
- **Foot locking:** world-space planted-foot points across run-stance phase, swing phase uses smooth arch with true 2-bone knee IK.
- **Character identity:** both eyes are rebuilt so only **one pupil per eye** remains; source's large cheeky toothy grin is restored for sly/celebrate, while action beats show neutral, focused, worried, shocked faces. No extra character generation.
- **Comedy staging:** anticipation → dash → hard brake → 3 knocks → shock → panic jump → slip/fall → recovery → "PULL!" reveal → sly "OOPS!" ending.
- **QA:** decoded frames, audio/video codecs, authored contact distance and foot-drift metrics; note that numerical checks aren't human-level artistic evaluation.

## What is AI-powered, and what is not

The default V3 demo uses a **deterministic, structured, constrained action grammar**, *not an executed Qwen3 or SSD-1B inference call*. The JSON schema `fte-motion-v3` is ready to accept a separately verified reasoning-generated motion plan via `--plan`. Optional `--background` accepts any scene-background PNG/JPG provided by the existing **Qwen3 / Segmind SSD-1B ShortGPT pipeline**. A source-derived mascot foreground is composited on top; the model does **not** regenerate the mascot on each frame. These integrations are interface-compatible but not a proof of arbitrarily complex prompt animation.

## Run locally

```bash
python -m pip install -r requirements.txt
sudo apt-get install -y ffmpeg
python src/extract_canonical.py --sheet ../config/permanent_mascot.webp --output assets/canonical_neutral_pose.png
python src/v3_director.py --prompt 'The sneaky mascot rushes to the toilet door and slips' --output output/MOTION_PLAN.json
python src/render.py --plan output/MOTION_PLAN.json --sheet assets/canonical_neutral_pose.png --output output/Funny_Toon_Ever_V3_Fast_IK_Super_Test.mp4
python src/quality.py --video output/Funny_Toon_Ever_V3_Fast_IK_Super_Test.mp4 --report output/Funny_Toon_Ever_V3_Fast_IK_Super_Test.json
```

The source image is already tracked by the original repository at `mascot-lab/config/permanent_mascot.webp`; this project does not distribute font files or unnecessary duplicated large model weights.

## Optional external image and director plans

- `python src/render.py --background /path/to/generated_hallway.png ...` uses an optional local generated image. **Existing code draws a calibrated authored door on top**, so the background should be a location mood/texture, not a conflicting second door.
- `python src/render.py --plan /path/to/validated_ffe_motion_json ...` accepts a validated action plan, not executable code. The currently proven choreography is **one locked-door gag with the authored temporal layout**. Entirely different actions/environments require adding stage and motion scripts.
- No hosted service token is needed for this CPU renderer, and existing Qwen3/SSD-1B can remain on separate GitHub jobs.

## Honest limitations

This V3 improves true joint IK and landing foot locks over the earlier whole-pose V2. **The reference head is extracted from original artwork; body and independently animated limbs are a matching redraw**, not image-conditioned 3D rigging or real-time neural animation. Hand contact is calibrated against authored door coordinates. Further work should add contact-aware elbow constraints, ankle orientation, eye tracking, safer fall mechanics, dynamic AI storyboard-to-rig mapping for varied scenes, and more natural speech/lip-sync. Avoid claiming that arbitrary prompts work before new scenario coverage is tested.

## Production plan

1. Use approved permanent mascot head and fixed style identity.
2. Generate constrained motion JSON from a safe offline template or a Qwen3 backend with JSON validation.
3. Reuse optional SSD-1B backgrounds for new locations, drawing clearly grounded door/object anchors.
4. Apply IK to limbs and planted feet; render vertical H264/AAC and original SFX.
5. Decode the resulting MP4, run numeric QA and human visual review, archive the **real** MP4/artifact and its scene JSON. Keep heavy model downloads opt-in, not in every hourly QA run.

The existing hourly experimental mascot QA workflow remains untouched; V3 is tested independently until reviewed.