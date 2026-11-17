"""Funny Toon Ever V6 — shoulder-connected front arms, moon-garden episode.

V5 motion, permanent canonical mascot and V4 chase legs are preserved.

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
from garden_sound import make_audio
from moon_garden import background as garden_background
from shoulder_guard import clean_shoulder_flecks
from speed_chase_hybrid import chase_foot, leg_control, lane_ok, rounded_joint_path
from front_arm_motion import front_arm_pose, is_front_motion, near_arm_side

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
    # V6 shoulder ROOT embedding: original V5 rooted shoulder strokes at x=175/255,
    # y=294, outside the rounded torso contour at that height, leaving a white
    # pixel crack and broken ink outline. Shift each root ~10px INSIDE the torso
    # and slightly down so the limb stroke overlaps a filled shoulder socket.
    # Preserve frontal arm motion, elbow bend, contact-only hand IK and V4 legs.
    shoulders={-1:(186,303+bounce*.2),1:(244,303+bounce*.2)}
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

    # V5 front-facing arms: normally DOWN, and during a frontal sprint each
    # arm alternates near-chest/front and behind-hip. No horizontal windmills.
    # Only actual contact/expressive gestures use the proven V4 analytic IK.
    def arm_target(side):
        sx,sy=shoulders[side]
        if action=='knock' and side>0:
            elapsed=t-3.4
            hits=(.32,.81,1.31)
            near=min(abs(elapsed-q) for q in hits)
            displacement=min(31,near*155)
            return (KNOB[0]-origin_x-displacement, KNOB[1]-origin_y)
        if action=='knock':return (sx-32,sy+52)
        if action in ('shock','jump'):return (sx+side*58,sy-50-25*math.sin(math.pi*z))
        if action in ('slip','fall'):return (sx+side*74,sy-45)
        if action in ('reveal','celebrate') and side>0:
            return (sx+49,sy-35 if action=='celebrate' else sy+7)
        return (sx+side*20,sy+108)

    near_side=near_arm_side(action,gait_phase)
    far_side=-near_side
    def render_arm(side):
        if is_front_motion(action):
            projected=front_arm_pose(action,side,shoulders[side],gait_phase,z)
            elbow,end=projected.elbow,projected.hand
            logs['frontal_arm_frames']+=1
            if action=='dash':
                logs['run_arm_swing_signs'][str(side)].append(round(projected.swing,5))
                logs['run_arm_screen_horizontal_max_px']=max(
                    logs['run_arm_screen_horizontal_max_px'],abs(end[0]-shoulders[side][0]))
                logs['run_arm_hand_y_samples'][str(side)].append(round(end[1],3))
        else:
            target=arm_target(side)
            elbow,end,unreach=two_bone_ik(shoulders[side],target,66,66,
                elbow_sign=1 if side>0 else -1)
            logs['max_hand_ik_unreach_px']=max(logs['max_hand_ik_unreach_px'],unreach)
        draw_limb(d,shoulders[side],elbow,end,23 if side>0 else 28)
        hand(d,end,side,open_hand=action in ('shock','jump','slip','fall'))
        return end

    # Render the swung-back arm UNDER the torso and the forward one OVER it.
    # The front-vs-back layer order swaps as the running gait alternates.
    render_arm(far_side)

    # Body main white mascot torso with same black outline visual weight.
    d.rounded_rectangle((175,274+bounce*.2,255,379+bounce*.18),radius=37,fill=INK)
    d.rounded_rectangle((182,280+bounce*.2,248,372+bounce*.18),radius=31,fill=FILL)
    d.ellipse((187,300,244,360),fill=FILL)
    # Neck connects to canonical round head.
    d.rounded_rectangle((196,250,237,297),radius=10,fill=INK)
    d.rounded_rectangle((202,254,230,295),radius=10,fill=FILL)

    visible_end=render_arm(near_side)
    # Seal subpixel compositing seams on the NEAR arm: a tiny white in-torso
    # overlap hides the square root cap without adding a robotic joint circle.
    # The patch is 100% inside the outlined upper torso, never on the outer limb.
    nsx,nsy=shoulders[near_side]
    inner_x=nsx-near_side*13
    # Remove only the black internal root seam INSIDE the torso silhouette.
    # The actual upper arm starts outside this repaired region, so the joint
    # still appears continuous and has no explicit circular shoulder ring.
    if near_side>0:
        d.rounded_rectangle((229,299,239,318),radius=4,fill=FILL)
    else:
        d.rounded_rectangle((191,299,201,318),radius=4,fill=FILL)
    # For knock the V4 right arm remains in front; right side is always near
    # when not running, preserving the original direct door contact metric.
    if action=='knock':
        end=visible_end
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
    local,removed=clean_shoulder_flecks(local)
    logs["shoulder_specks_removed"]=logs.get("shoulder_specks_removed",0)+removed
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
    """An original layered garden environment, not the V5 restroom scene."""
    return garden_background(t,action,z,source_bg)


def draw_speed_lines(scene,t,action,z):
    # Recast the locked-door mechanics as an original moon-garden wishing bell
    # story, with dialogue-free expressive reaction caption cues.
    d=ImageDraw.Draw(scene)
    if action=='dash':
        cx=anchor_x(t)
        for j in range(4):
            yy=522+j*53+math.sin(t*15+j)*6
            xx=max(15,int(cx-92-j*7))
            d.line((xx,yy,max(4,xx-50-j*5),yy),fill='#d1d9c8',width=3)
    if action in ('shock','jump'):
        msg='OH!' if action=='shock' else 'WHOA!'
        d.rounded_rectangle((31,390,208,464),radius=22,fill='#fcf2df',outline='#3e4b77',width=4)
        d.text((119,404),msg,font=font(32,True),fill='#343d65',anchor='mt')
    if action=='reveal' and z>.40:
        d.rounded_rectangle((35,380,276,455),radius=20,fill='#faf3e0',outline='#4f5982',width=4)
        d.text((155,395),'IT BLOOMS!',font=font(26,True),fill='#41436b',anchor='mt')
    return


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
          'run_pose_counts':{k:0 for k in ('contact','down','passing','up')},
          'shoulder_specks_removed':0,
          'frontal_arm_frames':0,'run_arm_swing_signs':{'-1':[],'1':[]},
          'run_arm_hand_y_samples':{'-1':[],'1':[]},
          'run_arm_screen_horizontal_max_px':0.0}
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
    thumbs=output.with_name('ACTUAL_V6_FRAMES.jpg');thumb.save(thumbs,quality=88)
    elapsed=time.perf_counter()-t0
    report={'project':'Funny Toon Ever V6 Moon Garden: shoulder socket repair, colorful bell story, original reaction soundscape',
         'director':plan['director'],'duration':plan['duration'],'fps':fps,'frames':n,
         'resolution':[W,H],'render_wall_seconds':round(elapsed,2),
         'reference_used':str(sheet),'reference_head_preserved':True,
         'permanent_character':'funny_toon_ever_permanent',
         'face_states_used':sorted(logs['expressions']),
         'one_pupil_per_eye':head_meta['one_pupil_per_eye'],
         'hand_ik_reach_limited_px':round(logs['max_hand_ik_unreach_px'],2),
         'leg_motion_engine':'hybrid_speed_chase_fk_with_world_locked_stance',
         'arm_motion_engine':'front_sagittal_swing_plus_selective_V4_2bone_IK',
         'front_idle_arms_straight':True,'front_run_arms_alternate_in_depth':True,
         'shoulder_socket_embedded_px':{'left':11,'right':11},
         'shoulder_specks_removed':logs['shoulder_specks_removed'],
         'new_colorful_environment':'original procedural moon garden with magic wish bell',
         'run_arm_screen_horizontal_max_px':round(logs['run_arm_screen_horizontal_max_px'],2),
         'run_arm_y_excursion_px':{side:round(max(vals)-min(vals),2) if vals else 0 for side,vals in logs['run_arm_hand_y_samples'].items()},
         'frontal_arm_samples':logs['frontal_arm_frames'],
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
         'known_limitations':['The supplied Anime-Starter-Demo(2).mp4 shows relaxed arms and a wave, not a running cycle; running arm projection is an authored extrapolation',
             'Front/back swing is represented by 2D height, foreshortening and layer depth; it is not simulated 3D shoulder mechanics',
             'Hand IK target comes from authored door coordinates, not inferred from image',
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
    p.add_argument('--output',default='output/Funny_Toon_Ever_V6_Moon_Garden.mp4')
    a=p.parse_args()
    plan=load_or_compile(a.prompt,a.plan)
    result=render(plan,a.sheet,a.output,a.background)
    print('V6_MOON_GARDEN_VIDEO_RENDERED',json.dumps(result,ensure_ascii=False))

if __name__=='__main__':cli()
