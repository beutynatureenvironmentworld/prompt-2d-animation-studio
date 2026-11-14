# Lantern Catch

A prompt-directed, CPU-rendered full-body character study. The shoulders, forearms, trousers and shoes have volume. A two-segment inverse-kinematics solver positions elbows and knees. Foot targets stay fixed during planted beats; two separate grips track the lantern. Four depth planes respond differently to the camera. Blinks and voice-driven mouth openings run independently. Audio combines original dialogue synthesized with local Flite and procedural chimes.

Replay on Linux with Node 18+, Python 3, librsvg2, Cairo and FFmpeg with Flite:

    python3 film.py story.json lantern.mp4

Render a lightweight preview by adding `--width 320`. Edit story.json to change lines and major timing marks; scene.cjs sends each generated SVG frame to the rasterizer. art.cjs contains this episode's character and staging.

For a different story, use a configured OpenCode model and a fresh output folder:

    python3 from_prompt.py "A dancer balances a parcel in the rain." rain --model PROVIDER/MODEL

The coding model authors new artwork and motion code; run trusted story-authoring jobs in a dedicated workspace. Model access and quality depend on the configured provider. This example's staging was authored by ChatGPT. Replay needs no remote model, account or GPU.
