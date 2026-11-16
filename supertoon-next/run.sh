#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 src/render.py --prompt "${1:-ටොයිලට් එකට දුවලා දොරට තට්ටු කරලා බය වෙලා ලිස්සලා වැටෙන විහිළුවක්}" --ratio 9:16 --duration 9 --output out/custom-funny-short.mp4