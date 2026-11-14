"""Tiny CPU-only Blender render to validate optional Cycles toolchain."""
import bpy
from pathlib import Path
from mathutils import Vector

scene=bpy.context.scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene.render.engine="CYCLES"
scene.cycles.device="CPU"
scene.cycles.samples=2
scene.view_layers[0].cycles.use_denoising=False
scene.render.resolution_x=320
scene.render.resolution_y=180
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.threads_mode="FIXED"
scene.render.threads=2
scene.frame_start=1
scene.frame_end=3
scene.render.fps=8
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=(0,0,0))
ball=bpy.context.object
for fr,z in ((1,0),(2,.45),(3,.1)):
    ball.location.z=z
    ball.keyframe_insert(data_path="location",frame=fr)
bpy.ops.object.camera_add(location=(0,-5,1.7))
camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.type="ORTHO"
camera.data.ortho_scale=4
scene.camera=camera
bpy.ops.object.light_add(type="AREA",location=(1,-2,4))
bpy.context.object.data.energy=400
root=Path(__file__).resolve().parent/"out"/"blender-smoke"
root.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(root/"frame_")
bpy.ops.render.render(animation=True)
print("BLENDER_CPU_FRAMES_OK")
