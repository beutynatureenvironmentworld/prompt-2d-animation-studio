# The Snore Collector

A silent 15-second original portrait cartoon. Node generates procedural SVG, Python calls the system librsvg/Cairo libraries, and FFmpeg streams H.264. No API key is needed to render. The shot descriptions and timing live in story.json. An author or coding agent follows DIRECTOR.md to adapt the drawings and staging to a new story.

On Ubuntu install nodejs, python3, librsvg2-2 and ffmpeg. From this folder:

    python3 render.py story.json short.mp4

To edit the React/Remotion version install Node 22 and run npm install, then npm run studio or npm run render. Both renderers use art.cjs.

For Blender 4 on Linux, generate transparent layer sequences then build the editable scene. Keep those PNG sequences with the blend file.

    python3 render.py story.json layers --layers --width 540 --fps 24
    blender -b --python-exit-code 1 -P build_blender.py -- 24 layers room.blend

Change the final frame format/output with Blender's normal render settings. Layers, physical depth, camera keys, area light and volume are editable. The distributed MP4 uses the SVG render. Blender uses a perspective camera so its framing can differ. Add shots by matching the previous camera and character end poses; keep the same absolute animation clock for continuing motion. The included camera and prop cues are specific to this short. No audio assets, generated voices, advertising or publishing credentials are required.
