import math
import cairo
S,C,PI=math.sin,math.cos,math.pi
ink='#263044'
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def col(h):g.set_source_rgb(*rgb(h))
def fill(h):col(h);g.fill()
def oval(x,y,a,b,h):
    g.save();g.translate(x,y);g.scale(max(.01,a),max(.01,b));g.arc(0,0,1,0,2*PI);g.restore();fill(h)
def path(points,h,w=0):
    g.move_to(*points[0])
    for q in points[1:]:g.line_to(*q)
    if w:col(h);g.set_line_width(w);g.stroke()
    else:g.close_path();fill(h)
def rect(x,y,w,h,c):g.rectangle(x,y,w,h);fill(c)
def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def sky(t,p,cam):
    night=p['tone']=='night';top,bot=('#41466a','#b08da0') if night else ('#92c9c6','#ffddad')
    grad=cairo.LinearGradient(0,0,0,460);grad.add_color_stop_rgb(0,*rgb(top));grad.add_color_stop_rgb(1,*rgb(bot))
    g.set_source(grad);g.paint();oval(276-cam*.2,125,28,28,'#fff0bf')
    if night:
        for i in range(27):oval((137*i)%370,30+(i*37)%190,1,1,'#f5dcbf')
    for j,h in enumerate(['#998c9d','#7d8593','#557780']):
        pts=[(x,290+23*j+25*S((x+cam*.25)/75+j*2)+9*C(x/43)) for x in range(-80,462,4)]
        path(pts+[(470,480),(-80,480)],h)
    g.save();g.translate(-cam*.45,0)
    if p['place']=='garden':
        for i in range(10):
            x=-55+i*51;y=361+11*S(i);path([(x,y),(x-2,y+64)],'#76665a',5)
            oval(x,y,23,27,'#537e75');oval(x-9,y-7,15,16,'#69978a')
    else:
        for i in range(12):
            x=i*43-52;y=295+(i*53)%81
            rect(x,y,38,153,'#626878' if night else '#947d79')
            for j in range(5):rect(x+6+(j%2)*16,y+10+(j//2)*15,7,8,'#d3aa85')
        if p['place']=='workshop':
            for x in (11,104,308):
                rect(x,188,6,221,ink);rect(x-20,219,48,6,ink)
                path([(x-21,219),(x+2,188),(x+26,219)],'#61636f',2)
    g.restore();rect(-80,458,535,220,'#908188' if night else '#a5ad85');rect(-80,473,535,5,'#655f6c')
    for i in range(-3,14):path([(i*43-cam,477),(i*43-cam-58,650)],'#777988',1.1)
    if p['place']=='garden':
        for i in range(24):
            x=(i*77)%390-12; y=432+(i*17)%23;path([(x,y),(x-2,y+8)],'#617a61',2);oval(x,y,3,2,'#f2bb83')
    else:
        for i in range(9):rect(i*52-16-cam*.65,413,5,46,'#4c5263')
        rect(-90,420,540,4,'#626375')
def ik(a,b,l,m,bend):
    dx,dy=b[0]-a[0],b[1]-a[1];dist=max(.01,math.hypot(dx,dy));d=max(abs(l-m)+.01,min(l+m-.01,dist))
    u=(l*l-m*m+d*d)/(2*d);v=math.sqrt(max(0,l*l-u*u))*bend
    return a[0]+(u*dx-v*dy)/dist,a[1]+(u*dy+v*dx)/dist
def limb(a,b,r,s,h):
    g.save();g.translate(*a);g.rotate(math.atan2(b[1]-a[1],b[0]-a[0]));l=math.dist(a,b)
    path([(0,-r),(l,-s),(l,s),(0,r)],h);oval(0,0,r,r,h);oval(l,0,s,s,h);g.restore()
def actor(t,k,p,cue,amp,mouth=None):
    dt=t-cue;wind=math.exp(-((dt+.25)/.18)**2);peak=math.exp(-(dt/.37)**2)
    j=peak if p['reaction']=='jump' else 0;duck=peak if p['reaction']=='duck' else 0
    x=186-8*wind+3*S(t*2);y=416+9*wind+26*duck-60*j
    feet=[(169,470-60*j),(206,470-71*j)];hips=[(x-7,y),(x+8,y)]
    for i,(f,a) in enumerate(zip(feet,hips)):
        b=ik(a,f,33,33,-1 if i else 1);limb(a,b,9.3,7,'#484d65');limb(b,f,7,4.5,'#555c71')
        oval(f[0]+3,f[1],10,5,'#443948');path([(f[0]-5,f[1]+3),(f[0]+11,f[1]+3)],'#d6ad92',2)
    sh=(x-4-9*duck,y-43+7*duck)
    path([(sh[0]-11,sh[1]-4),(sh[0]+12,sh[1]-4),(x+15,y+6),(x-16,y+6)],'#de7663')
    path([(sh[0]-7,sh[1]-3),(sh[0]+5,sh[1]+7),(sh[0]+10,sh[1]-3)],'#ffeece')
    path([(sh[0]-7,sh[1]),(x+9,y+1)],'#81505c',4)
    hx,hy=sh[0],sh[1]-17
    oval(hx-15,hy-13,10,10,ink);oval(hx,hy,19,21,ink);oval(hx+1,hy+1,17.7,19.6,'#edbb98')
    oval(hx-4,hy-14,17,8,'#3c3347');path([(hx-16,hy-13),(hx+13,hy-17),(hx+6,hy-6),(hx+3,hy-12),(hx-11,hy-2)],'#3c3347')
    blink=max(.1,min(1,abs(t%2.8-1.65)*16));look=-1 if k[0]<x else 1
    for ex in [-5,7]:
        oval(hx+ex,hy,4,4*blink,'#fff2de');oval(hx+ex+look*1.6,hy,1.8,(2.3+peak)*blink,ink)
        path([(hx+ex-3,hy-7-peak*3),(hx+ex+2,hy-7)],ink,1.5)
    oval(hx+2,hy+10,*(mouth or (3+2*amp,1+4*amp+2*peak)),'#784957')
    for i in [-1,1]:
        a=(sh[0]+i*11,sh[1]+3)
        if p['reaction']=='reach' and i==1:
            b=(a[0]+12+27*peak,a[1]+33-39*peak)
        else:b=(a[0]+i*(7+24*peak),a[1]+41-53*peak+2*S(t*3+i))
        joint=ik(a,b,23,22,-i)
        limb(a,joint,6,4.2,'#c1665a' if i<0 else '#e17e66');limb(joint,b,4.5,3,'#eabb96');oval(*b,4.6,4,'#f0c4a0')
def object_at(x,y,theta,p):
    g.save();g.translate(x,y);g.rotate(theta)
    if p=='ball':
        oval(0,0,17,17,ink);oval(0,0,15.5,15.5,'#f8bf64');path([(-15,0),(-6,-4),(7,-2),(15,-6)],'#bd775c',2);oval(-5,-7,3,2,'#fff1bf')
    elif p=='parcel':
        rect(-17,-14,34,28,'#795648');rect(-16,-13,32,26,'#cc946b');rect(-4,-13,7,26,'#f5d49a');rect(5,1,8,6,'#fff1ce')
    else:
        for sign in (-1,1):oval(sign*11,-15,7,4,'#e4a25c');path([(sign*8,13),(sign*12,18)],ink,3)
        oval(0,0,17,17,ink);oval(0,0,14.8,14.8,'#ffe3af')
        for i in range(12):oval(S(i*PI/6)*12,C(i*PI/6)*12,1,1,ink)
        path([(-6,-3),(0,0),(2,-8)],ink,2)
    g.restore()
def frame(t,i,p,sim,amp,character=None,plate=None,mouth=None):
    global g
    surf=cairo.ImageSurface(cairo.FORMAT_RGB24,WIDTH,WIDTH*16//9);g=cairo.Context(surf);g.scale(WIDTH/360,WIDTH/360)
    g.set_line_cap(cairo.LINE_CAP_ROUND);g.set_line_join(cairo.LINE_JOIN_ROUND)
    cue=sim['cue']/24;kx,ky,ang=sim['rows'][i];cut=cue-.26
    close=p['camera']=='close'
    if t<1.4:z=1.13+.04*t;cx,cy=191,361
    elif close and cut<=t<cue+.93:z=1.64;cx,cy=190+4*S(t*6),390
    else:z=1.01+.065*smooth((t-2)/3);cx,cy=182+6*S(t*.65),326
    shake=sum(math.exp(-(i-hit)/3)*2.5 for hit in sim['hits'] if 0<=i-hit<14)
    g.translate(180,320);g.scale(z,z);g.translate(-cx+shake*S(i*3),-cy)
    if plate is None:
        sky(t,p,4*S(t*.7))
    else:
        g.save()
        # Paint past the camera bounds so pans never reveal empty pixels.
        scale=max(540/plate.get_width(),800/plate.get_height())
        g.translate(180-plate.get_width()*scale/2,320-plate.get_height()*scale/2)
        g.scale(scale,scale)
        g.set_source_surface(plate)
        g.paint()
        g.restore()
    oval(186,473,30,3,'#797477')
    if i>=48:
        for n in (6,4,2):
            px,py,_=sim['rows'][max(0,i-n)]
            if math.hypot(px-kx,py-ky)>8:path([(px-4,py+2),(px+2,py+2)],'#dfbc9f',1.2)
    (character or actor)(t,(kx,ky),p,cue,amp,mouth);object_at(kx,ky,ang,p['prop'])
    for hit in sim['hits']:
        u=(i-hit)/10
        if 0<u<1:
            xx,yy,_=sim['rows'][hit]
            for n in range(5):
                dx=(n-2)*8;dy=-9-abs(n-2)*2
                path([(xx+dx*(.4+u),yy+13+dy*u),(xx+dx*(.6+u),yy+13+dy*(u+.2))],'#ffe0ac',1.5*(1-u))
    surf.flush();return bytes(surf.get_data())
