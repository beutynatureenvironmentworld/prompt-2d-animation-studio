# Shared character and background workers

Oracle has a persistent native SprongMotion worker. One four-second prompt produces a Blender-compatible skeleton and a 24 fps pose track. A second machine may render the same clip. The generated body is projected onto the existing actor layer. Eyes, mouth, camera and object simulation retain their separate stages. Fingers and exact hand-to-prop contacts need additional animation.

From the repository root on the configured host:

```sh
bash motion-worker/install.sh
python3 motion-worker/prepare.py 'A person steps sideways and throws both hands up in surprise' clips/surprise
/usr/bin/python3 kinetic-studio/film.py 'A ball bounces in the garden. The courier jumps.' episodes/garden-01 --motion-clip clips/surprise --motion-start 2
```

Use new clip and episode directories. Copy the entire clip directory to reuse motion on another machine. Use Blender with the BVH importer enabled. The CPU background workflow can also run on demand under GitHub Actions. It saves BVH, pose data and independent PNG plates. The default film renderer paints its procedural background unless a PNG is supplied with `--background-plate`. Background art uses a centered cover crop behind the animated character and foreground prop.

The optional ComfyUI API graph in `comfy-audio-api.json` accepts pre-aligned voice.wav, music.wav and effects.wav in ComfyUI/input. Send the parsed graph as the prompt field to the trusted ComfyUI instance's /prompt endpoint. The graph layers audio and saves the mix. Rhubarb can separately export phoneme cues with `rhubarb -f json -o cues.json voice.wav`. The film renderer uses these timed mouth shapes when the Rhubarb executable is installed. Otherwise it follows voice amplitude. Set RHUBARB_BIN to override executable discovery.

To generate and composite in one Oracle command, supply one English story prompt. Optional motion and background prompts let you direct those workers separately.

```sh
python3 motion-worker/episode.py 'On a rooftop at night a clock falls and a courier jumps back in surprise.' episodes/alarm --motion 'A person jumps backward, throwing both forearms up' --background 'Ink cartoon rooftop at night, no people'
```

The final video is render/short.mp4 inside the chosen directory. Omit --background for the procedural scene, or pass --plate to reuse previous artwork. With --clip, the source clip directory must remain available for a later rerender. Commercial use of the selected SD Turbo model requires registration under its published Stability AI license.

## Measurements on the Oracle CPU host

The official Blender 4.2.0 binary rendered the 320×480 studio at 16 Cycles CPU samples with Embree and Open Image Denoise in 66.61 seconds. The system Blender 4.0.2 build includes Embree and lacks OIDN. The separate system Blender BVH importer produced 96 samples at 24 fps from a four-second generated clip.

A 256×256 SD 2.1 Turbo Q4_0 experiment at one Euler step and seed 42 saved a PNG. The CLI took 494.7 seconds with the model already downloaded. Text conditioning took 32.81 s, sampling took 104.69 s and VAE decoding took 319.64 s. Visual review found colored noise with no recognizable rooftop. Keep this profile experimental. The default GitHub compositor uses the Blender plate. Oracle's default uses the procedural painted scene. This measurement does not establish SDXL-Turbo, SDXS or GPU performance.
