# Funny Toon Ever Audio Director (independent of ComfyUI)

Frame/second-aligned generated SFX, optional prerecorded expressive voice WAV files and an arbitrary existing MP4 are mixed by **FFmpeg**, checked by **ffprobe**, no GPU and no browser. Safe baseline for Oracle Cloud Always Free 1GB. FFmpeg can remux video (video stream copy), requiring less RAM than decoding/re-encoding every frame. Python standard library generates deterministic non-licensed-by-others demo noises. They are illustrative synthesized effects, *not* natural human speech or ML-generated sound effects.

```bash
sudo apt-get install -y ffmpeg
python3 audio-director/sound_director.py --video existing.mp4 --cues audio-director/demo_cues.json --output FTE_Sound_Mixed.mp4 --work audio-director/output
```

Cue keys: `at_seconds` or `at_fraction` (timeline), `sfx` procedural kind or `file` pointing to a WAV file, and `volume`. For natural narration, generate a voice track separately (e.g. Kokoro-82M Apache 2.0 or Resemble Chatterbox MIT, using suitable authorized voice); then specify that file as an event; generated voice must be decoded and its own license checked. No claim of natural TTS unless WAV really exists.

Preferred architecture: **Blender/Grease Pencil (character design, physical contact/IK, animation)** + **Python keyframe timing** + **FFmpeg audio and render**. Optionally use Remotion for cards/graphics on GitHub Actions, but Remotion has conditional commercial licensing and uses a headless browser. OpenToonz and Synfig are alternative character-animation tools; not automatically installed in tiny Oracle 1GB VM. AudioLDM2 weights are noncommercial; Stable Audio Open has a conditional Stability AI Community license, and free Hugging Face GPU access must not be assumed. Keep high-resolution video encoding on GitHub Actions rather than overloading Oracle 1GB RAM.
