"""Render a silent illustrated short from a sequence of stage directions."""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path
import cairo

S, C, PI = math.sin, math.cos, math.pi
INK = '#332d45'
ACTIONS = {'walk':2.5,'jump':1.25,'wave':2,'fly':2,'pull':1.7,'watch':1.4}
ALIASES = {'walks':'walk','jumps':'jump','waves':'wave','flies':'fly','pulls':'pull','watches':'watch',
           'ඇවිදින්න':'walk','පනින්න':'jump','අත වනන්න':'wave','සරුංගලය යවන්න':'fly','අදින්න':'pull','බලන්න':'watch'}

def plan(prompt):
    beats = []
    for phrase in re.split(r';|\n',prompt):
        line = phrase.strip().lower().rstrip('.')
        if not line:
            continue
        for word, action in ALIASES.items():
            line = re.sub(r'(?<!\w)'+word+r'(?!\w)',action,line)
        match = re.fullmatch(r'(mira|ravi)\s+(walk|jump|wave|fly|pull|watch)(?:\s+(left|right))?(?:\s+([\d.]+)s)?',line)
        if not match:
            raise ValueError(f'Unknown direction: {phrase}. Example: Mira walks right 2s; Ravi waves')
        actor,action,direction,duration = match.groups()
        if action in ('fly','pull') and actor != 'mira':
            raise ValueError('Mira is holding the kite in this rig. Use Mira for fly and pull.')
        if direction and action != 'walk':
            raise ValueError('left/right controls the walking direction')
        seconds = float(duration or ACTIONS[action])
        if not 0.4 <= seconds <= 12:
            raise ValueError('Each beat must be 0.4 to 12 seconds')
        beats.append(dict(actor=actor,action=action,direction=direction or 'right',seconds=seconds))
    if not beats or sum(b['seconds'] for b in beats)>120:
        raise ValueError('Use between one beat and 120 seconds of directions')
    return beats

def color(h):
    return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def fill(h):
    g.set_source_rgb(*color(h)); g.fill()
def poly(points,h):
    g.move_to(*points[0])
    for p in points[1:]: g.line_to(*p)
    g.close_path(); fill(h)
def oval(x,y,rx,ry,h):
    g.save(); g.translate(x,y); g.scale(rx,ry); g.arc(0,0,1,0,2*PI); g.restore(); fill(h)
def path(points,h,w):
    g.move_to(*points[0])
    for p in points[1:]: g.line_to(*p)
    g.set_source_rgb(*color(h)); g.set_line_width(w); g.stroke()
def curve(a,b,c,d,h,w):
    g.move_to(*a); g.curve_to(*b,*c,*d); g.set_source_rgb(*color(h)); g.set_line_width(w); g.stroke()
def smooth(u): return u*u*(3-2*u)
def stage(t,cam):
    grad=cairo.LinearGradient(0,0,0,360)
    for y,h in [(0,'#79baba'),(.55,'#ffdbac'),(1,'#faad83')]: grad.add_color_stop_rgb(y,*color(h))
    g.set_source(grad);g.paint()
    oval(598-cam*.06,113,48,48,'#fff2bc')
    for i in range(9):
        x=(i*113+t*1.8-cam*.12)%960-65;y=43+(i*47)%108
        for j in range(3): oval(x+j*13,y-3*S(j*2),17-j*2,4+j,'#fff1cb')
    for k,(base,amp,h,speed) in enumerate([(229,33,'#b3b59f',.12),(250,30,'#86a79b',.23),(275,25,'#568d86',.4)]):
        pts=[(x,base+amp*S((x+cam*speed)/86+k)+11*C(x/47+k)) for x in range(-10,820,5)]
        poly(pts+[(820,450),(-10,450)],h)
    for i in range(13):
        x=i*86-70-cam*.48;y=285+15*S(i)
        poly([(x,y),(x+43,y),(x+43,y+26),(x,y+26)],'#f5d6a1')
        poly([(x-5,y),(x+12,y-17),(x+42,y-17),(x+50,y)],'#a96151')
        poly([(x+12,y+26),(x+12,y+11),(x+19,y+11),(x+19,y+26)],'#67505a')
    poly([(0,315),(230,306),(510,325),(800,304),(800,450),(0,450)],'#7e9e68')
    poly([(0,345),(280,330),(540,343),(800,328),(800,450),(0,450)],'#b4ba79')
    poly([(0,375),(350,350),(800,357),(800,384),(290,371),(0,394)],'#eed398')
    for i in range(79):
        x=(i*103.7-cam*.86)%830-15;y=339+(i*31)%105
        path([(x-2,y-2),(x,y),(x+3,y-4)],'#91a16e',1.1)

def actor(x,y,t,name,action,u,direction):
    second=name=='ravi'; f=-1 if second else 1
    if action=='walk': f=direction
    skin='#b66d49' if second else '#ce875d'
    coat='#338a87' if second else '#e96d49'
    wave=S(PI*u)**.65
    stride=S(4*PI*u)*wave if action=='walk' else 0
    hop=47*S(PI*u)**2 if action=='jump' else 0
    bob=2*abs(stride)+.8*S(t*3+second)
    oval(x,y+1,24-hop*.19,4,'#939067')
    g.save();g.translate(x,y-hop-bob);g.scale(f,1)
    for side in [-1,1]:
        swing=side*stride
        pts=[(side*7,-31),(side*8+swing*6,-17-abs(swing)*3),(side*9+swing*16,-4-5*max(0,swing))]
        path(pts,INK,8);fx,fy=pts[-1];oval(fx+2,fy,8,4,'#423649')
    lift=wave if action in ('wave','jump','pull','fly') else 0
    hand=(24+4*stride+4*lift,-37-30*lift)
    if action=='wave': hand=(25+8*S(u*6*PI)*lift,hand[1]-5*lift)
    if action=='pull': hand=(24-16*lift,-37-21*lift)
    path([(-11,-51),(-19,-42),(-20-stride*9,-33-lift*9)],INK,6)
    poly([(-11,-58),(8,-59),(16,-49),(15,-27),(-16,-27),(-16,-46)],coat)
    poly([(-12,-33),(14,-34),(15,-27),(-16,-27)],'#514151')
    path([(12,-50),(21,-44-lift*4),hand],INK,6)
    oval(*hand,4.5,4.5,skin)
    g.save();g.translate(0,-73);g.rotate(.06*stride-.09*lift)
    oval(0,0,24,24,INK);oval(1,1,22,22,skin);oval(-19,5,5,6,skin)
    oval(-7,-13,18,12,INK)
    if second:
        oval(-15,-24,10,10,INK);oval(3,-14,15,6,INK)
    else:
        oval(-4,-19,23,10,'#eeaa45');oval(7,-14,22,4,'#a4553d')
    blink=max(.12,min(1,abs((t+second*.4)%3.1-2.6)*13))
    for dx in [7,17]:
        oval(dx,-1,2.2,3.5*blink,INK)
        path([(dx-3,-8-lift*2),(dx+2,-9)],INK,1.6)
    oval(4,7,4,2,'#dc9678');curve((9,10),(11,12+lift*2),(15,12),(17,9),INK,1.4)
    g.restore()
    poly([(-8,-57),(8,-56),(-3,-49)],'#ffe1a2')
    g.restore()
    return x+f*hand[0],y-hop-bob+hand[1]

def kite(hand,t,height,cam):
    x=225+29*S(t*.85)+.16*hand[0]-cam*.2;y=218-height+10*S(t*1.4)
    curve(hand,(hand[0]+18,hand[1]-22),(x-31,y+86),(x,y),'#735954',1.1)
    tail=[(x+4*i+4*S(t*3-i),y+19+i*6) for i in range(9)]
    path(tail,'#814d4a',1.4)
    for i in [2,5,8]:
        bx,by=tail[i];poly([(bx-4,by-3),(bx+4,by+3),(bx+4,by-3),(bx-4,by+3)],'#d85545')
    g.save();g.translate(x,y);g.rotate(.16*S(t*1.8)-.12)
    corners=[(0,-28),(26,-3),(0,28),(-26,-3)]
    for i,h in enumerate(['#e9664c','#f7b04b','#dd6849','#fff0a0']): poly([(0,-3),corners[i],corners[(i+1)%4]],h)
    path(corners+[corners[0]],'#865640',1.2);g.restore()

def render(beats,out,width):
    global g
    fps=24; height=width*9//16
    surf=cairo.ImageSurface(cairo.FORMAT_RGB24,width,height);g=cairo.Context(surf)
    g.scale(width/800,height/450);g.set_line_join(cairo.LINE_JOIN_ROUND);g.set_line_cap(cairo.LINE_CAP_ROUND)
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','bgr0','-video_size',f'{width}x{height}','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    pos={'mira':197,'ravi':592}; altitude=44; frame=0
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as enc:
        for beat in beats:
            who,action=beat['actor'],beat['action']; d=1 if beat['direction']=='right' else -1
            start=pos[who];end=max(85,min(704,start+105*d)) if action=='walk' else start
            hstart=altitude;hend={'pull':58,'fly':134}.get(action,altitude) if who=='mira' else altitude
            n=round(beat['seconds']*fps)
            for i in range(n):
                u=i/(n-1);t=frame/fps;frame+=1;pos[who]=start+(end-start)*smooth(u)
                altitude=hstart+(hend-hstart)*smooth(u);cam=(pos['mira']+pos['ravi']-789)*.27+8*S(t*.23)
                stage(t,cam)
                for name in ('ravi','mira'):
                    hand=actor(pos[name]-cam,354+(name=='mira')*13,t,name,action if name==who else 'watch',u,d)
                kite(hand,t,altitude,cam)
                for j in range(29):
                    x=(j*137-cam*1.45)%840-20;y=446+(j*19)%19
                    curve((x,y+8),(x+2,y-7),(x+8,y-10),(x+7+2*S(t+j),y-20-j%12),'#527a62',2)
                    if j%3==0: oval(x+7+2*S(t+j),y-21-j%12,3,2,'#f0ad67')
                surf.flush();enc.stdin.write(surf.get_data())
        enc.stdin.close()
        if enc.wait(): raise RuntimeError('FFmpeg failed')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('prompt');p.add_argument('output',type=Path);p.add_argument('--width',type=int,choices=[640,1280,1920],default=1920)
    p.add_argument('--extend',type=Path,help='Append to the prompt in a previous render JSON')
    a=p.parse_args()
    if a.extend:
        previous=json.loads(a.extend.read_text())
        a.prompt=previous['prompt']+'; '+a.prompt
    beats=plan(a.prompt);render(beats,a.output,a.width)
    a.output.with_suffix('.json').write_text(json.dumps({'prompt':a.prompt,'beats':beats},ensure_ascii=False,indent=2))
