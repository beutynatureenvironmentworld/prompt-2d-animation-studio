#!/usr/bin/env bash
# After: python -m pip install -r requirements.txt ; sudo apt install ffmpeg
set -euo pipefail
cd "$(dirname "$0")"
python src/prepare_poses.py
python -m unittest discover -s tests -v
python src/prompt_to_json.py --prompt "චරිතය පැනලා කේන්තියෙන් දුවලා බය වෙලා නැගිටිනවා" --output output/timeline.json
python src/render.py --timeline output/timeline.json --output output/NEW_custom_prompt_video.mp4
printf 'Finished: %s\n' "$(pwd)/output/NEW_custom_prompt_video.mp4"
