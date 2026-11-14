# Kite scene
Make silent 2D cartoons with an articulated cast in a layered landscape. Open Actions → Render a silent cartoon → Run workflow. Enter stage directions and download the silent-cartoon artifact after the job finishes.

Use semicolons between beats. Each beat accepts Mira or Ravi, then walk, wave, jump or watch. Mira also holds the kite and can fly or pull it. Walk accepts left or right. Add a duration such as 2s at the end of any beat. Unknown directions report an error. There is no model download or API key.

Example: Mira walks right; Ravi waves; Mira flies; Ravi jumps; Mira pulls; Mira waves

On Ubuntu install python3-cairo and ffmpeg, then run from the repository root:

```sh
/usr/bin/python3 kite/animate.py 'Ravi jumps; Mira walks left' first.mp4
/usr/bin/python3 kite/animate.py 'Mira අත වනන්න; Mira flies' extended.mp4 --extend first.json
```

Extension re-renders the original timeline and the added beats with the same cast and coordinates. Keep the JSON file. Default output is 1920×1080 at 24 fps. Set --width 640 for a small preview. The current vocabulary and illustrated scene are built in. New characters, props and movements require extending the renderer.
