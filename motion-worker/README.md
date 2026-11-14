# Shared character and background workers

Oracle has a persistent native SprongMotion worker. One four-second prompt produces a Blender-compatible skeleton and a 24 fps pose track. A second machine may render the same clip. The generated body is projected onto the existing actor layer. Eyes, mouth, camera and object simulation retain their separate stages. Fingers and exact hand-to-prop contacts need additional animation.

From the repository root on the configured host:

```sh
bash motion-worker/install.sh
python3 motion-worker/prepare.py 'A person steps sideways and throws both hands up in surprise' clips/surprise
/usr/bin/python3 kinetic-studio/film.py 'A ball bounces in the garden. The courier jumps.' episodes/garden-01 --motion-clip clips/surprise --motion-start 2
```

Use new clip and episode directories. Copy the entire clip directory to reuse motion on another machine. Use Blender with the BVH importer enabled. The CPU background workflow can also run on demand under GitHub Actions. It saves BVH, pose data and independent PNG plates. The default film renderer paints its procedural background unless a PNG is supplied with `--background-plate`. Background art uses a centered cover crop behind the animated character and foreground prop.

The optional ComfyUI API graph in `comfy-audio-api.json` accepts pre-aligned voice.wav, music.wav and effects.wav in ComfyUI/input. Send the parsed graph as the prompt field to the trusted ComfyUI instance's /prompt endpoint. The graph layers audio and saves the mix. Rhubarb can separately export phoneme cues with `rhubarb -f json -o cues.json voice.wav`. The current film mouth follows voice amplitude.
