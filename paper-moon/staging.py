"""The visitor, light trails and envelope. Drawn on the same clock as the actors."""
import math
from PIL import Image, ImageDraw
from room import font
def draw(im,t,clock,x,y,size,angle,lamp,shot,u):
    d=ImageDraw.Draw(im,'RGBA')
    # Reading lamp on the nightstand. Its pool brightens as the moth approaches.
    for r in range(82,9,-8):
        d.ellipse((478-r,294-r,478+r,294+r),fill=(255,201,114,int(2+6*lamp)))
    d.line((480,294,480,324),fill='#302938',width=5)
    d.ellipse((460,320,500,327),fill='#42384b',outline='#292437',width=2)
    d.polygon([(463,277),(490,277),(501,299),(453,299)],fill=(int(140+103*lamp),int(114+86*lamp),int(100+36*lamp),255),outline='#332b43',width=2)
    gust=shot.get('gust',0)*math.sin(math.pi*u)**2
    for i in range(8):
        if gust:
            xx=(900-clock*95+i*117)%970;yy=170+i%4*20
            d.arc((xx,yy,xx+43,yy+8),0,160,fill=(200,220,248,int(120*gust)),width=2)
    if size<=.01:return
    a=math.radians(angle);flap=.22+.78*abs(math.sin(clock*9.3));pulse=math.sin(clock*2)
    def pt(dx,dy):
        return x+size*(dx*math.cos(a)-dy*math.sin(a)),y+size*(dx*math.sin(a)+dy*math.cos(a))
    def shape(points,fill):d.polygon([pt(*p) for p in points],fill=fill,outline='#3a3445',width=max(1,round(size*1.4)))
    for sign in (-1,1):
        wing=sign*flap
        shape([(0,0),(wing*14,-17),(wing*23,-18),(wing*21,-4),(wing*9,4),(wing*3,1)],'#efcc98')
        shape([(0,0),(wing*14,-10),(wing*19,-13),(wing*8,-3)],'#bc927f')
        shape([(0,1),(wing*12,0),(wing*15,7),(wing*6,11)],'#e7b88e')
    d.line([pt(0,-8),pt(0,8)],fill='#554358',width=max(2,round(3*size)))
    for k in (-1,1):d.line([pt(0,-6),pt(k*5,-12)],fill='#5c4858',width=max(1,round(size)))
    if shot.get('parcel') or (shot.get('delivery') and u<.23):
        d.line([pt(0,7),pt(0,20)],fill='#e8cfab',width=2)
        shape([(-10,18),(10,18),(10,29),(-10,29)],'#fff0c1')
        d.line([pt(-9,19),pt(0,25),pt(9,19)],fill='#94755c',width=1)

    if shot.get('delivery') and u>=.23:
        k=min(1,(u-.23)/.13); px=490-13*k;py=295+29*k*k
        d.rectangle((px-11,py-6,px+11,py+6),fill='#fff0c1',outline='#826658',width=2)
        d.line([(px-10,py-5),(px,py+1),(px+10,py-5)],fill='#94755c',width=2)
