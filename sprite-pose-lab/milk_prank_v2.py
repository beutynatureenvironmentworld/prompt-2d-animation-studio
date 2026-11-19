"""Original 2D cartoon milk prank: procedural frame-by-frame animation, CPU only.

New hand-drawn pose art adapts the Pip/Luma silhouettes from sprite_factory.py:
Pip gets a golden cap + blue shirt; Luma gets a coral dress, dark bun.
No external copyrighted sprites, music, video frames or network services.

Install: pip install pillow numpy; install ffmpeg.
Render: python milk_prank_v2.py --output improved_milk_prank_1080p.mp4
"""
from __future__ import annotations
import argparse
import math
import shutil
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W,H = 720,1280
FPS=12
TOTAL=11.5
FRAME_COUNT=int(FPS*TOTAL)
FLOOR=1105
C = dict(outline='#252334', skinboy='#C88460', skingirl='#D8936E', hair='#4D302B',
         blue='#40A4E5', blue_dark='#2684BB', gold='#FFC83D', coral='#FF7A83',
         coral_dark='#E75A71', navy='#41547A', white='#FFFDFC', shadow='#9ACADD')


def clamp(x,lo=0,hi=1):return min(hi,max(lo,x))
def lerp(a,b,t):return a+(b-a)*t
def ease(t):t=clamp(t);return t*t*(3-2*t)
def tween(t, start, end):return ease((t-start)/max(.000001,end-start))
def pulse(t,a,b,c):return min(tween(t,a,b),1-tween(t,b,c))

def bez(p0,p1,p2,p3,n=23):
    out=[]
    for j in range(n+1):
        u=j/n;v=1-u
        out.append((round(v**3*p0[0]+3*v*v*u*p1[0]+3*v*u*u*p2[0]+u**3*p3[0]),
                    round(v**3*p0[1]+3*v*v*u*p1[1]+3*v*u*u*p2[1]+u**3*p3[1])))
    return out

def curve(d,a,b,c,e,fill,width=7):
    pts=bez(a,b,c,e)
    d.line(pts,fill=fill,width=width,joint='curve')
    r=width//2
    for xx,yy in [pts[0],pts[-1]]:d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=fill)

def oval(d,box,fill,outline=None,width=1):d.ellipse(tuple(map(round,box)),fill=fill,outline=outline,width=width)
def poly(d,points,fill,outline=None,width=6):
    pts=[(round(x),round(y)) for x,y in points]
    d.polygon(pts,fill=fill)
    if outline:d.line(pts+[pts[0]],fill=outline,width=width,joint='curve')

def arm(d,p0,control,end,skin,r=10):
    midpoint=((p0[0]+end[0])*.5,control[1])
    curve(d,p0,control,midpoint,end,C['outline'],10)
    oval(d,(end[0]-r,end[1]-r,end[0]+r,end[1]+r),skin,C['outline'],4)

def background(d,t):
    d.rectangle((0,0,W,H),fill='#D9F4FF')
    d.rectangle((0,0,W,190),fill='#EDF9FF')
    # cream wall strips / simple recognizable interior
    d.rounded_rectangle((72,223,274,517),25,fill='#FFFAEA',outline=C['outline'],width=9)
    d.rounded_rectangle((88,239,259,499),13,fill='#8AD6FF')
    d.polygon([(90,487),(148,413),(200,456),(260,408),(260,499),(90,499)],fill='#90D9AA')
    d.line((171,244,171,499),fill='#FFFFFF',width=9)
    d.line((91,370,260,370),fill='#FFFFFF',width=9)
    d.ellipse((595,195,648,248),fill='#FFE58A',outline=None)
    # framed minimalist picture
    d.rounded_rectangle((455,258,636,395),13,fill='#FFF8F1',outline=C['outline'],width=9)
    d.polygon([(473,376),(513,322),(545,355),(583,306),(620,376)],fill='#75C9A3')
    d.ellipse((485,277,520,312),fill='#FFC65D')
    d.rectangle((0,1100,720,H),fill='#FFE8B7')
    d.rectangle((0,1092,720,1103),fill=C['outline'])
    d.line((0,1182,W,1182),fill='#F1CFA3',width=3)
    # muted side table, stays behind characters
    d.rounded_rectangle((10,920,78,941),7,fill='#B9875B',outline=C['outline'],width=6)
    d.line((24,940,22,1093),fill=C['outline'],width=8)
    d.line((65,940,67,1093),fill=C['outline'],width=8)
    d.rounded_rectangle((26,852,61,922),7,fill='#F5BA78',outline=C['outline'],width=5)
    d.polygon([(43,854),(18,825),(32,815),(48,845)],fill='#72BE86')
    d.polygon([(46,852),(75,819),(85,834),(47,863)],fill='#4B9D69')


def boy_face(d,x,y,t,smirk=1,laugh=0):
    ol=C['outline']
    # Round face in same character proportions as former Pip PNG family
    oval(d,(x-78,y-78,x+78,y+84),C['skinboy'],ol,8)
    oval(d,(x-85,y+8,x-65,y+41),C['skinboy'],ol,5)
    oval(d,(x+65,y+8,x+85,y+41),C['skinboy'],ol,5)
    # cap golden-yellow with thick hand-drawn lineart
    poly(d,[(x-78,y-52),(x-59,y-81),(x-16,y-100),(x+47,y-91),(x+78,y-54),(x+72,y-26),(x-69,y-26)],C['gold'],ol,7)
    curve(d,(x-61,y-31),(x-3,y-19),(x+64,y-20),(x+94,y-24),ol,10)
    curve(d,(x-43,y-62),(x-10,y-83),(x+29,y-80),(x+52,y-68),'#FFDE7B',4)
    # brow and expressive cheek
    curve(d,(x-49,y-6),(x-36,y-19),(x-25,y-19),(x-10,y-5),ol,6)
    curve(d,(x+13,y-8),(x+25,y-17),(x+40,y-17),(x+51,y-11),ol,6)
    for ex,pdx in [(x-29,5),(x+31,7)]:
        oval(d,(ex-17,y+1,ex+17,y+40),'#FFFFFF',ol,5)
        oval(d,(ex+pdx-5,y+15,ex+pdx+6,y+29),ol)
        oval(d,(ex+pdx-3,y+17,ex+pdx,y+20),'#FFFFFF')
    d.arc((x-46,y+26,x-25,y+57),0,110,fill='#A95D59',width=3)
    if laugh>0.15:
        amp=math.sin(t*18)**2
        oy=4*amp
        oval(d,(x-36,y+44+oy,x+41,y+93+oy),ol,ol,4)
        poly(d,[(x-29,y+49+oy),(x+34,y+49+oy),(x+29,y+61+oy),(x-23,y+61+oy)],'#FFFFFF')
        oval(d,(x-13,y+73+oy,x+17,y+86+oy),'#FD8183')
    elif smirk>0.5:
        poly(d,[(x-34,y+43),(x-11,y+54),(x+15,y+56),(x+39,y+37),(x+32,y+63),(x+1,y+72),(x-23,y+64)],ol)
        poly(d,[(x-29,y+47),(x+27,y+45),(x+25,y+56),(x-18,y+57)],'#FFFFFF')
    else:
        curve(d,(x-22,y+55),(x-8,y+62),(x+13,y+61),(x+25,y+56),ol,5)
    oval(d,(x-51,y+49,x-36,y+62),'#E78A84')


def boy(d,t):
    laugh=t>6.6
    bob=0
    if laugh:bob=-8*abs(math.sin((t-6.6)*14))
    elif t>1.15:bob=-3*math.sin((t-1.15)*6)
    x=190+(-10 if 3.95<t<4.45 else 0)
    y=615+bob
    ol=C['outline']
    # legs and shoes (single smooth strokes, no exposed joints)
    curve(d,(x-35,y+280),(x-44,y+347),(x-38,y+406),(x-50,y+470),ol,13)
    curve(d,(x+33,y+280),(x+49,y+335),(x+29,y+421),(x+48,y+470),ol,13)
    oval(d,(x-80,y+460,x-43,y+479),ol)
    oval(d,(x+41,y+460,x+79,y+479),ol)
    poly(d,[(x-56,y+245),(x+55,y+245),(x+54,y+301),(x+13,y+301),(x-7,y+275),(x-15,y+301),(x-56,y+301)],C['navy'],ol,7)
    # blue shirt
    poly(d,[(x-64,y+120),(x-30,y+104),(x+34,y+107),(x+66,y+124),(x+59,y+264),(x-60,y+264)],C['blue'],ol,9)
    curve(d,(x-45,y+163),(x-34,y+195),(x-40,y+225),(x-32,y+246),'#79C7F4',4)
    curve(d,(x-50,y+132),(x-69,y+157),(x-76,y+194),(x-64,y+230),ol,10)
    oval(d,(x-72,y+225,x-52,y+244),C['skinboy'],ol,4)
    # right arm repeatedly aims at carton or flails while laughing
    if laugh:
        elbow=(x+110,y+155)
        hand=(x+125+12*math.sin(t*16),y+124-18*abs(math.sin(t*13)))
    else:
        hand=(300-5*tween(t,1.5,2.0),680+9*math.sin(7*t)*tween(t,1.4,2.1))
        elbow=(x+90,y+112)
    arm(d,(x+58,y+139),elbow,hand,C['skinboy'],12)
    boy_face(d,x,y,t,laugh=float(laugh))
    if laugh:
        # visual laughing bouncing lines
        for i in range(3):
            ax=x-96-i*14
            curve(d,(ax,y+10+i*10),(ax-7,y+2+i*10),(ax-10,y-7+i*8),(ax-11,y-15+i*10),ol,3)


def angry_mark(d,x,y,t):
    if t>5.15:return
    d.line((x+77,y-91,x+88,y-110,x+103,y-105),fill='#E64E5C',width=7,joint='curve')
    d.line((x+85,y-111,x+93,y-99,x+102,y-119),fill='#E64E5C',width=7,joint='curve')


def eyes_springs(d,x,y,t):
    # two socket-to-eye zig-zag springs, more readable than plain pop shock PNG
    q=tween(t,5.28,5.45)*(1-.13*tween(t,5.7,6.2))
    q=max(0,q)
    for sign in (-1,1):
        sx=x+sign*34
        ex=sx+sign*(13+16*q)
        ey=y-13-91*q+5*math.sin((t-5.3)*22+sign)*q
        pts=[]
        for i in range(11):
            u=i/10
            xx=lerp(sx,ex,u)+sign*11*q*math.sin(u*8*math.pi)
            yy=lerp(y+1,ey+25,u)
            pts.append((xx,yy))
        d.line(pts,fill=C['outline'],width=5,joint='curve')
        oval(d,(ex-25,ey-31,ex+25,ey+27),'#FFFFFF',C['outline'],6)
        oval(d,(ex-4,ey-6,ex+10,ey+10),C['outline'])
        oval(d,(ex,ey-3,ex+4,ey+1),'#FFFFFF')


def girl_face(d,x,y,t,wet):
    ol=C['outline']
    angry = t<5.10 or t>9.2
    shocked = 5.15<=t<=9.25
    # nape + bun behind face
    oval(d,(x+38,y-107,x+107,y-29),C['hair'],ol,7)
    for i in range(3):d.arc((x+49+i*7,y-96+i*8,x+97-i*5,y-30-i*2),165,330,fill='#986D57',width=3)
    oval(d,(x-78,y-79,x+78,y+83),C['skingirl'],ol,9)
    oval(d,(x-84,y+6,x-64,y+38),C['skingirl'],ol,4)
    oval(d,(x+64,y+6,x+84,y+38),C['skingirl'],ol,4)
    # dark brown sweeping hair cap
    poly(d,[(x-78,y-13),(x-74,y-54),(x-45,y-89),(x+15,y-101),(x+65,y-75),(x+76,y-19),(x+46,y-50),(x+5,y-50),(x-39,y-30)],C['hair'],ol,5)
    curve(d,(x-57,y-47),(x-12,y-67),(x+22,y-64),(x+56,y-45),'#936458',4)
    if shocked:
        eyes_springs(d,x,y,t)
        oval(d,(x-27,y+33,x+27,y+102),ol,ol,5)
        oval(d,(x-16,y+73,x+17,y+89),'#F7778C')
        # speed / surprise lines
        for p,q in [((-105,-49),(-129,-71)),((97,-65),(125,-90)),((-83,13),(-112,6))]:
            d.line((x+p[0],y+p[1],x+q[0],y+q[1]),fill=ol,width=5)
    elif angry:
        # squint + heavy furious inward brows
        oval(d,(x-59,y-11,x-9,y+39),'#FFFFFF',ol,5)
        oval(d,(x+12,y-11,x+60,y+39),'#FFFFFF',ol,5)
        d.line((x-61,y-24,x-12,y+4),fill=ol,width=9)
        d.line((x+61,y-24,x+12,y+4),fill=ol,width=9)
        oval(d,(x-32,y+6,x-20,y+23),ol)
        oval(d,(x+21,y+6,x+33,y+23),ol)
        curve(d,(x-24,y+73),(x-9,y+51),(x+9,y+52),(x+26,y+74),ol,6)
        angry_mark(d,x,y,t)
    else:
        for sx in (-31,31):
            oval(d,(x+sx-18,y+3,x+sx+18,y+36),'#FFFFFF',ol,5)
            oval(d,(x+sx-5,y+13,x+sx+8,y+28),ol)
        oval(d,(x-19,y+57,x+17,y+89),ol)
    if wet>0:
        # white milk matting on face hair and chin, visible long after impact
        alpha=clamp(wet)
        if alpha>.05:
            poly(d,[(x-65,y-58),(x-51,y-67),(x-29,y-54),(x-17,y-71),(x+17,y-60),(x+46,y-75),(x+64,y-45),(x+43,y-38),(x+17,y-50),(x-15,y-37),(x-53,y-47)],'#FFFFFF','#A8D7EA',3)
            for dx,v in [(-59,39),(-34,79),(43,61),(57,93)]:
                yy=y+17
                d.rounded_rectangle((x+dx-7,yy,x+dx+7,yy+v),7,fill='#FFFFFF',outline='#A8D7EA',width=2)
                oval(d,(x+dx-7,yy+v-4,x+dx+7,yy+v+9),'#FFFFFF','#A8D7EA',2)


def girl(d,t):
    x=552
    bob=0
    if 3.4<=t<=4.1:bob=-8*tween(t,3.4,3.9)
    if 5.3<=t<=6.0:bob=-10*abs(math.sin((t-5.3)*16))
    y=610+bob
    ol=C['outline']
    wet=tween(t,4.73,5.45)
    # legs continuous rounded curves + flat feet
    curve(d,(x-31,y+276),(x-33,y+341),(x-29,y+407),(x-36,y+478),ol,12)
    curve(d,(x+27,y+276),(x+46,y+361),(x+37,y+407),(x+47,y+478),ol,12)
    oval(d,(x-63,y+462,x-22,y+480),ol)
    oval(d,(x+39,y+462,x+76,y+480),ol)
    # coral pink dress
    poly(d,[(x-46,y+113),(x+48,y+112),(x+69,y+273),(x+96,y+315),(x-95,y+315),(x-65,y+266)],C['coral'],ol,9)
    d.line((x-70,y+290,x+73,y+290),fill='#FFC2BF',width=6)
    d.arc((x-34,y+150,x+45,y+200),190,355,fill=C['coral_dark'],width=4)
    # far right arm angled down or fists
    arm(d,(x+53,y+138),(x+106,y+154),(x+98,y+251),C['skingirl'])
    # left arm goes up to squeeze carton: silhouette stays one smooth stroke
    prep=tween(t,2.55,3.72)
    slam=tween(t,3.72,4.06)
    if t<2.55:
        endpoint=(x-99,y+255)
        elbow=(x-106,y+210)
    elif t<4.09:
        endpoint=(lerp(x-99,395,prep),lerp(y+255,y+25,prep)-30*slam)
        elbow=(lerp(x-115,410,prep),lerp(y+191,y+8,prep))
    elif t<5.15:
        endpoint=(394,673)
        elbow=(421,720)
    elif t<6.6:
        endpoint=(x-111,y+185)
        elbow=(x-105,y+157)
    else:
        endpoint=(x-110,y+215)
        elbow=(x-109,y+157)
    arm(d,(x-54,y+145),elbow,endpoint,C['skingirl'],14)
    girl_face(d,x,y,t,wet)
    if t>8.55:
        for i in range(4):
            px=x-66+(i*35)
            py=y+55+(i%2)*20+(t-8.55)*24
            oval(d,(px,py,px+11,py+20),'#FFFFFF','#A7D9EB',2)


@lru_cache(maxsize=1)
def carton_art():
    # Horizontal after the boy flips the carton; nozzle aims toward girl.
    w,h=220,195
    im=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(im)
    ol=C['outline']
    # source drawing is upright before 90-degree rotation
    poly(d,[(58,43),(152,43),(172,82),(167,170),(52,170),(48,82)],'#FFFEF7',ol,9)
    poly(d,[(58,43),(78,13),(139,13),(152,43)],'#E4F3FB',ol,7)
    d.line((78,13,103,42,139,13),fill=ol,width=5)
    d.polygon([(52,94),(170,94),(168,142),(51,142)],fill='#56BDE6')
    d.line((59,105,164,105),fill='#D6F7FD',width=4)
    d.ellipse((84,110,137,135),fill='#FFFFFF')
    d.ellipse((102,109,120,131),fill='#70B9E6')
    # small sealed flat bottom distinct from open straw top
    d.line((54,170,167,170),fill='#78819B',width=10)
    # hole at top + straw angled toward top
    oval(d,(112,-2,141,18),'#9ADAF2',ol,4)
    curve(d,(126,5),(129,-19),(149,-30),(168,-28),'#FFFFFF',12)
    curve(d,(126,5),(129,-19),(149,-30),(168,-28),'#9DD5E7',4)
    oval(d,(161,-38,181,-19),'#FFFFFF',ol,3)
    return im


def carton_state(t):
    f=tween(t,1.1,2.32)
    y=722-18*tween(t,1.4,2.3)
    rot=-95*f
    if t>3.8:
        y+=8*pulse(t,3.85,4.04,4.35)
    if t>6.03:
        drop=tween(t,6.03,7.20)
        y+=340*drop
        rot-=195*drop
    scx=1-.22*pulse(t,3.89,4.15,4.6)
    scy=1+.18*pulse(t,3.89,4.15,4.6)
    return (340+8*tween(t,1.5,2.3),y,rot,scx,scy)


def carton(base,t):
    if t>8.25:return
    cx,cy,rot,sx,sy=carton_state(t)
    im=carton_art()
    im=im.resize((round(im.width*.74*sx),round(im.height*.74*sy)),Image.Resampling.BICUBIC)
    im=im.rotate(rot,expand=True,resample=Image.Resampling.BICUBIC)
    x=round(cx-im.width/2);y=round(cy-im.height/2)
    base.alpha_composite(im,(x,y))
    # boy's comic "pretend sipping from SEALED end" dashes at close range
    if 2.23<t<3.85:
        d=ImageDraw.Draw(base)
        for i in range(3):
            xx=266+i*9
            curve(d,(xx,673),(xx+3,668),(xx+6,669),(xx+7,675),'#7894AB',3)


def milk_jet(d,t):
    intensity=tween(t,4.20,4.47)*(1-tween(t,5.65,6.1))
    if intensity<=0.01:return
    nozzle=(443,696)
    face=(539,611)
    wobble=9*math.sin(t*22)
    mid=(500,677+wobble)
    end=(face[0],face[1]+10*math.sin(t*25))
    width=round(41*intensity)
    pts=bez(nozzle,(474,681),(506,640+wobble),end,40)
    d.line(pts,fill='#91CFE5',width=width+10,joint='curve')
    d.line(pts,fill='#FFFDF9',width=width,joint='curve')
    for xx,yy in [pts[0],pts[-1]]:
        oval(d,(xx-width//2,yy-width//2,xx+width//2,yy+width//2),'#FFFEFB')
    # radial splash at girl's face
    spike=clamp(intensity)*55
    polypts=[]
    for j in range(20):
        angle=2*math.pi*j/20
        radius=(25+spike) if j%2 else (13+spike*.4)
        polypts.append((face[0]+math.cos(angle)*radius,face[1]+math.sin(angle)*radius))
    poly(d,polypts,'#FDFEFC','#93CDE4',4)
    # seeded by frame, cinematic droplet continuity without flash randomization
    f=int(t*FPS)
    rng=np.random.default_rng(1267+f)
    for i in range(19):
        prog=rng.random()
        px=lerp(nozzle[0],face[0],prog)+rng.normal(0,12)
        py=lerp(nozzle[1],face[1],prog)+rng.normal(0,25)
        r=2+rng.random()*7*intensity
        oval(d,(px-r,py-r,px+r,py+r),'#FFFFFF','#9ED4E7',2)
    for k in range(8):
        dx=rng.uniform(-100,110)
        dy=rng.uniform(-120,160)
        r=rng.uniform(4,11)*intensity
        oval(d,(face[0]+dx-r,face[1]+dy-r,face[0]+dx+r,face[1]+dy+r),'#FFFFFF','#92C9E0',2)


def impact(d,t):
    p=pulse(t,3.88,4.06,4.32)
    if p<=0:return
    cx,cy=397,695
    pts=[]
    for k in range(16):
        th=2*math.pi*k/16
        r=(25 if k%2 else 73)*p
        pts.append((cx+math.cos(th)*r,cy+math.sin(th)*r))
    poly(d,pts,'#FFE15A',C['outline'],6)
    for th in [0,math.pi/4,math.pi,3*math.pi/2,5*math.pi/4]:
        dx,dy=math.cos(th),math.sin(th)
        d.line((cx+90*p*dx,cy+90*p*dy,cx+127*p*dx,cy+127*p*dy),fill='#F4AE3D',width=7)


def action_streaks(d,t):
    if 1.18<t<2.48:
        p=pulse(t,1.18,1.80,2.48)
        for k in range(3):
            yy=713+k*21
            curve(d,(292-55*p,yy),(284-50*p,yy-5),(291,yy-11),(317,yy-8),'#7AABC5',3)
    if 3.68<t<4.27:
        q=pulse(t,3.68,3.94,4.27)
        for k in range(4):
            x=403+22*k
            d.line((x,605-50*q,x-17*q,650-18*q),fill='#62768B',width=4)


def emotion_marks(d,t):
    if 6.6<t<10.5:
        # chuckles swirl in air around boy, timed in pose holds
        p=abs(math.sin(t*10))
        for k in range(3):
            xx=70+17*k;yy=515+38*k
            d.arc((xx-15,yy-12,xx+18,yy+14),30,160,fill=C['outline'],width=4)
            oval(d,(xx+14,yy-12,xx+19,yy-7),'#A1D7E5')
        # little milk drops shed from girl's face
        for k in range(4):
            xx=500+34*k;yy=720+((int(t*10)+k*13)%80)
            oval(d,(xx-3,yy-9,xx+5,yy+5),'#FFFDFC','#8DD1EA',2)
    if t>9.6:
        # Girl re-forms angry brows after the surprise
        d.line((622,489,637,475,644,497),fill='#E65A65',width=5)


def camera(base,t):
    # camera punch zoom on crush and eye pop, camera shake follows cartoon beats
    zoom=1.11+.12*pulse(t,3.84,4.12,4.73)+.16*pulse(t,5.2,5.58,6.45)
    if 4.16<t<5.1:zoom+=.045
    shakemag=12*pulse(t,3.91,4.12,4.5)+10*pulse(t,5.2,5.45,5.9)
    dx=int(shakemag*math.sin(t*92));dy=int(shakemag*math.cos(t*70))
    cw=round(W/zoom);ch=round(H/zoom)
    left=max(0,min(W-cw,round((W-cw)*.50+dx)))
    top=max(0,min(H-ch,round((H-ch)*.5+60+dy)))
    return base.crop((left,top,left+cw,top+ch)).resize((W,H),Image.Resampling.BICUBIC) if zoom!=1 else base


def frame(t):
    im=Image.new('RGBA',(W,H),(255,255,255,255));d=ImageDraw.Draw(im)
    background(d,t)
    boy(d,t)
    girl(d,t)
    # Milk carton on top of the two characters, girl's near hand is then painted above carton
    carton(im,t)
    d=ImageDraw.Draw(im)
    if 3.65<t<5.2:
        q=tween(t,3.70,3.96)
        # foreground hand re-emphasizes contact with carton while gripping/squeezing
        ex=lerp(402,398,q);ey=lerp(675,695,q)
        oval(d,(ex-15,ey-16,ex+16,ey+16),C['skingirl'],C['outline'],5)
        for k in range(3):d.line((ex-7+k*8,ey-9,ex-7+k*8,ey-17),fill=C['outline'],width=3)
    action_streaks(d,t)
    impact(d,t)
    milk_jet(d,t)
    emotion_marks(d,t)
    im=camera(im,t)
    return im.convert('RGB')


def _tone(freq, secs, sr, v=0.4, ending=0.05):
    ts=np.arange(round(secs*sr))/sr
    freq=np.asarray(freq(ts) if callable(freq) else np.full_like(ts,freq))
    phase=2*np.pi*np.cumsum(freq)/sr
    env=np.exp(-np.linspace(0,1,len(ts))*(-math.log(max(ending,.00001))))
    return np.sin(phase)*env*v


def sound_mix(duration,output):
    sr=48000
    n=int(sr*duration)
    a=np.zeros(n,dtype=np.float64)
    rng=np.random.default_rng(325)
    def add(start,x):
        st=round(start*sr);end=min(n,st+len(x))
        if st>=0 and st<n:a[st:end]+=x[:end-st]
    def whoosh(st,length=.35,amp=.22):
        tim=np.arange(round(length*sr))/sr
        env=np.sin(np.pi*tim/length)**2
        white=rng.standard_normal(len(tim))
        filt=np.convolve(white,[.16,.22,.24,.22,.16],mode='same')
        add(st,amp*env*filt)
    def boing(st,fr=260,length=.36,amp=.31):
        tim=np.arange(round(length*sr))/sr
        f=fr+(460-fr)*np.exp(-tim*13)+24*np.sin(tim*52)*np.exp(-tim*6)
        add(st,amp*np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-tim*8))
    def pop(st,amp=.42):
        length=.26;tim=np.arange(round(length*sr))/sr
        note=np.sin(2*np.pi*(240*tim-160*tim*tim))
        add(st,amp*(note+rng.normal(0,.6,len(tim)))*np.exp(-tim*26))
    def splash(st,length=.75,amp=.4):
        tim=np.arange(round(length*sr))/sr
        noise=rng.standard_normal(len(tim))
        sm=np.convolve(noise,np.ones(15)/15,mode='same')
        bubbles=np.sin(2*np.pi*(650*tim-230*tim*tim))*np.exp(-tim*8)
        add(st,amp*(sm*.75+bubbles*.3)*np.exp(-tim*4))
    def giggle(st):
        # rhythmic 'ha ha' vocal-like synth with two formant bands and breathy tails
        for i in range(7):
            onset=st+i*.23
            length=.18
            tim=np.arange(round(length*sr))/sr
            env=np.sin(np.pi*tim/length)**1.8
            base=(225+40*np.sin(i*1.7))*(1-.33*tim/length)
            phase=2*np.pi*np.cumsum(np.full(len(tim),base))/sr
            wave=np.sin(phase)+.35*np.sin(phase*2)+.19*np.sin(phase*3)
            breath=rng.normal(0,.12,len(tim))
            add(onset,(wave*.095+breath*.06)*env)
        boing(st+.05,310,.21,.13)
    whoosh(1.12,.48,.19);whoosh(3.64,.35,.35)
    boing(2.1,310,.28,.15)
    pop(3.99,.42);boing(4.04,170,.30,.19)
    whoosh(4.18,.44,.20);splash(4.32,1.15,.47);splash(4.91,.75,.23)
    pop(5.38,.22);boing(5.48,370,.64,.31)
    giggle(6.65);giggle(8.38)
    splash(9.2,.30,.16)
    # prevent clipping and remove abrupt edges
    a=np.tanh(a*1.3)*.85
    fade=min(3000,len(a)//2)
    if fade:
        a[:fade]*=np.linspace(0,1,fade)
        a[-fade:]*=np.linspace(1,0,fade)
    pcm=(np.clip(a,-1,1)*32767).astype('<i2')
    with wave.open(str(output),'wb') as f:
        f.setframerate(sr);f.setsampwidth(2);f.setnchannels(1);f.writeframes(pcm.tobytes())


def make_video(out,res='1080p'):
    if not shutil.which('ffmpeg'):raise RuntimeError('Please install ffmpeg')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    ww,hh=(1080,1920) if res=='1080p' else (720,1280)
    raw=out.with_suffix('.silent.mp4');audio=out.with_suffix('.wav')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
         '-r',str(FPS),'-i','pipe:0','-vf',f'fps=24,scale={ww}:{hh}:flags=lanczos',
         '-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(raw)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(FRAME_COUNT):
            p.stdin.write(frame(i/FPS).tobytes())
    except Exception:
        p.kill();p.wait();raise
    finally:
        if p.stdin and not p.stdin.closed:p.stdin.close()
    if p.wait()!=0:raise RuntimeError('ffmpeg encode failed')
    sound_mix(TOTAL,audio)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-i',str(audio),'-c:v','copy',
                    '-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(out)],check=True)
    raw.unlink(missing_ok=True);audio.unlink(missing_ok=True)
    print('SUCCESS',out,'size',out.stat().st_size,'frames',FRAME_COUNT,'duration',TOTAL,'resolution',ww,hh)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',default='improved_milk_prank_1080p.mp4')
    ap.add_argument('--resolution',choices=['720p','1080p'],default='1080p')
    ap.add_argument('--preview',action='store_true')
    a=ap.parse_args()
    if a.preview:
        times=[.3,1.8,2.8,3.9,4.3,4.8,5.4,5.8,6.5,7.5,8.6,10.6]
        contact=Image.new('RGB',(720,1280))
        import PIL.ImageOps as ImageOps
        thumbs=[frame(t).resize((180,320),Image.Resampling.LANCZOS) for t in times]
        sheet=Image.new('RGB',(720,960),'white')
        for j,im in enumerate(thumbs):sheet.paste(im,((j%4)*180,(j//4)*320))
        preview=Path(a.output).with_suffix('.contact.jpg');sheet.save(preview,quality=85);print('preview:',preview)
    else:make_video(a.output,a.resolution)