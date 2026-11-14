#!/usr/bin/env python3
"""Oracle A1-friendly, CPU-only procedural 2D cartoon animation prototype.

Renders vector-like characters with Pillow, streams frames to FFmpeg, optionally
creates original synthetic sound effects. No CUDA/GPU, remote API or credits needed.
This is a *scene-template renderer*, not text-to-video AI or automatic image rigging.
"""
import argparse
import math
import os
import random
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_W, BASE_H = 960, 540
OUTLINE = (20, 24, 37)


def osc(t, hz=1.0, phase=0):
    return math.sin(2 * math.pi * (hz * t + phase))


def rectangle(d, box, fill, outline=OUTLINE, width=4, radius=0):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def poly(d, points, fill, outline=OUTLINE, width=4):
    d.polygon(points, fill=fill)
    if outline:
        d.line(points + [points[0]], fill=outline, width=width, joint="curve")


def stroke(d, pts, fill=OUTLINE, width=6):
    d.line(pts, fill=fill, width=width, joint="curve")
    r = width / 2
    for x, y in [pts[0], pts[-1]]:
        d.ellipse((int(x-r), int(y-r), int(x+r), int(y+r)), fill=fill)


def circle(d, cx, cy, rx, ry=None, fill="white", outline=OUTLINE, width=4):
    if ry is None:
        ry=rx
    d.ellipse((int(cx-rx), int(cy-ry), int(cx+rx), int(cy+ry)), fill=fill,
              outline=outline, width=width if outline else 1)


def font(size=28):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def night_background():
    im = Image.new('RGB', (BASE_W, BASE_H)); pix = im.load()
    for y in range(BASE_H):
        k = y / BASE_H
        col = (int(34+25*k), int(43+27*k), int(79+22*k))
        for x in range(BASE_W): pix[x,y] = col
    d = ImageDraw.Draw(im)
    # moonlight glow, wall and floor
    circle(d, 770, 165, 260, 220, (72,83,125), None)
    poly(d, [(0,425),(960,425),(960,540),(0,540)], (53,55,87), None)
    stroke(d, [(0,425),(960,425)], (23,27,47), 4)
    rectangle(d, (775,65,933,318), (95,131,176), width=6, radius=5)
    circle(d, 851,132,56,56,(224,238,245),None)
    poly(d, [(777,274),(933,274),(933,315),(777,315)], (105,127,158), None)
    d.rounded_rectangle((775,65,933,318),radius=4,fill=None,outline=(13,19,34),width=7)
    stroke(d,[(853,65),(853,318)],(20,23,42),6)
    stroke(d,[(775,202),(933,202)],(20,23,42),6)
    # framed family scribble
    poly(d, [(379,88),(523,78),(538,185),(391,202)],(110,116,143),width=6)
    rectangle(d,(398,100,514,176),(151,159,182),width=4)
    for i,x in enumerate([425,448,470,492]):
        circle(d,x,124+(i%2)*5,10,10,(170,175,189),width=3)
        stroke(d,[(x,134),(x,159)],width=3)
        stroke(d,[(x-8,149),(x+8,149)],width=3)
    stroke(d,[(442,91),(452,69),(466,88)],width=3)
    # floating corner stars
    for x,y in [(70,88),(155,125),(622,105),(707,61)]:
        stroke(d,[(x-3,y),(x+3,y)],(117,137,181),2)
        stroke(d,[(x,y-3),(x,y+3)],(117,137,181),2)
    return im


def bed(d,x,y,w,blanket,front=True):
    # y=headboard upper; feet at y+180
    rectangle(d,(x+10,y+10,x+w-6,y+169),(72,77,108),width=5,radius=14)
    rectangle(d,(x,y-8,x+20,y+183),(68,61,88),width=5,radius=2)
    rectangle(d,(x+w-20,y-8,x+w,y+183),(68,61,88),width=5,radius=2)
    rectangle(d,(x+23,y+70,x+w-23,y+148),blanket,width=5,radius=18)
    stroke(d,[(x+38,y+120),(x+93,y+114),(x+168,y+129),(x+w-31,y+117)],(63,68,108),3)
    # foot-board
    if front:
        rectangle(d,(x-8,y+133,x+w+8,y+190),(76,68,101),width=6,radius=7)


def bedroom_frame(t, bg, pose=None):
    pose=pose or {}
    im = bg.copy()
    d = ImageDraw.Draw(im)
    # right bed, left bed, and central bedside table
    bed(d, 545, 272, 358, (151,159,191), front=False)
    bed(d, 85, 255, 309, (135,145,179), front=False)
    rectangle(d,(432,329,526,432),(85,76,112),width=6,radius=4)
    rectangle(d,(442,338,516,378),(116,107,135),width=4,radius=4)
    circle(d,480,359,4,4,(197,183,185),outline=None)
    rectangle(d,(445,385,512,422),(65,64,91),width=4,radius=4)
    # left irritated character body / hand, visible upper torso
    lx = 275 + 3*osc(t,.5); ly = 277 + 3*osc(t,.65)
    stroke(d,[(lx,ly+37),(lx-12,360),(lx-8,410)],width=8)
    # left arm sways subtly toward head in frustration
    hand=pose.get('hand',0)
    elbow = (lx+63+4*osc(t,1)-20*hand,ly+24-28*hand)
    stroke(d,[(lx+9,ly+62),elbow,(lx+49-28*hand,ly-2-14*hand)],width=8)
    circle(d,lx,ly,43,43,(221,225,238),width=5)
    # long nightcap, with swinging pompom
    poly(d,[(lx-42,ly-8),(lx-38,ly-44),(lx-9,ly-72),(lx+23,ly-63),
            (lx+35,ly-28),(lx+29,ly-22)],(95,106,144),width=5)
    stroke(d,[(lx-35,ly-30),(lx+20,ly-42)],(52,59,98),4)
    circle(d,lx-39,ly-13,9,9,(94,103,151),width=4)
    # annoyed eyes and eyebrows
    stroke(d,[(lx-27,ly-7),(lx-5,ly-11)],width=5)
    stroke(d,[(lx+5,ly-14),(lx+30,ly-5)],width=5)
    blink = (t % 3.8 < .13) or pose.get('sigh',0)>.7
    for ex in [-14,15]:
        if blink: stroke(d,[(lx+ex-9,ly+4),(lx+ex+7,ly+4)],width=3)
        else:
            circle(d,lx+ex,ly+5,12,7,(232,235,241),width=3)
            circle(d,lx+ex+3+pose.get('gaze',0)*4,ly+7,3,3,(34,37,51),None)
    speech=pose.get('left_mouth',0)
    if speech>.07:
        circle(d,lx,ly+23,9,3+12*speech,(22,19,35),width=3)
        circle(d,lx+1,ly+26+5*speech,5,2,(209,125,150),None)
    else: stroke(d,[(lx-17,ly+26),(lx-4,ly+20),(lx+19,ly+21)],width=3)
    # left blanket upper layer
    poly(d,[(111,341),(167,332),(225,338),(298,343),(371,327),(377,408),
            (356,426),(107,426)],(148,157,194),width=5)
    stroke(d,[(124,363),(201,362),(260,367),(329,356)],(82,91,132),3)
    # right snoring character: raised head, mouth, shifting arm
    awake=pose.get('awake',0)
    bob = (1-awake)*6*osc(t,.82)-9*awake
    rx, ry = 694, 338 + bob
    stroke(d,[(rx,ry+40),(rx+78,395),(rx+125,442)],width=8)
    arm = 10*osc(t,.82+.17)
    stroke(d,[(rx+28,ry+45),(rx+110,ry+70+arm),(rx+153,ry+49+arm)],width=8)
    circle(d,rx,ry,46,46,(241,242,248),width=5)
    if awake>.5:
        for ex in [-17,18]:
            circle(d,rx+ex,ry-4,8,4+7*awake,(245,246,250),width=3)
            circle(d,rx+ex-2,ry-3,3,4,(28,30,42),None)
    else:
        stroke(d,[(rx-26,ry-5),(rx-13,ry+2),(rx-1,ry-5)],width=4)
        stroke(d,[(rx+8,ry-5),(rx+22,ry+2),(rx+31,ry-6)],width=4)
    breath = (.5+.5*osc(t,.31))**2
    speech = pose.get('right_mouth',0)
    # Corners stay together on a quiet exhale; upper and lower lip travel differently.
    opening = (1-awake)*breath*5 + awake*speech*14
    mx,my=rx+3,ry+20
    width=13+(1-awake)*4+awake*speech*4
    upper=[];lower=[]
    for k in range(27):
        u=k/26; x=mx+width*(2*u-1)
        arch=math.sin(math.pi*u)
        line=my+1.8*arch+2*u
        upper.append((x,line-opening*.26*arch))
        lower.append((x,line+opening*arch**.72))
    if opening<1.4: stroke(d,upper,width=2)
    else:
        d.polygon(upper+lower[::-1],fill=(48,32,48))
        if opening>6: stroke(d,lower[11:21],(199,126,146),2)
    # pillow and blanket over sleeping figure
    poly(d,[(562,360),(607,349),(647,364),(664,384),(606,406),(567,398)],(164,170,207),width=4)
    poly(d,[(602,417),(648,404),(728,407),(819,399),(892,414),(894,463),
            (837,481),(660,476)],(168,178,210),width=5)
    stroke(d,[(642,439),(714,448),(806,440)],(104,118,164),3)
    # foreground footboards
    rectangle(d,(77,425,404,473),(80,73,104),width=6,radius=6)
    rectangle(d,(532,462,912,508),(79,76,113),width=6,radius=6)
    # float Zs with varying opacity simulated via color
    for k in range(3 if awake<.5 else 0):
        phase = ((t*.6 + k/3) % 1)
        x=772 + 27*k + 12*osc(t,.2,k/3)
        y=289 - 65*phase - k*16
        s=20+4*k
        d.text((int(x),int(y)),"Z",font=font(s),fill=(171+15*k,183+8*k,215))
    return im


