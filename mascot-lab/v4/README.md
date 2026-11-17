# Funny Toon Ever V4 — Speed-Chase Hybrid Motion

A reproducible **CPU-based, permanent-reference mascot** video experiment that addresses the V3 crossed-X legs and robot-style visible joint rings while **preserving V3 hand IK, facial personality and door contact**.

**Reference study:** user-provided `Funny_Toon_Ever_V3_Direct.mp4` (11.52s, 360×640) vs. `04_speed_chase(7).mp4` (6s, 960×540) of the original cat Super Test. The earlier cartoon uses clearly separated fast chase poses. V3 drew independent 2-bone IK legs with visible joint circles, producing an X silhouette even in idle. V4 uses a separate key-pose-inspired leg control, without modifying original V3.

## Hybrid motion policy

| Action | Motion solution | What changed |
|---|---|---|
| dash / fast chase | **Speed-chase pose-driven FK legs**, four run phases (contact/down/passing/up) + separately planted world-space feet | Knee/foot positions stay on opposite sides of body. Running remains clear and quick, without V3 X legs. |
| sneak, brake, knock, recover, reveal | Separate stylized FK leg lanes | Wide readable stance, no crossed shins. |
| shock, jump, slip, fall | Animated stylized leg FK while torso rotates | Avoid crossing before body transforms. |
| all actions / arms | **Original V3 analytic 2-bone IK** | Keep natural hand-to-door target and expressive arm swings. |
| all limbs visual | **Continuous black-outline/white-fill stroke** | No joint donut/circle at elbow or knee. Shoulder joint remains hidden by torso, wrist by hand. |
| face | **Original extracted head** and seven facial states | Keep user's sly grin when emotionally appropriate; one pupil per eye. |

This is **not** a realistic full-body physics solver, nor an unrestricted generative video model. The leg lane QA operates in local coordinates before global stumbles/rotations. Foot-lock tests cover planted running samples; artistic review is separate.

### Reproducible local run

```bash
sudo apt-get install -y ffmpeg
python -m pip install -r requirements.txt
# If canonical sprite not already present:
python src/extract_canonical.py --sheet ../config/permanent_mascot.webp --output assets/canonical_neutral_pose.png
python -m unittest discover -s tests -v
python src/v3_director.py --prompt 'Mascot sprints to door, knocks and slips' --output output/MOTION_PLAN.json
python src/render.py --plan output/MOTION_PLAN.json --sheet assets/canonical_neutral_pose.png --output output/Funny_Toon_Ever_V4_Speed_Chase_Hybrid.mp4
python src/quality_v4.py --video output/Funny_Toon_Ever_V4_Speed_Chase_Hybrid.mp4 --report output/Funny_Toon_Ever_V4_Speed_Chase_Hybrid.json
```

`v3_director.py` intentionally uses a bounded offline locked-door comedy grammar; `--plan` accepts separately generated schema-validated motion JSON. **No Qwen3 or SSD-1B inference was run in this V4 demo**, but integration inputs remain available (permanent source, plan JSON, optional AI-generated `--background`). It should not be advertised as unrestricted custom-prompt animation.

## Verified initial result

- 11.5 seconds, 276 frames, **540×960, 24fps H.264/AAC**, original sound cues.
- **12/12 local Python tests pass**, original V3 tests retained and expanded.
- **0 crossed-knee/foot local-lane violations across 276 frames**, four chase gait states all used.
- **0 px analytic world stance foot drift** in qualifying planted consecutive frames.
- **Max V3 authored hand-to-door error ~6.2px**, unchanged.
- No visible elbow/knee outline ring is drawn by the continuous-limb stroke function.
- Seven face states and one pupil per eye remain.

A baseline V3 vs V4 side-by-side video is rendered locally for manual comparisons. GitHub Actions CI repeats actual real MP4 generation and FFprobe/decoded-frame QA.

## Next-stage limits

Motion still uses procedural torso and limbs matching the source head. Some shoulder anatomy/leg proportions may benefit from artist tuning; fast-run foot stance is a stylized compromise, not a mocap solve. Arbitrary new scenes need reference-backed prop anchors, LLM plan checking and per-action tuning. Do not overwrite the original V3 successful version.
