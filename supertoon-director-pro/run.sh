#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v ffmpeg >/dev/null; then echo 'Install FFmpeg first (sudo apt-get install -y ffmpeg)' >&2; exit 1; fi
if ! /usr/bin/python3 -c 'import cairo' 2>/dev/null; then echo 'Install python3-cairo: sudo apt-get install -y python3-cairo' >&2; exit 1; fi
PROMPT="${1:-Funny boy runs to toilet, knocks, panics, slips then recovers}"
RATIO="${2:-9:16}"
DURATION="${3:-9}"
OUTPUT="${4:-output/custom-funny-short.mp4}"
/usr/bin/python3 src/render.py --prompt "$PROMPT" --duration "$DURATION" --ratio "$RATIO" --output "$OUTPUT"
