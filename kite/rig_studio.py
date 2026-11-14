"""Blender NLA choreography with a lightweight Cairo cartoon compositor."""
import json
import math
import re
import sys
from pathlib import Path

ACTIONS = ('idle','watch','point','wave','bow','cheer','jump','clap','reach','nod','dance','walk')
WORDS = {'points':'point','waves':'wave','bows':'bow','cheers':'cheer','jumps':'jump','claps':'clap',
         'reaches':'reach','nods':'nod','dances':'dance','walks':'walk','watches':'watch',
         'අත වනන්න':'wave','පනින්න':'jump','නටන්න':'dance','අත්පුඩි ගහන්න':'clap','ඇවිදින්න':'walk'}
BONES = {'body':((0,0),(0,32),None),'head':((0,32),(0,53),'body')}
for side, sign in [('L',-1),('R',1)]:
    BONES['arm'+side]=((sign*11,28),(sign*17,12),'body')
    BONES['hand'+side]=((sign*17,12),(sign*20,-3),'arm'+side)
    BONES['leg'+side]=((sign*7,0),(sign*8,-17),'body')
    BONES['foot'+side]=((sign*8,-17),(sign*9,-32),'leg'+side)

def directions(prompt):
    result=[]
    for clause in re.split(r';|\n|\s+then\s+|\s+ඊළඟට\s+',prompt.strip().lower()):
        m=re.fullmatch(r'\s*(mira|ravi|මීරා|රවි)\s+(.+?)\s*[.!]?\s*',clause)
        if not m: raise ValueError('Use Mira or Ravi before each action: '+clause)
        verb=re.fullmatch(r'(.+?)(?:\s+([0-9]+(?:\.[0-9]+)?)s)?',m[2])
        action=WORDS.get(verb[1],verb[1]); seconds=float(verb[2] or 1.6)
        if action not in ACTIONS or not .5<=seconds<=12: raise ValueError('Unsupported direction: '+clause)
        result.append(({'මීරා':'mira','රවි':'ravi'}.get(m[1],m[1]),action,round(seconds*24)))
    if sum(b[2] for b in result)>2880: raise ValueError('Maximum scene duration is 120 seconds')
    return result

def pose(action,u):
    e=math.sin(math.pi*u)**1.2
    s=math.sin(4*math.pi*u); c=math.cos(4*math.pi*u)
    p={}; height=0
    if action=='point': p={'armR':80,'handR':-7,'head':-8,'body':-6}
    if action=='reach': p={'armR':112,'handR':-14,'armL':-27,'body':-12}
    if action=='wave': p={'armR':112,'handR':36+23*s,'head':5}
    if action=='bow': p={'body':-27,'head':-18,'armR':-12,'handR':-47}
    if action=='cheer': p={'armR':130,'armL':-135,'handR':20,'handL':-20};height=4*e
    if action=='jump':
        height=35*math.sin(math.pi*u)**3-4*math.sin(2*math.pi*u)**2
        p={'armL':-106,'armR':118,'legL':-25,'footL':47,'legR':17,'footR':-37}
    if action=='clap': p={'armR':-40-13*c,'handR':-100,'armL':40+13*c,'handL':100}
    if action=='nod': p={'head':-12+9*c}
    if action=='dance': p={'body':9*s,'head':-12*s,'armR':75+45*s,'armL':-75+42*s,'legR':18*s,'legL':-18*s};height=4*abs(s)*e
    if action=='walk': p={'legL':36*s,'legR':-36*s,'footL':-19*max(0,s),'footR':-19*max(0,-s),'armR':29*s,'armL':-29*s};height=2*abs(s)*e
    if action=='watch': p={'head':8,'body':3}
    if action=='idle': p={'head':2,'body':1}
    return {k:math.radians(v*e) for k,v in p.items()},height

def blender_build(folder,beats):
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.fps=24
    rigs={}
    for name in ('mira','ravi'):
        data=bpy.data.armatures.new(name); rig=bpy.data.objects.new(name,data)
        scene.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig
        bpy.ops.object.mode_set(mode='EDIT')
        for label,(a,b,parent) in BONES.items():
            bone=data.edit_bones.new(label);bone.head=(*a,0);bone.tail=(*b,0)
            if parent: bone.parent=data.edit_bones[parent]
        bpy.ops.object.mode_set(mode='OBJECT');rig.animation_data_create();rigs[name]=rig
        for bone in rig.pose.bones: bone.rotation_mode='XYZ'
    maker=rigs['mira'];library={}
    for verb in ACTIONS:
        act=bpy.data.actions.new(verb);act.use_fake_user=True;maker.animation_data.action=act
        for frame in range(1,50,2):
            angles,dy=pose(verb,(frame-1)/48)
            for bone in maker.pose.bones:
                bone.rotation_euler.z=angles.get(bone.name,0)
                bone.keyframe_insert(data_path='rotation_euler',index=2,frame=frame,group=bone.name)
            root=maker.pose.bones['body'];root.location.y=dy;root.keyframe_insert(data_path='location',index=1,frame=frame)
        library[verb]=act;maker.animation_data.action=None
    for j,(name,rig) in enumerate(rigs.items()):
        rig.location.x=j*110
        track=rig.animation_data.nla_tracks.new();track.name='Choreography'
        frame=1
        for actor,verb,n in beats:
            action=library[verb if actor==name else 'idle']
            strip=track.strips.new(action.name,frame,action);strip.scale=n/48;strip.extrapolation='NOTHING'
            frame+=n
    scene.frame_end=frame-1;scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'choreography.blend'))
    frames=[]
    for frame in range(1,scene.frame_end+1):
        scene.frame_set(frame)
        frames.append({name:{b.name:[[round(v,3) for v in point[:2]] for point in (b.head,b.tail)] for b in rig.pose.bones} for name,rig in rigs.items()})
    (folder/'poses.json').write_text(json.dumps(frames,separators=(',',':')))

def composite(folder,beats,width):
    import subprocess
    import cairo
    import animate as art
    frames=json.loads((folder/'poses.json').read_text())
    height=width*9//16;surface=cairo.ImageSurface(cairo.FORMAT_RGB24,width,height)
    g=cairo.Context(surface);art.g=g;g.scale(width/800,height/450)
    g.set_line_cap(cairo.LINE_CAP_ROUND);g.set_line_join(cairo.LINE_JOIN_ROUND)
    command=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr0','-s',f'{width}x{height}','-r','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'cartoon.mp4')]
    positions={'mira':259,'ravi':540};idx=0
    with subprocess.Popen(command,stdin=subprocess.PIPE) as ff:
        for who,verb,n in beats:
            x0=positions[who];x1=x0
            if verb=='walk': x1=x0+(1 if who=='mira' else -1)*min(88,max(0,abs(positions['mira']-positions['ravi'])-76))
            for k in range(n):
                t=idx/24;u=k/(n-1);positions[who]=x0+(x1-x0)*art.smooth(u)
                cam=6*math.sin(t*.4);art.stage(t,cam)
                for name in ('ravi','mira'):
                    rig=frames[idx][name];flip=1 if name=='mira' else -1
                    x=positions[name]-cam;y=350;art.oval(x,y+2,32,5,'#919667')
                    g.save();g.translate(x,y);g.scale(flip*1.55,1.55);g.translate(0,-32)
                    def joint(b,end=1):
                        a,h=rig[b][end];return a,-h
                    skin='#d5946c' if flip==1 else '#b77352'
                    for side in ('L','R'):
                        leg='leg'+side;foot='foot'+side
                        art.path([joint(leg,0),joint(leg),joint(foot)],art.INK,7)
                        fx,fy=joint(foot);art.oval(fx+2,fy,6,3,'#423649')
                    def arm(side):
                        a='arm'+side;b='hand'+side
                        art.path([joint(a,0),joint(a),joint(b)],art.INK,5)
                        art.oval(*joint(b),3.8,3.8,skin)
                    arm('L')
                    hip=joint('body',0);neck=joint('body')
                    art.poly([(neck[0]-10,neck[1]),(neck[0]+10,neck[1]),(hip[0]+13,hip[1]+2),(hip[0]-13,hip[1]+2)],'#eb704c' if flip==1 else '#298988')
                    art.poly([(neck[0]-8,neck[1]),(neck[0]+7,neck[1]),(neck[0]-1,neck[1]+8)],'#ffe6a7')
                    hx,hy=joint('head');ax,ay=joint('head',0)
                    g.save();g.translate(hx,hy);g.rotate(math.atan2(hx-ax,-hy+ay))
                    art.oval(0,0,19,20,art.INK);art.oval(.5,.5,18,19,skin)
                    art.oval(-6,-12,14,9,art.INK)
                    if flip==1:
                        art.oval(-2,-15,19,8,'#e8a541');art.oval(8,-12,17,3,'#a5563f')
                    else: art.oval(-13,-20,9,9,art.INK)
                    blink=max(.12,min(1,abs((t+.3*(flip==1))%3.2-2.7)*14))
                    for dx in (5,13): art.oval(dx,-2,1.8,2.8*blink,art.INK)
                    art.curve((6,8),(8,11),(13,11),(15,7),art.INK,1.2);g.restore()
                    arm('R');g.restore()
                surface.flush();ff.stdin.write(surface.get_data());idx+=1
        ff.stdin.close()
        if ff.wait(): raise RuntimeError('FFmpeg encoding failed')

if __name__=='__main__':
    if '--' in sys.argv and 'bpy' in sys.modules:
        root=Path(sys.argv[sys.argv.index('--')+1]);blender_build(root,json.loads((root/'story.json').read_text())['beats'])
    elif '--' in sys.argv and Path(sys.argv[0]).name.startswith('blender'):
        root=Path(sys.argv[-1]);blender_build(root,json.loads((root/'story.json').read_text())['beats'])
    else:
        import argparse,subprocess
        p=argparse.ArgumentParser();p.add_argument('prompt');p.add_argument('folder',type=Path)
        p.add_argument('--extend',type=Path);p.add_argument('--width',type=int,choices=[640,1280,1920],default=1920)
        args=p.parse_args();prompt=args.prompt
        if args.extend: prompt=json.loads(args.extend.read_text())['prompt']+'; '+prompt
        beats=directions(prompt);folder=args.folder.resolve();folder.mkdir(parents=True,exist_ok=False)
        (folder/'story.json').write_text(json.dumps({'prompt':prompt,'beats':beats},ensure_ascii=False,indent=2))
        subprocess.run(['blender','-b','-t','2','--python-exit-code','1','-P',str(Path(__file__).resolve()),'--',str(folder)],check=True)
        composite(folder,beats,args.width)
