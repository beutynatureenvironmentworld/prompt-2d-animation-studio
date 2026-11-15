# Continue the video project on ChatGPT Plus, without buying R2

## සිංහල

**Cloudflare R2 දැන්ම මිලදී ගන්න අවශ්‍ය නැහැ.** GitHub Actions වෙතින් CPU animation video සහ GPU notebook බාගත කරගන්න පුළුවන්. Kaggle හෝ Colab හි GPU session එකක් නොමිලේ ලැබුණොත් පසුව තෝරාගත් තත්පර කිහිපයක් සඳහා LTX / Wan / ToonCrafter AI video generation පරීක්ෂා කළ හැක. GPU quota, availability සහ model terms තහවුරු කළ යුතුයි.

1. GitHub -> Actions -> Free CPU cartoon and GPU notebook handoff -> Run workflow.
2. Select ltx, wan, or toon (only chooses a notebook target).
3. When successful, download the free-cartoon-and-gpu-handoff artifact.
4. Play watch-me-silent.mp4. It is a real CPU-rendered silent cartoon.
5. If you later have an available Kaggle or Colab GPU, import gpu-trial-notebook.ipynb. Inspect the cells and memory/disk requirements first. GPU inference has NOT been confirmed in your Kaggle account.

## English

This no-secret CI exercise uses an already authored Snap2D scene, makes an editable storyboard, generates a GPU-shot ZIP containing reference frames, builds a portable notebook and verifies that the original 2D MP4 is preserved as a fallback. No GPU, R2 bucket or external AI inference is used.

Run locally, inside the repository, with Python 3.11+, ffmpeg and system python3-cairo:

    python3 hybrid-gpu/cpu_handoff_smoke.py --model ltx --output handoff-test

The output directory must be new/empty to prevent overwrites. It creates:

- watch-me-silent.mp4: validated silent H.264 portrait cartoon.
- editable-cartoon-storyboard.json: original reusable pose/shot plan.
- gpu-shot-plan.json: the exact frame-range intended for GPU generation.
- gpu-handoff-bundle.zip: self-contained CPU episode plus reference stills.
- gpu-trial-notebook.ipynb: interactive notebook targeting the selected model.
- test-result.json: explicitly records gpu_used=false and r2_used=false.

The CI job intentionally removes R2_BUCKET and Kaggle environment variables for its subprocesses; it does not submit a notebook, enable billing, or upload a private reference. Re-running the orchestration is safe if the same bundle and output directory are retained, and missing GPU results always fall back to the CPU video.

R2 is optional for long-term checkpoint sharing after GitHub Artifacts expire; it is not required for test videos. Before creating a bucket or enabling storage, check current R2 usage limits/fees and use bucket-scoped, least-privilege secrets (never paste secrets in chat).

Known limitation: this verifies CPU -> notebook handoff, not actual ComfyUI GPU inference. Image-to-video model weights are large; Kaggle / Colab GPUs are limited and not guaranteed. The currently installed ComfyUI source/node CI validates node registrations but does not prove all model checkpoints produce good video. The user's ChatGPT Plus subscription does not include paid GPU services or unlimited GitHub Actions runtime.
