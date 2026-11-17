# Kaggle H3 pilot — decision and safety gates

**Purpose:** Add MiniMax H3 as an OPTIONAL image-to-video GPU shot engine for the existing Funny Toon Ever black-and-white permanent mascot. Do not replace the verified V4/V6/spicy-chili reference-derived CPU rigs. This is a **safe pilot**, not a claim that H3 runs on the user's GPUs.

## Tested baseline

The existing `kaggle-studio/` and `hybrid-gpu/` directories already contain Kaggle submission helpers and CPU render fallbacks. The user requested a best-plan selection from a sample script that includes invalid/unconfirmed MiniMax model aliases. **Do not run** `python wgp.py --model minimax_h3_int8 --ref-image ... --offload cpu` as though those flags were a supported headless interface.

WanGP upstream documents **saved-queue processing**:
```bash
python wgp.py --process /kaggle/input/your-private-queue/queue.zip --output-dir /kaggle/working/fte-h3-test
```
Source: https://github.com/deepbeepmeep/WanGP/blob/main/docs/CLI.md

## Highest quality with the least Kaggle GPU time

1. Qwen3/story planner authors scene JSON with fixed mascot identity. Keep the **permanent reference file** `mascot-lab/config/permanent_mascot.webp`.
2. CPU renderer creates the whole video first (FK fast run, IK arms and hand-to-door contact, character eyes and mouth, cuts, shakes, sound). Keep the CPU short as an always-ready fallback.
3. Mark at most **one** hard special-effect shot (for example a 3–5-second flaming chili blast) as a GPU trial. Most regular acting stays CPU.
4. Prepare source, Kaggle private dataset/cache and saved queue while GPU is OFF wherever possible. Save a *real* exported WanGP queue with the user's input image. Pin tested upstream versions. First H3 test must check T4 memory, disk, CPU RAM and supported INT8 kernels; T4 ×2 ≠ automatic 32 GiB shared VRAM.
5. Allocate Kaggle T4 GPUs only for one bounded 480p 3–5-second run and capture actual timing, log, input image, seed, output MP4, checksum, and error details. If OOM/timeout, fall back to CPU, and benchmark a lighter compatible model before further quota expense.
6. Collect outputs through **Kaggle Kernel Outputs**, optionally upload verified MP4 directly to private Cloudflare R2 with scoped bucket credentials; do **not** transfer huge weights through the 1GiB Oracle VPS. Never expose unauthenticated public model APIs.
7. Normalize video/audio on GitHub Actions CPU; concat with `-c copy` only for matching codec, fps, dimensions and audio stream layout. QA visual continuity before distribution.
8. After a successful benchmark, compute feasible quota use from measured wall-clock minutes per *successful* clip, startup and retries. The 30h weekly Kaggle GPU budget is variable; 15–20 videos/week is an estimate, not a guarantee.

## Honest status

- **Decision/source review done:** MiniMax H3 and WanGP saved-queue CLI exist. Avoid unverified model aliases and automatic blind batch downloads.
- **CPU scaffold prepared separately:** shot budgeting, safe queue preflight, direct R2 uploader, guarded FFmpeg stitching, 6 unit tests locally passed. This GitHub README is a staged planning file, NOT proof of a committed/verified GPU renderer.
- **Not done:** No authorized Kaggle session, H3 model weights, successful H3 inference, R2 credentials or generated H3 clip have been verified in this pilot.
- Keep all existing V4/V6/Spicy/Horde/Kaggle workflows untouched.

Official reference links:
- Kaggle quota: https://www.kaggle.com/docs/efficient-gpu-usage
- MiniMax H3: https://design.minimax.io/h3
- WanGP CLI: https://github.com/deepbeepmeep/WanGP/blob/main/docs/CLI.md
- Kaggle CLI: https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md
- R2 free-tier: https://developers.cloudflare.com/r2/pricing/
