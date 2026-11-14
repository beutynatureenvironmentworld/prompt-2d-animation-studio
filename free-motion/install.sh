#!/usr/bin/env bash
# Ubuntu x86_64. Set MOTION_RUNTIME to override the private installation folder.
set -euo pipefail
cd "$(dirname "$0")"
runtime="${MOTION_RUNTIME:-$PWD/runtime}"
[[ "$(uname -m)" == x86_64 ]] || { echo 'This installer requires x86_64.' >&2; exit 1; }
sudo apt-get install -y --no-install-recommends blender python3-cairo ffmpeg curl
mkdir -p "$runtime"
scratch=$(mktemp -d "$runtime/install.XXXXXX")
trap 'rm -rf "$scratch"' EXIT
if [[ ! -x "$runtime/llama-b7300/llama-cli" ]]; then
  curl -fLsS --retry 2 https://github.com/ggml-org/llama.cpp/releases/download/b7300/llama-b7300-bin-ubuntu-x64.tar.gz -o "$scratch/llama.tgz"
  tar -xzf "$scratch/llama.tgz" -C "$scratch"
  mv "$scratch/llama-b7300" "$runtime/"
fi
if [[ ! -s "$runtime/motion.gguf" ]]; then
  curl -fLsS --retry 2 'https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf?download=true' -o "$scratch/model"
  mv "$scratch/model" "$runtime/motion.gguf"
fi
