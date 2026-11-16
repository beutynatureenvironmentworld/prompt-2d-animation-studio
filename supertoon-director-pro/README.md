# Funny Toon Ever — SuperToon Director Pro (original Super Test upgrade)

**Goal:** Enter one English or Sinhala prompt; choose vertical 9:16 for YouTube Shorts/TikTok; generate a new **original 2D animation MP4** without API keys. This independent project does not change the earlier cat Super Test, InkRig, vid.best, or Oracle production services. The original owner-supplied Super Test run / jump / door / chase clips inform visual timing, but their frames are **not** used/copy-pasted.

## Measured result (local proof)

Four original code-drawn H.264/AAC portrait MP4s were generated and ffprobe checked, including cat/beach, boy/toilet, original mono mascot, and two-character cat-and-boy chase. All four have 24 FPS and distinct geometric facial/body poses. The 8 Python unit tests passed. User-provided original images and audio are not redistributed here. Example render times measured on the current container: ~1.1–1.4 seconds for 7–9s **432×768** drafts, not a 1080p/30-second guarantee.

## Free offline use

```sh
sudo apt-get update && sudo apt-get install -y ffmpeg python3-cairo
./run.sh 'ටොයිලට් එකට දුවගෙන ගිහින් දොරට තට්ටු කරලා බය වෙලා ලිස්සලා වැටෙන ළමයෙක්' 9:16 9 output/toilet.mp4
./run.sh 'Cat and boy chase a ball on the beach, then jump and laugh' 9:16 9 output/cat.mp4
```

Or use `Actions → EXPERIMENT - SuperToon Director Pro Custom Funny Short → Run workflow`. Choose prompt, duration, orientation and color/black-white style. GitHub Actions runs all tests and outputs a downloadable MP4 as an artifact (7-day retention). GitHub public repository minutes are still subject to fair-use and abuse constraints; not an unlimited render farm.

## How the physics/animation works

- **Per-frame vector art:** PyCairo draws original character, eyes, mouth, hair, torso, background, props and FX from reusable authored templates. No AI models are loaded into the renderer and no fixed six-pose sheet is needed.
- **2-bone IK:** independently animated elbow, knee and ankle coordinates; alternating sprint phase and airborne jump arcs; distinct open/neutral/surprised facial expressions.
- **Fast comedy:** anticipation, speed lines, squash/stretch, camera punches, impacts, 24 FPS, original synthesized SFX; optional manual WAV narration imported with `--voice`.
- **Environment templates:** toilet, park, beach, school, kitchen, bedroom, street, forest, space, office, rooftop.
- **Reusable characters:** cat, boy, girl, robot, mono mascot; original two-character scenes detected from prompt. **Not** arbitrary newly invented character art.
- **Props:** banana, ball, cookie, phone, skateboard, toilet paper, cup.
- **Actions:** notice, anticipate, sprint, jump, knock, point, talk, wave, dodge, slip, fall, panic, laugh, dance, recover.

The planner is **offline rule-based** for predictable free default operation. Unknown prompts map to supported templates; a novel environment/character/complex action needs an additional art/motion template. `src/llm_plan.py` is a separate **opt-in** OpenAI-compatible JSON-only LLM storyboard adaptor. LLM output is **strictly validated against known actions**; model-provided code is never executed. If no supported output, fallback offline with `--fallback-offline`.

## Free AI story reasoning (optional)

- The linked Oracle AI host already contains a small quantized local GGUF (about 469 MB) and llama.cpp CLI. It successfully ran a tiny JSON completion with **1 CPU thread, context 256 and batch 16** under a virtual-memory cap on 16 Nov 2026. This is **not** yet a verified complex full-story planning run. The low-RAM (~952 MiB) host should not run a large LLM concurrently with production processes.
- If you run an existing OpenAI-compatible local llama-server safely (not enabled by this project), configure `STORY_LLM_BASE=http://127.0.0.1:8080`, `STORY_LLM_MODEL=local` and call `src/llm_plan.py`.
- Gemini AI Studio's model-specific **free API tier** is an optional cloud story planner. Use [AI Studio API keys](https://aistudio.google.com/apikey), save the key in GitHub Actions Secrets as `STORY_LLM_API_KEY` and set an API-compatible endpoint/model. This isn't required for offline video creation, and is subject to model-based free quota and provider terms.
- Hugging Face [settings/tokens](https://huggingface.co/settings/tokens) is optional for persistent asset/model storage or routed inference. Storage and inference allowances are different; free inference is not guaranteed unlimited. Never share the key in chat or code.

## Infrastructure safety

- **GitHub Actions:** full video rendering, source of truth, transient artifact; optional HF/R2 storage once separately configured.
- **Oracle AI host (1GB, existing local llama.cpp):** *only* CPU low-quality/cutout renders or limited local planning in an isolated process. Never touch production VidBest services.
- **Other Oracle instance(s):** this chat's connected Oracle tools expose an AI host and one separate OS-status endpoint, not proven administrative control over all claimed three instances. Do not assume a third was installed or tested.
- **GPU Kaggle/Colab/Horde:** not needed for the vector workflow. Optional GPU can build illustrated character assets, but arbitrary GPU image generation does not guarantee consistent limbs or characters.

## Tests

```sh
/usr/bin/python3 -m unittest discover -s tests -v
/usr/bin/python3 src/render.py --prompt 'Cat sprints, jumps and laughs on beach' --ratio 9:16 --quality draft --duration 7 --output output/sample.mp4
```

Default draft is **432×768**; `--quality hd` creates 648×1152. 1GB VPS should trial low quality first. Test output quality on actual phone screen and adjust acting; do not claim RicoAnimations-like frame-by-frame artistry without visual proof.
