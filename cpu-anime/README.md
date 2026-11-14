# CPU Anime Studio (isolated prototype)

සිංහල: මෙය පවතින `free-motion/`, `kite/`, `midnight-jar/` projects වෙනස් නොකරන **වෙනම** CPU animation module එකකි. Silent cartoon demo එක Pillow + FFmpeg මඟින් render කරයි. එක prompt එකකින් ඕනෑම natural frame-by-frame anime video එකක් සෑදෙන AI model එකක් **නොවේ**. Reusable rigging, pose/contact constraints සහ authored backgrounds තවත් අවශ්‍යයි.

## Run without GPU or paid API
```bash
sudo apt-get install ffmpeg
python3 -m pip install -r cpu-anime/requirements.txt
python3 -m unittest discover -s cpu-anime -p 'test_*.py' -v
python3 cpu-anime/render_demo.py --prompt "A girl walks, waves and blinks in a lantern garden" --duration 6 --fps 15 --output cpu-anime/out/anime-demo.mp4
```
The output is H.264 MP4 with **no sound**. Existing outputs are not overwritten. Only a fixed allowed list of actions is recognized; user prompts are always data, never shell commands or executable Python.

## GitHub Actions
On push or pull request affecting this module, the workflow creates a small deterministic MP4 and uploads the artifact `cpu-anime-demo`. Use the **Actions → CPU anime tools → Run workflow** menu for optional independent tests:
- `blender_smoke=true`: installs Blender + Synfig and renders three tiny CPU Blender frames (OIDN disabled when not available).
- `build_sd_cpp=true`: compiles a pinned commit of stable-diffusion.cpp for CPU. **No model weights** are downloaded; compiling alone produces no AI images.

## Architecture and limitations
`validated prompt → bounded scene plan → authored 2D character/rig/scene → CPU renderer → FFmpeg → silent MP4`.

The optional stable-diffusion.cpp C++ engine supports compatible locally supplied weights, including some quantized GGUF formats. Users must verify a specific model's architecture, license and memory consumption. A low-memory CPU runner may take minutes or longer per diffusion frame and cannot be presumed GPU-fast. LCM/Turbo require compatible model checkpoints and schedulers. AI-generated individual frames do **not** by themselves ensure character continuity.

Blender Cycles can use CPU ray tracing and denoising when provided by the selected build; a distribution's Blender may lack Open Image Denoise, so this test deliberately disables denoising. Synfig has vector tweening/bones and can supplement authored scenes. Sound, voice, Suno/ElevenLabs, and MoneyPrinterTurbo are intentionally **not** required for this silent first milestone.

GitHub-hosted runners are ephemeral and have time, usage, storage, network and quota limits. GitHub Actions does not permanently install software on your computer or Oracle instance. Do not upload private reference media, models, tokens, secrets or licensed assets to a public repository. Check licenses separately for models, artwork, voices and outputs.

Upstream: https://github.com/leejet/stable-diffusion.cpp · https://www.blender.org/ · https://www.synfig.org/ · https://ffmpeg.org/
