# Advanced 2D + AI anime stack

Actual installed-and-executed GitHub Actions workflow performs:
- Blender: installed; an original 2D scene with an editable 2D text object and Grease Pencil data block (if compatible) saved to .blend, one headless PNG render; **not** a fully animated Grease Pencil sequence.
- Synfig CLI: installed and verified; does not yet render from an editable Synfig scene.
- Rhubarb Lip Sync 1.14.0: downloaded verified official release, executed on original \`espeak-ng\` synthesized dialogue; resulting viseme timing saved as JSON. Rig mouth mapping is a future integration, not falsely marked complete.
- FFmpeg: installed and verified; full 11.5-second InkRig animation rendered in a separate proven workflow.
- Official ComfyUI, LTX-Video, Wan2.1, ToonCrafter repositories: **source checkouts only** with no large checkpoint downloads, GPU inference or claims of free VRAM.

Why: Full-sized Wan 14B and newer video diffusion checkpoints cannot simply be run on a GitHub Actions CPU virtual machine. Kaggle T4 is a separate GPU service; model size/VRAM must be verified before installation. Prioritize a feasible lower-memory LTX-Video 2B distilled workflow once a real Kaggle GPU is scheduled. Hugging Face can store licensed model weights in a scoped private dataset, not necessarily necessary for public Hub downloads. AI Horde volunteer workers currently returned image frames, not coherent video.

Sources: https://docs.blender.org/manual/en/latest/grease_pencil/introduction.html, https://github.com/DanielSWolf/rhubarb-lip-sync, https://github.com/Lightricks/LTX-Video .
