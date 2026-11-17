# Funny Toon Ever — Dream Kick MiniMax H3 recovery, 18 Nov 2026

**Correct episode:** a 2D pigtail girl runs outside, winds up and kicks a *green soccer ball*. Hard **match cut** into the bedroom: the sleeping girl delivers the same extended-leg kick to the bald boy next to her, launching him off the mattress. Boy crashes; girl wakes shocked.

**Final target:** 9:16 portrait, funnytoonever watermark at the bottom (never vid.best), original whoosh/kick-thud/crash/scream comedic SFX and soft location ambience.

## Verified Kaggle blockers

- The old **real** private Kaggle H3 kernel was `gamagekasun/fte-dreamkick-h3-44116299561-4132f6c6`. **2 Tesla T4 GPUs allocated**, but model download failed **ENOSPC before inference**; RESULT.json said h3_inference_verified=false; no H3 video.
- The later Kaggle **CPU-only storage probe** failed with **403 Forbidden for GetKernelSessionStatus**, so it did not return a reliable free-disk capacity. The old H3 kernel itself is in ERROR status. A successful GitHub poll is not a successful GPU render.
- Two 16GB T4 cards are not one 32GB device. GPU availability, VRAM placement, disk, licensing and model size still need verification.

## Fixed: exact cached-model profile

The H3 job **actually runs Singularity Ref2VA INT8**, while an old preflight used an ordinary **base Ref2VA FP8** checkpoint name. The repaired worker now requires the right Singularity checkpoint together with the three common assets in a **private Kaggle Input dataset**:

```text
/kaggle/input/fte-h3-models/models/
  text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
  vae/minimax_h3_video_vae_fp16.safetensors
  vae/minimax_h3_audio_vae_fp32.safetensors
  diffusion_models/Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors
```

On a **CPU-only notebook** with the private model dataset mounted, run:

```bash
python dreamkick-h3/storage_guard.py --cache-root /kaggle/input/fte-h3-models/models --out /kaggle/working/FTE_H3_STORAGE_READINESS.json --require-complete
```

This guard does not download models or use GPU quota. A private dataset must be provisioned separately, subject to **Kaggle disk/output limits** and the model owners' license terms. A simple 20GB notebook output may be insufficient for the complete model bundle. The guard checks **filenames and nontrivial sizes**, not all weight hashes; validate pinned revisions and integrity using upstream loaders.

The H3 notebook now **refuses direct model downloading by default**, instead of repeating the known full-disk failure. On a separately confirmed large-disk setup, the explicit opt-in `FTE_H3_ALLOW_DIRECT_DOWNLOAD=1` permits direct download subject to the existing conservative 50GiB free-space check; neither setting guarantees enough disk.

## API 403 blocker

Inspect [Kaggle's API token settings](https://www.kaggle.com/settings/api) and the current token's notebook session read permission. Store a replacement token only in the existing GitHub Actions **KAGGLE_API_TOKEN** secret. Do not paste credentials in the chat or store in the repository. If Kaggle disallows session-status via your token, use the **private Kaggle notebook UI and Output tab** for results; never claim generation just because polling is blocked.

## Next authorized GPU run

Only after a complete model cache passes a **real Kaggle CPU-only preflight** and the account has session access: submit **one** private Kaggle H3 job, verify RESULT.json and an actual H3 MP4, then generate the second scene and review contact/match-cut. 9:16 may require cropping a native 4:3 result; preserve action inside the safe area. Verify sound, watermark, audio and full MP4 streams.

A separate **10.2s 540×960 H.264/AAC CPU preview** (not H3) was generated in the conversation as a shot/audio-timing guide and **must never be labelled an H3 output**.

**No further GPU job was submitted by this recovery patch.**
