"""Free prose -> constrained local LLM poses -> Blender animation -> Cairo MP4."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'kite'))
from rig_studio import BONES

CHANNELS = ('body','head','armL','handL','armR','handR','legL','legR')
ANGLE = '("-120" | "-90" | "-60" | "-30" | "0" | "30" | "60" | "90" | "120")'
GRAMMAR = '\n'.join([
    'root ::= pose "\\n" pose "\\n" pose "\\n" pose',
    'pose ::= angle "," angle "," angle "," angle "," angle "," angle "," angle "," angle',
    'angle ::= '+ANGLE])
INSTRUCTION = """You animate a front-facing 2D human, Mira. Read the story as motion.
Answer exactly four consecutive poses: preparation, middle, peak, recovery or hold.
Each line has eight joint angles, in this exact order:
torso,head,left shoulder,left elbow,right shoulder,right elbow,left thigh,right thigh.
0 is rest. Positive right shoulder raises the right arm outward; negative left
shoulder raises the left arm outward. For hands above the head use left shoulder
-120 and right 120. Elbows and head rotate relative to the parent. Negative
torso tilts right. Use 0 for limbs that should remain relaxed. Respect left
versus right and exaggerate silhouettes. Output only four CSV lines."""

def generate(prompt):
    runtime=Path(os.environ.get('MOTION_RUNTIME',HERE/'runtime'))
    cli=next(runtime.rglob('llama-cli'))
    model=runtime/'motion.gguf'
    examples = [
        ("Curl forward to examine a tiny flower, then straighten.", "0,-30,0,0,0,0,0,0\n-30,-30,0,0,30,-30,0,0\n-60,-30,0,0,60,-30,0,0\n0,0,0,0,0,0,0,0"),
        ("Stretch both arms toward opposite sides and hold.", "0,0,-30,0,30,0,0,0\n0,0,-60,0,60,0,0,0\n0,0,-90,0,90,0,0,0\n0,0,-90,0,90,0,0,0"),
        ("Shield your eyes with your left elbow, then relax.", "0,0,-30,-30,0,0,0,0\n30,-30,-90,-90,0,0,0,0\n30,-30,-120,-90,0,0,0,0\n0,0,-30,0,0,0,0,0")]
    turns=''.join('<|im_start|>user\n'+q+'<|im_end|>\n<|im_start|>assistant\n'+a+'<|im_end|>\n' for q,a in examples)
    chat='<|im_start|>system\n'+INSTRUCTION+'<|im_end|>\n'+turns+'<|im_start|>user\n'+prompt+'<|im_end|>\n<|im_start|>assistant\n'
    run=subprocess.run([str(cli),'-m',str(model),'-p',chat,'--grammar',GRAMMAR,
        '-b','32','-ub','16','-n','220','-c','1024','-t','2','--temp','0.65','--seed','19',
        '--no-display-prompt','-no-cnv','--simple-io','--no-warmup'],
        capture_output=True,text=True,timeout=240)
    if run.returncode: raise RuntimeError(run.stderr[-1500:])
    import re
    rows=re.findall(r'(?m)^\s*(-?\d+(?:,-?\d+){7})\s*$',run.stdout.replace('[end of text]',''))
    poses=[list(map(int,row.split(','))) for row in rows]
    if len(poses)!=4 or len(set(map(tuple,poses)))<2:
        raise ValueError('Model returned incomplete or static poses: '+run.stdout[-400:])
    return poses

def bake(folder):
    import bpy
    story=json.loads((folder/'motion.json').read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_end=121
    rigs={}
    for index,name in enumerate(('mira','ravi')):
        data=bpy.data.armatures.new(name)
        rig=bpy.data.objects.new(name,data);scene.collection.objects.link(rig)
        bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
        for label,(a,b,parent) in BONES.items():
            bone=data.edit_bones.new(label);bone.head=(*a,0);bone.tail=(*b,0)
            if parent: bone.parent=data.edit_bones[parent]
        bpy.ops.object.mode_set(mode='OBJECT');rig.location.x=index*110;rigs[name]=rig
        for f,angles in zip((1,25,54,86,121),[[0]*8]+story['poses']):
            for label,angle in zip(CHANNELS,angles):
                bone=rig.pose.bones[label];bone.rotation_mode='XYZ'
                bone.rotation_euler.z=math.radians(angle if name=='mira' else 0)
                bone.keyframe_insert(data_path='rotation_euler',index=2,frame=f)
    scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'motion.blend'))
    frames=[]
    for f in range(1,122):
        scene.frame_set(f)
        frames.append({n:{b.name:[[round(v,3) for v in point[:2]] for point in (b.head,b.tail)] for b in r.pose.bones} for n,r in rigs.items()})
    (folder/'poses.json').write_text(json.dumps(frames,separators=(',',':')))

if __name__=='__main__':
    if '--' in sys.argv:
        bake(Path(sys.argv[-1]))
    else:
        from rig_studio import composite
        p=argparse.ArgumentParser();p.add_argument('prompt');p.add_argument('folder',type=Path)
        p.add_argument('--width',type=int,choices=(640,1280,1920),default=1280)
        args=p.parse_args()
        if not 1<=len(args.prompt.strip())<=1200: p.error('Enter 1 to 1200 characters')
        out=args.folder.resolve();out.mkdir(parents=True,exist_ok=False)
        poses=generate(args.prompt)
        (out/'motion.json').write_text(json.dumps(dict(prompt=args.prompt,channels=CHANNELS,poses=poses),ensure_ascii=False,indent=2))
        subprocess.run(['blender','-b','-t','2','--python-exit-code','1','-P',str(Path(__file__).resolve()),'--',str(out)],check=True)
        composite(out,[('mira','generated',121)],args.width)
