# CPU anime toolchain status / CPU Anime මෙවලම්

This is a reproducible **hybrid test**, not a claim that a GPU-free prompt alone can generate a polished multi-character natural animation. All modules live in `cpu-anime/` or its dedicated workflows so previous projects remain intact. The GitHub-hosted runner is **ephemeral**.

| Tool | Purpose | Automated check |
|---|---|---|
| Pillow + FFmpeg | Deterministic original authored silent anime-inspired cartoon | `cpu-anime.yml`: actual MP4, tests, artifact |
| Blender Cycles | 2.5D/3D geometry, CPU render, staged action | `cpu-anime-creative-stack.yml`: renders a tiny CPU scene with denoising disabled |
| Synfig + Synfig Studio | Rigging/tweening/vector animation | Installs both and renders 121 stickman sample frames |
| Inkscape + Pencil2D | Author layered SVG art and draw 2D assets | Binary installation and detection only; **no automated drawing** |
| stable-diffusion.cpp | Optional CPU GGUF image diffusion inference | Compiles pinned source. **No model weights**; no actual AI image inference/benchmark |
| Three.js, Motion Canvas, Remotion | Optional procedural visuals and composition | npm install+module resolution only; no JS output video yet |
| MoneyPrinterTurbo | Optional footage/script/video assembly | Isolated upstream source checkout only; not an anime character engine or a fully installed service |
| OpenToonz, Manim, MoviePy, Revideo | Other creative tools considered | Not installed by default; optional after licenses/dependencies and resource limits are checked |

**Important:** Diffusion generation with SDXS/SDXL-Turbo/LCM and GGUF quantization requires a **compatible**, licensed model file, memory capacity and validated inference commands. This repository deliberately downloads **no model weights**, no private reference files and no model API keys. Consequently it does not demonstrate 2–5-second CPU images, GPU-equivalent performance, consistent characters across independent diffusion frames, or automatic extraction of motion from reference videos.

Blender on some Linux distros is built without OIDN; the smoke scene turns denoising off for portability. CPU Cycles can be accelerated by Embree, and OIDN may reduce noise when that particular build supports it. Installed binary support must be inspected. Neither technique guarantees GPU-like performance.

For grounded natural movement, author an armature or bone rig, key contact points and scene constraints; use root motion, IK, foot planting, body weight transfer, overlapping action and hand-authored corrective frames. A skeleton animation is not automatically anatomically correct. The demo in this starter is a simple stylized 2D illustration; it is **not** an unconstrained text-to-video AI generator.

Resource note: A typical 1GB RAM Oracle VM is unsuitable for large CPU image diffusion models or the full MoneyPrinterTurbo stack. GitHub Actions CPU runners can run independent tests, but do not offer unlimited time/storage and disappear after the job. Use Actions artifacts to download completed demos. User-supplied content, model licensing and copyrights remain the user's responsibility.

Useful upstreams:
- https://github.com/leejet/stable-diffusion.cpp
- https://www.blender.org/
- https://www.synfig.org/
- https://github.com/harry0703/MoneyPrinterTurbo
- https://motioncanvas.io/
- https://www.remotion.dev/docs/license/pricing
