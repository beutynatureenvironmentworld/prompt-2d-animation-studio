# Funny Toon Ever V5 — Natural front-facing arm motion

This is an **actual CPU MP4 animation system**, not a still or an automatic text-to-video model. It preserves the user’s **permanent black-and-white mascot** reference and V4 non-crossing speed-chase FK legs, the sly grin/facial states, contact-only hand IK, and offline original SFX.

## User reference — arms only

The user supplied `Anime-Starter-Demo(2).mp4` (640×360, 15 fps, 6 seconds). Visible frames show a front-facing stylized figure with arms **straight and DOWN by the sides** during resting/walking, then a distinct **raised-hand gesture** after about 2 seconds. This reference **does not demonstrate a fast run cycle**. Our run swing is a reasoned original cartoon projection, not an extracted motion capture from the sample. Do not copy the reference's character design/background.

## V5 selective arm motion logic

- **sneak / neutral / recover:** arm hangs at the side with straight, collinear invisible elbow, rather than both hands stretched out horizontally.
- **dash:** alternating **sagittal front/back arm pump**. One hand comes inward toward the chest with a naturally bent elbow, while the other reaches low behind the hip. 2D projection uses vertical hand height, subtle foreshortening, and dynamic near/far torso compositing. Horizontal hand displacement from shoulder remains <=23px. No outward side-swinging windmills.
- **brake:** sinusoidal swing amplitude eases back to straight, resting arms.
- **knock / shock / jump / fall / reveal / celebrate:** retain original V4 **selective IK** for intentional hand contact, fear, and expressive gestures.
- **legs:** exactly the proven V4 four-stage speed-chase FK with planted stance; no X-crossing. Original face and smile personality remain.
- **arm shape:** continuous white-filled rubber-hose tube with black outline and invisible joint; no robotic elbow circle.

## Reproduce (Ubuntu / GitHub Actions)

```bash
sudo apt-get install -y ffmpeg
python -m pip install -r requirements.txt
python src/extract_canonical.py --sheet ../config/permanent_mascot.webp --output assets/canonical_neutral_pose.png
python -m unittest discover -s tests -v
python src/v3_director.py --prompt 'A cheeky mascot runs to a bathroom door and knocks' --output output/MOTION_PLAN.json
python src/render.py --plan output/MOTION_PLAN.json --sheet assets/canonical_neutral_pose.png --output output/Funny_Toon_Ever_V5_Front_Arm_Swing.mp4
python src/quality_v5.py --video output/Funny_Toon_Ever_V5_Front_Arm_Swing.mp4 --report output/Funny_Toon_Ever_V5_Front_Arm_Swing.json
```

Current validated `fte-motion-v3` JSON grammar is a restricted locked-door short, not arbitrary general purpose AI animation. V5 does **not** call Qwen3 or SSD-1B. Existing `--plan` and `--background` entrypoints can accept validated outputs from the independent model workflows; do not confuse this with an executed AI inference run.

## Actual test result

- **17/17 Python tests** passed including V3/V4 compatibility.
- **11.5 sec, 276 frames, 540×960 at 24 fps**, real H.264/AAC MP4.
- Both running hands alternate with **~77.85px vertical screen motion** and **<=23px lateral hand displacement** from corresponding shoulders.
- Planted-foot drift 0px in qualifying stance samples, **0 X-leg crossings** in 276 local-coordinate samples.
- Authored V4 hand-to-door target maximum **6.2px** error unchanged.
- Actual MP4 is decoded and compared for meaningful frame changes; visual frame contact sheet is reviewed separately.

**Limitations:** 2D screen-depth arm projection is a stylized technique, not 3D skeletal physics; actor body is procedurally drawn around the extracted canonical head. The new reference's arm idle/gesture movement informs our design, but not the running technique as the reference does not show it.
