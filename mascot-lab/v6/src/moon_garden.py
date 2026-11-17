"""Original procedural painted moon-garden scene; no licensed image dependencies.

Canonical permanent Funny Toon Ever mascot foreground is supplied by V5 renderer.
Bell button anchor is exactly (406,606) so unchanged hand IK touches the object.
"""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FLOOR=540,960,833
INK='#151d2b'

def font(n=22,bold=False):
    names=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    try:return ImageFont.truetype(names[0 if bold else 1],n)
    except Exception:return ImageFont.load_default()

def blend(a,b,t):return tuple(int(x*(1-t)+y*t) for x,y in zip(a,b))

@lru_cache(maxsize=1)
def backplate():
    im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
    for y in range(H):
        q=y/max(1,H-1)
        if q<.68:
            if q<.4:c=blend((25,33,84),(107,80,154),q/.4)
            else:c=blend((107,80,154),(254,174,123),(q-.4)/.28)
        else:c=blend((51,123,127),(16,76,80),min(1,(q-.68)/.32))
        d.line([(0,y),(W,y)],fill=c)
    # clouds, distant hills and moon
    d.ellipse((34,66,180,212),fill=(239,224,188,250))
    d.ellipse((48,80,166,198),fill=(255,250,218,255))
    for x,y,rx in [(200,135,53),(328,210,62),(406,110,48)]:
        d.ellipse((x-rx,y-10,x+rx,y+14),fill=(170,150,188,105))
        d.ellipse((x-rx*.3,y-29,x+rx*.5,y+12),fill=(184,157,193,135))
    for yshift,color in [(570,'#776d9c'),(613,'#525e98'),(669,'#386e85')]:
        pts=[(-10,785)]+[(x,int(yshift-90*math.sin((x+80)/230)*math.sin((x+200)/120))) for x in range(-10,571,30)]+[(550,820)]
        d.polygon(pts,fill=color)
    d.rectangle((0,745,W,H),fill='#265e61')
    d.polygon([(0,755),(118,729),(249,768),(390,744),(540,765),(540,960),(0,960)],fill='#277c6c')
    d.polygon([(0,833),(540,833),(540,960),(0,960)],fill='#405f57')
    # Curving cobblestone path
    d.polygon([(105,960),(347,960),(347,833),(160,833)],fill='#d7a385')
    for x,y,w in [(102,873,165),(89,917,210),(86,950,230)]:
        d.arc((x,y,x+w,y+35),180,350,fill='#be826c',width=4)
    # left and right tree trunks
    d.polygon([(0,330),(30,336),(45,841),(0,841)],fill='#3c4352')
    d.polygon([(522,200),(550,216),(540,854),(516,854)],fill='#2c394e')
    for x,y,r,col in [(38,371,92,'#276a70'),(70,280,79,'#23787f'),(13,230,68,'#386b72'),(544,315,69,'#2d7279'),(506,205,83,'#357b76')]:
        d.ellipse((x-r,y-r,x+r,y+r),fill=col)
        d.ellipse((x-r*.8,y-r*.86,x+r*.5,y+r*.4),outline='#56a6a0',width=3)
    rng=random.Random(101)
    for _ in range(110):
        x=rng.randint(0,539);y=rng.randint(35,830)
        if y>580 and x>350:continue
        r=rng.choice([1,2,3]);tone=rng.choice(['#f6cd94','#c7f1e0','#ffe7a5','#e1b3ec'])
        d.ellipse((x-r,y-r,x+r,y+r),fill=tone)
    for i in range(44):
        x=rng.randrange(15,540);y=rng.randrange(777,960)
        if 112<x<345 and y>830:continue
        stem=rng.randint(11,22);d.line((x,y,x+4,y-stem),fill='#2c896a',width=3)
        cc=rng.choice(['#fbb3c6','#e4cc66','#b2b9fc','#f9e3f3','#9af0bb'])
        for a in range(0,360,72):
            px=x+4+8*math.cos(math.radians(a));py=y-stem+8*math.sin(math.radians(a))
            d.ellipse((px-5,py-5,px+5,py+5),fill=cc)
        d.ellipse((x,y-stem-2,x+8,y-stem+6),fill='#f7b04e')
    return im

def draw_bell_tower(im,t,action,z):
    d=ImageDraw.Draw(im,'RGBA')
    # the magic bell and tree trunk are authored around the retained hand-contact target (406,606)
    d.ellipse((337,818,530,851),fill=(4,43,49,110))
    d.rounded_rectangle((359,347,523,835),radius=19,fill='#403b72',outline='#f8dc9a',width=8)
    d.rounded_rectangle((374,363,508,823),radius=13,fill='#67467c',outline='#ad8fc1',width=4)
    for xx,yy in [(393,407),(482,417),(394,760),(481,750)]:
        d.ellipse((xx-7,yy-7,xx+7,yy+7),fill='#f4d68e',outline='#6d4f52',width=2)
    d.rounded_rectangle((382,376,501,462),radius=13,fill='#1b4569',outline='#e5c993',width=4)
    d.text((442,396),'WISH',font=font(25,True),fill='#ffeeb6',anchor='mt')
    d.text((442,424),'BELL',font=font(24,True),fill='#ffeeb6',anchor='mt')
    d.arc((382,482,497,557),185,358,fill='#fbd9aa',width=5)
    for xx in range(391,500,17):d.ellipse((xx-3,541,xx+3,547),fill='#dec4f6')
    # bronze bell at contact; a small luminous tap target where retained V5 fist goes
    d.ellipse((390,587,425,626),fill='#a9693c',outline='#f9db93',width=4)
    d.ellipse((397,595,415,617),fill='#f7c66d',outline='#f9efbc',width=2)
    d.ellipse((400,619,412,625),fill='#583e56')
    if action=='knock':
        elapsed=t-3.4;nearness=min(abs(elapsed-v) for v in (.32,.81,1.31))
        if nearness<.14:
            k=1-nearness/.14
            for rr in (28,43,61):
                d.arc((406-rr,606-rr,406+rr,606+rr),240,65,fill=(255,246,177,int(210*k)),width=max(2,int(5*k)))
            for j in range(5):
                angle=2*math.pi*j/5+t*7
                px=406+70*math.cos(angle);py=606+70*math.sin(angle)
                d.ellipse((px-4,py-4,px+4,py+4),fill='#fff4bf')
    if action in ('reveal','celebrate'):
        p=min(1,max(0,(t-9.26)/1.1))
        if p:
            # reveal is a blooming luminous flower rather than the original restroom opening
            radius=15+74*math.sin(p*math.pi/2)
            cx,cy=440,595
            for a in range(0,360,45):
                rad=math.radians(a+t*8)
                px=cx+radius*.6*math.cos(rad);py=cy+radius*.6*math.sin(rad)
                d.ellipse((px-radius*.38,py-radius*.38,px+radius*.38,py+radius*.38),fill=(244,153,209,int(230*p)),outline=(255,219,178,255),width=3)
            d.ellipse((cx-radius*.29,cy-radius*.29,cx+radius*.29,cy+radius*.29),fill='#ffdb6c',outline='#fff3b9',width=4)


def background(t,action,z,source_bg=None):
    im=source_bg.copy() if source_bg is not None else backplate().copy()
    if im.mode!='RGBA':im=im.convert('RGBA')
    draw_bell_tower(im,t,action,z)
    d=ImageDraw.Draw(im,'RGBA')
    # parallax floating fireflies/lanterns make the setting feel alive
    for k in range(14):
        a=k*2.398;t0=t*.8+k*.3
        x=75+(k*37)%340+10*math.sin(t0);y=455+(k*47)%330+10*math.cos(t0)
        r=2+(k%2);d.ellipse((x-r,y-r,x+r,y+r),fill=(255,244,184,150+int(75*(math.sin(t0)+1)/2)))
    if action in ('shock','jump','slip','fall'):
        # Short magical glitter cloud rather than generic black speed lines.
        q=math.sin((t-5.28)*2)
        for k in range(9):
            a=math.radians(k*40)+t*2
            x=416+(35+(k%3)*17)*math.cos(a);y=575+(35+(k%4)*17)*math.sin(a)
            d.line((x-5,y,x+5,y),fill=(255,235,170,180),width=3)
            d.line((x,y-5,x,y+5),fill=(255,235,170,180),width=3)
    if action=='celebrate':
        d.rounded_rectangle((297,473,508,537),radius=20,fill=(31,68,86,232),outline='#ffe3b5',width=4)
        d.text((402,485),'WOW!',font=font(30,True),anchor='mt',fill='#fff3bc')
    return im
