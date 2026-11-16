# ShortGPT Super Test — Animation Quality + Asset Memory Guide

The model is not the only problem. Review of the original 4.52-second user MP4 showed an AI-generated hallway and a separate vector boy, but the running cycle barely moved towards the door, character/background styles did not match, and comedy reactions were too brief. Qwen3 generated structured story scenes and SSD-1B generated an image; neither generated articulated video frames.

## What this update really fixes

- Character continuity: user-controlled settings.json colors for hair, clothing, skin, shoes, pants. Real configurable vector actor, not automatic rigging from reference photos.
- Spatial intent: layout.start_x and layout.door_x in settings.json move the character across the frame to a contact point instead of treadmill running.
- Project creative memory: style.md, story_bible.md, memory.md and skills/*.md are loaded for each job as bounded creative notes. Editing and committing files affects future Qwen3 planning; the LLM is NOT retrained and memory is NOT updated automatically by watching videos.
- User-uploaded backgrounds: background_toilet.png, background_school.jpg and other supported locations are used with --images assets; absent locations fall back to procedural backgrounds. With --images cpu, SSD-1B continues generating original AI backgrounds and reads the style notes, but your uploaded backgrounds are not loaded.
- Readable timing: --pacing readable expands too-short story beats and budgets for speech, within a 12-second max. This reduces, but cannot entirely eliminate, clipped audio.
- QA: the MP4 metadata includes quality_warnings for overly brief gags, wordy dialogue or continuity concerns.
- User story JSON: story_plan.json bypasses model planning when explicitly chosen; validated against renderer action/location vocabulary.

## Upload files via GitHub on Android

1. Open the Assets directory: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/tree/main/shortgpt-supertest/assets/default
2. Choose Add file > Upload files and commit a PNG/JPG/WebP file named background_toilet.png, etc. Or edit style.md, memory.md, story_bible.md, skills/comedy_timing.md or settings.json.
3. Commit your changes. For a second character, create assets/my_style/ with the same filenames and use asset_profile=my_style.
4. Open the Full Local AI workflow: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/workflows/shortgpt-full-local-ai-mp4.yml
5. Choose Run workflow, main branch, asset_profile=default, background_mode=assets (for uploaded images) or cpu (for genuine SSD-1B generation), and pacing=readable. Download MP4/JSON via Actions > Artifacts.

No new API key is needed for local GitHub CPU inference. Public images in a public GitHub repository are public. Keep private photos and secrets out of public assets. Character reference images may be stored but are NOT currently traced into a full-body rig.

## Example stronger custom prompt

An original teal-hoodie boy looks worried, runs across the bathroom hallway towards the door on the right, knocks twice, discovers it is locked, freezes in shock, then slowly recovers. One coherent background, one character, expressive eye direction, clear physical timing, no constant smiling, setup/action/surprise/payoff.

This renderer currently supports notice, run, knock, jump, shock, slip, recover, dance and six predeclared locations. Completely arbitrary new gestures and true image-conditioned character rigging require further renderer work. A larger reasoning/image model does not by itself animate limbs naturally.

## Remaining quality improvements (NOT claimed complete)

Real reference-based character rigging; scene object/keypoint tracking; collision-aware hands and doors; true pose interpolation; better TTS, sound effects and audio timing; ControlNet/IP-Adapter/LoRA for image consistency (usually GPU heavy); visual QA across rendered frames rather than text-only warning rules.
