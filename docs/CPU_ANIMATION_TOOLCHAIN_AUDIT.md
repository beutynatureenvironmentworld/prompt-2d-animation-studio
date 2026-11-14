# CPU Animation Toolchain — Independent Installation & Smoke-Test Audit

**Project**: `beutynatureenvironmentworld/prompt-2d-animation-studio`  
**As-of**: 2026-11-15 (Asia/Colombo)  
**Scope**: Separate GitHub-hosted Ubuntu 24.04 runners plus isolated tests on 1 GiB Oracle `vidbest-ai-engine`.  
**Status**: A documented engineering audit, **NOT** evidence that all tools produce a polished 2D story or that all were installed on the Oracle instance.

## Test definitions

- **Rendered**: tool generated and saved a tiny real MP4/PNG/SVG or mouth-cue JSON. It does not guarantee high-quality natural movement.
- **Build**: dependencies installed and an editor/browser bundler successfully built.
- **Import**: installed and loaded a Python or JS library; no end-to-end inference/renders.
- **CLI/GUI installed**: package or CLI executable was installed and version/package probed, but not used for a complete workflow.
- **Source only**: git checkout only; **not installed** as a functioning service.
- **Blocked**: not installed, or real render failed. A CI row may be green if it merely **detected** an unavailable program.

## 12 independently executed core CI jobs

GitHub Actions run: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43632009751 — **12/12 job-success**.

| Software | Test performed | Result and constraints |
|---|---|---|
| FFmpeg | Headless synthetic input → H.264 MP4 | **Rendered**, CPU |
| Blender | Workbench CPU scene → PNG | **Rendered**, not a complete animated movie |
| Synfig | Authored self-contained SIF vector scene → PNG | **Rendered**; earlier upstream stickman sample failed due to external linked `#project.sif`, fixed by independent SIF |
| Inkscape | SVG → PNG | **Rendered** |
| Manim | Tiny moving dot scene → MP4 | **Rendered** |
| MoviePy | Python ColorClip → H.264 MP4 | **Rendered** |
| Rhubarb Lip Sync | Synthetic WAV tone → JSON `mouthCues` | **Analyzed**, NOT a validated spoken English/Sinhala lip-sync accuracy test |
| Potrace | PBM → SVG | **Rendered vector conversion** |
| VTracer | PNG → SVG via Python library | **Rendered vector conversion** |
| MediaPipe | Python import with system EGL dependencies | **Imported**; real pose tracking requires compatible model and video |
| Piper TTS | Python runtime import | **Imported**; no voice weights downloaded, no real speech synthesis |
| edge-tts | Python client import | **Imported**; online voice service is external and not an offline open-source voice model |

An initial core run failed because Ubuntu's FFmpeg was missing, a Synfig sample referenced a missing file, VTracer offers Python binding rather than the assumed CLI, and MediaPipe needed graphics libraries. These were fixed; the final core matrix is green.

## 10 independently executed advanced CI jobs

GitHub Actions run: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43632009761 — **10/10 test jobs completed successfully, with important scope limits**.

| Software | Verified scope | Assessment |
|---|---|---|
| OpenCode CLI | npm install, actual `opencode v2.3.0` command | Installed/CLI tested; no AI API credentials or model inference |
| Remotion | npm install, real headless Chromium still image | Browser screenshot rendered; separate actual MP4 test also passed |
| Revideo | npm install and Vite browser bundle | Browser build passed; independent **headless MP4 test FAILED** (below) |
| Motion Canvas | npm install and Vite browser bundle | Browser build passed; earlier separate TypeScript editor build also passed; not connected to Snap2D |
| StykAnimate | GPL project clone, JS syntax and `npm ci --ignore-scripts` | Dependencies present on ephemeral runner; **no GUI/WebGPU render** |
| Stick | GPL project clone, JS syntax and `npm ci --ignore-scripts` | Dependencies present on ephemeral runner; **no GUI/WebGPU render** |
| Krita | APT installed package check | GUI installation only; not automated |
| Pencil2D | APT installed package check | GUI installation only; not automated |
| OpenToonz | APT repository presence check | **NOT INSTALLED**. Ubuntu 24.04 stock apt did not offer package. Probe job is green only because it correctly detected this absence; see `audit-advanced-opentoonz` artifact, contents explicitly `NOT_INSTALLED`. |
| MoneyPrinterTurbo | Shallow source checkout & README presence | **SOURCE ONLY**, not a working service or animation generator; no API keys |

**Not every green job means the software is fully installed or production ready.** Source checkout, package check, or Vite build should not be presented as an animated video output.

## Real headless video renderer comparison

Actions runs: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43632640009 (exporter setting) and latest https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43633140886 (named project and scene with official settings).

| Engine | Actual silent H.264 MP4 result |
|---|---|
| **Remotion** | **PASS**: 160×90, 12fps, 12-frame CPU-rendered H.264 MP4 through Chromium |
| **Revideo** | **FAIL**: npm install and Vite build succeeded; initial `renderVideo()` aborted with `Cannot read properties of undefined (reading 'name')`; after adding the official `@revideo/core/wasm` exporter and named scene/project, the latest headless run failed with `The thread is not available in the current context.` No MP4 output was verified; not certified as a production renderer here. |
| Python + PyCairo + FFmpeg (Snap2D) | **PASS**: authored silent portrait fast-action video, verified independently in Snap2D workflow |
| Motion Canvas | TypeScript editor/browser build passed; no standalone MP4 render in these tests. |

**Licensing:** Remotion source is visible but *not* OSI open-source. It uses proprietary Remotion License; qualifying individuals/small teams may use a Free License, other automations may need payment. See https://www.remotion.dev/docs/terms and https://www.remotion.dev/docs/license/pricing. Do not use Remotion as the default of a **strictly 100% OSS** distributable project. Revideo is MIT-licensed (https://github.com/midrender/revideo/blob/main/LICENSE); its unverified headless exporter is the current technical blocker. Motion Canvas is an open-source authored editor candidate.

**CI note:** an earlier renderer-comparison artifact incorrectly included `node_modules` (~73 MB and ~133 MB artifacts). Subsequent workflow now uploads only small report/MP4/metadata (retention: 2 days), not dependency folders.

## Oracle production-host isolated verification

Host is **x86_64** and has ~952 MiB RAM, ~2 GiB swap, ~38 GiB available disk; it is **NOT** an ARM64 VM.

Actual test directory: `/home/ubuntu/snap2d-tools-audit`, separate from existing application directories.

- Already present: FFmpeg, PyCairo 1.25.1, Blender 4.0.2, Synfig, Inkscape, Krita and Pencil2D executables.
- Newly installed small `potrace` apt package and produced a real SVG from PBM.
- Built an isolated Python virtual environment, installed **VTracer** and **MoviePy** with Pillow; produced real `small.svg` and `oracle-smoke.mp4`.
- Existing Blender, Synfig and Inkscape executables were tested with fresh authored content and produced independent PNG files (`blender.png`, `synfig.png`, `inkscape.png`).
- **Did not** run multi-GB ML model downloads, OpenToonz GUI, GPU effects, OpenPose build, Ollama or production server reconfiguration. Safety/risk on a 1 GiB shared server outweighs speculative completeness.

## Other mentioned technologies: explicitly *not* proven installed

| Software / service | Reason and responsible status |
|---|---|
| Ollama, local Qwen / Llama | No Ollama runtime or LLM model was installed/tested for this project. A 1 GiB server is a very small environment for general model inference; a separate prior repo `free-motion/` uses llama.cpp, not Ollama. |
| Kokoro TTS | Model/runtime NOT downloaded or synthesized; speech/audio not required for current silent animation goal. |
| OpenPose | Full OpenPose CUDA/C++ stack NOT installed. MediaPipe Python import is NOT an OpenPose benchmark. |
| Wan, CogVideoX, AnimateDiff, FLUX, Stable Diffusion diffusion checkpoints | NOT downloaded or inferred in this audit. GPU/large-memory workloads and multi-GB weights are inappropriate for 1 GiB Oracle + lightweight GitHub CI. |
| stable-diffusion.cpp | Another existing repository workflow can compile its CPU CLI without weights; compilation alone does NOT produce model-generated images. |
| Google Colab / Kaggle / Cloudflare R2 | External compute/storage services, not installable software; require separate account, permissions, budgets/limits. No storage upload performed. |
| ChatGPT/Gemini API, Suno | External products/services, not locally installed; usage/licensing and charges depend on provider. Suno is not free OSS. |
| OpenGameArt, Openclipart, Kenney, Freesound | Asset repositories. No third-party asset packs automatically downloaded or relicensed. |
| 2D animation techniques (pose-to-pose, squash/stretch, reaction zoom, camera shake, hand-built SVG rigs) | They are methods, not applications. These effects are concretely implemented in the separate Snap2D authored cartoon but do not become fully automatic for arbitrary subjects. |

## Decision for the final **silent, CPU-only, 100% OSS-first** animation stage

1. **Current production-proven baseline**: Snap2D's reusable authored characters + safe data-only beat timeline → **Python + PyCairo** pose/keyframe/vector render → **FFmpeg** H.264 MP4. Keep Oracle as a light planner/controller and use GitHub CPU runners for reproducible renders. No copyrighted reference frames uploaded to public repositories.
2. **Optional motion design/editor**: **Motion Canvas** for authored TypeScript scenes and manual easing; its package/CI build passes, but it is **not automatically integrated** with Snap2D yet.
3. **Optional assets**: **Inkscape + Potrace/VTracer** to author/vectorize original legally usable characters and props; **Synfig/Blender** for specific authored movement/rigging, rather than installing all of them in the critical path.
4. **When audio is requested**: import an authorized voice track and add **Rhubarb** to generate timing cues, followed by FFmpeg mixing. Synthetic tone test is not proof of accurate dialogue lip-sync.
5. **Research-only, not the final OSS renderer yet**: Revideo until a real MP4 smoke test passes; Remotion renders MP4 but has a non-OSI proprietary license, so licensing suitability must be reviewed before including in a strictly open-source release.

**Next acceptance criterion before claiming final pipeline**: a new user-supplied text prompt selects multiple gestures, shot cuts and camera cues; same authored character stays consistent throughout; a real portrait silent MP4 is emitted; GitHub Actions uploads the playable artifact; no hand-edited executable code from the prompt and no API credentials. Do not claim any of this is automatically generated for unconstrained natural-language poses until tested.

## Evidence links

- Core matrix: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43632009751
- Advanced matrix: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43632009761
- Real headless renderer comparison (latest): https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/actions/runs/43633140886
- Snap2D fast-action animation: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/pull/3
- Tool audit proposal: https://github.com/beutynatureenvironmentworld/prompt-2d-animation-studio/pull/4
- GitHub standard public runner usage and limits: https://docs.github.com/en/actions/concepts/billing-and-usage

**Privacy and safety**: no secrets or private media in public logs. Never claim unlimited free GitHub Actions CPU/GPU. This report documents discrete verification scopes only.
