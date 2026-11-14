#!/usr/bin/env bash
set -euo pipefail
: "${SD_BIN:?Specify the path to the stable-diffusion.cpp sd-cli binary}"
: "${SD_MODEL:?Specify the SD Turbo model path}"
time "$SD_BIN" -m "$SD_MODEL" -p "${1:?Supply a background prompt}" --mmap --vae-tiling -W 256 -H 256 --steps 1 --cfg-scale 1 --sampling-method euler -s 42 -t 2 -o "${2:?Supply an output PNG path}"
