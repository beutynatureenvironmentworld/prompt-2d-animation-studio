"""Safe AI-authored SVG-like vector props and animation keyframes.

Only primitive data, never code execution, external image URLs, HTML, JS or scripts.
Allows arbitrary new drawn objects when a language model returns validated JSON.
"""
import math,re
from draw import rect,oval,line,path,fill,col
ALLOWED={'rect','ellipse','line','polygon','star','text'}
HEX=re.compile(r'^#[0-9a-fA-F]{6}$')

def validate_props(props,duration):
    if not isinstance(props,list) or len(props)>32:raise ValueError('props must be list of <=32 items')
    allowed={'kind','x','y','w','h','fill','stroke','points','text','motions','layer'}
    for p in props:
        if not isinstance(p,dict) or set(p)-allowed:raise ValueError('Unexpected prop field')
        if p.get('kind') not in ALLOWED:raise ValueError('Unsupported vector shape')
        if p.get('layer','back') not in ('back','front'):raise ValueError('Invalid prop layer')
        for k,lo,hi in [('x',-500,1300),('y',-300,720),('w',1,430),('h',1,430)]:
            if k not in p or not isinstance(p[k],(int,float)) or not lo<=float(p[k])<=hi:raise ValueError('Invalid '+k)
        for k in ('fill','stroke'):
            if not HEX.fullmatch(p.get(k,'#222222')):raise ValueError('Invalid color')
        points=p.get('points',[])
        if p['kind'] in ('line','polygon'):
            if not isinstance(points,list) or not 2<=len(points)<=20:raise ValueError('Invalid point count')
            if any(not isinstance(q,list) or len(q)!=2 or any(not isinstance(v,(int,float)) or abs(v)>430 for v in q) for q in points):raise ValueError('Invalid point')
        if 'text' in p and (not isinstance(p['text'],str) or len(p['text'])>40):raise ValueError('Text too long')
        motions=p.get('motions',[])
        if not isinstance(motions,list) or len(motions)>12:raise ValueError('Motions invalid')
        last=-1
        for m in motions:
            if not isinstance(m,dict) or set(m)-{'t','dx','dy','angle','scale'}:raise ValueError('Invalid motion fields')
            for k in ('t','dx','dy','angle','scale'):
                if k not in m or not isinstance(m[k],(int,float)):raise ValueError('Missing motion value')
            if not last<float(m['t'])<=duration+.001 or not -700<=m['dx']<=700 or not -400<=m['dy']<=400 or not -720<=m['angle']<=720 or not .15<=m['scale']<=3:raise ValueError('Invalid keyframe range')
            last=float(m['t'])
    return props

def lerp(a,b,s):return a+(b-a)*s

def motion_at(frames,t):
    default={'t':0.,'dx':0.,'dy':0.,'angle':0.,'scale':1.}
    if not frames:return default
    if t<=frames[0]['t']:return frames[0]
    if t>=frames[-1]['t']:return frames[-1]
    for a,b in zip(frames,frames[1:]):
        if a['t']<=t<b['t']:
            s=(t-a['t'])/(b['t']-a['t']);s=s*s*(3-2*s)
            return {k:lerp(a[k],b[k],s) for k in ('dx','dy','angle','scale')}
    return frames[-1]

def draw_props(c,props,t,layer='back'):
    for p in props:
        if p.get('layer','back')!=layer:continue
        m=motion_at(p.get('motions',[]),t)
        c.save();c.translate(p['x']+m['dx'],p['y']+m['dy']);c.rotate(math.radians(m['angle']));c.scale(m['scale'],m['scale'])
        w=p['w'];h=p['h'];colour=p.get('fill','#f7ebc7');outline=p.get('stroke','#222222');kind=p['kind']
        if kind=='rect':rect(c,-w/2,-h/2,w,h,colour,outline,3,6)
        elif kind=='ellipse':oval(c,0,0,w/2,h/2,colour,outline,3)
        elif kind in ('line','polygon'):
            pts=[(float(x),float(y)) for x,y in p['points']]
            if kind=='line':line(c,pts,outline,3)
            else:path(c,pts,closed=True);fill(c,colour,outline,3)
        elif kind=='star':
            pts=[]
            for i in range(10):
                theta=-math.pi/2+i*math.pi/5;size=(1 if i%2==0 else .42)
                pts.append((math.cos(theta)*w/2*size,math.sin(theta)*h/2*size))
            path(c,pts,closed=True);fill(c,colour,outline,3)
        elif kind=='text':
            col(c,outline);c.select_font_face('Sans');c.set_font_size(min(30,h));c.move_to(-w/2,0);c.show_text(p.get('text','')[:40])
        c.restore()