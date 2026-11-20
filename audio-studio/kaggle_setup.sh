#!/usr/bin/env bash
# One-time audio setup for a Kaggle Notebook. No automatic huge Wan downloads.
set -euo pipefail
MODE="cpu"
if [ "$#" -ge 1 ]; then MODE="$1"; fi
case "$MODE" in cpu|gpu) ;; *) echo "usage: $0 cpu|gpu"; exit 2 ;; esac
python -m pip install -U "numpy>=1.26,<3" soundfile kokoro
command -v espeak-ng >/dev/null || echo "Install espeak-ng for English TTS"
python audio-studio/fasttoon_audio.py scene --seconds 9 \
  --out /kaggle/working/fasttoon_open_foley.wav
python audio-studio/wan_gpu_gate.py --audit
if [ "$MODE" = gpu ]; then
  echo "Optional AI audio model install: pip install -r audio-studio/requirements-stable-audio.txt"
fi
echo "No Wan checkpoint downloaded. Full Wan2.2 needs >=24GB GPU VRAM."
