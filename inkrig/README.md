# InkRig original 2D cartoon motion engine

This is a genuine 2D cutout/vector **joint animation** with head/face changes, articulated elbows/knees, mouth shapes, blink, morphing cat tail and action cuts. It is an original 11.5-second prototype, *not an AI image model* nor an LTX/Wan diffusion result, *not copied from the supplied reference*, and not a static still zoom.

No Colab, Kaggle or AI Horde quota is used for this rendering step. Purpose: usable prompt-to-storyboard → full body/face vector rig → procedural timing → sound compositing while AI GPU generators are queued. Output is a new MP4, not the earlier Snap2D demo.

Run locally after installing \`pycairo\` and \`ffmpeg\`:
\`\`\`bash
python inkrig/inkrig_animation.py
\`\`\`
GitHub Actions installs the needed dependencies and validates the produced MP4.

Model side: AI Horde provides original styled scene images only, not in-between body motion. For GPU-generated motion, use the separate official LTX-Video 2B distilled (lighter than 13B), ToonCrafter or Wan on an actual available VRAM-compatible GPU. Do not claim their installs or renders until logs and results prove them.
