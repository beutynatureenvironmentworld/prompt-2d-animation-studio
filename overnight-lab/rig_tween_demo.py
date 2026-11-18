"""Pure CPU hierarchical rig with bone pivots and cubic ease, real encoded MP4."""
import json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
W,H,FPS,N=360,640,20,80
out=Path('overnight-lab/out/rig')
out.mkdir(parents=True,exist_ok=True)
def ease(x):
    x=max(0,min(1,x))
    return x*x*(3-2*x)
def limb(draw,root,angle,length,width,color):
    end=(root[0]+length*math.sin(angle),root[1]+length*math.cos(angle))
    draw.line([root,end],fill=color,width=width,joint='curve')
    draw.ellipse((end[0]-width/2,end[1]-width/2,end[0]+width/2,end[1]+width/2),fill=color)
    return end
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
 '-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0',
 '-f','lavfi','-i','sine=frequency=520:sample_rate=44100:duration=4',
 '-shortest','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',
 '-c:a','aac',str(out/'FTE_Hierarchical_Rig_Tween.mp4')],stdin=subprocess.PIPE)
for f in range(N):
    t=f/FPS
    img=Image.new('RGB',(W,H),'#fff6e8')
    d=ImageDraw.Draw(img)
    d.rectangle((0,530,W,H),fill='#f5d6af')
    for idx,x in enumerate((95,267)):
        is_girl=idx==0
        pulse=math.sin(t*5+idx)*3
        d.ellipse((x-49,258+pulse,x+49,357+pulse),fill='black')
        d.ellipse((x-44,263+pulse,x+44,351+pulse),fill='white')
        for ox in (-16,16):
            d.ellipse((x+ox-5,294+pulse,x+ox+5,307+pulse),fill='black')
        d.arc((x-20,312+pulse,x+20,337+pulse),start=10,end=175,fill='black',width=4)
        d.rounded_rectangle((x-36,360,x+36,462),radius=13,fill='#ff6c95' if is_girl else '#85baff',outline='black',width=4)
        for leg in (-18,18):
            limb(d,(x+leg,460),.13*math.sin(t*4+idx+leg),60,10,'black')
        if is_girl:
            for ox in (-50,50):d.ellipse((x+ox-16,270,x+ox+16,304),fill='white',outline='black',width=4)
        # Shoulder -> elbow -> wrist, independently articulated local rotations
        side=1 if is_girl else -1
        shoulder=(x+side*30,385)
        swing=ease((t-.5)/1.0) if is_girl else ease((t-1.4)/.9)
        elbow=limb(d,shoulder,side*(-1.3+.45*swing),43,11,'black')
        wrist=limb(d,elbow,side*(-.85+.7*swing),38,9,'black')
    # Carton center moves through a separately eased translation path
    cx=185+12*ease((t-1.1)/.8)
    cy=398-20*ease((t-1.1)/.8)
    d.rounded_rectangle((cx-27,cy-38,cx+27,cy+38),radius=5,fill='white',outline='black',width=4)
    d.text((cx-15,cy-8),'MILK',fill='black')
    if t>2.1:
        amount=ease((t-2.1)/.5)
        d.line([(cx-27,cy-22),(cx-27-70*amount,cy-54)],fill='#a4e5fa',width=max(1,int(12*amount)))
    d.text((75,55),'HIERARCHICAL RIG LAB',fill='black')
    d.text((70,600),'Cubic easing + bone pivots',fill='black')
    p.stdin.write(img.tobytes())
p.stdin.close()
assert p.wait(timeout=90)==0
data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/'FTE_Hierarchical_Rig_Tween.mp4')],text=True))
v=next(x for x in data['streams'] if x['codec_type']=='video')
assert (v['width'],v['height'])==(W,H)
assert any(x['codec_type']=='audio' for x in data['streams'])
assert float(data['format']['duration'])>=3.9
(out/'QA.json').write_text(json.dumps({'method':'hierarchical joint transforms + smoothstep cubic interpolation','video':'FTE_Hierarchical_Rig_Tween.mp4','fps':FPS,'resolution':[W,H],'duration':data['format']['duration'],'verified':True},indent=2)+'\n')
print('RIG_MP4_PASS',data['format']['duration'])
