#!/usr/bin/env python3
"""Original 2D slapstick test: deterministic CPU-only frame animation (Pillow+FFmpeg).
No third-party artwork, audio, GPU, or pretrained models are used.
"""
import argparse, math, subprocess, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FPS=24
DURATION=12.0
W=720
S=1.25
Z=lambda a:int(round(a*S))

def mix(a,b,t): return a+(b-a)*max(0,min(1,t))
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def easeout(t):
    t=max(0,min(1,t));return 1-(1-t)**3

def ink(d,points,fill='#11131b',width=6,joint='curve'):
    pts=[(Z(x),Z(y)) for x,y in points]
    if len(pts)>1: d.line(pts,fill=fill,width=Z(width),joint=joint)
    r=Z(width*.49)
    for p in (pts[0],pts[-1]):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=fill)

def oval(d,x0,y0,x1,y1,fill,outline=None,width=0):
    d.ellipse((Z(x0),Z(y0),Z(x1),Z(y1)),fill=fill,outline=outline,width=Z(width))
def rect(d,x0,y0,x1,y1,fill,outline=None,width=0,radius=0):
    if radius: d.rounded_rectangle((Z(x0),Z(y0),Z(x1),Z(y1)),radius=Z(radius),fill=fill,outline=outline,width=Z(width))
    else:d.rectangle((Z(x0),Z(y0),Z(x1),Z(y1)),fill=fill,outline=outline,width=Z(width))
def poly(d,pts,fill,outline=None,width=0):
    pts=[(Z(x),Z(y)) for x,y in pts];d.polygon(pts,fill=fill)
    if outline:d.line(pts+[pts[0]],fill=outline,width=Z(width),joint='curve')

def font(size,bold=False):
    f='/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('-Bold' if bold else '')+'.ttf'
    return ImageFont.truetype(f,Z(size))
FONT=font(24,True); BIGFONT=font(46,True)

def text(d,xy,s,color='#16172b',f=FONT,stroke=0,sc='#fff'):
    d.text((Z(xy[0]),Z(xy[1])),s,font=f,fill=color,stroke_width=Z(stroke),stroke_fill=sc)

def bg_room(d,t,cam=0):
    rect(d,0,0,720,530,'#bde9f8');rect(d,0,527,720,720,'#729dbb')
    rect(d,0,527,720,538,'#334e73')
    # multi-pane left window
    rect(d,16,120,143,352,'#effbfb','#3e5b83',6,4)
    rect(d,25,128,135,341,'#8dcbf1')
    oval(d,49,151,113,214,'#fff5aa');poly(d,[(25,310),(52,273),(88,286),(135,252),(135,340),(25,340)],'#76ca82')
    ink(d,[(80,128),(80,340)],'#3e5b83',5)
    # shelf and books
    rect(d,175,138,374,151,'#a96f54','#7b4b39',2,2)
    for bx,by,col in [(215,95,'#e4f2f8'),(240,91,'#5f87cc'),(275,98,'#f29a89'),(306,84,'#61baba')]:
        rect(d,bx,by,bx+22,138,col,'#36506e',2,2)
    rect(d,179,104,202,138,'#b97450');oval(d,173,73,211,107,'#44a85b');oval(d,182,59,200,99,'#278f56')
    for x,y,sz in [(405,119,71),(505,150,61),(610,100,51)]:
        rect(d,x,y,x+sz,y+sz*1.15,'#fd9a81','#ef765e',4,3)
        rect(d,x+9,y+10,x+sz-9,y+sz*1.15-10,'#fff7d6')
    # sofa
    rect(d,179,400,508,537,'#a41043','#521d3b',6,28)
    rect(d,198,386,493,485,'#ea1950','#7d0c39',5,24)
    rect(d,184,455,508,538,'#c41049','#6c0c35',5,15)
    rect(d,181,514,229,553,'#73173b',radius=6);rect(d,468,513,505,553,'#73173b',radius=6)
    ink(d,[(350,399),(350,514)],'#a00b39',3)
    # entrance and floor-side plant
    rect(d,551,231,706,528,'#335781','#0d3658',6,4)
    rect(d,562,242,697,515,'#8ab7d9')
    rect(d,575,254,688,400,'#7ce3f6')
    poly(d,[(575,400),(688,369),(688,514),(575,514)],'#75be65')
    rect(d,684,231,710,534,'#416d99')
    oval(d,681,371,698,388,'#f9d85c','#6e5035',2)
    rect(d,526,528,568,574,'#dd8247','#954c34',3,4)
    for px,py in [(546,497),(536,475),(552,459),(529,497)]:oval(d,px-12,py-26,px+12,py+18,'#23865c')

def bg_street(d,t):
    rect(d,0,0,720,488,'#9cdfef');rect(d,0,487,720,720,'#8eb6c9')
    # bright skyline
    for x,y,w,h,col in [(-10,160,128,328,'#6486ac'),(104,102,113,390,'#7c90c3'),(211,184,151,303,'#8e91cb'),(358,83,127,412,'#5678af'),(480,149,135,338,'#7090ba'),(610,112,142,375,'#7c8eaf')]:
        rect(d,x,y,x+w,y+h,col)
        for wx in range(x+19,x+w-14,29):
            for wy in range(y+25,y+h-16,39):rect(d,wx,wy,wx+12,wy+17,'#d3e3ff')
    rect(d,0,455,720,500,'#62c875');rect(d,0,510,720,720,'#626781');rect(d,0,533,720,540,'#f2d1a1')
    for x in range(-130,950,180):rect(d,x-(int(t*230)%180),634,x+92-(int(t*230)%180),646,'#f4daa0',radius=4)
    # distant pink store
    rect(d,318,364,442,485,'#ffe8c5','#d48279',5,8);rect(d,329,392,432,448,'#b8e9ed')
    poly(d,[(301,367),(458,367),(445,334),(315,334)],'#fa8185','#b14f77',4)

def bg_wall(d,t):
    rect(d,0,0,720,557,'#fde2ae');rect(d,0,557,720,720,'#7b9eb3')
    rect(d,0,543,720,566,'#b2cddd')
    for x in [69,496]:
        rect(d,x,161,x+150,454,'#e7ab83','#c18170',6,8)
        rect(d,x+16,184,x+133,432,'#ffecc9')
    # big prop cushion
    rect(d,287,479,466,572,'#ea3160','#a41e49',6,25)
    # little shelf
    rect(d,534,271,684,290,'#ad7559')
    oval(d,575,222,652,274,'#4e9f69')

def donut(d,x,y,rot=0,scale=1):
    """Hand-painted rotating ring based on ellipse with colorful sprinkles."""
    r=30*scale;oval(d,x-r,y-r*.8,x+r,y+r*.8,'#b66d3b','#3b2631',5)
    oval(d,x-r*.84,y-r*.71,x+r*.86,y+r*.7,'#f2a3d2','#6e3f53',2)
    oval(d,x-r*.31,y-r*.33,x+r*.31,y+r*.33,'#6f4032','#703e39',2)
    oval(d,x-r*.21,y-r*.25,x+r*.21,y+r*.25,'#a7ddeb')
    for an in range(0,360,60):
        a=(an+rot)*math.pi/180
        px=x+math.cos(a)*r*.63;py=y+math.sin(a)*r*.44
        ink(d,[(px-3,py-3),(px+3,py+2)],['#e4ff82','#e56d70','#9be2ff','#fff'][an//60%4],3)

def action_lines(d,x,y,side=1,n=4):
    for j in range(n):
        yy=y+(j-2)*18
        ink(d,[(x-side*(35+j*14),yy-4),(x-side*(13+j*7),yy-6)],'#fff3bf',4)

def starburst(d,x,y,k=1,col='#ffd442'):
    pts=[]
    for i in range(14):
        ang=math.pi*i/7; r=(37 if i%2==0 else 18)*k
        pts.append((x+math.cos(ang)*r,y+math.sin(ang)*r))
    poly(d,pts,col,'#3d2c43',3)

def toon(d,x,y,who='girl',pose='idle',phase=0,look=1,expr='smile',angle=0,s=1,donut_hand=False):
    """Draw an original character with smooth single-stroke limbs, no visible joint circles."""
    # Coordinates are local, transformed with simple squash/stretch and tilt.
    tall=1.0 if pose!='squash' else .72
    def p(a,b):return (x+(a*math.cos(angle)-b*math.sin(angle))*s, y+(a*math.sin(angle)+b*math.cos(angle))*s)
    dark='#171522'
    g=who=='girl'
    skin='#c68561' if g else '#eaa268'
    dress='#ffe15e' if g else '#57dff2'
    hair='#43303a' if g else '#2b2638'
    cy=-130*tall; # head
    hip=-23*tall
    # run cycles; fully extended stride to communicate fast action
    if pose=='run':
        swing=math.sin(phase); swing2=math.cos(phase)
        left=( -25+52*swing,70-22*max(0,swing2))
        right=(25-52*swing,70-22*max(0,-swing2))
        knee1=(-15+23*swing,19-22*max(0,swing2))
        knee2=(15-23*swing,19-22*max(0,-swing2))
    elif pose=='jump':
        left=(-42,40);right=(48,22);knee1=(-39,8);knee2=(32,2)
    elif pose=='fall':
        left=(-52,18);right=(42,16);knee1=(-43,-2);knee2=(38,-6)
    elif pose=='sit':
        left=(-26,54);right=(36,47);knee1=(-45,3);knee2=(42,-3)
    else:
        left=(-22,70);right=(24,70);knee1=(-19,22);knee2=(20,24)
    # legs behind torso, elegant single strokes: no joint dots
    for hk,kn,ft in [(-14,knee1,left),(14,knee2,right)]:
        pts=[p(hk,hip),p(kn[0],kn[1]),p(ft[0],ft[1])]
        ink(d,pts,dark,7)
        if pose!='fall':
            sx,sy=p(ft[0]+look*8,ft[1]+3)
            oval(d,sx-13*s,sy-3*s,sx+9*s,sy+5*s,dark)
    # arms behind torso unless donut held
    ax=p(-27,-77*tall);bx=p(27,-77*tall)
    if pose=='run':
        wav=math.sin(phase)
        ahand=p(-43+23*wav,-25-37*wav)
        bhand=p(43-23*wav,-25+37*wav)
    elif pose=='jump':ahand=p(-63,-128);bhand=p(64,-138)
    elif pose=='fall':ahand=p(-78,-86);bhand=p(68,-38)
    elif pose=='sit':ahand=p(-38,-48);bhand=p(42,-53)
    elif pose=='reach':ahand=p(-37,-40);bhand=p(86,-140)
    else:ahand=p(-40,-31);bhand=p(40,-44)
    if donut_hand:bhand=p(78,-119)
    ink(d,[ax,p(-40,-60*tall),ahand],dark,7)
    ink(d,[bx,p((bx[0]-x)/s+9,-67*tall),bhand],dark,7)
    # torso
    if g:
        poly(d,[p(-24,-93*tall),p(25,-92*tall),p(39,-21*tall),p(-36,-21*tall)],dress,dark,5)
        ink(d,[p(-19,-90*tall),p(20,-91*tall)],'#fff1b8',3)
    else:
        poly(d,[p(-25,-99*tall),p(28,-100*tall),p(29,-27*tall),p(-26,-27*tall)],dress,dark,5)
        ink(d,[p(-9,-32*tall),p(14,-32*tall)],'#35a8c9',3)
    # head and ears
    hx,hy=p(0,cy)
    oval(d,hx-52*s,hy-49*s,hx+52*s,hy+50*s,skin,dark,5)
    if g:
        # curly bun, hair crown, little forehead flick
        bx0,by0=p(42,cy-34);oval(d,bx0-24*s,by0-24*s,bx0+25*s,by0+25*s,hair,dark,4)
        for dx,dy in [(25,-62),(47,-54),(55,-34),(34,-43)]:
            xx,yy=p(dx,cy+dy);oval(d,xx-13*s,yy-12*s,xx+13*s,yy+12*s,hair)
        poly(d,[p(-41,cy-21),p(-16,cy-52),p(17,cy-51),p(35,cy-43),p(9,cy-24),p(-6,cy-38)],hair)
    else:
        poly(d,[p(-47,cy-21),p(-54,cy-44),p(-12,cy-63),p(28,cy-56),p(44,cy-29),p(15,cy-43),p(-10,cy-37)],hair)
        poly(d,[p(-49,cy-56),p(31,cy-62),p(49,cy-44),p(-45,cy-35)],'#fa555c',dark,3)
        ink(d,[p(22,cy-43),p(66,cy-34)],'#ad263f',9)
    # bulging asymmetrical whites. For surprise make eyes notably larger.
    e=1.14 if expr in ('shock','panic') else 1
    yy=cy-3
    for dx,rad in [(-22,18),(17,22)]:
        ex,ey=p(dx,yy)
        oval(d,ex-rad*s,ey-rad*e*s,ex+rad*s,ey+rad*e*s,'white',dark,3)
        pupil=look*5 if expr!='panic' else -look*3
        px,py=p(dx+pupil,yy+1)
        oval(d,px-5*s,py-7*s,px+6*s,py+6*s,dark)
        oval(d,px-1*s,py-5*s,px+2*s,py-2*s,'white')
    # expressive mouth
    mx,my=p(6,cy+28)
    if expr in ('shock','panic'):
        oval(d,mx-12*s,my-12*s,mx+17*s,my+19*s,'#451f29',dark,3)
        oval(d,mx-6*s,my+7*s,mx+8*s,my+15*s,'#f98b9c')
    elif expr=='grin':
        oval(d,mx-19*s,my-10*s,mx+23*s,my+12*s,'#3d1c2b',dark,3)
        rect(d,mx-13*s,my-7*s,mx+16*s,my+1*s,'white',radius=3)
    else:
        ink(d,[p(-10,cy+26),p(4,cy+31),p(18,cy+25)],'#4b1e2b',3)
    if donut_hand:donut(d,bhand[0]+look*8,bhand[1]-14,rot=phase*2,scale=.75)

def burst_caption(d,t,word,x=290,y=105,col='#fff598'):
    p=min(1,max(0,t)*9)
    if p<=0:return
    sc=.75+.35*(1-(1-p)**3)
    starburst(d,x,y,sc,col)
    f=font(22,True)
    bb=d.textbbox((0,0),word,font=f); tw=(bb[2]-bb[0])/S
    text(d,(x-tw/2,y-14),word,'#20204e',f)

def render_at(t):
    im=Image.new('RGB',(Z(W),Z(W)),'#f9d9a0');d=ImageDraw.Draw(im)
    # Multiple deliberately staged shots with physical anticipation / contact / follow-through.
    if t<3.25:
        bg_room(d,t)
        # subtle pop-in and confident walk
        bx=mix(-65,154,easeout(t/.8)) if t<.8 else 154+min(22,(t-.8)*7)
        g_x=366; by=465
        if t<1.55:
            toon(d,g_x,470,'girl','sit',t*8,1,'smile',s=.96)
            toon(d,bx,488,'boy','run' if t<.8 else 'idle',t*16,1,'grin',s=.9,donut_hand=True)
        else:
            surprise=smooth((t-1.56)/.3)
            # Girl startled standing with exaggerated squash/stretch, then lean forward
            gy=470-mix(0,38,surprise)
            toon(d,g_x+16*surprise,gy,'girl','jump' if t>2.18 else 'idle',t*13,1,'shock',s=.95+surprise*.1)
            toon(d,bx+12,487,'boy','reach',t*7,1,'panic' if t>2.4 else 'grin',s=.91,donut_hand=True)
            if 1.63<t<2.55:burst_caption(d,t-1.63,'MY DONUT?!',367,228,'#fff0a0')
        if t>2.65:
            for k in range(4):action_lines(d,208+k*9,335+k*7,1,3)
    elif t<6.0:
        u=t-3.25
        bg_street(d,u)
        # real directional translation with shared camera-ish pan
        gx=130+u*180; bx=278+u*168
        # brisk run / eye lines / exaggerated alternating gait
        for j in range(5):action_lines(d,gx-30-j*14,445+j*12,1,3)
        gy=512-12*abs(math.sin(u*14));by=514-8*abs(math.sin(u*15))
        toon(d,gx,gy,'girl','run',u*17,1,'grin',s=.92)
        toon(d,bx,by,'boy','run',u*18,1,'panic',s=.90,donut_hand=u<1.35)
        # hand slip releases pastry into ballistic arc
        if u>=1.35:
            q=u-1.35
            donut(d,bx+48+q*61,350-150*q+110*q*q,rot=q*500,scale=.75)
            if q<.45:burst_caption(d,q,'OOPS!',488,170)
        if u>2.42:
            rect(d,667,375,717,570,'#ffb83d','#572b3a',6,12)
    elif t<8.55:
        u=t-6
        bg_wall(d,u)
        # wall crash scene - the donut flies upward, girl vaults toward it
        if u<1.05:
            gx=130+u*245; gy=500-145*math.sin((u/1.05)*math.pi)
            toon(d,gx,gy,'girl','jump',u*16,1,'grin',s=.98)
            bx=545-u*60
            toon(d,bx,512,'boy','run',u*24,-1,'shock',s=.92)
            donut(d,400+u*102,160+40*u+70*u*u,rot=u*610,scale=.95)
        elif u<1.63:
            p=smooth((u-1.05)/.58)
            toon(d,385,389+75*p,'girl','reach',u*13,1,'shock' if p>.72 else 'grin',s=.99)
            # donut held at girl's outstretched hand at moment of catch
            donut(d,471,257+75*p,rot=u*360,scale=.86)
            toon(d,492+40*p,504+70*p,'boy','fall',u*14,-1,'panic',angle=-p*.8,s=.94)
            burst_caption(d,u-1.1,'CATCH!',487,137)
        else:
            p=smooth((u-1.63)/.8)
            toon(d,385,463,'girl','idle',u*12,1,'grin',s=.95,donut_hand=True)
            toon(d,535,553,'boy','fall',u*12,-1,'shock',angle=-1.15,s=.92)
            for j in range(5):
                xx=530+math.cos(j*math.tau/5+u*2)*83; yy=460+math.sin(j*math.tau/5)*61
                starburst(d,xx,yy,.18,'#fff3b4')
            burst_caption(d,u-1.65,'BONK!',520,294,'#ffcb7f')
    else:
        u=t-8.55
        bg_room(d,t)
        # safe payoff after impact; donut bounces onto boy's cap
        girlx=345; boyx=480
        toon(d,girlx,480,'girl','sit',u*5,1,'grin',s=.94)
        if u<1.5:
            fallp=smooth(u/1.15)
            toon(d,boyx+35*(1-fallp),480-45*(1-fallp),'boy','fall' if u<.65 else 'sit',u*9,-1,'shock',angle=-.7*(1-fallp),s=.86)
            donut(d,500-9*fallp,180+235*easeout(u/1.3),rot=u*340,scale=.78)
        else:
            toon(d,boyx,480,'boy','sit',u*7,-1,'panic',s=.88)
            donut(d,480,287-6*math.sin(u*5),rot=10,scale=.78)
            if u<3.1:burst_caption(d,u-1.5,'SERIOUSLY?!',470,190)
        if u>2.75:
            for i in range(14):
                x=90+(i*113)%570; y=((i*193+u*75)%430)+26
                col=['#fb84a7','#fbe386','#9b83ed','#66d4d4'][i%4]
                poly(d,[(x,y),(x+8,y+4),(x+3,y+15)],col)
    # crisp native image, with anti-aliased strokes from SSAA and no watermark.
    return im.resize((W,W),Image.Resampling.LANCZOS)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='Fast_Action_Donut_Chase_CPU.mp4');ap.add_argument('--duration',type=float,default=DURATION);ap.add_argument('--fps',type=int,default=FPS);ap.add_argument('--contact-sheet',default='Fast_Action_Donut_Chase_contact.jpg');args=ap.parse_args()
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg:raise SystemExit('ffmpeg is required')
    cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{W}','-framerate',str(args.fps),'-i','pipe:0','-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast','-crf','21','-movflags','+faststart',args.output]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    count=int(round(args.duration*args.fps))
    try:
        for n in range(count):
            im=render_at(n/args.fps)
            proc.stdin.write(im.tobytes())
        proc.stdin.close();err=proc.stderr.read();rc=proc.wait()
        if rc!=0:raise RuntimeError(err.decode('utf-8','replace'))
    finally:
        if proc.poll() is None:proc.kill()
    # Actual timeline thumbnails for independent visual QA.
    samples=[render_at(t) for t in [0.55,1.65,2.5,3.6,4.6,5.5,6.45,7.3,8.2,9.1,10.1,11.35]]
    cs=Image.new('RGB',(4*288,3*322),'#fff')
    dd=ImageDraw.Draw(cs)
    for i,img in enumerate(samples):
        x=(i%4)*288;y=(i//4)*322
        cs.paste(img.resize((288,288),Image.Resampling.LANCZOS),(x,y))
        dd.text((x+12,y+291),f'{[0.55,1.65,2.5,3.6,4.6,5.5,6.45,7.3,8.2,9.1,10.1,11.35][i]:.2f} sec',fill='#222')
    cs.save(args.contact_sheet,quality=91)
    print(json.dumps({'video':args.output,'frames':count,'fps':args.fps,'seconds':args.duration,'size':f'{W}x{W}','sound':'none','gpu':'not required','contact_sheet':args.contact_sheet},indent=2))
if __name__=='__main__':main()