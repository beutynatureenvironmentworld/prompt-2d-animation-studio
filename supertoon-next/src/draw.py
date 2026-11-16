"""Procedural 2D Super Test director: original vector cartoon, true joint motion and camera.

No static face overlay: eye/mouth/limb coordinates are evaluated anew for every frame.
Works on Python+Cairo and FFmpeg on CPU. Scenes are safe declarative JSON.
"""
from __future__ import annotations
import math,random
import cairo

TAU=math.tau
P={'ink':'#22212b','bone':'#f9ead9','teal':'#21b7a8','teal_dark':'#117c78','orange':'#f8a940','cream':'#fff7e8','gray':'#535667','silver':'#d4dfdf','ground':'#78bf70','sky':'#9bdcf6','bg':'#f5ead7'}

def rgb(c):
    if isinstance(c,tuple):return c
    return tuple(int(c[i:i+2],16)/255 for i in (1,3,5))
def col(c,hex,a=1):col3=rgb(hex);c.set_source_rgba(*col3,a)
def path(c,pts,closed=False):
    c.new_path();c.move_to(*pts[0]);[c.line_to(*p) for p in pts[1:]]
    if closed:c.close_path()
def fill(c,pigment,stroke=None,width=3):
    col(c,pigment)
    if stroke:
        c.fill_preserve();col(c,stroke);c.set_line_width(width);c.set_line_join(cairo.LINE_JOIN_ROUND);c.stroke()
    else:c.fill()
def stroke(c,pigment='#22212b',width=3):
    col(c,pigment);c.set_line_width(width);c.set_line_cap(cairo.LINE_CAP_ROUND);c.set_line_join(cairo.LINE_JOIN_ROUND);c.stroke()
def rect(c,x,y,w,h,colour,edge=None,lw=3,r=0):
    c.new_path()
    if r:
        r=min(r,w/2,h/2)
        c.arc(x+w-r,y+r,r,-math.pi/2,0);c.arc(x+w-r,y+h-r,r,0,math.pi/2)
        c.arc(x+r,y+h-r,r,math.pi/2,math.pi);c.arc(x+r,y+r,r,math.pi,3*math.pi/2)
        c.close_path()
    else:c.rectangle(x,y,w,h)
    fill(c,colour,edge,lw)
def oval(c,x,y,rx,ry,colour,edge=None,lw=3):
    c.save();c.translate(x,y);c.scale(max(rx,.01),max(ry,.01));c.new_path();c.arc(0,0,1,0,TAU);c.restore();fill(c,colour,edge,lw)
def line(c,pts,colour='#22212b',lw=3):path(c,pts);stroke(c,colour,lw)
def bez(c,a,b,c1,d,colour='#22212b',lw=3):
    c.new_path();c.move_to(*a);c.curve_to(*b,*c1,*d);stroke(c,colour,lw)
def capsule(c,a,b,thick=10,paint='#f9ead9'):
    path(c,[a,b]);stroke(c,P['ink'],thick+5)
    path(c,[a,b]);stroke(c,paint,thick)
    oval(c,*a,thick/2,thick/2,paint)
    oval(c,*b,thick/2,thick/2,paint)
def clamp(x,a=0,b=1):return max(a,min(b,x))
def ease(p):p=clamp(p);return p*p*(3-2*p)
def ik(a,b,l=47,m=47,bend=1):
    x,y=b[0]-a[0],b[1]-a[1];d=max(.01,math.hypot(x,y));dst=min(l+m-1,max(abs(l-m)+1,d));u=(l*l-m*m+dst*dst)/(2*dst);v=math.sqrt(max(0,l*l-u*u))*bend
    return (a[0]+(u*x-v*y)/d,a[1]+(u*y+v*x)/d)

def cloud(c,x,y,s=1):
    c.save();c.translate(x,y);c.scale(s,s)
    oval(c,0,0,35,10,'#f8fcff');oval(c,-15,-6,15,12,'#f8fcff');oval(c,12,-7,23,14,'#f8fcff');c.restore()

def background(c,setting,t):
    gr=cairo.LinearGradient(0,0,0,320)
    if setting in ('park','street'):
        gr.add_color_stop_rgb(0,.56,.81,.96);gr.add_color_stop_rgb(1,.96,.95,.82)
    else:
        gr.add_color_stop_rgb(0,.92,.90,.85);gr.add_color_stop_rgb(1,.98,.95,.88)
    c.rectangle(-200,0,1250,400);c.set_source(gr);c.fill()
    if setting in ('park','street'):
        for i in range(7):cloud(c,-70+i*165+math.sin(t*.2+i)*5,55+(i*49)%83,.6+.15*(i%3))
        for i in range(-2,16):
            x=i*91
            if setting=='street':
                rect(c,x,134+(i*7)%45,76,165,'#99a5b0',P['ink'],2,2)
                for j in range(3):rect(c,x+13+j*21,157+(i*7)%45,10,14,'#f6e2ad',P['ink'],1)
            else:
                line(c,[(x,260),(x+2,193+(i%2)*21)],'#705545',7)
                for dx,dy in ((-17,-7),(0,-20),(15,0)):
                    oval(c,x+dx,189+(i%2)*21+dy,23,24,'#4d9666','#2e6e52',2)
        rect(c,-200,280,1250,120,'#75c383');rect(c,-200,299,1250,8,'#65a96f')
    else:
        line(c,[(-200,285),(1030,285)],'#88877e',3)
        rect(c,-200,286,1250,115,'#c1b3a1')
        for x in range(-100,1200,60):line(c,[(x,286),(x-35,395)],'#a99e90',1)
        if setting=='school':
            rect(c,60,67,205,120,'#335a51',P['ink'],5,4)
            for i in range(4):rect(c,85+i*41,219,33,7,'#82684e')
            rect(c,75,225,6,65,'#82684e');rect(c,203,225,6,65,'#82684e')
        elif setting=='office':
            rect(c,50,178,248,12,'#8b725f',P['ink'],3);rect(c,69,191,10,100,'#8b725f')
            rect(c,264,191,10,100,'#8b725f')
            rect(c,156,139,64,40,'#a7b8bc',P['ink'],4,3)
        elif setting=='kitchen':
            for x in (20,95,170,245):
                rect(c,x,174,72,90,'#d6e4d9',P['ink'],3)
                oval(c,x+35,210,5,5,'#6f7773')
            rect(c,20,156,304,9,'#8b735e')
        elif setting=='bedroom':
            rect(c,30,211,240,58,'#8eabc9',P['ink'],5,6)
            rect(c,30,187,55,36,'#f9f8ed',P['ink'],4,4)
            rect(c,45,271,12,23,'#77655e');rect(c,248,271,12,23,'#77655e')
    if setting=='toilet':
        # An actual drawn funny toilet stall door, centered near the character's final x.
        rect(c,385,81,137,216,'#b7c0c0',P['ink'],6,5)
        rect(c,398,98,111,188,'#f0f4ee',P['ink'],4,3)
        rect(c,410,112,81,159,'#dce8e5',P['ink'],2,2)
        oval(c,489,201,6,6,P['orange'],P['ink'],2)
        rect(c,397,49,116,36,'#fdfbf5',P['ink'],4,5)
        col(c,P['ink']);c.select_font_face('Sans',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD);c.set_font_size(18);c.move_to(422,73);c.show_text('TOILET')
    if setting=='park':
        rect(c,395,239,118,9,'#9e6745',P['ink'],2)
        for x in (414,486):line(c,[(x,248),(x,286)],'#6b503b',5)

def character_scene_state(plan,t):
    beats=plan['beats'];b=beats[-1]
    for e in beats:
        if t<e['end']:b=e;break
    action=b['action'];z=clamp((t-b['start'])/(b['end']-b['start']));period=math.sin(TAU*(t-b['start'])*3.7)
    if action=='notice':x=150;y=0;tilt=0
    elif action=='sprint':x=130+240*ease(z);y=-7*abs(period);tilt=.16
    elif action=='knock':x=352;y=0;tilt=.09
    elif action=='jump':x=230+110*ease(z);y=-82*math.sin(math.pi*z);tilt=-.06
    elif action=='slip':x=365-85*ease(z);y=15*ease(z);tilt=-.95*ease(z)
    elif action=='panic':x=365-35*ease(z);y=-22*math.sin(math.pi*z);tilt=-.17
    elif action=='recover':x=330-35*ease(z);y=0;tilt=-.08*(1-ease(z))
    elif action=='laugh':x=315;y=-6*abs(math.sin(t*9));tilt=.04*math.sin(t*9)
    elif action=='dance':x=260+35*math.sin(t*4);y=-12*abs(math.sin(t*8));tilt=.12*math.sin(t*6)
    else:x=310;y=0;tilt=.03*math.sin(t*4)
    return action,z,x,290+y,tilt,period

def limbs(c,action,t,z,phase,cat=False):
    # Complete unique joint geometry per frame (not static PNG sprite swapping).
    hip_y=0
    for side,offs in [(-1,math.pi),(1,0)]:
        p=math.sin(TAU*t*3.7+offs)
        if action=='sprint':
            ankle=(side*13 + 45*p,81-35*max(0,p))
        elif action=='jump':
            ankle=(side*19+20*side,54-13*math.sin(math.pi*z))
        elif action=='slip':
            ankle=(side*20+65*side*z,83-22*z)
        elif action=='panic':
            ankle=(side*31,73-27*math.sin(math.pi*z))
        elif action=='dance':
            ankle=(side*24+33*p,80-25*max(0,p))
        else:ankle=(side*20,83)
        h=(side*12,0);k=ik(h,ankle,46,47,bend=-side)
        leg_colour=P['orange'] if cat else P['gray']
        capsule(c,h,k,10,leg_colour);capsule(c,k,ankle,9,leg_colour)
        oval(c,ankle[0]+7,ankle[1]+3,18,8,P['cream'] if cat else P['ink'],P['ink'],2)
    # Arms, shoulders / elbows / wrists entirely separate from body.
    for side,offs in [(-1,0),(1,math.pi)]:
        p=math.sin(TAU*t*3.7+offs)
        shoulder=(side*25,-66)
        if action=='sprint':elbow=(side*46 + 12*p,-43+26*p);wrist=(side*56+30*p,-17+43*p)
        elif action=='knock' and side==1:
            v=max(0,math.sin(z*TAU*4));elbow=(52,-108);wrist=(84+18*v,-120)
        elif action in ('panic','slip','jump'):
            v=10*math.sin(t*14+side)
            elbow=(side*(55+v),-111);wrist=(side*(73+v),-153)
        elif action=='point' and side==1:elbow=(61,-90);wrist=(91,-106)
        elif action=='wave' and side==1:elbow=(54,-108);wrist=(67+12*math.sin(t*13),-156)
        elif action=='dance':elbow=(side*(50+10*p),-90-20*p);wrist=(side*(70+15*p),-121-20*p)
        else:elbow=(side*42,-49);wrist=(side*47,-19+8*math.sin(t*3+side))
        colour=P['orange'] if cat else P['teal']
        capsule(c,shoulder,elbow,11,colour);capsule(c,elbow,wrist,10,colour)
        oval(c,*wrist,8,8,P['cream'],P['ink'],2)

def draw_human(c,t,action,z,tilt,phase,kind='boy'):
    # Character local origin is pelvis at (0,0), head at y=-139.
    c.save();c.rotate(tilt)
    if action=='jump':c.scale(1-.1*math.sin(math.pi*z),1+.16*math.sin(math.pi*z))
    if action in ('slip','panic'):c.scale(1+.04*math.sin(t*18),1-.05*math.sin(t*18))
    limbs(c,action,t,z,phase)
    # Rounded torso, hoodie jacket with clean high-contrast outline.
    c.new_path();c.move_to(-27,-79);c.curve_to(-39,-63,-35,-14,-27,-4)
    c.curve_to(0,7,24,7,32,-9);c.curve_to(41,-48,35,-70,26,-79);c.close_path()
    jacket=P['teal'] if kind in ('boy','girl') else '#ececf4'
    fill(c,jacket,P['ink'],4)
    bez(c,(-18,-11),(-2,-4),(14,-3),(22,-12),P['ink'],2)
    line(c,[(-6,-79),(-7,-58)],P['cream'],2);line(c,[(6,-79),(7,-56)],P['cream'],2)
    # Neck connects torso and head; one head only, no face sprite overlays.
    capsule(c,(0,-77),(0,-105),12,'#f4c9a7')
    head_skin = '#ffffff' if kind=='mascot' else '#f4c9a7'
    oval(c,0,-139,36,39,head_skin,P['ink'],4)
    if kind=='girl':
        oval(c,-30,-164,11,18,'#3d3446',P['ink'],2)
        oval(c,29,-164,11,18,'#3d3446',P['ink'],2)
    if kind!='mascot':
        c.new_path();c.move_to(-34,-149)
        for px,py in [(-39,-171),(-19,-176),(-25,-194),(-4,-179),(8,-199),(13,-177),(37,-186),(33,-151),(17,-166),(0,-167),(-17,-160)]:c.line_to(px,py)
        c.close_path();fill(c,'#302d38')
    # Eyes: blinking and looking ahead; single eye/pupil each side.
    blink=(t%2.65)<.085 and action not in ('panic','slip')
    eyesize=7.5 if action in ('panic','slip') else 5.5
    for side in (-1,1):
        x=side*12;col(c,P['ink']);c.set_line_width(2)
        bez(c,(x-6,-158),(x-3,-164),(x+3,-164),(x+7,-157),P['ink'],2.4)
        if blink:line(c,[(x-5,-146),(x+5,-146)],P['ink'],2)
        else:
            oval(c,x,-146,eyesize,eyesize+1,'#fdfef8',P['ink'],2)
            oval(c,x+(2 if action=='sprint' else -1),-145,2.3,3.3,P['ink'])
    # Avoid always-smiling mouth. Only speak/shock/laugh mouth opens.
    if action in ('panic','slip'):
        oval(c,1,-122,8,12,'#3b2330',P['ink'],2)
    elif action=='speak':
        oval(c,0,-123,5+4*abs(math.sin(t*10)),5+6*abs(math.sin(t*10)),'#3b2330',P['ink'],2)
    elif action in ('laugh','recover'):
        bez(c,(-12,-125),(-4,-114),(4,-113),(13,-125),P['ink'],3)
    elif action=='sprint':line(c,[(-9,-122),(8,-124)],P['ink'],2.5)
    else:bez(c,(-9,-122),(-3,-124),(3,-124),(9,-122),P['ink'],2.4)
    c.restore()

def draw_cat(c,t,action,z,tilt,phase):
    c.save();c.rotate(tilt)
    limbs(c,action,t,z,phase,cat=True)
    # Tail curves every frame, 100% original.
    bez(c,(-22,-25),(-70,-8),(-65,-75+10*math.sin(t*9)),(-83,-60+22*math.sin(t*8)),P['ink'],13)
    bez(c,(-22,-25),(-70,-8),(-65,-75+10*math.sin(t*9)),(-83,-60+22*math.sin(t*8)),P['orange'],9)
    oval(c,0,-36,40,48,P['orange'],P['ink'],4)
    oval(c,15,-42,17,26,P['cream'])
    oval(c,0,-134,45,40,P['orange'],P['ink'],4)
    path(c,[(-39,-151),(-45,-185),(-15,-171)],True);fill(c,P['orange'],P['ink'],4)
    path(c,[(19,-172),(43,-185),(42,-147)],True);fill(c,P['orange'],P['ink'],4)
    oval(c,0,-120,26,18,P['cream'],P['ink'],2)
    for side in (-1,1):
        oval(c,side*17,-143,11,14,'#fdfaf5',P['ink'],2)
        oval(c,side*18+2,-142,3.8,6,P['ink'])
        for dy in (0,7):line(c,[(side*22,-119+dy),(side*48,-122+dy)],P['ink'],1.6)
    oval(c,0,-121,5,4,P['ink'])
    if action in ('panic','slip'):oval(c,1,-108,6,10,P['ink'])
    elif action in ('recover','laugh'):bez(c,(-12,-110),(0,-101),(7,-101),(15,-110),P['ink'],2.3)
    else:line(c,[(-7,-109),(8,-109)],P['ink'],2)
    c.restore()

def draw_robot(c,t,action,z,tilt,phase):
    c.save();c.rotate(tilt);limbs(c,action,t,z,phase)
    rect(c,-29,-81,58,78,'#afbbc3',P['ink'],4,9)
    rect(c,-38,-177,76,71,'#c9d9d8',P['ink'],4,12)
    for x in (-18,18):
        rect(c,x-11,-153,22,18,'#f5f0c7',P['ink'],2,4)
        oval(c,x,-145,3.5,4,P['ink'])
    if action=='panic':oval(c,0,-125,8,11,P['ink'])
    else:rect(c,-13,-127,26,5,P['ink'],r=2)
    line(c,[(0,-178),(0,-193)],P['ink'],4);oval(c,0,-195,7,7,P['orange'],P['ink'],2)
    c.restore()

def punch_fx(c,t,action,actor_x,actor_y,z,phase):
    if action=='sprint':
        random.seed(int(t*24)+99)
        for i in range(7):
            x=actor_x-random.randint(70,125);y=actor_y-random.randint(45,150)
            line(c,[(x,y),(x-random.randint(14,38),y)],'#e6ffff' if i%2 else '#3e6f71',2+i%2)
        for i in range(3):oval(c,actor_x-34-i*13,actor_y-3-i*5,3+i,2+i,'#ece5d8')
    if action=='jump':
        oval(c,actor_x,291,25*(1-.6*math.sin(math.pi*z)),5*(1-.7*math.sin(math.pi*z)),'#494141',None)
    if action in ('panic','slip'):
        for i in range(9):
            a=TAU*i/9;x=actor_x+80*math.cos(a);y=actor_y-104+70*math.sin(a)
            line(c,[(x,y),(x+14*math.cos(a),y+14*math.sin(a))],P['ink'],2)
    if action=='knock' and math.sin(z*TAU*4)>.3:
        for i in range(3):
            x=428+10*i;y=146+14*i
            bez(c,(x,y),(x+10,y-5),(x+11,y-15),(x+13,y-19),P['ink'],2.5)

def draw_frame(c,plan,t,w,h):
    setting=plan['setting'];kind=plan['character']
    action,z,x,y,tilt,phase=character_scene_state(plan,t)
    # Camera follows the subject for true 9:16 shorts and makes reaction punch-ins.
    zoom=1.0
    if action in ('panic','slip'):zoom=1+.08*math.sin(math.pi*z)
    elif action=='knock':zoom=1+.035*ease(z)
    elif action=='jump':zoom=1-.07*math.sin(math.pi*z)
    base_scale=h/360*zoom
    visible_w=w/base_scale; visible_h=h/base_scale
    camera_x=x+(20 if action=='knock' else 0)
    c.save();c.scale(base_scale,base_scale)
    c.translate(visible_w/2-camera_x,(visible_h-360)/2)
    background(c,setting,t)
    # impact cut and shaky camera rather than whole-frame blur artifacts
    if action in ('panic','slip') and .1<z<.8:
        shake=2.5*math.sin(t*TAU*13)
        c.translate(shake,1.3*math.cos(t*TAU*11))
    c.save();c.translate(x,y-82)
    if kind=='cat':draw_cat(c,t,action,z,tilt,phase)
    elif kind=='robot':draw_robot(c,t,action,z,tilt,phase)
    else:draw_human(c,t,action,z,tilt,phase,kind)
    c.restore()
    punch_fx(c,t,action,x,y,z,phase)
    c.restore()
    # screen space tiny branding; avoid overlay on body
    col(c,'#172a2c',.82)
    c.rectangle(10,11,w-20,32);c.fill()
    col(c,'#ffffff');c.select_font_face('Sans',cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(min(19,w/20));c.move_to(20,34);c.show_text('FUNNY TOON EVER  /  '+action.upper())
    return action