# Funny Toon Ever — Original Style + IK + Stereo Foley + Hugging Face Voices

This experimental branch preserves the original The Snore Collector Node/SVG drawing engine and the five-layer background/camera design. It does not modify the canonical reference source in midnight-jar or merge into main.

## Motion engine
- art.cjs uses the original artwork and includes rig_ik.cjs.
- rig_ik.cjs uses analytic two-bone inverse kinematics on elbows and knees; hand-to-carton grip and planted left foot are explicit world-space targets. The other foot rises during a step.
- test_ik.cjs asserts reachable joints, exact hand contact, foot planting, SVG validity, and preservation of gradient/background art across scenes.
- story.json has 5 three-second animated shots including prank reversal, squeeze, splash and reaction.

## Professional audio
- audio_pro.py generates original 48 kHz stereo Foley, water spray, cloth, compressions, footsteps, spring, laughter and original music notes with per-effect timing, no borrowed samples.
- kokoro_voice.py uses REAL Apache-licensed hexgrad/Kokoro-82M model inference for two short original dialogue lines, requiring download and execution on a runner, and records waveform provenance.
- FFmpeg mixes the voice recordings at 10.72s and 12.42s into the scene-matched 48 kHz Foley. The Foley MP4 remains independently downloadable if voice inference fails.
- Possible future GPU sound generation: OpenMOSS-Team/MOSS-SoundEffect-v2.0 (Apache-2.0 1.3B, CUDA/Triton + text encoder). NOT run in the CPU workflow and NOT claimed as current audio. Optional GPU checks and license review would be needed.
- Other audio weights and code can have separate commercial terms; do not assume the AudioGen/Stable Audio model weights are commercially unrestricted.

## Encoding and quality checks
- Workflow: .github/workflows/fte-milk-prank-ik-pro-render.yml
- Source animation is native 720x1280 at 24 fps; final portrait 1080x1920 H.264 CRF16 plus 48 kHz AAC stereo.
- qa_video.py decodes 7 actual frames, builds a contact sheet, checks H264/AAC metadata, screen dimensions, duration and real motion.
- Numeric checks alone do NOT prove perfect artistic movement, facial matching, or lip sync. Human frame inspection remains required.
- No neural video generation claimed; pure code keeps character identity stable.

## Limits and recommended hardware
- GitHub Actions CPU runner can do animation and sound; heavy AI text-to-SFX requires separate GPU availability checks.
- Oracle 1GB RAM can do FFmpeg audio mixing and modest video sizes but heavy neural models and 1080p renders may require more RAM/swap.
- No source assets or private HF secrets are committed in this branch.

## Next visual improvements
1. Review decoded motion around reaching and squeezing.
2. Adjust elbow occlusion, box-face grip, heel-toe contact and splash collision.
3. Phoneme-timed lip shapes only after real generated voice clips are analyzed.
