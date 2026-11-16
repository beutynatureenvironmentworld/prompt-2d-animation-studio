# ShortGPT Open-Weights CPU — සරල Setup Guide

මෙය **සැබෑ AI** භාවිතා කරන පද්ධතියකි. Qwen3 CPU model එකෙන් script සහ JSON story එක ලියයි, Segmind SSD-1B CPU model එකෙන් පසුබිම් image එක නිර්මාණය කරයි. espeak-ng හඬ සහ FFmpeg MP4 සකසයි.

## එක Prompt එකකින් Video එකක් — පියවර 4

1. GitHub [ShortGPT Full Local AI workflow](https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/workflows/shortgpt-full-local-ai-mp4.yml) විවෘත කරන්න. **Actions** tab එක සක්‍රීයව තිබිය යුතුයි.
2. **Run workflow** තෝරා `main` branch එක තෝරන්න. `prompt` field එකට English හෝ Sinhala comedy scene idea එක ඇතුළත් කරන්න. උදා: `A boy runs to the toilet and gets frightened when the door locks`.
3. `image_steps` තෝරන්න: **9** = වේගවත් test, **14** = balanced, **20** = හොඳ quality සඳහා වැඩි CPU කාලයක්. ඉන්පසු **Run workflow** ඔබන්න.
4. GitHub workflow එක සාර්ථකව අවසන් වූ පසු **Artifacts → full-shortgpt-openweights-real-ai-cartoon-video** යටතේ MP4, verification JSON සහ AI background PNG ලබාගන්න.

**නව API key/secret එකක් අවශ්‍ය නැහැ.** මේ mode එක public Hugging Face models **download කර GitHub Actions CPU එකේම run කරනවා**. HF_TOKEN භාවිත වන්නේ වෙනම HF-provider optional mode එකකට පමණි; එය කලින්ම GitHub Secret එකක් ලෙස සුරක්ෂිතයි.

## Tested original model combination

- **Reasoning:** `bartowski/Qwen_Qwen3-4B-Instruct-2507-GGUF` / `Qwen_Qwen3-4B-Instruct-2507-Q4_K_M.gguf` (~2.5GB), Qwen3 4B Instruct base model Apache-2.0.
- **Image:** `segmind/SSD-1B` (only required ~4.5GB fp16 component files, Apache-2.0).
- **Voice:** `espeak-ng` offline English; optional edge-tts network.
- **Video:** procedural 2D foreground, original diffusion background, FFmpeg H.264/AAC output.

## Real verification

- **Two models actually installed and inferred separately:** https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43934867587
  - Qwen3 produced **4 valid story scenes**, measured 67.81 seconds (download/load/inference).
  - SSD‑1B generated actual **320×448 cartoon image**, measured 76.62 seconds (download/load/inference).
- **FULL end-to-end on CPU:** https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43936165702
  - Qwen3 + SSD‑1B + offline speech + MP4 passed, 4 scenes, **4.52 seconds playable video**, render stage 79.71 sec (dependency install excluded).
  - No GPU inference and **no paid model API request** in these tests.
- Direct video proof: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/blob/experiment/shortgpt-supertest-hf-oracle/shortgpt-supertest/demo/ShortGPT_FULL_Qwen3_SSD1B_CPU_AI_Video.mp4

## Important boundaries

- GitHub standard public Ubuntu runner: 4 vCPU, 16GB RAM, ~14GB SSD. File size tolerance does not remove hardware limits.
- Your connected **Oracle AI host has 952 MiB RAM + 2GiB swap**, unsuitable for these large models. Keep CPU image diffusion on GitHub, and keep Oracle for small orchestrator/FFmpeg tasks; do not overload VidBest production.
- A video with AI **backgrounds** is not an AI video diffusion output. The foreground actor remains an animated vector character. Current demo is a **technical production pipeline proof**, not yet fully polished frame-by-frame cartoon acting.
- Workflow model downloads can be slow; image_steps affects time and quality. Real free quotas depend on GitHub policy. Do not paste API secrets into prompts, logs, or code.
- Full inference models **aren't committed to GitHub**, only reproducible scripts; they download fresh to ephemeral runners.
