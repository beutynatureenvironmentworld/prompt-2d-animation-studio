"""Headless Blender 2D production scene sanity test; no proprietary assets/models."""
import bpy, json, os
from pathlib import Path
base=Path(os.environ.get("RUNNER_TEMP","/tmp"))/"inkrig-blender-proof"
base.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.resolution_x=360
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.filepath=str(base/"original-2d-title.png")
scene.render.engine="BLENDER_WORKBENCH"
scene.render.film_transparent=False
scene.render.image_settings.color_mode="RGBA"
scene.view_settings.view_transform="Standard"
# Add genuine Grease Pencil data block if supported by this Blender build.
gp_created=False
try:
    if hasattr(bpy.data,"grease_pencils_v3"):
        pen=bpy.data.grease_pencils_v3.new("Original InkRig Grease Pencil")
        ob=bpy.data.objects.new("Editable 2D strokes",pen)
        scene.collection.objects.link(ob)
        gp_created=True
    elif hasattr(bpy.data,"grease_pencils"):
        pen=bpy.data.grease_pencils.new("Original InkRig Grease Pencil")
        ob=bpy.data.objects.new("Editable 2D strokes",pen)
        scene.collection.objects.link(ob)
        gp_created=True
except (TypeError,RuntimeError,AttributeError) as exc:
    print("Grease Pencil API unavailable in selected distro Blender build",type(exc).__name__)
# Proper 2D text object to prove viewport and scene exports work.
data=bpy.data.curves.new("Funny 2D action","FONT")
data.body="INK RIG!"
data.size=1.2
obj=bpy.data.objects.new("Title - original 2D cartoon",data)
scene.collection.objects.link(obj)
obj.location=(-2,0,0)
camera_data=bpy.data.cameras.new("2D Ortho")
camera=bpy.data.objects.new("2D Camera",camera_data)
scene.collection.objects.link(camera)
camera.location=(0,0,10)
camera_data.type="ORTHO"
camera_data.ortho_scale=6
scene.camera=camera
bpy.ops.wm.save_as_mainfile(filepath=str(base/"original-2d-animation-scene.blend"))
bpy.ops.render.render(write_still=True)
assert (base/"original-2d-animation-scene.blend").stat().st_size>1000
assert (base/"original-2d-title.png").stat().st_size>1000
report={"blender_version":bpy.app.version_string,"grease_pencil_created":gp_created,
        "two_d_scene_saved":True,"rendered_png":True,
        "gpu_model_inference":False,"note":"Blender headless 2D editing/render smoke test, not cartoon video or AI generation"}
(base/"blender-validation.json").write_text(json.dumps(report,indent=2)+"\n")
print("BLENDER_REAL_HEADLESS_2D_SCENE_OK",report)
