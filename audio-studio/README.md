# FastToon Audio Studio (2026-11-20)

The existing 2D character rig and 172 action poses remain unchanged. The
pink-dress girl and blue-shirt boy share expressions; hair/clothing/props are
configured per scene. Headphones and cape are **OFF by default**.

## Verified: Kokoro 82M on GitHub Actions CPU

Actual completed run: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/44767764955

- Boy voice: Kokoro-82M am_puck, generated 1.975s, 24kHz PCM WAV.
- Girl voice: Kokoro-82M af_heart, generated 3.150s, 24kHz PCM WAV.
- Each file passed nonzero samples / non-silent / output length checks.
- Original CPU procedural Foley: six clips + nine-second stereo soundtrack.
- The two artifact archives are attached to the run and can be downloaded.
- This establishes successful CPU synthesis, not an independent blind listening
  comparison with real voice actors.

## Roles

- Kokoro-82M: default speech, Apache-2.0 source/weights.
- Rhubarb Lip Sync: phoneme cues mapped into original cartoon mouth sprites.
- Applio/RVC: optional voice conversion, needs authorized model and separate
  heavy environment. Official code checkout was verified in workflow 44767764807.
- Stable Audio Open Small: GPU-generated SFX, conditional on accepting gated HF
  Stability AI Community License. Inference NOT YET EXECUTED.
- Stable Audio 3 Small SFX: newer optional GPU SFX model; has additional
  Hugging Face/Gemma terms. Inference NOT YET EXECUTED.
- Freesound: manually download CC0/CC-BY recordings, maintain author/license
  credits. **Free API use is noncommercial only**; commercial APIs require approval.
- FFmpeg: timed mix, audio ducking, normalization; no Audacity prerequisite.
- Wan 2.2: separate video-generation GPU renderer; official TI2V5B >=24 GB VRAM.
  CPU GitHub/Kaggle hosts do preprocessing only, not realistic full Wan inference.

## Running the CPU demo

GitHub repository Actions -> FastToon Open Audio - Kokoro CPU and Foley ->
Run workflow -> download voice/Foley artifacts.

Locally with Python 3.11 and ffmpeg:
1) pip install --index-url https://download.pytorch.org/whl/cpu torch
2) pip install -r audio-studio/requirements-kokoro.txt
3) python audio-studio/fasttoon_audio.py tts --cpu --voice am_puck --text "I've got you!" --out voice.wav
4) python audio-studio/fasttoon_audio.py scene --seconds 9 --timeline audio-studio/timeline_superhero_sfx.json --speech voice.wav --out scene_audio.wav

## Licensed real SFX from Freesound

Use browser downloads from a creator page; select CC0 or CC-BY, record the
exact author and URL. CC-BY-NC is not suitable for monetized cartoons.

python audio-studio/freesound_assets.py import-local --file path/to/sound.wav --title "Sound Title" --author "Actual Creator" --source-url "https://freesound.org/s/actual-number/" --license CC0

Importer writes 48 kHz stereo WAV and credits.csv. No Freesound sample has
been downloaded in the GitHub project without verified license metadata.

## Generated SFX from Stable Audio Open Small

1) Accept required gated license at:
   https://huggingface.co/stabilityai/stable-audio-open-small
2) Review commercial terms for monetized YouTube.
3) Run on sufficient GPU; never commit HF token:
   pip install -r audio-studio/requirements-stable-audio.txt
   python audio-studio/stable_audio_sfx.py --model open-small --seconds 3 --prompt "Fast bouncy cartoon whoosh with rubbery wind, clean effect without voices" --out whoosh.wav

Newer optional model after *separate* license acceptance:
   python audio-studio/stable_audio_sfx.py --model 3-small-sfx --seconds 3 --prompt "Cartoon comedic fart pop with room reverberation, no voices" --out pop.wav

Neither large model was downloaded without account license acceptance.

## Applio/RVC

bash audio-studio/install_applio.sh --source-only
# OPTIONAL on suitable machine / owner-approved voice model:
bash audio-studio/install_applio.sh --full

## Wan feasibility

python audio-studio/wan_gpu_gate.py --audit
# opt-in --run only on GPU >=24 GiB after reading model license.

References:
- https://huggingface.co/hexgrad/Kokoro-82M
- https://github.com/IAHispano/Applio
- https://huggingface.co/stabilityai/stable-audio-open-small
- https://huggingface.co/stabilityai/stable-audio-3-small-sfx
- https://freesound.org/docs/api/terms_of_use.html
- https://github.com/Wan-Video/Wan2.2
