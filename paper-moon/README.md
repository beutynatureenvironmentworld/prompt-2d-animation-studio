# Midnight Mail
A 69-second two-character episode. The CPU renderer keeps characters and lip timing consistent across shots. Each episode can supply new Python drawing and interaction code in staging.py. Story JSON is an authored shot plan, including object paths, camera, acting and dialogue.

Requirements: Python 3, Pillow, FFmpeg with flite and libx264, Linux, DejaVu Sans. No model or key is needed to replay the included episode.

    python3 episode.py story.json build

Edit/append shots and run the same command. Completed shots are cached using shot data, start time and renderer source. Changing shared drawing code invalidates cached shots. Each section is rendered independently so long episodes can resume. Keep disk space for scenes and joined video.

For a new story using your already configured OpenCode provider:

    python3 from_prompt.py "A paper boat sails through the room during a rainstorm. Tell the story in two minutes." rain-episode --model PROVIDER/MODEL

Authoring and rendering are separate. OpenCode writes new episode code and requires a working model. The supplied sample was authored by ChatGPT. Dialogue uses local English Flite voices and sound amplitude for lip opening. Image generation is optional; consistent recurring art is drawn from code. Master is 960x540 at 24 fps.
