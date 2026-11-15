# Free GPU connections: truthful setup status (2026-11-15)

## සිංහල
**සියලු GPU installations අවසන් නොවේ.** GitHub repository එකේ ComfyUI install sources, version-pinned workflow JSON, scripts, CPU renderer සහ GPU notebook handoff තිබේ. GitHub CPU Actions එකේ ComfyUI node registration සහ CPU fallback පරීක්ෂා කළා. **Kaggle / Colab / Lightning / Hugging Face provider account එකකින් සැබෑ GPU-generated clip තවම තහවුරු වී නැහැ.**

### GPU providers

| Provider | What is ready | Still needed |
|---|---|---|
| Kaggle | Optional private notebook submission via GitHub Actions workflow and Kaggle CLI | Log in to Kaggle; set GitHub Actions repository *variable* KAGGLE_USERNAME and *secret* KAGGLE_API_TOKEN; verify a GPU session, run a short clip |
| Colab Free | Self-contained notebook | Open manually, enable GPU, run interactively; free Colab may prohibit unattended remote control and primarily web-UI use |
| Lightning AI | Notebook re-usable in an approved Studio | User-initiated Studio and usable free credits; verify billing setting before testing |
| Hugging Face ZeroGPU | Gradio Space client and example configs | Confirm a currently working compatible Space API and quota; opt in before sending images |
| R2 | Optional boto3 uploader in hybrid-gpu/hybrid.py | Not needed initially; bucket and limited-use credentials only if durable cross-provider storage is required |

**Run a safe read-only health check:**

    bash hybrid-gpu/bootstrap.sh --check

**Check out pinned ComfyUI sources and custom nodes only (no weights):**

    bash hybrid-gpu/bootstrap.sh --sources-only --model ltx

**Install multi-GB model weights ONLY from inside a user-selected Kaggle/Colab/Lightning GPU notebook:**

    bash hybrid-gpu/bootstrap.sh --install --model ltx

Models can take substantial disk, RAM and provider GPU quota. This install mode stops without an active NVIDIA GPU. The environment needs compatible CUDA PyTorch and FFmpeg. Inspect upstream model licenses and available space first.

**Direct launch:** GitHub Actions > Hybrid video GPU > Run workflow. Kaggle requires GitHub variable KAGGLE_USERNAME and GitHub secret KAGGLE_API_TOKEN. Keep tokens in provider Secret settings, never paste tokens into chat, notebooks or the repository. The job submits to the account you explicitly connected. It does not grant perpetual free GPU access.

**Colab:** use hybrid-gpu/Start_Here.ipynb interactively; free Colab is not a supported 24/7 GPU service. Running exposed ComfyUI public endpoints through unauthenticated Quick Tunnels is unsafe. Avoid it. Respect Colab restrictions.

**R2:** optional for long-lived video/checkpoint storage. Official R2 Standard free tier is 10 GB-month of storage, not enough for all 15-30GB models at once. Reuse original model downloads/HF cache where licensed and permitted. Do not treat private Hugging Face Hub storage as unlimited: current free private quota is 100GB subject to terms.

**Output volume:** 150-205 full shorts/week and ~2,000/month are UNSUPPORTED estimates, not tested. Actual GPU hours, clip runtime, model throughput, scene consistency, credits and quotas differ by provider. Never claim fixed Colab weekly hours, unlimited GitHub CPU or automatically available Lightning credits.

### Security architecture

GitHub is the versioned **source/configuration store**, not a large-model object store. Oracle is a lightweight coordinator (only ~1GiB RAM). GitHub Actions renders CPU fallback and can submit authorized Kaggle kernels, but does not create new Colab free GPU sessions. Kaggle/Colab/Lightning runtime actually installs the AI weights. Completed GPU shots may be manually copied to the same bundle-hash output folder, or optionally stored in an authorized private R2 bucket. HF ZeroGPU calls require currently supported API signatures.

Never expose a bare ComfyUI /prompt endpoint on a public tunnel. If remote job submission is later added, use an authenticated reverse proxy / provider-supported credentials and strict authorization rather than passing a changing trycloudflare URL to an open Oracle endpoint.

### Reference cartoon

User-provided reference clip is 23.08 seconds, 360x640 at 30fps. Its visual language: distinct comic facial changes, surprise punch-in closeups, pose-to-pose motion, exaggerated expressions and fast shot cuts. The clip is a **visual reference**, not a source we reproduce or commit. We prefer original authored character rigs/poses for consistency and optional GPU-generated shots only where motion complexity justifies GPU consumption.

## English quick summary

This PR adds an offline provider readiness diagnostic and GPU-only install wrapper. CI proves the expected code/workflows exist, JSON graph files parse, and the diagnostic does not print secrets or falsely claim provider connection. It does NOT activate cloud accounts, automate prohibited free Colab tunnels, download model weights, or generate a diffusion AI video.

Supported stages: GitHub code and workflows -> CPU render / storyboard / short candidate GPU shots -> user-authorized private Kaggle notebook or interactive Colab/Lightning -> verify real generated MP4 -> optional private object storage -> final CPU composition.

Docs verified:
- Kaggle GPU hours: https://www.kaggle.com/docs/efficient-gpu-usage
- Colab policies: https://research.google.com/colaboratory/faq.html
- ZeroGPU quotas: https://huggingface.co/docs/hub/spaces-zerogpu
- HF storage limits: https://huggingface.co/docs/hub/storage-limits
- R2 limits/pricing: https://developers.cloudflare.com/r2/pricing/
