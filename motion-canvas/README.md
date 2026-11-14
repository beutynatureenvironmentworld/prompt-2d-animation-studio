# Optional Motion Canvas visual editing playground

This is a SECOND, separately authored TypeScript cartoon scene for editing/previewing manually. **It is NOT the render engine used by the Python prompt-to-MP4 CLI**, and importing a user photo does not generate a rig.

Run in this folder after installing Node.js 20+:

    npm install
    npm run typecheck
    npm run build
    npm start

Open the URL printed by Vite (typically localhost). Adjust reusable poses, shapes, easing and scene timing in src/scenes/bedroom.tsx. Motion Canvas is MIT-licensed; check its own dependencies. The top-level package versions are exact; a package-lock is currently NOT committed, so transitive dependency reproducibility remains a known issue. Do not claim editor tests passed unless the GitHub Motion Canvas CI workflow completed successfully.

For headless/cloud automation, use the repository's tested Python + FFmpeg flow; Motion Canvas's usual FFmpeg exporter is editor-driven. Revideo is another possible headless TypeScript backend but is NOT installed/integrated in this repo. The provided image/video was reference inspiration only.
