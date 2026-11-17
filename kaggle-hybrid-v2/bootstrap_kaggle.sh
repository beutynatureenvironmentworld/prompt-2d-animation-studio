#!/usr/bin/env bash
# Only run after manually starting a private Kaggle notebook with GPU enabled.
# Does NOT expose a public tunnel or try to bypass session/quota limits.
set -euo pipefail
MODE="${1:-probe}"
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ "$MODE" != "probe" && "$MODE" != "wan21-t2v" && "$MODE" != "wangp-queue" ]]; then echo 'Invalid mode' >&2; exit 2; fi
python "$HERE/preflight.py" --output /kaggle/working/fte_gpu_results --require-gpu
if [[ "$MODE" == probe ]]; then exit 0; fi
if [[ "$MODE" == wan21-t2v ]]; then
  python -m pip install --disable-pip-version-check --quiet 'diffusers>=0.35,<0.43' 'transformers>=4.50,<5' 'accelerate>=1.5,<2' 'imageio[ffmpeg]>=2.34' safetensors
fi
if [[ "$MODE" == wangp-queue ]]; then
  ROOT=/kaggle/working/Wan2GP
  if [[ ! -f "$ROOT/wgp.py" ]]; then
    git clone --depth 1 https://github.com/deepbeepmeep/Wan2GP.git "$ROOT"
  fi
  python -m pip install --disable-pip-version-check -r "$ROOT/requirements.txt"
  echo 'WanGP repo is installed but MiniMax weights are NOT predownloaded or tested. Provide an exported queue.'
fi
