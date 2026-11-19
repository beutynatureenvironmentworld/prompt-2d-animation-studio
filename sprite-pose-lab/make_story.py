"""Generate a reproducible 12 FPS editable timeline for an original slapstick cartoon test."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def actor(who,pose,x,y,x2=None,y2=None,scale=.48,z=2,**kw):
    return {'sprite':f'characters/{who}/{pose}.png','start':[x,y],'end':[x if x2 is None else x2,y if y2 is None else y2],'scale':scale,'z':z,**kw}

def prop(which,x,y,x2=None,y2=None,scale=.22,z=3,**kw):
    return {'sprite':f'props/{which}.png','start':[x,y],'end':[x if x2 is None else x2,y if y2 is None else y2],'scale':scale,'z':z,**kw}

def shot(n,*layers,**kwargs):return {'frames':n,'layers':list(layers),**kwargs}

STORY={'title':'Pip, Luma and the runaway ball - original slapstick cartoon','fps':12,'shots':[
    shot(12,actor('pip','idle',220,1060),actor('luma','grin',520,1060),prop('ball',420,1120,scale=.29,z=4)),
    shot(10,actor('pip','talk',220,1060),actor('luma','run',530,1060,425,1060),prop('ball',420,1120,scale=.29,z=4),sfx='whoosh'),
    shot(5,actor('pip','point',220,1060),actor('luma','kick',425,1060),prop('ball',420,1120,300,1000,scale=.29,z=4),sfx='boing'),
    shot(8,actor('pip','shock',220,1060),actor('luma','grin',425,1060),prop('ball',300,1000,205,900,scale=.29,z=4),zoom=1,zoom_end=1.12),
    shot(2,actor('pip','fall',220,1060,205,1050,scale=.52),actor('luma','shock',425,1060),prop('burst',225,870,scale=.75,z=5),impact=True,shake=17,zoom=1.15,sfx='pop'),
    shot(12,actor('pip','shock',220,1060),actor('luma','point',430,1060),prop('cup',285,800,330,710,scale=.32,z=4,rotation=15,rotation_end=-40),prop('splash',270,780,330,690,scale=.60,z=5,opacity=.7,opacity_end=.1),sfx='splash'),
    shot(12,actor('pip','shock',220,1060),actor('luma','grin',430,1060),prop('cup',330,710,490,1050,scale=.28,z=1,rotation=-45,rotation_end=-160),zoom=1.08),
    shot(13,actor('pip','blink',225,1060),actor('luma','celebrate',430,1060),sfx='laugh'),
    shot(12,actor('pip','grin',225,1060),actor('luma','grin',430,1060),zoom=1,zoom_end=1.07)
]}

def generate(path=HERE/'config'/'demo_story.json'):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(STORY,indent=2),encoding='utf8')
    print('Saved editable storyboard:',path)

if __name__=='__main__':generate()
