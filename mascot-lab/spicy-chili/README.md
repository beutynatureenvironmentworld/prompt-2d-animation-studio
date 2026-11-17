# Funny Toon Ever — Spicy Chili Actual MP4 / CPU animation experiment

This is a **real 11.4-second, 540×960, 24fps H.264/AAC animated MP4**, not a static sprite sheet or AI-generated GIF. Character identity is based on the user's **permanent six-pose Funny Toon Ever mascot** in `mascot-lab/config/permanent_mascot.webp`, including the actual source art's cheeky grin. The user-supplied new scene prompt is *a tiny chili bite → cheeks red → surprised eyes → panic → comically huge fire breath → smoke → sly recovery*.

## Actually used

* User's **original grin/face source image**, extracted from the permanent mascot sheet, plus deliberately authored emotional face sprites with a single pupil per eye.
* Analytic **two-bone IK** for both arms. Shoulder roots are covered by a continuous torso and connected with smooth tube strokes — **no elbow/shoulder donut circles**.
* V4-style side-separated **pose/FK legs**, no X-shaped crossing (tested).
* A hand-held chili with a consistent anchor; hand-to-mouth contact is measured and checked.
* Frame-by-frame Python/Pillow geometry, procedural rocket-fire particles and effects, camera vibration, original synthesized sound, FFmpeg H.264/AAC encoding.
* A constrained JSON **motion director** with explicit beats, so a future verified Qwen3 scene planner can feed this format safely. **No Qwen3/SSD-1B inference was actually called during this render.** No external API keys or large GPU model downloads are needed.

## Run in GitHub Actions / Linux

```bash
sudo apt-get install -y ffmpeg
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python source/spicy_motion_director.py --out output/motion_plan.json
python source/render_spicy.py --reference ../config/permanent_mascot.webp --plan output/motion_plan.json --out output/Funny_Toon_Ever_Spicy_Fire.mp4
python source/qa_spicy.py --video output/Funny_Toon_Ever_Spicy_Fire.mp4 --metadata output/Funny_Toon_Ever_Spicy_Fire.json
```

The standalone ZIP also includes `assets/permanent_mascot_reference.png` copied from the user's six-panel reference; point `--reference` there if running outside the main repo.

## Notes / limits

The head silhouette and mischievous grin are original reference-derived. Emotional heads, body/limbs, props, and flames are artistically scripted vector-like procedural drawings. This demonstration implements this exact authored spicy-food gag, **not unrestricted arbitrary text-to-film creation**. Numeric elbow/shoulder continuity QA cannot guarantee perfect hand-drawn visual polish. Users should watch the actual MP4 to judge animation quality.
