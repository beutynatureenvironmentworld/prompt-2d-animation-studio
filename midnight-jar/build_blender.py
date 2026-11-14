"""Build a movable layered diorama. Run with blender -b -P build_blender.py -- FPS LAYERS FILE."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
fps=int(args[0]);layers=Path(args[1]).resolve();out=Path(args[2]).resolve()
story=json.loads((root/'story.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=2;sc.cycles.use_denoising=False
sc.view_settings.view_transform='Standard'
sc.render.resolution_x=1080;sc.render.resolution_y=1920;sc.render.resolution_percentage=100;sc.render.fps=fps
sc.frame_end=round(sum(s['seconds'] for s in story['shots'])*fps)
bpy.ops.object.camera_add(location=(0,0,12))
cam=bpy.context.object;sc.camera=cam;cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=32;cam.data.lens=48
for i,(name,z) in enumerate(zip(('Room','Moonbeam','Sleeper and far bed','Roommate and jar','Snore lettering'),(-1,-.72,-.34,0,.02))):
    imgpath=layers/str(i)/'00001.png'
    if len(list(imgpath.parent.glob('*.png')))!=sc.frame_end: raise ValueError(f'Missing frames: {name}')
    height=(12-z)*32/48
    bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,z))
    obj=bpy.context.object;obj.name=name;obj.scale=(height*9/16,height,1)
    mat=bpy.data.materials.new(name);obj.data.materials.append(mat);mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear();link=mat.node_tree.links.new
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(imgpath));tex.image.source='SEQUENCE'
    tex.image_user.frame_duration=sc.frame_end;tex.image_user.use_auto_refresh=True
    em=nodes.new('ShaderNodeEmission');link(tex.outputs['Color'],em.inputs['Color'])
    mix=nodes.new('ShaderNodeMixShader');link(tex.outputs['Alpha'],mix.inputs[0])
    link(nodes.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[1]);link(em.outputs[0],mix.inputs[2])
    link(mix.outputs[0],nodes.new('ShaderNodeOutputMaterial').inputs['Surface'])
# An editable cone of participating media adds a faint shaft from the window.
bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.72,radius2=.10,depth=4,location=(.72,1.4,.65))
cone=bpy.context.object;cone.name='Moonlit haze';cone.rotation_euler=Vector((.72,1,.15)).to_track_quat('Z','Y').to_euler()
fog=bpy.data.materials.new('Thin moonlit air');cone.data.materials.append(fog);fog.use_nodes=True
nt=fog.node_tree;nt.nodes.clear();vol=nt.nodes.new('ShaderNodeVolumeScatter');vol.inputs['Density'].default_value=.013
nt.links.new(vol.outputs[0],nt.nodes.new('ShaderNodeOutputMaterial').inputs['Volume'])
bpy.ops.object.light_add(type='AREA',location=(2.5,3.4,2.4));light=bpy.context.object
light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=55;light.data.color=(.67,.75,1)
start=1
for s in story['shots']:
    for f,k in ((start,0),(start+round(s['seconds']*fps)-1,3)):
        x,y,zoom=s['camera'][k:k+3];cam.location=(-x*.008,y*.008,12/zoom)
        cam.keyframe_insert('location',frame=f)
    start+=round(s['seconds']*fps)
sc.frame_set(1);sc.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(out),relative_remap=True)
