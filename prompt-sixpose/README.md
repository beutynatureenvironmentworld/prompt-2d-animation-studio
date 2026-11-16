# Funny Toon Ever — CPU Prompt-to-Six-Pose 2D Animation Studio

This is a **separate project**, not the earlier full-body rigging workflow. It uses the user's provided / previously generated original **black-and-white six-pose mascot art**, prepared with OpenCV and PIL into six transparent PNGs; one **complete** pose is composited per frame. This prevents duplicate-face overlays from independently rigged head images.

## Working results

- Four separately rendered 960×540 H.264/AAC demos plus a 22-second combined MP4.
- One **actual** full-length 30-second 1920×1080 H.264/AAC CPU benchmark (720 frames).
- `src/prompt_to_json.py`: input English **or Sinhala** custom story prompt and compile ordered key-beats to validated JSON. No OpenAI key needed for the verified offline keyword parser.
- **Optional** `--llm` mode uses an OpenAI Responses structured output API and requires *separately obtained* `OPENAI_API_KEY` and potentially charged API usage. The LLM API branch is implemented, **not tested or used** to produce the attached demos; it must be configured and verified before production. Never commit a token.
- `src/prepare_poses.py`: image segmentation and transparent mascot-pose generation using OpenCV/Pillow.
- `src/render.py`: streaming FFmpeg encode, stable foreground sprite, key-pose swaps, camera zoom by actor scale, bounce, squash/stretch, running speed lines, knock, screen shake, original synthesized SFX; MoviePy v2 used to validate MP4.
- `tests`: asset, custom-prompt and image-variation tests.

## Run on CPU Ubuntu, GitHub Actions, or Oracle VPS

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg python3-pip
python3 -m pip install -r requirements.txt
bash run_demo.sh
```

Or supply an arbitrary supported prompt:

```bash
python src/prompt_to_json.py --prompt 'The mascot runs, knocks on a door, looks surprised, jumps and recovers' --output output/story.json
python src/render.py --timeline output/story.json --output output/another-story.mp4
```

For 1080p:

```bash
python src/render.py --timeline output/story.json --width 1920 --height 1080 --output output/1080p_story.mp4
```

LLM mode (optional remote paid API, not needed for CPU rendering):

```bash
# Set OPENAI_API_KEY securely in the shell or GitHub Secrets; do not paste in code
python src/prompt_to_json.py --llm --prompt 'He runs, gets surprised, slips and recovers' --output output/llm_plan.json
```

Supported action vocabulary: `idle`, `crouch`, `run`, `knock`, `jump`, `shock`, `slip`, `recover`; synonyms supported, including Sinhala action words. Unknown prompts produce a clear error rather than hallucinated unsupported motion. A true free-form LLM planner uses the optional API, not the offline rules.

## Measured performance — not marketing claims

Actual execution in this session:

| Test | Output | Time | Max Python RSS | FFmpeg subprocess max RSS |
|---|---|---:|---:|---:|
| 5.25s 960×540 / 126 frames | valid MP4 | 1.722s | ~159 MiB | ~152 MiB |
| 6.04s 1920×1080 / 145 frames | valid MP4 | 5.23s | ~187 MiB | ~223 MiB |
| **30s 1920×1080 / 720 frames** | **valid MP4** | **25.84s** | **~189 MiB** | **~270 MiB** |

These are not benchmarks on the user's Oracle VPS / GitHub Actions; speed and peak RSS will differ. **The claim that a 30s 1080p video takes only five seconds and ≤150 MB RAM is not supported by these runs.** All media use CPU only, but Python, codec, OS and process memory are additional. FFmpeg child RSS is reported separately and is not the peak of *total concurrent* memory.

## Visual limitations

The six poses are ready-made **full character drawings**, not manipulable anatomical puppet bones. Squash/stretch, 2D transforms, holds, camera effects and intentional pose swaps create cartoon motion. They **do not** create new true frame-to-frame arm/knee poses, optical-flow inbetweening, or GPU diffusion frames. The character expression changes with selected poses; it does **not** grin in every frame. Because the pose is one sprite, there is no independently overlaid double head/face.

The 6-pose source is a previously generated black-and-white mascot pose sheet; do not substitute an unrelated copyrighted character. `assets/six_pose_sheet_for_git.png` is an optional reduced-size deployment copy.

### Demo files
- `output/01_sinhala_prompt_jump_run_shock.mp4`
- `output/02_door_comedy.mp4`
- `output/03_jump_slip.mp4`
- `output/04_speed_chase.mp4`
- `output/00_ALL_FOUR_Custom_Prompt_Demos.mp4`
- `output/BENCHMARK_1080p_30s.mp4` (full benchmark video, available separately for download to keep ZIP small)
