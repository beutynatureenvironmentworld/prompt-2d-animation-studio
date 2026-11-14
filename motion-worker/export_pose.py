"""Run inside Blender. Sample the BVH on the renderer's 24 fps timeline."""
import json
import sys
from pathlib import Path

import bpy

source, target = map(Path, sys.argv[sys.argv.index("--") + 1:])
scene = bpy.context.scene
scene.render.fps = 24
bpy.ops.import_anim.bvh(filepath=str(source.resolve()), global_scale=1,
                        use_fps_scale=True, rotate_mode='NATIVE', frame_start=1)
rig = bpy.context.object
bones = rig.pose.bones
names = ["pelvis", "neck", "head"] + [
    side + "_" + joint for side in ("l", "r")
    for joint in ("shoulder", "elbow", "wrist", "hip", "knee", "ankle", "foot")]
action = rig.animation_data.action
frames = []
for frame in range(1, round(action.frame_range[1]) + 1):
    scene.frame_set(frame)
    frames.append({name: list(rig.matrix_world @ bones[name].head) for name in names})
target.write_text(json.dumps({"fps": 24, "frames": frames}, separators=(",", ":")))
