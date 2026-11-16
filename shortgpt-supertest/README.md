# ShortGPT SuperTest — original CPU-compatible short-video automation bridge

This project is **inspired by and independently integrates with** official [RayVentura/ShortGPT](https://github.com/RayVentura/ShortGPT), pinned for the upstream audit at commit `3df4e0f7a422bf7386565d498bf4521a2544c614`. ShortGPT is MIT-licensed; its original package uses OpenAI, Bing Image search, EdgeTTS, MoviePy, Torch, Whisper and other packages. **The official ShortGPT editor is not the code executing our bridge's rendered demo.** No false claim that a fully imported ShortGPT engine created the video.

### Pipeline

A single text prompt -> constrained scene planner -> **optional real remote LLM JSON** -> **optional Hugging Face AI-generated background(s)** -> fresh frame-by-frame procedural human body and face motion -> **real speech** from CPU espeak or optional EdgeTTS -> FFmpeg each scene -> concatenated H.264/AAC portrait MP4.

* Demo/offline: no API keys, uses English narrated scene scripts plus procedural flat backgrounds. **These are not AI-generated images and offline rule keywords are not LLM reasoning.**
* `--planner local`: LLM reasoning via a locally running OpenAI-compatible llama.cpp Chat Completions server, configurable `LOCAL_LLM_CHAT_URL` and `LOCAL_LLM_MODEL` (on Oracle, existing 469 MB GGUF can be reused only while resources permit).
* `--planner hf`: remote HF Inference Provider chat completions; needs `HF_TOKEN` and `HF_CHAT_MODEL`, subject to model/provider availability and credits.
* `--images hf`: invokes `huggingface_hub.InferenceClient.text_to_image`, needs `HF_TOKEN` and `HF_IMAGE_MODEL`, subject to providers/quotas. Defaults to max **two distinct AI image calls** per video (`HF_IMAGE_LIMIT`) with per-scene image caching, preventing surprise free-credit consumption. No silent API fallback.
* `--tts espeak`: **English** speech on CPU via espeak-ng or espeak. `--tts edge`: requires internet and a supported chosen voice (`EDGE_TTS_VOICE`); Sinhala text is blocked unless voice has the `si-LK-` prefix and is supported by that service. `--tts none`: video without speech.

The original upstream ShortGPT sources **have been cloned and Python bytecode syntax-checked** on the isolated Oracle AI VPS. A fully loaded upstream Gradio/torch/whisper installation requires substantially more RAM and optional external provider credentials than that host currently offers; for this reason we use GitHub Actions for compatibility audits and retain the small bridge on Oracle. Do **not** run a heavyweight Torch install on the 1GB production host.

### Local or Oracle isolated folder

```bash
sudo apt-get install ffmpeg espeak-ng
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python shortgpt_supertest.py --planner offline --images procedural --tts espeak \
  --prompt 'A kid runs to the toilet, knocks, panics, recovers' --output output/sample.mp4
```

For real AI images (may consume paid credits):

```bash
# Configure HF_TOKEN and HF_IMAGE_MODEL as *secrets*, not committed files
python shortgpt_supertest.py --planner local --images hf --tts espeak \
  --prompt 'Kid runs into an old school, jumps, gets surprised' --output output/ai_short.mp4
```

### GitHub Actions

`ShortGPT SuperTest CPU Bridge` installs on GitHub, downloads pinned original ShortGPT, performs syntax/compatibility audit, executes unit tests, and renders an actual offline 6.2-second MP4. An opt-in manual workflow flag can run HF provider validation if GitHub Secret `HF_TOKEN` and model settings are set. **Never print API keys in logs.** Optional full upstream dependency install is a separate job because Torch/Whisper are large.

### Hugging Face

A `huggingface_space/` Gradio UI and `Dockerfile` are provided. **Hugging Face compute-backed Gradio/Docker Spaces currently require a subscription even when CPU Basic's hourly price is free.** On a Free plan, use free Static Spaces for static documentation/front-end only, or use GitHub/Oracle for execution. HF Free monthly inference credits are small (official docs list $0.10 for Free users as of Nov 2026). A HF token is optional: use GitHub Settings → Secrets and variables → Actions → New repository secret `HF_TOKEN` with minimal permissions; do **not** post the token in chat.

### Resource safety and limitations

- Only the Oracle `vidbest-ai-engine` was reachable with write-enabled project tools. Three Oracle instances were *not* all examined or configured.
- Existing VidBest production services and prior Super Test/InkRig/Horde pipelines remain untouched; isolate this work in a separate GitHub experiment branch and Oracle workspace.
- CPU compositing is fast but advanced AI-image generation is a **remote inference** workload, likely GPU backed by provider; no guarantees of free unlimited use.
- Simple procedural puppet movement differs from generative AI animation and cinematic character acting. Character consistency is achieved by reusing the drawn foreground rig; background images can vary.
- The upstream ShortGPT code contains insecure SSL `verify=False` in Bing image scraping. We do **not** use that legacy scraper and never auto-run model-supplied programs.
- Content rights and usage restrictions for generated outputs remain the user's responsibility.

## Verified results, 16 November 2026

- GitHub standalone CPU bridge render, 5 tests, pinned official source compile/import audit **PASS**: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43864252487
- Full original ShortGPT CPU dependency installation, `pip check`, and `ContentShortEngine` import **PASS**: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43865140639 . Original upstream requirements and setup.py conflict on OpenAI 1.37.0 / 1.37.2; the isolated audit overrides to 1.37.2.
- Oracle AI host in separate workspace: original full ShortGPT source checked out and compiled, bridge produced a narrated 6.2-second H.264/AAC video in 9.8 seconds. Existing production services not changed.
- The existing GitHub `HF_TOKEN` passed read-only authentication; `HF_IMAGE_MODEL` repository variable missing. **No paid inference or actual AI image generation yet.**
- Private Hugging Face dataset containing source and generated MP4 **successfully created**: https://huggingface.co/datasets/gkasun/shortgpt-supertest-private-kit ; evidence https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43865707224 . Dataset is **storage, not a running compute Space**.
- Experiment PR (unmerged): https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/pull/18
