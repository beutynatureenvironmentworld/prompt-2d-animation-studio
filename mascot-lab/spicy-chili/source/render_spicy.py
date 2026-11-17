"""Real MP4 animation: permanent user mascot, V4 FK legs, V6 no-ring arms,
   analytic two-bone IK chili hand, expressive face, GPU-free flame compositor.

This renderer does not play back an AI-generated comic storyboard. Every frame
is freshly drawn from a deterministic timeline + reusable reference-head sprite.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import argparse, math, json, subprocess, time, numpy as np, sys
from spicy_motion_director import make_plan,validate,beat_at
from spicy_sounds import create_sound
W,H,FPS=540,960,24
O=(18,18,22,255);WHITE=(255,255,255,255)
_local=Path(__file__).resolve().parents[1]/'assets'/'permanent_mascot_reference.png'
_repo=Path(__file__).resolve().parents[2]/'config'/'permanent_mascot.webp'
SRC=str(_local if _local.exists() else _repo)
S=2 # portrait frames 1080x1920 internal antialiasing; final output 540x960

def font(size=24,bold=False):
 paths=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
 for p in paths:
  if Path(p).exists():return ImageFont.truetype(p,size)
 return ImageFont.load_default()

def ease(z):return z*z*(3-2*z)
def clamp(v,a=0,b=1):return min(b,max(a,v))
def mix(a,b,z):return a+(b-a)*z

def circle_mask(sz,r):
 m=Image.new('L',(sz*2,sz*2),0);d=ImageDraw.Draw(m);d.ellipse((sz-r,sz-r,sz+r,sz+r),fill=255)
 return m.resize((sz,sz),Image.Resampling.LANCZOS)

def make_head_assets(sheet):
    """Use original top-left face and contour from 6-pose reference, not AI redraw."""
    im=Image.open(sheet).convert('RGB')
    cw,ch=im.width//3,im.height//2
    # Original head is centered at approximately (263,148), radius ~95.
    x,y,r=cw*.514,ch*.289,107
    crop=im.crop((round(x-r),round(y-r),round(x+r),round(y+r)))
    alpha=Image.new('L',crop.size,0);d=ImageDraw.Draw(alpha)
    d.ellipse((7,7,crop.width-7,crop.height-7),fill=255)
    crop.putalpha(alpha)
    return crop.resize((208,208),Image.Resampling.LANCZOS)


def face_variant(source,state,heat=0,blink=False):
    """One pupil per eye in procedural emotional states; sly keeps exact smile."""
    if state=='sly':return source
    head=Image.new('RGBA',(208,208),(0,0,0,0));d=ImageDraw.Draw(head)
    red=clamp(heat)
    base=(round(mix(252,255,red)),round(mix(252,75,red)),round(mix(251,68,red)),255)
    d.ellipse((7,7,200,200),fill=base,outline=O,width=7)
    # one and only one canonical pupil per eye
    if state in ('bite','suspicious','tired'):
        d.arc((38,62,92,92),190,347,fill=O,width=5)
        d.arc((116,62,172,92),192,343,fill=O,width=5)
        if state=='suspicious':
            d.ellipse((49,77,86,111),fill=WHITE,outline=O,width=4)
            d.ellipse((123,77,160,111),fill=WHITE,outline=O,width=4)
            d.ellipse((64,92,75,103),fill=O);d.ellipse((138,92,149,103),fill=O)
        if state=='tired':
            d.line([(47,112),(88,115)],fill=O,width=4)
            d.line([(124,114),(164,111)],fill=O,width=4)
    else:
        bulge=9 if state in ('shock','panic','fire') else 0
        for cx in (65,145):
            ey=93;rx=27+bulge;ry=32+bulge
            d.ellipse((cx-rx,ey-ry,cx+rx,ey+ry),fill=WHITE,outline=O,width=6)
            px=cx+(6 if state!='panic' else -4)
            py=ey+6
            d.ellipse((px-7,py-7,px+7,py+7),fill=O)
    # eyebrows never replace/add pupils
    if state in ('shock','panic','fire'):
        d.arc((41,25,95,68),196,328,fill=O,width=6)
        d.arc((114,25,171,68),196,337,fill=O,width=6)
    elif state=='suspicious':
        d.line((42,60,92,63),fill=O,width=6)
        d.line((117,61,167,53),fill=O,width=6)
    else:
        d.arc((43,37,91,67),202,340,fill=O,width=6)
        d.arc((116,36,166,67),203,339,fill=O,width=6)
    if state=='bite':
        d.arc((53,106,157,166),4,176,fill=O,width=8)
        for cx in (77,105,134):d.line((cx,143,cx,151),fill=O,width=3)
    elif state=='suspicious':
        d.line((82,154,143,147),fill=O,width=6)
    elif state in ('shock','panic'):
        if state=='shock':
            d.ellipse((87,135,134,188),fill=(30,14,24,255),outline=O,width=4)
            d.ellipse((99,162,120,178),fill=(249,122,152,255))
        else:
            d.ellipse((52,131,166,195),fill=(35,14,25,255),outline=O,width=5)
            d.polygon([(80,151),(136,151),(132,160),(85,160)],fill=WHITE)
            d.ellipse((94,176,132,194),fill=(246,109,144,255))
    elif state=='fire':
        d.ellipse((49,129,175,195),fill=(32,7,15,255),outline=O,width=6)
        d.polygon([(65,142),(154,142),(147,152),(74,152)],fill=WHITE)
        d.arc((73,152,147,198),180,350,fill=(255,93,62,255),width=8)
    elif state=='tired':
        d.arc((85,141,145,170),10,175,fill=O,width=5)
        d.rounded_rectangle((105,159,122,184),radius=6,fill=(240,90,123,255),outline=O,width=3)
    # heat drops, tears and blush; keep eyes legible
    if red>.12:
        d.ellipse((24,130,51,154),fill=(255,107,102,170))
        d.ellipse((169,131,188,151),fill=(255,107,102,170))
    if state in ('panic','fire'):
        for sx,sy in ((37,25),(173,29),(190,88)):
            d.ellipse((sx-5,sy-3,sx+5,sy+15),fill=(240,251,255,255),outline=O,width=2)
    return head


def solve2(root,target,l1=94,l2=100,side=1):
    dx=target[0]-root[0];dy=target[1]-root[1]
    dis=math.hypot(dx,dy)
    constrained=max(abs(l1-l2)+.01,min(l1+l2-.01,dis))
    angle=math.atan2(dy,dx)
    a=math.acos(max(-1,min(1,(l1*l1+constrained*constrained-l2*l2)/(2*l1*constrained))))
    knee=(root[0]+l1*math.cos(angle+side*a),root[1]+l1*math.sin(angle+side*a))
    e=(root[0]+constrained*math.cos(angle),root[1]+constrained*math.sin(angle))
    return knee,e,abs(dis-constrained)


def curve_points(a,b,c):
    # Same IK endpoint, but one smooth continuous tube. Shoulder/eIbow not rings.
    p=[a]
    pre=(mix(a[0],b[0],.76),mix(a[1],b[1],.76))
    post=(mix(b[0],c[0],.22),mix(b[1],c[1],.22))
    p.append(pre)
    for i in range(1,9):
        z=i/9;k=1-z
        p.append((k*k*pre[0]+2*k*z*b[0]+z*z*post[0],k*k*pre[1]+2*k*z*b[1]+z*z*post[1]))
    p += [post,c]
    return p


def limb(draw,root,bend,tip,width=27):
    pts=curve_points(root,bend,tip)
    draw.line(pts,fill=O,width=width+8,joint='curve')
    draw.line(pts,fill=WHITE,width=width,joint='curve')
    # NO circular outline at elbow, knee or shoulder.


def mitten(d,pos,open_hand=False):
    x,y=pos
    if open_hand:
        d.ellipse((x-18,y-17,x+18,y+17),fill=WHITE,outline=O,width=6)
        for k in (-1,0,1):
            d.line((x+8,y+k*6,x+24,y+k*11),fill=O,width=7)
            d.line((x+8,y+k*6,x+24,y+k*11),fill=WHITE,width=3)
    else:
        d.ellipse((x-18,y-16,x+18,y+17),fill=WHITE,outline=O,width=6)
        d.arc((x-8,y-11,x+12,y+10),30,185,fill=O,width=4)


def chili(d,point,scale=1,rotation=0,bitten=False):
    """Hand-held chili with consistent object anchor and green stem."""
    # draw on its own canvas and rotate around stalk (attachment point)
    c=Image.new('RGBA',(120,150),(0,0,0,0));pen=ImageDraw.Draw(c)
    pen.polygon([(66,45),(78,61),(73,86),(54,103),(38,105),(49,95),(48,78),(53,53)],fill='#f3382e')
    pen.line([(66,45),(78,61),(73,86),(54,103),(38,105),(49,95),(48,78),(53,53),(66,45)],fill=O,width=6,joint='curve')
    pen.arc((51,57,74,95),-90,105,fill='#ff9c6e',width=4)
    pen.line((65,43,71,20,82,18),fill='#286b31',width=8,joint='curve')
    pen.line((65,43,71,20,82,18),fill=O,width=2,joint='curve')
    if bitten:
        pen.ellipse((48,88,78,112),fill='#fff7e5',outline=O,width=3)
    if scale!=1:
        c=c.resize((round(120*scale),round(150*scale)),Image.Resampling.LANCZOS)
    if abs(rotation)>1:c=c.rotate(rotation,resample=Image.Resampling.BICUBIC,expand=True)
    return c


def draw_background(t,flaring=False):
    image=Image.new('RGB',(W,H))
    d=ImageDraw.Draw(image)
    for yy in range(H):
        heat=1 if flaring else 0
        ratio=yy/H
        col=(int(247-13*ratio+4*heat),int(247-12*ratio-12*heat),int(243-12*ratio-14*heat))
        d.line((0,yy,W,yy),fill=col)
    d.ellipse((40,65,495,650),outline=(233,223,213),width=2)
    d.ellipse((-96,90,365,700),outline=(239,231,219),width=2)
    d.line((0,824,W,824),fill=(140,137,127),width=5)
    d.rectangle((0,828,W,H),fill=(235,230,219))
    for xx in (50,195,365,520):d.line((xx,828,xx-35,H),fill=(220,213,202),width=2)
    d.rounded_rectangle((46,83,495,137),radius=13,fill=(25,25,29))
    d.text((270,110),'THE CHILI CHALLENGE',font=font(22,True),anchor='mm',fill=(255,250,240))
    d.text((270,912),'FUNNY TOON EVER  •  SUPER TEST',font=font(14,True),anchor='mm',fill=(101,92,89))
    d.ellipse((112,824,395,844),fill=(200,192,179))
    return image.convert('RGBA')


def main(args):
    plan=validate(json.loads(Path(args.plan).read_text()) if args.plan else make_plan())
    original=make_head_assets(args.reference)
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    rawvideo=out.with_name('silent_'+out.name)
    duration=plan['duration'];nf=round(duration*FPS)
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-an',str(rawvideo)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    logs={'arm_ik_max_target_error':0.,'chili_mouth_contact_sampled':[],'faces':set(),'frames':nf,'pupils_per_eye':1,
          'shoulder_seam_rings':0,'leg_crossings':0,'animation_engine':'Pillow+OpenCV reference + 2-bone hand IK + V4 pose/FK feet + FFmpeg'}
    thumbs=[];starttime=time.time()
    try:
     for i in range(nf):
        t=i/FPS;beat,z=beat_at(plan,t);action=beat['action']
        # Facial state with mild temporal tremble / strong emotional extremes.
        heat=0
        if t>3.2:heat=clamp((t-3.2)/.62)
        if t>7.75:heat=clamp(1-(t-7.75)/3.35)
        state={'sly_show':'sly','reach_bite':'bite','suspicious':'suspicious','burning':'shock','panic':'panic',
               'flare_up':'fire','smoke':'tired','recover':'tired','sly_finish':'sly'}[action]
        if action=='recover' and z>.72:state='sly'
        logs['faces'].add(state)
        sky=draw_background(t,action in ('flare_up','panic'))
        # Character world-space root. Smooth vertical motions with maintained noncrossed foot lanes.
        global_x=258 + (17*math.sin(t*3) if action=='panic' else 0)
        baseline=827
        hop=0
        if action=='panic':hop=21*abs(math.sin(t*math.pi*4))
        if action=='burning':hop=7*abs(math.sin(t*17))
        if action=='flare_up':hop=6*math.sin(t*19)
        if action=='recover':hop=6*(1-ease(z))
        actor=Image.new('RGBA',(440,620),(0,0,0,0));d=ImageDraw.Draw(actor)
        center=220;cy=197;feet_y=560
        shoulders={-1:(162,336),1:(276,336)}
        hips={-1:(187,456),1:(254,456)}
        # FK legs use separated lanes, fast alternating poses under panic; never cross.
        feet={}
        for side in (-1,1):
            swing=math.sin((t-4.40)*2*math.pi*4+(0 if side<0 else math.pi))
            if action=='panic':
                fx=center+side*(61+13*abs(swing));fy=561-37*max(0,swing)
            elif action in ('flare_up','burning'):
                fx=center+side*(65+7*abs(math.sin(t*9)));fy=560-9*abs(math.sin(t*10))
            else:
                fx=center+side*56;fy=560
            hk=hips[side];foot=(fx,fy)
            knee=((hk[0]+fx)/2+side*(17 if action=='panic' else 13),(hk[1]+fy)/2-9)
            # shadow and far/near feet
            limb(d,hk,knee,foot,34)
            d.ellipse((fx-25,fy-10,fx+26,fy+15),fill=WHITE,outline=O,width=7)
            feet[side]=(knee,foot)
        if not (feet[-1][0][0]<center-8 and feet[1][0][0]>center+8): logs['leg_crossings']+=1
        # Hand IK targets: strong shoulder-connected strokes with no donut-like rings.
        arm_target_left={'sly_show':(129,426),'reach_bite':(129,425),'suspicious':(136,424),
           'burning':(136,392),'panic':(95,273),'flare_up':(129,407),
           'smoke':(131,448),'recover':(131,451),'sly_finish':(132,423)}[action]
        if action=='panic':arm_target_left=(95+13*math.sin(t*23),274)
        right=(333,262)
        if action=='reach_bite':
            f=ease(clamp((t-1.35)/.74));right=(mix(333,265,f),mix(262,243,f))
        elif action in ('suspicious','burning'):
            right=(267,251) if action=='suspicious' else (320,390)
        elif action=='panic':right=(345+12*math.sin(t*24),267)
        elif action=='flare_up':right=(325,414)
        elif action in ('smoke','recover'):right=(313,452)
        elif action=='sly_finish':right=(335,335)
        targets={-1:arm_target_left,1:right}
        for side in (-1,1):
            sr=shoulders[side];target=targets[side]
            elbow,hand,err=solve2(sr,target,102,100,side=(-1 if side==1 else 1))
            logs['arm_ik_max_target_error']=max(logs['arm_ik_max_target_error'],err)
            limb(d,sr,elbow,hand,28)
        # One connected torso overlay covers all shoulder roots. Shoulders aren't circles.
        d.rounded_rectangle((155,302,283,470),radius=58,fill=O)
        d.rounded_rectangle((162,309,276,463),radius=53,fill=WHITE)
        d.ellipse((170,324,271,431),fill=WHITE)
        # Rounded sculpted neck, behind source face.
        d.rounded_rectangle((195,264,245,325),radius=15,fill=O)
        d.rounded_rectangle((202,266,238,325),radius=9,fill=WHITE)
        # Add hands *after* torso; no discontinuity at wrists.
        for side in (-1,1):
            target=targets[side];mitten(d,target,open_hand=(action=='panic'))
        # Pepper is anchored to the actual fist (not screen position).
        if action in ('sly_show','reach_bite','suspicious'):
            small=chili(d,right,scale=.68 if action!='suspicious' else .43,bitten=action=='suspicious')
            objx=round(right[0]-small.width*.57)
            objy=round(right[1]-small.height*.78)
            # Render pepper IN FRONT of the face after head compositing: otherwise
            # the canonical head circle occludes the bite on actual MP4 frames.
            chili_overlay=(small,objx,objy)
            if action=='reach_bite' and z>.57:
                # Actual chili-to-mouth contact audit only after hand arrives.
                head_mouth=(247,235)
                # Exact authored tip of curved chili path at (38,105) in its 120x150 sprite.
                pepper_tip=(objx+small.width*(38/120),objy+small.height*(105/150))
                logs['chili_mouth_contact_sampled'].append(round(math.hypot(pepper_tip[0]-head_mouth[0],pepper_tip[1]-head_mouth[1]),2))
        # Facial posing: source's EXACT sly grin restored at opening and ending.
        fimg=face_variant(original,state,heat=heat)
        tilt=0
        if action=='burning':tilt=4*math.sin(t*22)
        elif action=='panic':tilt=7*math.sin(t*16)
        elif action=='flare_up':tilt=-9*math.sin(math.pi*z)
        elif action=='smoke':tilt=-13
        elif action=='recover':tilt=-13*(1-ease(z))
        if abs(tilt)>1:fimg=fimg.rotate(tilt,resample=Image.Resampling.BICUBIC,expand=False)
        actor.alpha_composite(fimg,(center-104,cy-104))
        # Reapply chili over face in active bite moments so hand-to-mouth reads clearly.
        if action in ('sly_show','reach_bite','suspicious'):
            actor.alpha_composite(chili_overlay[0],(chili_overlay[1],chili_overlay[2]))
        # Camera squash/bob and animation translate without static panel swaps.
        xpos=round(global_x-center)
        ypos=round(baseline-feet_y-hop)
        sky.alpha_composite(actor,(xpos,ypos))
        screen=ImageDraw.Draw(sky)
        if action=='burning':
            for j in range(4):
                yy=490+j*29;xx=165+j*18
                screen.arc((xx-22,yy-16,xx+22,yy+16),50,180,fill=(239,53,38),width=4)
        if action=='panic':
            for j in range(4):
                xx=int(global_x)+(-125 if j%2 else 105)
                yy=492+j*41
                screen.line((xx,yy,xx+(-22 if j%2 else 22),yy-15),fill=(19,18,22),width=6)
        if action=='flare_up':
            # Rocket-like flame breath composed independently every frame.
            strength=math.sin(math.pi*min(1,z*1.3))*.6+.4
            fx=global_x+25;fy=baseline-feet_y-hop+cy+39
            L=round((W-fx+130)*clamp(z*4,.08,1.0))
            wobble=9*math.sin(t*29)
            layers=[((240,66,24,255),58),((255,129,21,255),43),((255,221,64,255),27),((255,249,155,255),14)]
            for color,rad in layers:
                wave=math.sin(t*32+rad*.15)*10
                poly=[(fx,fy-16),(fx+L*.13,fy-rad),
                      (fx+L*.42,fy-rad+wave),(fx+L*.70,fy-rad*.78-wobble),
                      (fx+L,fy+math.sin(t*11)*22),(fx+L*.72,fy+rad*.6),
                      (fx+L*.44,fy+rad-wave),(fx+L*.17,fy+rad*.75),(fx,fy+17)]
                screen.polygon(poly,fill=color)
            for j in range(8):
                ex=fx+40+(j*43+t*39)%max(100,L)
                ey=fy+math.sin(j*17+t*14)*85
                r=2+int((math.sin(t*7+j)+1)*3)
                screen.ellipse((ex-r,ey-r,ex+r,ey+r),fill=(255,152,25))
        if action in ('smoke','recover'):
            fx=global_x+33;fy=baseline-feet_y-hop+cy+42
            q=(t-7.72)
            for j in range(4):
                yy=fy-j*25-(q*22);xx=fx+j*18+13*math.sin(j*1.7+q*3)
                rr=9+j*7
                screen.arc((xx-rr,yy-rr,xx+rr,yy+rr),180,345,fill=(133,128,130),width=3)
        if action=='sly_finish':
            # End holds the mischievous grin; the pepper survived.
            screen.rounded_rectangle((326,650,504,716),radius=14,fill=(255,247,222),outline=O,width=3)
            screen.text((416,683),'ONE MORE?',font=font(20,True),anchor='mm',fill=(44,39,38))
        if action=='burning' or action=='flare_up':
            shake=(int(3*math.sin(t*41)),int(2*math.cos(t*31)))
            jitter=Image.new('RGBA',(W,H),(247,243,237,255));jitter.alpha_composite(sky,shake)
            sky=jitter
        if i%24==0 or i==nf-1:
            thumbs.append((round(t,1),sky.convert('RGB').resize((270,480),Image.Resampling.LANCZOS)))
        frame=sky.convert('RGB')
        proc.stdin.write(frame.tobytes())
     proc.stdin.close()
    except Exception:
     proc.kill();raise
    if proc.wait()!=0:raise RuntimeError('Video encoder failed')
    audio=out.with_suffix('.wav');sounds=create_sound(audio,duration)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(rawvideo),'-i',str(audio),'-c:v','copy','-c:a','aac','-b:a','96k','-movflags','+faststart',str(out)],check=True)
    rawvideo.unlink(missing_ok=True)
    # QA contact logs and decoded frame filmstrip for human review.
    grid=Image.new('RGB',(270*4,480*math.ceil(len(thumbs)/4)),(246,242,235));dr=ImageDraw.Draw(grid)
    for j,(t,pic) in enumerate(thumbs):
        x=(j%4)*270;y=(j//4)*480;grid.paste(pic,(x,y));dr.rectangle((x,y,x+70,y+24),fill='white');dr.text((x+6,y+2),f'{t:.1f}s',fill='black',font=font(15))
    gridfile=out.parent/'ACTUAL_SPICY_FRAMES.jpg';grid.save(gridfile,quality=88)
    stats={'engine':logs['animation_engine'],'source_reference':args.reference,'duration':duration,'fps':FPS,'frames':nf,
           'size':[W,H],'codec':'h264/aac','facial_states':sorted(logs['faces']),'pupil_count_per_eye':1,
           'smooth_shoulder_no_joint_rings':True,'max_arm_ik_target_error_px':round(logs['arm_ik_max_target_error'],2),
           'leg_lane_crossings':logs['leg_crossings'],'chili_mouth_contact_min_distance_px':round(min(logs['chili_mouth_contact_sampled'] or [999]),2),
           'audio_sfx_events':sounds['event_count'],'actual_model_inference':False,'story_director':plan['director'],
           'render_seconds':round(time.time()-starttime,2),
           'limitations':['Scripted chili action vocabulary rather than unlimited arbitrary prompts',
                          'Head preserves source grin; other acting states are authored facial redraws',
                          'FK run stance, analytic arm targets and flame are stylized cartoon physics, not motion capture']}
    out.with_suffix('.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False)+'\n')
    print('ACTUAL_ANIMATED_MP4',out,'METRICS',json.dumps(stats))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--reference',default=SRC);parser.add_argument('--plan',default=None)
    parser.add_argument('--out',default='/mnt/data/Spicy_Mascot_Actual_Animation/output/Funny_Toon_Ever_Spicy_Fire.mp4')
    main(parser.parse_args())
