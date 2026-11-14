"""Render an atmospheric cartoon-studio background with the Cycles CPU backend."""
import os
import sys
import time
import bpy
import _cycles
from mathutils import Vector

output = sys.argv[sys.argv.index("--")+1]
scene = bpy.context.scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
if not _cycles.with_embree or not _cycles.with_openimagedenoise:
    raise RuntimeError("Use the official Blender Linux build with Embree and OIDN")
def box(name, pos, scale, color):
    bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    obj.data.materials.append(mat)
def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
box("Stage",(0,0,-.15),(8,8,.15),(.13,.19,.29))
box("Night wall",(0,3,2),(8,.12,3),(.12,.20,.32))
for x in (-2,0,2):
    box("Window",(x,2.80,2.5),(.8,.04,1.2),(.38,.67,.88))
    box("Mullion",(x,2.72,2.5),(.035,.05,1.2),(.07,.11,.21))
box("Bench",(0,1,.7),(1.4,.45,.13),(.74,.31,.14))
for x in (-1,1):
    box("Leg",(x,1,.32),(.08,.33,.32),(.17,.12,.16))
bpy.ops.object.light_add(type="AREA",location=(1,-2,5))
lamp=bpy.context.object
lamp.data.energy=650
lamp.data.shape='DISK'
lamp.data.size=3
aim(lamp,(0,0,0))
bpy.ops.object.camera_add(location=(3,-7,3))
scene.camera=bpy.context.object
aim(scene.camera,(0,1,1.5))
scene.render.resolution_x=320
scene.render.resolution_y=480
scene.render.resolution_percentage=100
scene.render.filepath=os.path.abspath(output)
start=time.monotonic()
bpy.ops.render.render(write_still=True)
print(f"Cycles CPU / Embree / OIDN: 16 samples, 320x480, {time.monotonic()-start:.2f}s")
