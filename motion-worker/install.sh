#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
revision=e11fe9ae04cefdf964345670eea0427e4d0049a3
if ! test -d runtime/.git; then
  git clone https://github.com/SegerEnd/sprongmotion-runtime.git runtime
fi
git -C runtime checkout --detach "$revision"
make -C runtime -j2 build/examples/01_hello
digest=68fbd311a0d7d75f60508b35254171583c85880e7e124140457b57ac84c5de9d
if ! echo "$digest  model.gguf" | sha256sum -c --status; then
  temp=$(mktemp .model.XXXXXX)
  trap 'rm -f "$temp"' EXIT
  curl -fLsS --retry 3 https://huggingface.co/SegerEnd/SprongMotion-14M/resolve/main/SprongMotion-14M-v1.0-Q8_0.gguf -o "$temp"
  echo "$digest  $temp" | sha256sum -c
  mv "$temp" model.gguf
fi
