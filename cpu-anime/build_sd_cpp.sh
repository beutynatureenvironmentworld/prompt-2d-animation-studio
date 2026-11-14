#!/usr/bin/env bash
set -euo pipefail
# CPU build only, no model weights, no credentials. Commit verified from upstream.
SD_COMMIT=5dcfa79801213f23e27b3e83617350ebb8ea93aa
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$ROOT/vendor/stable-diffusion.cpp"
if [[ -e "$TARGET" ]]; then echo "Refusing to overwrite $TARGET" >&2; exit 1; fi
mkdir -p "$(dirname "$TARGET")"
git clone --no-checkout https://github.com/leejet/stable-diffusion.cpp "$TARGET"
git -C "$TARGET" checkout "$SD_COMMIT"
git -C "$TARGET" submodule update --init --recursive --depth 1
cmake -S "$TARGET" -B "$TARGET/build" -DCMAKE_BUILD_TYPE=Release -DSD_CUDA=OFF
cmake --build "$TARGET/build" --parallel 2
echo "CPU engine compiled; AI inference requires separately supplied compatible model weights."
