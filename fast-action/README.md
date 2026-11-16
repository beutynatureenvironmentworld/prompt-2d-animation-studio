# Fast Clear-Limb 2D Comedy — isolated experiment

A new **original 12-second, 24 FPS, 360×640** hand-drawn-style cartoon. A cookie-stealing cat flees a boy; the boy runs with changing knee and elbow positions, knocks at the door, talks, panics, slips, rebounds and lands in a comic freeze-frame. A simple muted olive/blue line-art palette is deliberate. This is **not a recreation of any RicoAnimations footage**.

## Actual connected engines

- **Iki** (MIT): uses 24 browser/WebGL2 facial parameter poses generated with the upstream Iki auto-rigger in earlier verified action run 43787114551. These face poses originated from the **upstream MIT sample illustration**, not an arbitrary original image generated from a prompt. The full body is rendered by the original separate vector geometry in fast_action.py; Iki did **not** auto-rig the limbs in this experiment.
- **Line-Art Animation** by JDhruv14 (MIT): the workflow clones the upstream repository and executes its real gait.ts IK solver on **288 frames** using the small original adapter generate_gait.mjs. The Python renderer uses this true hip/knee/ankle data for running, plus original independently posed elbows, hands, body and action effects.
- **Rhubarb Lip Sync**: uses the previously verified generated original speech recording and A-H mouth-cue JSON from run 43764399085; the dynamic 2D mouth shapes and audio are aligned with a 3.96s delay.

This project uses **GitHub Actions CPU**, Pillow and FFmpeg. It is not AI-generated video diffusion, nor automatically generated character layers from text prompts. It does **not** claim photorealism or match professional studio acting quality.

## Proof / download

Successful end-to-end production run: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43793408681

Download the artifact called **NEW-fast-clear-IK-Iki-Rhubarb-original-action-demo** from the successful run. Includes MP4, the actual upstream IK JSON, three scene keyframes, and provenance JSON.

## Rerun limits

The current workflow downloads previously verified Iki and Rhubarb assets from GitHub Actions run artifacts which have a **7-day retention**. It will need those assets archived to user-owned private Hugging Face storage or regenerated when those temporary artifacts expire. The private HF storage already exists, but **this experiment has not yet archived its dependencies there**. Do not mistake temporary Actions artifact storage for permanent production storage.

Only the separate experiment branch is modified; the existing InkRig main workflow is unchanged. The code is openly reviewable and contains no secrets.
