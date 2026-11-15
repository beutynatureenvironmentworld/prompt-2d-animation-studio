#!/usr/bin/env bash
# Manual, GPU runtime installation adapter. No open/public tunneling.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
MODE=check
MODEL=ltx
ROOT="$PWD/VidBestComfy"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --check) MODE=check; shift ;;
    --sources-only) MODE=sources; shift ;;
    --install) MODE=install; shift ;;
    --model) test "$#" -ge 2 || exit 2; MODEL="$2"; shift 2 ;;
    --help) echo 'Usage: bootstrap.sh [--check|--sources-only|--install] [--model ltx|wan|toon]'; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$MODEL" in ltx|wan|toon) ;; *) echo 'Invalid model' >&2; exit 2 ;; esac
command -v python3 >/dev/null || { echo 'Missing Python 3' >&2; exit 1; }
if [ "$MODE" = check ]; then
  python3 hybrid-gpu/provider_readiness.py
  exit 0
fi
command -v git >/dev/null || { echo 'Missing Git' >&2; exit 1; }
if [ "$MODE" = sources ]; then
  echo "Checking out pinned ComfyUI sources for $MODEL; no weights."
  python3 hybrid-gpu/setup.py "$MODEL" --sources-only --root "$ROOT"
  exit 0
fi
command -v ffmpeg >/dev/null || { echo 'Install FFmpeg on the GPU runtime first' >&2; exit 1; }
python3 - <<'PY'
try:
    import torch
except ImportError:
    raise SystemExit('CUDA PyTorch missing; enable a supported GPU runtime first.')
if not torch.cuda.is_available():
    raise SystemExit('No active NVIDIA CUDA GPU; select GPU in Kaggle, Colab or Lightning.')
print('GPU accessible:', torch.cuda.get_device_name(0))
PY
echo "Installing selected $MODEL multi-GB model; review license, disk, quotas."
python3 hybrid-gpu/setup.py "$MODEL" --root "$ROOT"
echo 'Installation completed; actual GPU video generation is a separate test.'
