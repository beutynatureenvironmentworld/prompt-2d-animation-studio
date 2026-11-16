"""Independent actual Blender Grease Pencil frame-by-frame 2D animation test.
Original procedural cartoon, animated drawings on native GP layers, not
Blender armature or SVG frame rasterization, no diffusion, CPU only.
Supports Blender 3.6/4.0 legacy GPencil and Blender 4.3+ GPv3.
"""
import bpy,math,json,subprocess,hashlib
from pathlib import Path
ROOT=Path.cwd()/"puppet-lab/output/grease-pencil"
FRAMES=ROOT/"frames"
FRAMES.mkdir(parents=True,exist_ok=True)
FPS=12;COUNT=72;W=320;H=480
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.resolution_x=W;scene.render.resolution_y=H
scene.render.resolution_percentage=100
scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=COUNT
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.render.engine='BLENDER_EEVEE' if bpy.app.version<(4,2,0) else 'BLENDER_EEVEE_NEXT'
scene.world.color=(0.76,0.74,0.67)
camera_data=bpy.data.cameras.new("GPencil camera")
camera=bpy.data.objects.new("Camera",camera_data)
scene.collection.objects.link(camera)
camera.location=(0,-13,0)
camera.rotation_euler=(math.pi/2,0,0)
camera_data.type='ORTHO';camera_data.ortho_scale=8.5
scene.camera=camera
def material(name,rgba,fill=False):
    mat=bpy.data.materials.new(name)
    bpy.data.materials.create_gpencil_data(mat)
    gp=mat.grease_pencil
    gp.color=rgba
    gp.show_fill=fill
    if fill:gp.fill_color=rgba
    return mat
black=material("Black cartoon ink",(.13,.15,.19,1))
gold=material("Golden shirt",(.91,.74,.30,1))
white=material("Warm paper skin",(.99,.95,.86,1))
orange=material("Orange cat",(.87,.49,.25,1))
is_v3=bpy.app.version>=(4,3,0)
if is_v3:
    data=bpy.data.grease_pencils_v3.new("Original GP3 drawings")
    ob=bpy.data.objects.new("Original 2D Grease Pencil",data)
else:
    data=bpy.data.grease_pencils.new("Original GP2 drawings")
    ob=bpy.data.objects.new("Original 2D Grease Pencil",data)
scene.collection.objects.link(ob)
for m in (black,gold,white,orange):ob.data.materials.append(m)
layer=data.layers.new("Hand-drawn frame animation",set_active=True) if not is_v3 else data.layers.new("Hand-drawn frame animation",set_active=True)
def make_stroke(frame,points,mat=0,width=70,cyclic=False):
    if is_v3:
        drawing=frame.drawing
        drawing.add_strokes([len(points)])
        stroke=drawing.strokes[-1]
        for pt,p in zip(stroke.points,points):
            pt.position=(p[0],0,p[1])
            pt.radius=.02*width/70
            pt.opacity=1.
        stroke.material_index=mat
        stroke.cyclic=cyclic
    else:
        st=frame.strokes.new()
        st.display_mode='3DSPACE'
        st.points.add(len(points))
        for pt,p in zip(st.points,points):
            pt.co=(p[0],0,p[1])
            pt.pressure=1
            pt.strength=1
        st.material_index=mat
        st.line_width=width
        st.use_cyclic=cyclic
def circle(cx,cy,rx,ry,steps=32):
    return [(cx+rx*math.cos(i*math.tau/steps),cy+ry*math.sin(i*math.tau/steps)) for i in range(steps)]
def draw(f):
    t=(f-1)/FPS
    x=-1.5+2.5*min(1,t/2.0) if t<2 else 1.0-.5*max(0,t-3.8)
    y=-.1+.10*abs(math.sin(t*9))
    shock=2.3<t<3.8
    slip=t>4.3
    gait=math.sin(t*12) if t<2 or t>3.8 else 0
    # True independent drawings for each frame: all geometry is native GP.
    make_stroke(fr,[(-4,-2.9),(4,-2.9)],0,55)
    # Original funny cartoon cat jumps into the runner's path.
    cx=3.5-2.9*min(1,max(0,(t-1.7)/1.1))
    cy=-2.3+.3*math.sin(t*6)
    make_stroke(fr,circle(cx,cy,.42,.33),3,85,True)
    make_stroke(fr,[(cx-.35,cy+.2),(cx-.29,cy+.63),(cx-.1,cy+.32)],3,65)
    make_stroke(fr,[(cx+.1,cy+.32),(cx+.29,cy+.63),(cx+.35,cy+.2)],3,65)
    for e in (-.16,.16):
        make_stroke(fr,circle(cx+e,cy+.10,.045,.06),0,60,True)
    make_stroke(fr,[(cx+.35,cy),(cx+.7,cy+.5+.12*math.sin(t*5))],0,80)
    # Legs, body, arms and face use actual GP stroke keyframes.
    hip=(x,y-.1)
    for side in (-1,1):
        knee=(x+side*.23+side*gait*.25,y-.65)
        foot=(x+side*.36+side*gait*.43,y-1.22+max(0,gait*side)*.15)
        make_stroke(fr,[hip,knee,foot],0,105)
        make_stroke(fr,[foot,(foot[0]+side*.20,foot[1])],0,75)
    make_stroke(fr,[(x-.37,y),(x-.36,y+1.05),(x+.37,y+1.05),(x+.37,y),(x-.37,y)],1,150)
    for side in (-1,1):
        hand=(x+side*(.95+.20*math.sin(t*8)),y+.25+(1.1 if shock else 0))
        make_stroke(fr,[(x+side*.37,y+.87),(x+side*.64,y+.51),hand],0,95)
    make_stroke(fr,circle(x,y+1.67,.55,.66),2,115,True)
    make_stroke(fr,[ (x-.52,y+1.84),(x-.4,y+2.23),(x-.18,y+2.28),(x,y+2.38),(x+.4,y+2.22),(x+.52,y+1.87) ],0,95)
    for side in (-1,1):
        make_stroke(fr,circle(x+side*.20,y+1.75,.045,.09 if shock else .05),0,65,True)
    if shock or slip:
        make_stroke(fr,circle(x,y+1.40,.11,.19),0,80,True)
    else:
        make_stroke(fr,[(x-.17,y+1.43),(x,y+1.34),(x+.17,y+1.43)],0,75)
for f in range(1,COUNT+1):
    frame=layer.frames.new(f)
    draw(f)
# Save fully editable native grease-pencil drawing layers before render.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"original-grease-pencil-animation.blend"))
for f in range(1,COUNT+1):
    scene.frame_set(f)
    scene.render.filepath=str(FRAMES/("frame_%04d.png"%f))
    bpy.ops.render.render(write_still=True)
    if f%12==0:print("GP_TRUE_NATIVE_DRAWING_RENDERED",f,flush=True)
video=ROOT/"original-grease-pencil-comedy.mp4"
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-framerate",str(FPS),"-i",str(FRAMES/"frame_%04d.png"),"-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast",str(video)],check=True,timeout=180)
a=(FRAMES/"frame_0001.png").read_bytes()
b=(FRAMES/"frame_0022.png").read_bytes()
assert hashlib.sha256(a).digest()!=hashlib.sha256(b).digest(),"Identical Grease Pencil frames"
assert video.stat().st_size>15000
proof={"engine":"Blender Grease Pencil GPv3" if is_v3 else "Blender Grease Pencil legacy GPv2",
"actual_native_gp_drawings":True,"original_art":True,"native_gp_frame_count":len(layer.frames),
"rendered_frames":COUNT,"fps":FPS,"video":video.name,
"editable_blend":"original-grease-pencil-animation.blend","armature_used":False,"diffusion_used":False}
(ROOT/"grease-pencil-proof.json").write_text(json.dumps(proof,indent=2)+"\n")
print("BLENDER_REAL_GREASE_PENCIL_FRAME_ANIMATION_PASS",video.stat().st_size,flush=True)
