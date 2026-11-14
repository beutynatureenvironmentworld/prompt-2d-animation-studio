# Free prose to motion

Run the **Free text to character motion** workflow, or on the configured Oracle host:

```sh
cd /home/ubuntu/vidbest-ai-engine
/usr/bin/python3 free-motion/prompt_motion.py "Mira leans to one side and draws her right elbow across her face." free-motion/my-gust --width 640
```

Use a fresh output directory each time. On a new x86_64 Ubuntu worker run `bash free-motion/install.sh` first. It downloads a quantized Qwen2.5 0.5B model. Each job starts a private, temporary localhost llama.cpp process, requests four sets of joint angles, then stops inference before Blender starts. No hosted inference API or API key.

The model reads ordinary English. It controls Mira’s eight planar joints with angles spaced at 30 degrees. Blender interpolates them over 121 frames. Ravi remains a spectator. Fingers, props, changing locations, locomotion and multi-actor interactions require additional rig controls. Generation quality and left/right consistency vary. Static or malformed sequences fail explicitly. See `motion.json` for the actual generated poses, `motion.blend` for keyframes and `cartoon.mp4` for the silent render.