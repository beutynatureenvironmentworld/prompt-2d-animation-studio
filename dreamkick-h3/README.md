# Funny Toon Ever — Dream Kick → Bedroom Crash (MiniMax H3 experimental)

This is a **private Kaggle GPU submission** for two 5-second portrait shots using the MiniMax H3 Singularity Ref2VA INT8 model and the pinned Turbo adapter from [celunah/kaggle_h3](https://github.com/celunah/kaggle_h3). It is **not** a claim that H3 actually rendered successfully.

## Scene choreography
1. A pigtail cartoon girl runs toward a GREEN soccer ball with a sly grin, winds her leg back and kicks. The last frame holds the extended leg.
2. Match cut to a nighttime bedroom: same girl sleeping, extends the same leg, kicks the bald cartoon boy sleeping beside her, launches him off the bed; shock, crash, dizzy reaction.

Final target is 9:16, 540×960 and H264/AAC with original comedy SFX, ambient sound and bottom lowercase **funnytoonever** watermark. **Never add vid.best.**

## How to run
1. GitHub repository variable: KAGGLE_USERNAME
2. GitHub repository secret: KAGGLE_API_TOKEN. Never paste token into chat or source files.
3. GitHub Actions workflow **Funny Toon Ever — Dream Kick Kaggle H3** can submit ONE PRIVATE notebook via the explicitly guarded \`gpu-submit-once:\` commit trigger on \`feature/fte-dreamkick-kaggle-h3\`. A new run is not automatically submitted on every push.
4. The notebook clones only public source code, uses Kaggle-allocated GPU(s) and public H3 weights; total model loading may take substantial time. No public ComfyUI tunnel.
5. The private Kaggle output folder \`FTE_H3_Dream_Kick\` contains \`RESULT.json\`, source MP4s (when genuinely generated) and \`Funny_Toon_Ever_Dream_Kick_ACTUAL_H3.mp4\` **only after both shots succeed**.
6. GPU is a genuine experiment. T4×2 are two separate ~16GB devices—not one pooled 32GB card. OOM, missing models, dependency problems and Kaggle queues are possible. Do not misrepresent a submitted job as completed.

## CPU fallback
A separate **11.4s 540×960, 24fps** source-driven cartoon episode was rendered locally and checked with FFprobe. It is explicitly labelled CPU, not H3, and is downloadable in the conversation. Keep the original CPU fallback if H3 cannot fit the available VRAM.

## Rendering and permissions
This project uses the user-provided illustrated concept only as *reference direction*, not an exact tracing or a guarantee that all characters remain pixel-identical. H3 uses simple programmatic stills for visual conditioning and generates its own video frames. No copyrighted SFX are downloaded; audio in the final concatenated episode is synthesized from code, while original H3 scene outputs may retain their native generated audio. A human must review final continuity, shoulder geometry and the exact kick-to-kick cut. No output is automatically uploaded to YouTube or TikTok.
