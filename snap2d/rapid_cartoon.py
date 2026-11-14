#!/usr/bin/env python3
"""Original CPU 2D slapstick animation: editable shots, reusable vector characters.

No scraped video frames, proprietary assets, executable model output, paid APIs,
GPU models or user media are used. Cairo draws all frames into FFmpeg stdin.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import random
import re
import shutil
import subprocess
from pathlib import Path

import cairo

W, H = 540, 960
DURATION = 13.6
FPS = 30
PAPER = (0.716, 0.723, 0.629)
INK = (0.078, 0.092, 0.096)
CREAM = (0.913, 0.906, 0.812)
TEAL = (0.22, 0.46, 0.44)
ROSE = (0.68, 0.38, 0.33)
OCHRE = (0.71, 0.43, 0.21)
BLUE = (0.32, 0.37, 0.49)

SHOTS = [
    ('setup', 1.10), ('sneak', 1.65), ('grab', .85),
    ('glare', 1.15), ('chase', 1.65), ('trip', 1.35),
    ('shock', 1.10), ('catch', 1.50), ('stare', 1.45), ('button', 1.80),
]
ACTIONS = {name for name, _ in SHOTS}


def clamp(x, lo=0, hi=1): return max(lo, min(hi, x))
def mix(a, b, q): return a + (b-a)*q

def ease(t):
    t=clamp(t)
    return t*t*(3-2*t)

def overshoot(t):
    t=clamp(t)
    c1=1.70158
    return 1+c1* (t-1)**3+(c1+1)*(t-1)**2


def color(ctx,c,a=1): ctx.set_source_rgba(*(c+(a,)))

def stroke(ctx, linewidth=4, c=INK):
    ctx.set_line_width(linewidth)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    color(ctx,c);ctx.stroke()

def path(ctx,points,weight=4, c=INK):
    ctx.new_path();ctx.move_to(*points[0]);[ctx.line_to(*p) for p in points[1:]];stroke(ctx,weight,c)

def fill_path(ctx, pts, fill, line=INK,weight=3):
    ctx.new_path();ctx.move_to(*pts[0]);[ctx.line_to(*p) for p in pts[1:]];ctx.close_path()
    color(ctx,fill);ctx.fill_preserve()
    if line is not None:stroke(ctx,weight,line)
    else: ctx.new_path()

def ellipse(ctx,x,y,rx,ry,fill=None,line=INK,width=4):
    ctx.save();ctx.translate(x,y);ctx.scale(rx,ry)
    ctx.new_path();ctx.arc(0,0,1,0,2*math.pi)
    if fill is not None:
        color(ctx,fill);ctx.fill_preserve()
    if line is not None:
        ctx.set_line_width(width/max(rx,ry));color(ctx,line);ctx.stroke()
    else: ctx.new_path()
    ctx.restore()

def rect(ctx,x,y,w,h,fill,line=None,lw=3):
    ctx.new_path();ctx.rectangle(x,y,w,h)
    if fill is not None:
        color(ctx,fill);ctx.fill_preserve()
    if line is not None:stroke(ctx,lw,line)
    else:ctx.new_path()

def curve(ctx,pts,weight=4,c=INK):
    ctx.new_path();ctx.move_to(*pts[0]);ctx.curve_to(*pts[1],*pts[2],*pts[3]);stroke(ctx,weight,c)


def bg(ctx, seconds, shot='setup'):
    # Matte handdrawn bedroom-kitchen studio: original colors + independently authored props.
    rect(ctx,0,0,W,H,PAPER)
    rect(ctx,0,771,W,189,(.55,.55,.46))
    # paper grain and subtle hand-inked wall texture
    r = random.Random(11)
    for j in range(380):
        x=r.randrange(W);y=r.randrange(H)
        a=r.uniform(.02,.08)
        color(ctx,(.12,.14,.12),a)
        ctx.rectangle(x,y,r.choice((1,2)),r.choice((1,2,3)));ctx.fill()
    path(ctx,[(0,772),(540,772)],2,(.32,.34,.31))
    # door on right
    fill_path(ctx,[(383,166),(547,125),(544,757),(391,780)],(.36,.40,.47),INK,6)
    fill_path(ctx,[(406,183),(506,165),(507,738),(412,743)],(.48,.53,.57),INK,4)
    fill_path(ctx,[(424,209),(485,197),(487,350),(421,355)],(.38,.42,.48),INK,3)
    fill_path(ctx,[(425,399),(486,392),(487,709),(427,711)],(.39,.43,.49),INK,3)
    ellipse(ctx,487,546,8,12,(.90,.78,.39),INK,3)
    # hanging window / clock
    ellipse(ctx,106,181,46,46,(.83,.79,.65),INK,5)
    path(ctx,[(106,181),(108,149)],3)
    path(ctx,[(106,181),(128,195)],3)
    ellipse(ctx,106,181,5,5,INK,None)
    # shelf, leaf jar, poster
    rect(ctx,30,384,170,14,(.47,.41,.34),INK,3)
    rect(ctx,49,335,36,49,(.72,.52,.32),INK,2)
    for j in range(4):
        x=58+j*6
        curve(ctx,[(x,344),(x-17,307),(x+16,308),(x+3,296)],3,(.29,.42,.33))
    rect(ctx,106,349,58,35,(.80,.76,.68),INK,2)
    path(ctx,[(118,362),(150,360)],2)
    path(ctx,[(118,369),(147,367)],2)
    # table foreground: narrow rather than static panel
    fill_path(ctx,[(85,685),(269,675),(303,711),(79,732)],(.52,.42,.34),INK,6)
    fill_path(ctx,[(87,722),(302,709),(307,731),(83,748)],(.43,.35,.31),INK,4)
    path(ctx,[(97,742),(95,848)],9)
    path(ctx,[(285,733),(290,838)],9)
    # shallow plate
    ellipse(ctx,195,683,70,14,(.84,.82,.67),INK,3)
    ellipse(ctx,195,683,45,7,(.68,.65,.50),None)


def cookie(ctx,x,y,s=1,angle=0,visible=True):
    if not visible: return
    ctx.save();ctx.translate(x,y);ctx.rotate(angle);ctx.scale(s,s)
    ellipse(ctx,0,0,29,24,OCHRE,INK,4)
    for xx,yy,rr in [(-12,-6,4),(3,6,5),(14,-5,4),(-4,-15,3)]:
        ellipse(ctx,xx,yy,rr,rr,(.29,.20,.15),None)
    curve(ctx,[(-22,6),(-10,23),(4,25),(13,13)],2,(.86,.58,.33))
    ctx.restore()


def speed_lines(ctx, x,y, amount=14, angle=0):
    rand=random.Random(18)
    for i in range(amount):
        q=(i+1)/amount
        sx=x-rand.uniform(35,170)-q*38
        sy=y+rand.uniform(-160,165)
        path(ctx,[(sx,sy),(sx-rand.randrange(60,170),sy+rand.uniform(-14,15))],rand.choice([2.2,3.0,4.5]),(.34,.35,.30))


def face(ctx, name, expression, age=0, blink=False, mouth='auto', look=0, tilt=0, exaggerated=0):
    """Local coords, face center (0,0), radius ~54; varying expressions and eyegaze.

    Body and expression remain consistent across shots and zooms.
    """
    ctx.save();ctx.rotate(tilt)
    c=CREAM if name=='pip' else (.88,.86,.76)
    ellipse(ctx,0,0,54,59,c,INK,5)
    # hair silhouette and tuft: original distinguishing features
    if name=='pip':
        curve(ctx,[(-35,-42),(-28,-69),(-6,-67),(6,-58)],5)
        curve(ctx,[(-14,-53),(0,-86),(16,-66),(23,-53)],4)
        ellipse(ctx,40,17,10,12,c,INK,3)
    else:
        curve(ctx,[(-42,-40),(-19,-74),(16,-65),(37,-40)],5)
        curve(ctx,[(-20,-55),(-11,-81),(4,-70),(9,-60)],4)
        curve(ctx,[(2,-61),(21,-81),(29,-63),(33,-49)],4)
        ellipse(ctx,-46,13,8,13,c,INK,3)
    shocked=expression in {'shock','panic'}
    angry=expression in {'angry','glare'}
    smug=expression=='smug'
    if blink:
        path(ctx,[(-36,-1),(-5,2)],4)
        path(ctx,[(12,2),(37,-1)],4)
    else:
        erx = 21 if shocked else 17
        ery = 26 if shocked else 19
        for ex in (-20,21):
            ellipse(ctx,ex,-8,erx,ery,(.975,.97,.90),INK,4)
            pup=6 if shocked else 5
            px=ex + (0 if shocked else look*6)
            py=-7 + (5 if angry else 0)
            ellipse(ctx,px,py,pup,pup,INK,None)
            if shocked: ellipse(ctx,px-2,py-2,1.9,1.9,(1,1,1),None)
        if angry:
            path(ctx,[(-39,-39),(-5,-23)],7)
            path(ctx,[(9,-24),(40,-41)],7)
        elif shocked:
            curve(ctx,[(-37,-49),(-22,-62),(-9,-57),(-1,-48)],4)
            curve(ctx,[(9,-47),(19,-61),(37,-53),(43,-46)],4)
        elif smug:
            path(ctx,[(-38,-32),(-9,-35)],4)
            path(ctx,[(12,-34),(39,-28)],4)
        else:
            path(ctx,[(-37,-34),(-8,-36)],4)
            path(ctx,[(11,-34),(39,-33)],4)
    ellipse(ctx,0,21,7,6,(.82,.78,.69),INK,2.5)
    if mouth!='auto':expression=mouth
    if expression in ('shock','panic'):
        ellipse(ctx,7,39,16,21,(.24,.14,.13),INK,4)
        ellipse(ctx,9,47,8,6,(.74,.32,.34),None)
    elif expression in ('angry','glare'):
        ctx.new_path();ctx.move_to(-19,40);ctx.curve_to(-1,32,9,31,24,44);stroke(ctx,5)
    elif expression=='smug':
        ctx.new_path();ctx.move_to(-17,34);ctx.curve_to(5,53,19,48,31,37);stroke(ctx,4)
        path(ctx,[(26,37),(32,32)],3)
    elif expression in ('sneak','focus'):
        curve(ctx,[(-11,38),(3,34),(11,38),(16,37)],3)
    elif expression=='grin':
        ellipse(ctx,1,39,21,12,(.29,.19,.16),INK,3)
        rect(ctx,-12,32,26,5,(.99,.96,.85),None)
    else:
        curve(ctx,[(-15,35),(0,44),(14,41),(21,34)],3)
    if shocked:
        for x in (-47,43):
            path(ctx,[(x,62),(x+(8 if x>0 else -8),78)],3)
    ctx.restore()


def actor(ctx,who,x,feet,pose='idle',t=0,expression='normal',scale=1,arm=None,lean=0,look=0):
    ctx.save();ctx.translate(x,feet);ctx.scale(scale,scale);ctx.rotate(lean)
    running=pose in ('run','chase')
    walking=pose=='sneak'
    phase=t*19 if running else t*11
    stride=math.sin(phase)
    bob=2*math.cos(phase*2) if running else (2.5*math.sin(phase*2) if walking else 1.8*math.sin(t*4))
    head_y=-184+bob
    # legs hinged: ankle relative to moving hip
    hip=(-1,-91)
    if running:
        leftfoot=(-36+42*stride,0-30*max(0,-stride))
        rightfoot=(35-42*stride,0-30*max(0,stride))
        lk=(-20+25*stride,-38);rk=(20-25*stride,-38)
    elif pose=='trip':
        leftfoot=(-88,-18);rightfoot=(88,-67);lk=(-51,-58);rk=(53,-43)
    else:
        leftfoot=(-24+12*stride if walking else -25,0)
        rightfoot=(24-12*stride if walking else 25,0)
        lk=(-17+6*stride,-43);rk=(16-6*stride,-43)
    path(ctx,[hip,lk,leftfoot],5.8)
    path(ctx,[hip,rk,rightfoot],5.8)
    for fx,fy in (leftfoot,rightfoot):
        ctx.new_path();ctx.move_to(fx-13,fy);ctx.curve_to(fx-19,fy+10,fx+15,fy+12,fx+18,fy+2);stroke(ctx,4)
    # torso
    shirt=TEAL if who=='pip' else ROSE
    ctx.new_path();ctx.move_to(-17,-160);ctx.curve_to(-38,-145,-29,-116,-16,-94)
    ctx.line_to(22,-92);ctx.curve_to(34,-127,28,-147,15,-160);ctx.close_path()
    color(ctx,shirt);ctx.fill_preserve();stroke(ctx,5)
    path(ctx,[(-7,-102),(14,-102)],2,(.80,.76,.64))
    # animated arms and palms
    if pose=='handsup' or pose=='trip':
        a1=[(-18,-145),(-53,-186),(-87,-230)]
        a2=[(18,-145),(61,-191),(84,-219)]
    elif pose in ('run','chase'):
        a1=[(-18,-145),(-57,-129-15*stride),(-45,-87-35*stride)]
        a2=[(20,-145),(57,-128+15*stride),(50,-80+35*stride)]
    elif pose in ('grab','reach'):
        a1=[(-18,-145),(-48,-127),(-49,-93)]
        a2=[(18,-147),(47,-156),(84,-172)]
    elif pose=='sneak':
        a1=[(-18,-145),(-46,-126),(-29,-101+5*stride)]
        a2=[(20,-142),(43,-126),(43,-105-6*stride)]
    elif pose=='glare':
        a1=[(-18,-145),(-58,-125),(-54,-101)]
        a2=[(20,-143),(59,-128),(44,-104)]
    else:
        a1=[(-18,-145),(-35,-115),(-39,-92)]
        a2=[(20,-145),(37,-115),(39,-96)]
    if arm=='point': a2=[(20,-145),(48,-165),(100,-174)]
    for armpts in (a1,a2):
        path(ctx,armpts,5.2)
        ellipse(ctx,*armpts[-1],6.5,6.5,CREAM,INK,3)
    ctx.save();ctx.translate(0,head_y)
    face(ctx,who,expression,blink=bool(.87<((t*1.7)%4)<.97),look=look)
    ctx.restore()
    ctx.restore()


def cat(ctx,x,y,t,expression='sleep'):
    ctx.save();ctx.translate(x,y)
    # tail swishes
    curve(ctx,[(41,57),(90,37+8*math.sin(t*4)),(91,101),(72,104+9*math.sin(t*6))],8)
    ellipse(ctx,0,43,65,70,(.48,.49,.48),INK,6)
    fill_path(ctx,[(-41,-11),(-47,-65),(-12,-35)],(.50,.50,.49),INK,5)
    fill_path(ctx,[(11,-35),(46,-68),(41,-8)],(.50,.50,.49),INK,5)
    ellipse(ctx,0,-1,57,49,(.60,.60,.57),INK,5)
    if expression=='catch':
        ellipse(ctx,-21,-8,14,18,(.94,.92,.76),INK,3)
        ellipse(ctx,23,-8,14,18,(.94,.92,.76),INK,3)
        ellipse(ctx,-21,-7,5,10,INK,None)
        ellipse(ctx,23,-7,5,10,INK,None)
        ellipse(ctx,1,25,22,28,(.24,.19,.20),INK,3)
    else:
        curve(ctx,[(-38,-9),(-28,1),(-21,1),(-7,-6)],5)
        curve(ctx,[(9,-5),(19,3),(28,2),(36,-8)],5)
        curve(ctx,[(-12,21),(-2,30),(8,30),(18,21)],3)
    fill_path(ctx,[(-6,12),(5,12),(-1,21)],(.88,.55,.52),INK,2)
    for side in (-1,1):
        path(ctx,[(side*7,22),(side*48,14)],2)
        path(ctx,[(side*8,28),(side*49,33)],2)
    ctx.restore()


def ink_burst(ctx,ox,oy,r=110,lines=20):
    rnd=random.Random(81)
    for i in range(lines):
        a=2*math.pi*i/lines
        l=rnd.uniform(24,60)
        x=ox+math.cos(a)*r;y=oy+math.sin(a)*r
        path(ctx,[(x,y),(x+math.cos(a)*l,y+math.sin(a)*l)],rnd.uniform(2,5))


def card(ctx, text, y):
    ctx.select_font_face('DejaVu Sans',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(36)
    ext=ctx.text_extents(text)
    x=(W-ext.width)/2-ext.x_bearing
    color(ctx,INK);ctx.move_to(x+2,y+2);ctx.show_text(text)
    color(ctx,(.99,.94,.79));ctx.move_to(x,y);ctx.show_text(text)


def frame(ctx,t,shot,progress,duration):
    """Draw a changing frame. Timeline is authored and values are numeric only."""
    # Shot cuts + smears, no slow slide-show.
    p=clamp(progress)
    ctx.save()
    if shot in ('glare','shock','stare'):
        bg(ctx,t,shot)
        if shot=='glare':
            scale=mix(1.7,2.75,overshoot(clamp(p/.18)))
            shake=7*(1-p)*math.sin(t*73)
            ctx.translate(W/2+shake,410);ctx.scale(scale,scale)
            actor(ctx,'bobo',0,185,'glare',t,'glare',lean=-.06)
            ctx.restore()
            return
        if shot=='shock':
            scale=mix(1.5,3.2,overshoot(clamp(p/.12)))
            shake=8*(1-p)*math.sin(t*87)
            ctx.translate(W/2+shake,435);ctx.scale(scale,scale)
            actor(ctx,'pip',0,180,'handsup',t,'shock',lean=.11)
            ctx.restore()
            return
        if shot=='stare':
            scale=mix(1.1,1.9,ease(min(1,p*5)))
            shake=6*math.sin(t*69)*(1-p)
            ctx.translate(W/2+shake,493);ctx.scale(scale,scale)
            actor(ctx,'pip',-87,120,'handsup',t,'shock',scale=1.07,lean=-.1)
            actor(ctx,'bobo',92,130,'glare',t,'shock',scale=1.14,lean=.13)
            ctx.restore()
            return
    # layered background continuous camera
    bg(ctx,t,shot)
    if shot=='setup':
        cookie(ctx,194,682)
        actor(ctx,'pip',73,860,'idle',t,'sneak',scale=.92,lean=.01,look=1)
        actor(ctx,'bobo',434,870,'idle',t,'normal',scale=1.1,look=-1)
        cat(ctx,450,826,t,'sleep')
    elif shot=='sneak':
        cookie(ctx,194,682)
        x=mix(65,177,ease(p))
        actor(ctx,'pip',x,864,'sneak' if p<.82 else 'reach',t,'sneak',scale=.92,lean=.06,look=1)
        actor(ctx,'bobo',451,868,'idle',t,'normal',scale=1.06,look=-1)
        cat(ctx,455,846,t,'sleep')
        for xline in (48,62):
            path(ctx,[(x-xline,705),(x-xline-28,706)],2.5,(.37,.39,.32))
    elif shot=='grab':
        # purposefully abrupt insert shot: hand, plate and cookie in extreme closeup
        ctx.save();ctx.translate(-235,-580);ctx.scale(2.65,2.65)
        ellipse(ctx,195,683,70,14,(.81,.78,.62),INK,4)
        grabbed=p>.55
        cookie(ctx,195+105*ease(clamp((p-.5)*2)),676-90*ease(clamp((p-.5)*2)),1.1)
        path(ctx,[(55,670),(115+120*ease(p),658),(170+120*ease(p),664)],10)
        ellipse(ctx,170+120*ease(p),664,15,11,CREAM,INK,4)
        if grabbed: ink_burst(ctx,270,575,28,10)
        ctx.restore()
    elif shot=='chase':
        x=mix(88,390,ease(p))
        speed_lines(ctx,270,641,18)
        actor(ctx,'pip',x,858,'run',t+.7,'grin',scale=.94,lean=-.17)
        actor(ctx,'bobo',x-178,860,'chase',t,'angry',scale=1.10,lean=-.18)
        cookie(ctx,x+61,566,.72,-.23)
        if p>.45:
            ink_burst(ctx,480,620,18,8)
    elif shot=='trip':
        # squash/stretch and anticipation at the start, projectile takes over after stumble
        q=ease(clamp((p-.13)*2.7))
        x=mix(210,255,q)
        actor(ctx,'pip',x,858,'trip' if p>.21 else 'run',t,'shock',scale=mix(.96,1.1,q),lean=mix(-.18,-.84,q))
        actor(ctx,'bobo',78,856,'chase',t,'shock',scale=1.03,lean=-.12)
        px=mix(305,438,q);py=543-300*math.sin(math.pi*clamp((p+.08)*.9))
        cookie(ctx,px,py,1.0,t*8)
        path(ctx,[(240,774),(317,772),(374,775)],2,(.40,.35,.28))
        ink_burst(ctx,280,755,35,12)
    elif shot=='catch':
        q=ease(clamp((p-.06)/.66))
        cat(ctx,278,696,t,'catch' if p<.68 else 'smug')
        fy=mix(268,698,q)
        cookie(ctx,277,fy,.95,t*5,visible=p<.80)
        if .58<p<.83:ink_burst(ctx,273,684,62,14)
        # dark foreground plinth cat sits on
        rect(ctx,90,757,351,28,(.54,.43,.34),INK,5)
    elif shot=='button':
        cat(ctx,270,707,t,'smug')
        cookie(ctx,281,738,.48,0)
        ctx.save()
        # subtle loopable involuntary body slump
        actor(ctx,'pip',64,857,'idle',t,'angry',scale=.80,lean=-.09)
        actor(ctx,'bobo',475,841,'idle',t,'shock',scale=.78,lean=.1)
        ctx.restore()
        card(ctx,'NOT FOR YOU.',246)
        rect(ctx,90,770,350,30,(.53,.42,.35),INK,5)
    ctx.restore()


def storyboard(prompt='The last cookie, a funny fast 2D stick figure chase'):
    # Deterministic prompt-to-timeline support: recognized action beats are data,
    # never generated/executed Python, SVG scripts or shell commands.
    if not isinstance(prompt,str) or not 1 <= len(prompt.strip()) <= 800:
        raise ValueError('Prompt must be 1–800 characters')
    chosen=SHOTS
    sequence=re.search(r'(?im)(?:^|\s)(?:shots|sequence|beats)\s*:\s*([a-z_,\s-]+)',prompt)
    if sequence:
        allowed={n:d for n,d in SHOTS}
        actions=[x.strip().lower() for x in sequence.group(1).split(',') if x.strip()]
        if not 1 <= len(actions) <= 12 or any(action not in allowed for action in actions):
            raise ValueError('Custom beat list must contain 1-12 supported action names')
        chosen=[('setup',allowed['setup'])]+[(x,allowed[x]) for x in actions]+[('button',allowed['button'])]
    start=0;shots=[]
    for name,duration in chosen:
        shots.append({'name':name,'start':round(start,3),'duration':duration,'action':name,'camera': 'reaction-closeup' if name in {'glare','shock','stare'} else 'composed'})
        start+=duration
    return {'version':1,'prompt':prompt,'title':'THE LAST COOKIE','style':'original-hand-inked-comedy','fps':30,
            'width':540,'height':960,'sound':False,'shots':shots}


def validate(board):
    if not isinstance(board,dict) or board.get('version') != 1: raise ValueError('version 1 required')
    if (board.get('width'),board.get('height')) not in ((540,960),(360,640)): raise ValueError('invalid 9:16 dimensions')
    fps=board.get('fps')
    if type(fps)!=int or fps not in (12,24,30):raise ValueError('invalid FPS')
    shots=board.get('shots')
    if not isinstance(shots,list) or not 1<=len(shots)<=20: raise ValueError('need 1-20 shots')
    last=0.
    for s in shots:
        if not isinstance(s,dict) or s.get('name') not in ACTIONS:raise ValueError('unsupported authored action')
        duration=s.get('duration');start=s.get('start')
        if type(duration) not in (float,int) or not math.isfinite(duration) or not .2<=duration<=5:raise ValueError('bad duration')
        if type(start) not in (int,float) or not math.isfinite(start) or abs(start-last)>0.001:raise ValueError('shots need contiguous start times')
        last+=duration
    if last>40: raise ValueError('max 40 seconds on CPU')
    return round(last,3)


def render(board,output,preview=None):
    duration=validate(board);output=Path(output)
    if output.exists():raise FileExistsError(output)
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg:raise RuntimeError('FFmpeg is required; install it first')
    w=board['width'];h=board['height'];fps=board['fps']
    # Reuse one Cairo surface and direct ARGB32 -> BGRA raw frames; memory <= ~2MB per frame.
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
    ctx=cairo.Context(surface)
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','bgra',
         '-video_size',f'{w}x{h}','-framerate',str(fps),'-i','pipe:0','-an',
         '-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    output.parent.mkdir(parents=True,exist_ok=True)
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    n=round(duration*fps)
    shot_idx=0
    try:
        for i in range(n):
            current_t=i/fps
            while shot_idx < len(board['shots'])-1 and current_t>=board['shots'][shot_idx]['start']+board['shots'][shot_idx]['duration']-.0001:
                shot_idx+=1
            shot=board['shots'][shot_idx]
            t=(current_t-shot['start'])/shot['duration']
            ctx.save();ctx.scale(w/W,h/H)
            frame(ctx,current_t,shot['name'],t,shot['duration'])
            ctx.restore();surface.flush()
            if preview is not None and i==round(1.8*fps):
                surface.write_to_png(str(preview))
            proc.stdin.write(surface.get_data())
        proc.stdin.close()
        err=proc.stderr.read().decode('utf8','replace')
        if proc.wait()!=0:raise RuntimeError(err)
    except Exception:
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
        proc.kill();proc.wait();raise
    finally:
        if proc.stderr and not proc.stderr.closed:proc.stderr.close()
    return n


def main():
    ap=argparse.ArgumentParser(description='Original pose-to-pose vector cartoon CPU renderer')
    ap.add_argument('--prompt',default='A funny quick stickman story about the last cookie')
    ap.add_argument('--storyboard',help='Use an editable data-only JSON storyboard')
    ap.add_argument('--output',default='output/last-cookie.mp4')
    ap.add_argument('--save-storyboard',default=None)
    ap.add_argument('--preview',default=None)
    ap.add_argument('--width',type=int,default=540)
    ap.add_argument('--fps',type=int,default=30)
    args=ap.parse_args()
    board=json.loads(Path(args.storyboard).read_text()) if args.storyboard else storyboard(args.prompt)
    if not args.storyboard:
        board['width']=args.width;board['height']=int(args.width*16/9);board['fps']=args.fps
    validate(board)
    if args.save_storyboard:
        dest=Path(args.save_storyboard)
        if dest.exists():raise FileExistsError(dest)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(board,indent=2,ensure_ascii=False)+'\n')
    frames=render(board,Path(args.output),Path(args.preview) if args.preview else None)
    print('Rendered',frames,'frames to',args.output)

if __name__=='__main__':main()
