# Funny Toon Ever: Wrong Door — custom prompt short

Uses the user's **original permanent black-and-white 6-pose sheet**. A simple **offline bounded storyboard** maps the supplied prompt into a tested 8.85-second comedy beat, using original whole-body poses (not a regenerated or retouched character). 360x640, 24fps, H.264/AAC; spatial sprint, door opening, knock bursts, slip, punchline, original synthesized sound.

## Reproduce

```bash
python -m pip install Pillow opencv-python-headless numpy
sudo apt-get install -y ffmpeg
python story_engine.py --source path/to/permanent_mascot.webp --prompt 'Funny Toon mascot runs to the toilet, knocks, gets surprised, slips, recovers' --output my_video.mp4
```

This is **not** unconstrained LLM video generation and not complete skeletal rigging. `parse_prompt()` currently supports a limited action recognition vocabulary but executes a single authored seven-beat storyboard. The source poses all have a grin, including the surprised pose, and the user's extra-pupil concern has **not** been visually repaired. Door contact is staged rather than hand-pose IK; it can be improved in later QA loops. Full original source remains unchanged.