#!/usr/bin/env bash
set -euo pipefail
command -v python3 >/dev/null || { echo 'Install Python 3.11+ first'; exit 1; }
command -v ffmpeg >/dev/null || { echo 'Install FFmpeg (apt/brew/winget) first'; exit 1; }
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m studio.core doctor
