#!/usr/bin/env bash
# Original synthesized comedy voice track; optional improvement on already verified InkRig MP4.
set -euo pipefail
cd "$(dirname "$0")/output"
espeak-ng -v en+f3 -s 195 -p 65 -w voice0.wav 'Ooh! A cookie!'
espeak-ng -v en+f3 -s 235 -p 78 -w voice1.wav 'Hey!'
espeak-ng -v en+f3 -s 200 -p 65 -w voice2.wav 'My cookie!'
espeak-ng -v en+f3 -s 215 -p 76 -w voice3.wav 'Whoaaa!'
espeak-ng -v en+f3 -s 185 -p 84 -w voice4.wav 'Nice hat!'
ffmpeg -hide_banner -loglevel error -y \
  -i original-rigged-2d-comedy.mp4 \
  -i voice0.wav -i voice1.wav -i voice2.wav -i voice3.wav -i voice4.wav \
  -filter_complex '[1:a]volume=1.3,adelay=780:all=1[v0];[2:a]volume=1.3,adelay=2690:all=1[v1];[3:a]volume=1.5,adelay=3410:all=1[v2];[4:a]volume=1.4,adelay=7380:all=1[v3];[5:a]volume=1.3,adelay=10300:all=1[v4];[0:a][v0][v1][v2][v3][v4]amix=inputs=6:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.92[xa]' \
  -map 0:v:0 -map '[xa]' -c:v copy -c:a aac -b:a 128k \
  -t 11.5 original-rigged-2d-comedy-with-voices.mp4
test -s original-rigged-2d-comedy-with-voices.mp4
echo "ORIGINAL_SYNTH_VOICE_COMEDY_ADDED; note: this is a timed dub, not viseme-perfect lip-sync."
