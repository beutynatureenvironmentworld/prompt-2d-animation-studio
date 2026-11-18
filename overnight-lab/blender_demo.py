"""Flat orthographic Blender code-only animation. No video diffusion, no neural generation."""
import bpy, math
from pathlib import Path
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.render.engine="BLENDER_WORKBENCH"
s.display.shading.light="FLAT"
s.display.shading.color_type="OBJECT"
s.display.shading.background_type="WORLD"
s.world.color=(0.95,0.89,0.76)
s.render.resolution_x=360
s.render.resolution_y=640
s.render.resolution_percentage=100
s.render.fps=12
s.frame_start=1
s.frame_end=36
s.render.image_settings.file_format="PNG"
s.render.filepath="//overnight-lab/out/blender_frames/frame_"

def disk(name,x,y,rx,ry,rgb):
    bpy.ops.mesh.primitive_circle_add(vertices=48,fill_type="NGON",location=(x,y,0))
    o=bpy.context.object
    o.name=name
    o.scale=(rx,ry,1)
    o.color=(*rgb,1)
    return o

def box(name,x,y,rx,ry,rgb):
    bpy.ops.mesh.primitive_plane_add(size=2, location=(x,y,-0.05))
    o=bpy.context.object
    o.name=name
    o.scale=(rx,ry,1)
    o.color=(*rgb,1)
    return o

white=(0.98,0.98,0.98)
black=(0.025,0.025,0.04)
box("girl_dress",-0.9,-0.8,0.38,0.48,(0.95,0.3,0.45))
box("boy_shirt",0.9,-0.8,0.38,0.48,(0.35,0.62,1.0))
for name,x in [("girl",-0.9),("boy",0.9)]:
    disk(name+"_head",x,0.30,0.45,0.47,black)
    disk(name+"_face",x,0.30,0.42,0.44,white)
    for delta in (-0.17,0.17):
        disk(name+"_eye"+str(delta),x+delta,0.35,0.04,0.08,black)
    disk(name+"_mouth",x,0.02,0.12,0.045,black)
disk("left_pigtail",-1.38,0.58,0.19,0.17,white)
disk("right_pigtail",-0.42,0.58,0.19,0.17,white)
box("sealed_carton",0.04,-0.14,0.35,0.30,white)
box("milk_label",0.04,-0.14,0.18,0.07,(0.25,0.66,1))
straw=box("straw",-0.45,-0.08,0.20,0.04,(0.78,0.91,1))
jet=box("milk_jet",-0.53,-0.08,0.02,0.04,(0.94,0.98,1))
for frame in (1,10,15,25,36):
    s.frame_set(frame)
    bend={1:0.01,10:0.01,15:0.20,25:0.46,36:0.01}[frame]
    jet.scale.x=max(0.03,bend*2.8)
    jet.location.x=-0.55-bend
    jet.keyframe_insert(data_path="scale",frame=frame)
    jet.keyframe_insert(data_path="location",frame=frame)
    head=bpy.data.objects["girl_head"]
    head.location.y=0.3+0.07*math.sin(frame/4)
    head.keyframe_insert(data_path="location",frame=frame)
bpy.ops.object.camera_add(location=(0,0,12))
cam=bpy.context.object
cam.data.type="ORTHO"
cam.data.ortho_scale=7.2
s.camera=cam
s.render.filepath=str(Path.cwd()/"overnight-lab/out/blender_frames"/"frame_")
Path("overnight-lab/out/blender_frames").mkdir(parents=True,exist_ok=True)
bpy.ops.render.render(animation=True)
print("BLENDER_ORTHOGRAPHIC_FRAMES",s.frame_end)
