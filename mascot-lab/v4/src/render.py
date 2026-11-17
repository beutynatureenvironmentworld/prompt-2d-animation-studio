"""Funny Toon Ever V4 — original V3 expressive head and IK arms, hybrid chase FK legs.

Actual portrait MP4, original procedural SFX, deterministic motion plan JSON,
audit metrics. No AI inference is claimed by this demo. Qwen3 integration accepts
only the schema-validated JSON plan; optional SSD-1B background PNG is accepted
via --background when supplied by the independent model-inference workflow.
"""
from __future__ import annotations
import argparse,io,json,math,os,subprocess,sys,time
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
from v3_director import load_or_compile,active_beat
from ik import two_bone_ik,planted_foot,smooth,lerp,clamp
from face import crop_original_head
from sound import make_audio
from speed_chase_hybrid import chase_foot, leg_control, lane_ok, rounded_joint_path

W,H=540,960
FLOOR=833
KNOB=(406,606)
INK='#191818';FILL='#ffffff';BG='#f3f1eb'
SCENE=[(.0,'sneak'),(.9,'dash'),(2.7,'brake'),(3.4,'knock'),(5.28,'shock'),
       (5.96,'jump'),(6.68,'slip'),(7.45,'fall'),(8.2,'recover'),(9.26,'reveal'),(10.25,'celebrate')]


def font(sz=24,bold=False):
    for name in (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'] if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']):
        if os.path.isfile(name):return ImageFont.truetype(name,sz)
    return ImageFont.load_default()


def squash_ease(z):return z*z*(3-2*z)


def anchor_x(t):
    if t<.9:return 133+3*math.sin(t*8)
    if t<2.7:return lerp(133,286,smooth((t-.9)/1.8))
    if t<3.4:
        z=(t-2.7)/.7;return 286+11*math.sin(math.pi*z)*(1-z)
    if t<5.28:return 286
    if t<5.96:return lerp(286,269,smooth((t-5.28)/.68))
    if t<6.68:return lerp(269,239,smooth((t-5.96)/.72))
    if t<7.45:return lerp(239,216,smooth((t-6.68)/.77))
    if t<8.2:return 216
    if t<9.26:return lerp(216,266,smooth((t-8.2)/1.06))
    if t<10.25:return 266
    return 266+2*math.sin((t-10.25)*4)


def draw_limb(d,a,b,c,width=24):
    """Smooth single rubber-hose outline; V3 IK endpoint is preserved for arms.

    The V3 black elbow/knee circle is intentionally REMOVED; drawing is one
    continuous path (black silhouette then white interior), not segment rings.
    """
    pts=[tuple(round(q) for q in pt) for pt in rounded_joint_path(a,b,c)]
    d.line(pts,fill=INK,width=width+7,joint='curve')
    d.line(pts,fill=FILL,width=width,joint='curve')


def hand(d,p,side=1,open_hand=False):
    x,y=p;r=15 if open_hand else 17
    d.ellipse((x-r-1,y-r-1,x+r+1,y+r+1),fill=INK)
    d.ellipse((x-r+3,y-r+3,x+r-3,y+r-3),fill='white')
    if open_hand:
        for i in (-1,0,1):
            xx=x+10*side;yy=y+i*6
            d.line((x,yy,xx+side*12,yy+i*1.5),fill=INK,width=5)
            d.line((x,yy,xx+side*12,yy+i*1.5),fill='white',width=2)
    else:
        d.arc((x-8,y-8,x+10,y+9),-35,140,fill=INK,width=3)


def body_illustration(t,action,z,heads,logs):
    """Each frame draws true IK arms+legs and uses a canonical head crop."""
    root_x=anchor_x(t)
    lift=0.;turn=0.;bounce=0.
    if action=='dash':
        bounce=8*abs(math.sin((t-.9)*math.pi*4.8))
        turn=-6
    elif action=='brake':turn=12*math.sin(math.pi*z);bounce=10*(1-z)
    elif action=='knock':turn=-4*math.sin(math.pi*(t-3.4)*2)
    elif action=='shock':turn=10*math.sin(math.pi*z)
    elif action=='jump':lift=120*math.sin(math.pi*z);turn=12*math.sin(math.pi*z)
    elif action=='slip':turn=-39*smooth(z);lift=15*math.sin(math.pi*z)
    elif action=='fall':turn=-50-35*smooth(z)
    elif action=='recover':turn=-85*(1-smooth(z))
    elif action=='reveal':turn=-7
    elif action=='celebrate':bounce=9*math.sin(math.pi*z)

    local=Image.new('RGBA',(430,500),(0,0,0,0));d=ImageDraw.Draw(local)
    center=215;foot_y=455
    hip_y=366+bounce*.30
    head_y=187+bounce*.6
    origin_x=root_x-center
    origin_y=FLOOR-foot_y-lift+bounce
    shoulders={-1:(175,294+bounce*.2),1:(255,294+bounce*.2)}
    hips={-1:(190,hip_y),1:(240,hip_y)}
    gait_phase=(t-.9)*2*math.pi*2.4
    foot_world=[];foot_locked=[]
    leg_points={}
    for side in (-1,1):
        if action=='dash':
            # Speed-chase hybrid: use planned foot POSES and planted contacts.
            # V3 hand IK is unchanged, but feet/knees do NOT use 2-bone IK.
            p,plant,pose=chase_foot(t,anchor_x,side,.9,2.7)
            target=(p[0]-origin_x,p[1]-origin_y)
        elif action in ('slip','fall','jump'):
            target=(center+side*(51+13*math.sin(z*math.pi)),
                    foot_y-10-18*math.sin(z*math.pi)*(1 if side>0 else -1))
            plant=False;pose='passing'
        else:
            target=(center+side*51,foot_y)
            plant=True;pose='contact'
        knee=leg_control(hips[side],target,side,pose)
        leg_points[side]=(hips[side],knee,target)
        foot_world.append((side,round(target[0]+origin_x,2),round(target[1]+origin_y,2)))
        foot_locked.append((side,plant))
        if action=='dash': logs['run_pose_counts'][pose]+=1
        if action=='dash' and plant: logs['planted_foot_samples']+=1
        # Outward silhouettes and feet, not two inward knee elbows.
        draw_limb(d,hips[side],knee,target,30)
        fx,fy=target
        d.ellipse((fx-23,fy-7,fx+25,fy+14),fill=INK)
        d.ellipse((fx-19,fy-4,fx+21,fy+10),fill=FILL)
    if not lane_ok(*(leg_points[-1]+leg_points[1])):
        logs['leg_lane_crossings']+=1
    logs['leg_samples']+=1

    # Left arm behind torso and right arm in front.
    def arm_target(side):
        sx,sy=shoulders[side]
        if action=='dash':
            swing=math.sin(gait_phase+(math.pi if side<0 else 0))
            return (sx+side*(26+16*abs(swing))+45*swing,sy+48-38*swing)
        if action=='sneak':return (sx+side*43,sy+52+5*math.sin(t*3))
        if action=='brake':return (sx+side*45,sy+35-26*math.sin(math.pi*z))
        if action=='knock' and side>0:
            elapsed=t-3.4
            hits=(.32,.81,1.31)
            near=min(abs(elapsed-q) for q in hits)
            displacement=min(31,near*155)
            # Exact intended knob contact at the three hit instants.
            return (KNOB[0]-origin_x-displacement, KNOB[1]-origin_y)
        if action=='knock':return (sx-32,sy+52)
        if action in ('shock','jump'):return (sx+side*58,sy-50-25*math.sin(math.pi*z))
        if action in ('slip','fall'):return (sx+side*74,sy-45)
        if action=='recover':return (sx+side*48,sy+17)
        if action in ('reveal','celebrate') and side>0:
            return (sx+49,sy-35 if action=='celebrate' else sy+7)
        return (sx+side*42,sy+53)

    for side in (-1,):
        target=arm_target(side)
        elbow,end,unreach=two_bone_ik(shoulders[side],target,66,66,elbow_sign=-1)
        logs['max_hand_ik_unreach_px']=max(logs['max_hand_ik_unreach_px'],unreach)
        draw_limb(d,shoulders[side],elbow,end,28);hand(d,end,side)

    # Body main white mascot torso with same black outline visual weight.
    d.rounded_rectangle((175,274+bounce*.2,255,379+bounce*.18),radius=37,fill=INK)
    d.rounded_rectangle((182,280+bounce*.2,248,372+bounce*.18),radius=31,fill=FILL)
    d.ellipse((187,300,244,360),fill=FILL)
    # Neck connects to canonical round head.
    d.rounded_rectangle((196,250,237,297),radius=10,fill=INK)
    d.rounded_rectangle((202,254,230,295),radius=10,fill=FILL)

    target=arm_target(1)
    elbow,end,unreach=two_bone_ik(shoulders[1],target,66,66,elbow_sign=1)
    logs['max_hand_ik_unreach_px']=max(logs['max_hand_ik_unreach_px'],unreach)
    draw_limb(d,shoulders[1],elbow,end,23);hand(d,end,1,open_hand=action in ('shock','jump','slip','fall'))

    if action=='knock':
        near=min(abs((t-3.4)-q) for q in (.32,.81,1.31))
        if near<=1/24:
            h=(end[0]+origin_x,end[1]+origin_y)
            err=math.hypot(h[0]-KNOB[0],h[1]-KNOB[1])
            logs['knock_contact_max_error_px']=max(logs['knock_contact_max_error_px'],round(err,2))
            logs['knock_contact_frames']+=1

    expression={
        'sneak':'sly','dash':'sly' if z<.76 else 'focus','brake':'focus','knock':'effort',
        'shock':'shock','jump':'shock','slip':'worried','fall':'worried',
        'recover':'focus' if z<.62 else 'sly','reveal':'sly','celebrate':'grin'
    }.get(action,'sly')
    if action=='knock' and z<.18:expression='sly'
    if action=='reveal' and z<.38:expression='neutral'
    # Independent blink, occurs only on calm beats, no duplicate pupils.
    img=heads[expression]
    headsize=155
    if action=='shock':headsize=161
    if action=='celebrate':headsize=160
    scaled=img.resize((headsize,headsize),Image.Resampling.LANCZOS)
    hx=center-headsize//2+(-7 if action=='brake' else 0)
    hy=int(head_y-headsize/2)
    local.alpha_composite(scaled,(hx,hy))
    # Rotate around pelvis for stumbles: true body angular motion, not just camera shake.
    if abs(turn)>1:
        local=local.rotate(-turn,resample=Image.Resampling.BICUBIC,center=(center,342),expand=False)
    logs['expressions'].add(expression)
    # Per-frame world-space foot locking diagnostics only for planted dash phases.
    if action=='dash':
        for side,x,y in foot_world:
            if dict(foot_locked)[side]:logs['stance_tracks'].append((side,t,x,y))
    return local,round(origin_x),round(origin_y),expression


def background(t,action,z,source_bg=None):
    if source_bg is not None:
        base=source_bg.copy().convert('RGBA')
    else:
        base=Image.new('RGB',(W,H));d=ImageDraw.Draw(base)
        for y in range(H):
            q=y/H
            col=(int(247-12*q),int(246-10*q),int(242-13*q))
            d.line((0,y,W,y),fill=col)
        # Soft repeatable wall motifs and floor grid.
        d.rectangle((0,FLOOR,W,H),fill='#e9e5df')
        d.line((0,FLOOR,W,FLOOR),fill='#a5a19a',width=5)
        for xx in (0,135,270,405,540):d.line((xx,FLOOR,xx-23,H),fill='#d5d1cb',width=2)
        for yy in (876,922):d.line((0,yy,W,yy),fill='#d5d1cb',width=2)
        # sign, wall framing
        d.rounded_rectangle((356,254,522,306),radius=12,fill='#272727')
        d.text((439,280),'RESTROOM',font=font(23,True),anchor='mm',fill='white')
        d.rounded_rectangle((36,360,130,489),radius=8,fill='#e3e0da',outline='#bcb5a9',width=3)
        d.ellipse((62,384,102,423),outline='#77766f',width=3)
        d.line((83,423,83,464),fill='#77766f',width=4)
        d.text((82,471),'WASH',font=font(12,True),anchor='mm',fill='#77766f')
        base=base.convert('RGBA')
    d=ImageDraw.Draw(base)
    # Door panel is fixed in the first 9 seconds; opens only at the punchline.
    frame=(365,333,515,FLOOR)
    d.rounded_rectangle((frame[0]-7,frame[1]-7,frame[2]+7,frame[3]+6),radius=9,
                        fill='#292929')
    d.rectangle((frame[0]+4,frame[1]+5,frame[2]-4,frame[3]-4),fill='#dcd9d4')
    open_amount=0
    if action in ('reveal','celebrate'):
        open_amount=72*smooth(z) if action=='reveal' else 72
    door_left=int(375+open_amount)
    if open_amount:
        d.polygon(((375,340),(door_left,348),(door_left,824),(375,828)),fill='#66645f')
    door_right=510
    door_poly=[(door_left,342),(door_right,342),(door_right,826),(door_left,826)]
    d.polygon(door_poly,fill='#faf8f2')
    d.line(door_poly+[door_poly[0]],fill=INK,width=6,joint='curve')
    if not open_amount:
        d.rounded_rectangle((393,390,492,786),radius=5,outline='#c4c1bb',width=3)
        d.ellipse((399,600,413,614),fill='#f2c86d',outline=INK,width=3)
    else:
        d.polygon([(375,340),(400,342),(400,827),(375,825)],fill='#302f2e')
    if action=='knock':
        near=min(abs((t-3.4)-q) for q in (.32,.81,1.31))
        if near<.075:
            shake=7*(1-near/.075)
            for r in (21,34):d.arc((406-r-shake,606-r,406+r+shake,606+r),-70,55,fill='#474645',width=3)
    # slippage source: a small wet floor patch
    d.ellipse((151,836,279,857),fill='#a6c3c4',outline='#82a5a7',width=2)
    d.arc((163,838,265,856),200,345,fill='white',width=2)
    return base


def draw_speed_lines(scene,t,action,z):
    d=ImageDraw.Draw(scene)
    if action=='dash':
        cx=anchor_x(t)
        for j in range(5):
            yy=525+j*53+math.sin(t*16+j)*9
            xx=max(12,int(cx-100-j*9))
            d.line((xx,yy,max(0,xx-65-j*5),yy),fill='#989691',width=2+j%2)
    if action=='shock':
        cx=anchor_x(t);cy=545
        for a in (-2.0,-1.45,-.95,-.35):
            xx=cx+math.cos(a)*105;yy=cy+math.sin(a)*105
            d.line((xx,yy,xx+math.cos(a)*24,yy+math.sin(a)*24),fill=INK,width=6)
    if action=='slip':
        cx=anchor_x(t)
        for j in range(3):
            d.line((cx-75,740+j*23,cx-112-j*7,732+j*22),fill='#4c4949',width=3)
    if action in ('reveal','celebrate'):
        if action=='reveal' and z>.46:
            d.rounded_rectangle((318,469,496,535),radius=17,fill='white',outline=INK,width=4)
            d.text((407,498),'PULL!',font=font(32,True),anchor='mm',fill=INK)
        elif action=='celebrate':
            d.rounded_rectangle((322,463,504,532),radius=17,fill='white',outline=INK,width=4)
            d.text((413,499),'...OOPS!',font=font(25,True),anchor='mm',fill=INK)


def add_camera(img,t,action,z):
    if action=='shock':
        zoom=1+.065*math.sin(math.pi*z)
    elif action=='fall':zoom=1+.03*math.sin(math.pi*z)
    else:zoom=1
    if zoom>1.001:
        ww=int(W/zoom);hh=int(H/zoom)
        cx=285;cy=610
        box=(max(0,cx-ww//2),max(0,cy-hh//2),max(0,cx-ww//2)+ww,max(0,cy-hh//2)+hh)
        box=(min(max(0,box[0]),W-ww),min(max(0,box[1]),H-hh),min(W,box[2]),min(H,box[3]))
        box=(box[0],box[1],box[0]+ww,box[1]+hh)
        img=img.crop(box).resize((W,H),Image.Resampling.BICUBIC)
    return img


def render(plan,sheet,output,background_file=None,preview_every=24):
    import cv2
    source=Image.open(sheet).convert('RGBA')
    headbank,head_meta=crop_original_head(source)
    optional_image=None
    if background_file:
        with Image.open(background_file) as b:
            from PIL import ImageOps
            optional_image=ImageOps.fit(b.convert('RGB'),(W,H)).convert('RGBA')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    n=round(plan['duration']*plan['fps']); fps=int(plan['fps'])
    silent=output.with_name('silent_'+output.name)
    audio=output.with_suffix('.wav')
    logs={'max_leg_ik_unreach_px':0.,'max_hand_ik_unreach_px':0.,
          'knock_contact_max_error_px':0.,'knock_contact_frames':0,
          'planted_foot_samples':0,'stance_tracks':[],'expressions':set(),
          'leg_lane_crossings':0,'leg_samples':0,
          'run_pose_counts':{k:0 for k in ('contact','down','passing','up')}}
    raw_cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-threads','2',
       '-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
       '-framerate',str(fps),'-i','-','-an','-c:v','libx264','-preset','veryfast',
       '-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)]
    proc=subprocess.Popen(raw_cmd,stdin=subprocess.PIPE)
    previews=[];t0=time.perf_counter()
    try:
        for i in range(n):
            t=i/fps;beat,z=active_beat(plan,t)
            action=beat['action']
            bg=background(t,action,z,optional_image)
            sprite,ox,oy,expression=body_illustration(t,action,z,headbank,logs)
            if action=='knock' and .31< t-3.4 <.38: pass
            # Maintain actual silhouette visibility during off-balance rotations.
            # Large anticlockwise fall arcs previously clipped the reference head.
            if action in ('slip','fall','recover'):
                box=sprite.getbbox()
                if box:
                    left=ox+box[0];right=ox+box[2]
                    if left<22:ox+=22-left
                    if right>W-22:ox-=right-(W-22)
            bg.alpha_composite(sprite,(ox,oy))
            draw_speed_lines(bg,t,action,z)
            bg=add_camera(bg,t,action,z)
            image=bg.convert('RGB')
            if i%preview_every==0 or i==n-1:previews.append((t,image.resize((270,480))))
            proc.stdin.write(image.tobytes())
        proc.stdin.close()
    except Exception:
        proc.kill();raise
    if proc.wait()!=0:raise RuntimeError('FFmpeg encoding failed')
    sound=make_audio(audio,plan['duration'])
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(silent),'-i',str(audio),
          '-c:v','copy','-c:a','aac','-b:a','96k','-movflags','+faststart','-shortest',str(output)],check=True)
    silent.unlink(missing_ok=True)
    # Debug metrics: expected exactly one pupil per eye from sanitized head,
    # and stationary world-space feet across consecutive stance samples.
    stable=[];by_side={-1:[],1:[]}
    for side,t,x,y in logs['stance_tracks']:
        by_side[side].append((t,x,y))
    for side,tr in by_side.items():
        for (t1,x1,y1),(t2,x2,y2) in zip(tr,tr[1:]):
            if t2-t1<=1/fps+.002 and abs(x1-x2)<24:stable.append(math.hypot(x1-x2,y1-y2))
    max_stance=max(stable or [0.])
    total_cols=4; thumb=Image.new('RGB',(270*total_cols,480*math.ceil(len(previews)/total_cols)),'#e3e3e3')
    td=ImageDraw.Draw(thumb)
    for j,(t,frame) in enumerate(previews):
        x=(j%total_cols)*270;y=(j//total_cols)*480
        thumb.paste(frame,(x,y));td.rectangle((x,y,x+73,y+22),fill='white');td.text((x+4,y+4),f'{t:.1f}s',font=font(14),fill=INK)
    thumbs=output.with_name('ACTUAL_V4_FRAMES.jpg');thumb.save(thumbs,quality=88)
    elapsed=time.perf_counter()-t0
    report={'project':'Funny Toon Ever V4 speed-chase hybrid mascot lab',
         'director':plan['director'],'duration':plan['duration'],'fps':fps,'frames':n,
         'resolution':[W,H],'render_wall_seconds':round(elapsed,2),
         'reference_used':str(sheet),'reference_head_preserved':True,
         'permanent_character':'funny_toon_ever_permanent',
         'face_states_used':sorted(logs['expressions']),
         'one_pupil_per_eye':head_meta['one_pupil_per_eye'],
         'hand_ik_reach_limited_px':round(logs['max_hand_ik_unreach_px'],2),
         'leg_motion_engine':'hybrid_speed_chase_fk_with_world_locked_stance',
         'visible_elbow_knee_circles':False,
         'run_pose_counts':logs['run_pose_counts'],
         'leg_lane_crossings':logs['leg_lane_crossings'],'leg_samples':logs['leg_samples'],
         'leg_ik_reach_limited_px':None,
         'knock_contact_max_error_px':logs['knock_contact_max_error_px'],
         'knock_contact_frames':logs['knock_contact_frames'],
         'foot_stance_max_drift_px':round(max_stance,3),
         'foot_planted_samples':logs['planted_foot_samples'],
         'sound_events':len(sound['events']),
         'codec':'H.264/AAC','actual_ai_inference_used':False,
         'ai_motion_plan_supported_as_input':True,'background_diffusion_used':background_file is not None,
         'known_limitations':['Hand IK target comes from authored door coordinates, not inferred from image',
             'Legs use staged stylized FK, not skeletal leg IK: outward lane policy avoids X-shaped intersections',
             'Foot planting is analytic for dash; not full-body physics',
             'The canonical head is reference-derived but the torso/limbs are drawn as a matching procedural rig',
             'This demo uses an offline motion director, not an executed Qwen3 model'],
         'output_video':str(output),'contact_sheet':str(thumbs)}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report


def cli():
    p=argparse.ArgumentParser()
    p.add_argument('--prompt',default='Permanent Funny Toon mascot rushes to a locked restroom, knocks, slips and cleverly recovers')
    p.add_argument('--plan',default=None)
    p.add_argument('--sheet',default='assets/canonical_neutral_pose.png')
    p.add_argument('--background',default=None)
    p.add_argument('--output',default='output/Funny_Toon_Ever_V4_Speed_Chase_Hybrid.mp4')
    a=p.parse_args()
    plan=load_or_compile(a.prompt,a.plan)
    result=render(plan,a.sheet,a.output,a.background)
    print('V4_HYBRID_VIDEO_RENDERED',json.dumps(result,ensure_ascii=False))

if __name__=='__main__':cli()
