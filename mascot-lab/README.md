# Funny Toon Ever — Hourly Mascot Super Test Lab

**Original character:** the user's existing black-and-white permanent six-pose reference, reused from `prompt-sixpose/assets/six_pose_sheet_for_git.png` in the same repo. Never redraw or regenerate a replacement identity. Six original source poses, one complete facial layer per frame, no extra artificial pupils.

**Architecture:** source sheet → CPU OpenCV whole-character silhouette extraction → pose-to-pose 24 fps animation and physical staging → FFmpeg H.264/AAC MP4 → read actual encoded frames with OpenCV → check spatial travel, estimated door-hand reach, excessive image clipping, codec/length, motion. Compare two parameter variants, promote *only* the variant passing numeric gates; keep a real 3×3 filmstrip so future ChatGPT reviews can inspect frames directly.

The tests **do not claim full rigging or real video understanding**: door-contact gap is approximate and not measured by neural hand keypoints; the original facial poses all grin, and the user's reported extra pupils may still appear. Never claim those are fixed before image-level verification. These are priority tasks for subsequent hourly cycles. Animated cutouts are not neural video diffusion.

## Hourly schedule & safety

The workflow `.github/workflows/mascot-lab-hourly.yml` runs once per hour at UTC minute 37, a slightly offset schedule to avoid common top-of-hour GitHub delays. GitHub cron is not guaranteed to run to the minute. It rotates `door`, `prank`, `race`, `surprise` gags, runs tests and produces two distinct candidates. Only approved numeric QA results may replace `LATEST_VERIFIED.mp4`. Each run uploads its MP4, contact sheet and JSON report as an Actions artifact for 7 days. The permanent direct download on **experiment branch only** is refreshed at most every six hours (and first success); stable main and other production services are not touched.

A **separate ChatGPT hourly automation** reviews latest results and, when possible, uses connected tools to inspect real MP4 frames and improve the experimental code. The scheduled GitHub workflow itself uses deterministic numerical QA and **does not have an LLM reviewing the video**. Model-assisted code revision is not a guaranteed every-hour capability and never auto-merges to stable main.

## Run offline

```bash
sudo apt-get install -y ffmpeg
pip install -r mascot-lab/requirements.txt
python -m unittest discover -s mascot-lab/tests -v
python mascot-lab/src/loop.py \
    --sheet prompt-sixpose/assets/six_pose_sheet_for_git.png \
    --config mascot-lab/config/tuning.json --out mascot-lab/out --gag door
```

For manual GitHub Actions use **Actions > Funny Toon Mascot — Hourly Visual QA and Safe Animation Tests > Run workflow**, then select gag. For output, see artifacts of successful run or the experiment branch's `mascot-lab/out/LATEST_VERIFIED.mp4` file.

## Current limitations and next priorities

1. Original silhouette source has consistently grinning mouths; need preserve identity while authoring neutral/shock mouth variants and verifying **one pupil per eye** on actual pixels.
2. Door is an authored graphic, not a physical scene graph object with true hand/arm inverse kinematics; contact is approximate.
3. User visual standards require human review: image pixel variance is *not* artistic quality.
4. Actor feet still have cutout-slide artifacts during fast changes and would benefit from explicit rigged toe/heel anchors and body pivot motion.
5. No auto-parsing of arbitrary new objects, environments, scenes or gestures in this project; the repository's existing optional Qwen3 planner can be adapted later to this bounded motion-JSON action vocabulary.
6. User's original high-resolution pose sheet was used for local initial QA. GitHub uses the compact reference already committed to `prompt-sixpose/assets`; result may differ slightly.