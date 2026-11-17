# Funny Toon Ever — Kaggle GPU + Permanent CPU Mascot Hybrid (November 2026)

**Sinhala / English.** This is an **incremental, optional GPU lane** for the tested permanent mascot animations already in `mascot-lab` / `kaggle-studio` / `hybrid-gpu`. It **does not replace** the proven CPU rig, shoulder/no-X-leg fixes, expressions, audio and FFmpeg export. Never call a GPU render "successful" until the actual generated MP4 is collected, decoded, reviewed for mascot identity, and the Kaggle GPU run proves CUDA inference.

## Tested facts and recommendation

1. Kaggle's displayed GPU allowance may be 30h per week (T4 ×2 when available), but **two independent 16GB cards do not automatically behave as one 32GB VRAM device**. There are fluctuating quotas, GPU availability and nonzero download/initialization time.
2. **Default: CPU mascot motion** via `mascot-lab/v4`, `mascot-lab/v6` and `mascot-lab/spicy-chili`; deterministic 2D pose/rig for the character and 95% of facial/action/contact shots. The GPU lane should enhance at most 1–2 **selected** hard motion shots per story, not redraw 100% of all frames. All AI video clips require review to detect double pupils/limbs and drifting identity.
3. **First Kaggle test: `probe`** with real CUDA arithmetic, zero model weight download. **Second optional test: Wan2.1 T2V 1.3B** via official Diffusers (Apache-2.0 model weights), one 320×512, 49-frame 16fps test. T2V does **not condition on the actual mascot bitmap**; use only as a movement/style candidate, not publishable identity-perfect mascot without review. RTX4090 benchmarks should not be extrapolated to T4.
4. **Advanced MiniMax H3 INT8**: MiniMax H3 is available as open weights, and WanGP has H3 configurations. But its quantized checkpoint (~21GB **before** auxiliary encoders) can stress one T4 and Kaggle RAM/disk; 2×T4 VRAM is **not pooled**. WanGP queue setup must be created/exported in WanGP UI. Run CLI `python wgp.py --process exported_queue.zip` (or exported settings JSON), not fabricated flags `--model minimax_h3_int8 --quantize int8 --ref-image`. Use `--dry-run` first. It is an **optional experimental** profile, not the default.
5. **Licensing**: WanGP carries its **WanGP Community License 2.0**, not MIT/Apache; check outputs/service restrictions and attribution for monetized channels. MiniMax H3 weights carry their own **MiniMax H3 Community License**, including jurisdiction-specific restrictions. The Apache-2.0 Wan2.1 1.3B default reduces licensing ambiguity but still requires platform/content compliance. Verify current licences before commercial use; this is not legal advice.

## Architecture

`Prompt → validated shots JSON → CPU mascot poses / selected GPU candidate → private Kaggle GPU job → Kaggle private output (or optional private HF dataset) → CPU FFmpeg assembler/QA → YouTube/TikTok MP4`

No public ComfyUI/Gradio tunnel. No perpetual GPU backend on a Kaggle notebook. No arbitrary `os._exit()` claim that quota stops. Stop sessions using Kaggle controls and check the official quota page.

### Test completely free on GitHub CPU

```bash
python -m unittest discover -s kaggle-hybrid-v2/tests -v
python kaggle-hybrid-v2/story.py kaggle-hybrid-v2/examples/spicy_hybrid_story.json --out /tmp/fte_gpu_jobs.json --gpu-shots 1
python kaggle-hybrid-v2/preflight.py --output /tmp/fte_local_preflight
python kaggle-hybrid-v2/dispatch.py --username YOUR_KAGGLE_USERNAME --mode probe --minutes 12 --folder /tmp/fte-kaggle-probe
```

`dispatch.py` is **dry-run by default**: writes a **private** Kaggle kernel package without consuming GPU quota. To submit with the official Kaggle CLI, use `--submit`, a valid `KAGGLE_API_TOKEN` environment secret, and `pip install kaggle`. From GitHub Actions use manual workflow **FTE Kaggle Hybrid** and a selected `submit-probe` or `submit-wan21` mode.

**Secrets:** GitHub repository → Settings → Secrets and variables → Actions → `New repository secret` → `KAGGLE_API_TOKEN` (never paste into chat). Under Variables add `KAGGLE_USERNAME`. Existing keys should be reused without rotating unnecessarily. You can also use official Kaggle notebook UI to run `Start_GPU_Hybrid.ipynb` with no GitHub token at all.

### Kaggle two-phase workflow, to minimize quota burn

1. On **CPU only**, draft `examples/spicy_hybrid_story.json`, select 1–2 GPU candidates; optionally cache model checkpoints as a user-controlled **private Kaggle Dataset/Model**, subject to redistribution licences, quotas, and actual download size. Do not use public GitHub for multi-GB weights.
2. Create a **private** Kaggle T4 notebook. Set Internet On only if downloading licensed model weights. Run `bootstrap_kaggle.sh probe` first; this tests real GPU arithmetic without generating fake AI frames. Decide whether to continue once VRAM, system RAM and disk are visible.
3. Optionally `bootstrap_kaggle.sh wan21-t2v`, then execute a single `gpu_worker.py --mode wan21-t2v --jobs gpu_jobs.json ...` test. Only **one GPU** is used. You need to explicitly start the Kaggle session. No guaranteed T4 generation speed or successful 1st run.
4. For advanced H3: obtain an official exported WanGP queue from the actual UI, configure local/private Kaggle dataset media paths, choose the H3 profile and quantized checkpoint there, and run `bootstrap_kaggle.sh wangp-queue`. Then `gpu_worker.py --mode wangp-queue --queue /kaggle/input/YOUR_PRIVATE_DATASET/queue.zip --jobs ... --validate-only`, followed by generation if the preflight and licence review pass. This does NOT magically turn the saved queue into 10–15 independently controlled scenes; use one candidate per queue while validating results.
5. The worker saves real `scene_03.mp4` plus `JOB_RESULT.json` under `/kaggle/working/fte_gpu_results`. Download via authenticated `kaggle kernels output USER/SLUG -p output/collected` after verified completion, or optionally archive to an **existing private HF Dataset** using `hf_delivery.py` with an HF secret (no free-unlimited-storage promise).
6. CPU assembler `assemble.py` reads original scene sequence, expects explicit `scene_NN.mp4` from each intended engine, normalizes format, and stitches final portrait MP4. It **refuses to silently replace a missing GPU clip with a CPU one** unless you pass `--allow-cpu-fallback`, which is labelled in the output JSON. If a CPU audio master is available, pass `--audio` for end-to-end synchronized mix.

### Explicit assembly example

```bash
python kaggle-hybrid-v2/assemble.py kaggle-hybrid-v2/examples/spicy_hybrid_story.json \
  --cpu-dir path/to/permanent-rig-shots --gpu-dir path/to/kaggle-output \
  --out output/Funny_Toon_Ever_Hybrid_Story.mp4
```

### Oracle 1GB VPS

Oracle is **optional**, not a prerequisite. CPU FFmpeg packaging can run on GitHub Actions and avoid RAM pressure on a 1GB Oracle VPS. If storing/transfering large clips, prefer authenticated Kaggle outputs or a private Hugging Face dataset over a public unauthenticated `/upload_clip` endpoint. The exact MP4/audio re-encode cost depends on clip size, codec and CPU, not a guaranteed 50MB RAM or 2-second operation.

### What has really been checked

- **Local CPU:** storyboard validation, GPU-selection caps, dry-run Kaggle metadata, missing-queue safety, real ffmpeg assemble smoke (using synthetic test clips only), tests. These do not count as actual GPU video generation.
- **Not yet completed until an authenticated Kaggle GPU session runs:** MiniMax H3 inference, Wan2.1 inference, any actual image-to-video model quality, 2×T4 multi-GPU offload, Kaggle GPU quota/time, private HF upload, Oracle receiver deployment.
- Run human frame QA for shoulder seams, arm/elbow outlines, mouth/eye details, character identity, foot sliding, extra eyes/limbs and object contact before promoting a generated shot.

### Official docs / sources

- Kaggle GPU quotas: https://www.kaggle.com/docs/efficient-gpu-usage
- Kaggle CLI: https://github.com/Kaggle/kaggle-cli
- Official Diffusers Wan: https://huggingface.co/docs/diffusers/api/pipelines/wan
- Apache Wan2.1 1.3B weights: https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B-Diffusers
- Official WanGP `--process` CLI: https://github.com/deepbeepmeep/WanGP/blob/main/docs/CLI.md
- WanGP usage license: https://github.com/deepbeepmeep/WanGP/blob/main/LICENSE.txt
- MiniMax H3 official weights/license: https://huggingface.co/MiniMaxAI/MiniMax-H3
- WanGP H3 checkpoints: https://huggingface.co/DeepBeepMeep/MiniMax-H3
