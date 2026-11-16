"""Single-prompt English/Sinhala storyboard planning, bounded and deterministic.

The editable declarative JSON is the safe boundary for free local/remote LLMs.
Never execute model-written code, shell commands, HTML, or source imports.
"""
from __future__ import annotations
import re,json,argparse
from pathlib import Path

SETTINGS={
 'toilet':['toilet','bathroom','restroom','washroom','ටොයිලට්','වැසිකි','නාන කාමර'],
 'park':['park','garden','playground','ගෙවත්ත','උද්‍යා','වත්ත'],
 'beach':['beach','ocean','sea','මුහුද','වෙරළ'],
 'school':['school','classroom','පාසල','පන්ති'],
 'kitchen':['kitchen','cook','කුස්සි','උයන'],
 'bedroom':['bedroom','sleep','bed','නිදන'],
 'street':['street','road','city','පාර','නගර'],
 'forest':['forest','jungle','වනාන්තර','කැලෑ'],
 'space':['space','moon','planet','අභ්‍යවකාශ','සඳ'],
 'office':['office','desk','කාර්යාල'],
 'rooftop':['roof','rooftop','වහල'],
}
CHARACTERS={
 'cat':['cat','kitten','kitty','පූස','බළල'],
 'mascot':['mascot','stickman','logo','black and white','කළු සුදු'],
 'robot':['robot','android','රොබෝ'],
 'girl':['girl','sister','දැරිය','කෙල්ල'],
 'boy':['boy','kid','child','man','human','person','ළමය','කොල්ල','පුතා','මිනිස'],
}
ACTIONS={
 'notice':['notice','spot','see','look','බල','දකින','දැක'],
 'anticipate':['prepare','crouch','ready','පහත්','සූදානම්'],
 'sprint':['sprint','dash','run','rush','race','chase','දුව','දිව','හඹා'],
 'jump':['jump','hop','leap','vault','පැන','උඩ පැන'],
 'knock':['knock','bang door','door tap','තට්ටු'],
 'point':['point','පෙන්ව','අඟව'],
 'talk':['talk','shout','say','speak','කතා','කෑගහ'],
 'wave':['wave','hello','අත වන'],
 'dodge':['dodge','duck','avoid','මඟහර','බේරෙ'],
 'slip':['slip','skid','trip','ලිස්','පැටල'],
 'fall':['fall','bonk','crash','වැට','බිම'],
 'panic':['panic','scared','fright','shock','surprise','බය','පුදුම','තැති'],
 'laugh':['laugh','giggle','හාහ','හිනා','සිනා'],
 'dance':['dance','groove','නට','රඟ'],
 'recover':['recover','stand up','get up','return','නැගිට','නැගී','යථා'],
}
PROPS={
 'banana':['banana','peel','කෙසෙල්'],
 'ball':['ball','බෝල'],
 'cookie':['cookie','biscuit','බිස්කට්','කුකී'],
 'phone':['phone','mobile','දුරකථන'],
 'skateboard':['skateboard','ස්කේට්'],
 'paper':['paper','toilet roll','tissue','කඩදාසි','ටොයිලට් රෝල්'],
 'cup':['cup','coffee','කෝප්ප'],
}
WEIGHTS={'notice':.6,'anticipate':.5,'sprint':1.8,'jump':1.,'knock':1.1,
 'point':.7,'talk':1.0,'wave':.7,'dodge':.65,'slip':.95,'fall':.9,
 'panic':.75,'laugh':.85,'dance':1.4,'recover':.85}
ALLOWED=set(ACTIONS)

def choose(text,mapping,default):
    matches=[]
    for name,variants in mapping.items():
        for word in variants:
            pos=text.find(word)
            if pos!=-1:matches.append((pos,name))
    return min(matches)[1] if matches else default

def compile_story(prompt:str,duration:float=9,ratio:str='9:16',style='super-test-color'):
    if not isinstance(prompt,str) or not 4<=len(prompt.strip())<=700:raise ValueError('Prompt length 4–700 required')
    t=prompt.casefold()
    setting=choose(t,SETTINGS,'park')
    character=choose(t,CHARACTERS,'boy')
    cast=[name for name in CHARACTERS if any(word in t for word in CHARACTERS[name])]
    # Preserve first mentioned character as the leading actor.
    cast=sorted(cast,key=lambda name:min(t.find(w) for w in CHARACTERS[name] if w in t))[:2] or [character]
    character=cast[0]
    prop=choose(t,PROPS,'none')
    hits=[]
    for action,aliases in ACTIONS.items():
        for alias in aliases:
            for m in re.finditer(re.escape(alias),t):hits.append((m.start(),action))
    hits.sort(key=lambda x:x[0])
    action_sequence=[]
    for _,a in hits:
        if not action_sequence or action_sequence[-1]!=a:action_sequence.append(a)
    if not action_sequence:action_sequence=['notice','anticipate','sprint','panic','recover']
    else:
        if action_sequence[0]!='notice':action_sequence.insert(0,'notice')
        if action_sequence[-1] not in ('recover','laugh','dance','wave'):action_sequence.append('recover')
    action_sequence=action_sequence[:13]
    duration=max(3.,min(18.,float(duration)))
    base=sum(WEIGHTS[a] for a in action_sequence)
    time=0.0;beats=[]
    for i,a in enumerate(action_sequence):
        end=duration if i==len(action_sequence)-1 else round(time+duration*WEIGHTS[a]/base,3)
        beats.append({'action':a,'start':round(time,3),'end':end,'strength':1.0})
        time=end
    p={'version':2,'prompt':prompt,'planner':'offline-action-grammar-v3',
       'setting':setting,'character':character,'cast':cast,'prop':prop,'style':style,'ratio':ratio,
       'duration':duration,'fps':24,'beats':beats,
       'note':'Built-in character and environment templates; new arbitrary concepts need authored assets/animation.'}
    return validate(p)

def validate(p):
    if not isinstance(p,dict) or p.get('version')!=2:raise ValueError('Not a v2 plan')
    if p.get('setting') not in SETTINGS or p.get('character') not in CHARACTERS:
        raise ValueError('Unknown setting or character')
    cast=p.get('cast',[p['character']])
    if not isinstance(cast,list) or not 1<=len(cast)<=2 or any(x not in CHARACTERS for x in cast):raise ValueError('Invalid cast')
    if p.get('prop') not in [*PROPS,'none']:raise ValueError('Unsupported prop')
    if p.get('ratio') not in ('9:16','16:9','1:1'):raise ValueError('Invalid aspect ratio')
    if p.get('style') not in ('super-test-color','ink-monochrome'):raise ValueError('Unknown visual style')
    if not 3<=float(p.get('duration',0))<=18:raise ValueError('Duration 3–18 seconds')
    if not isinstance(p.get('beats'),list) or not 1<=len(p['beats'])<=16:raise ValueError('Bad beats')
    prev=0
    for b in p['beats']:
        if b.get('action') not in ALLOWED:raise ValueError('Unknown action: '+str(b.get('action')))
        if abs(float(b.get('start',-2))-prev)>.05:raise ValueError('Gaps/overlaps in beats')
        if not float(b.get('end',-1))>prev+.045:raise ValueError('Non-positive action duration')
        prev=float(b['end'])
    if abs(prev-float(p['duration']))>.05:raise ValueError('Beats must fill duration')
    return p

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('prompt',nargs='?',default='Funny boy rushes to the toilet, knocks, panics, slips, recovers')
    a.add_argument('--duration',type=float,default=9);a.add_argument('--ratio',choices=['9:16','16:9','1:1'],default='9:16')
    a.add_argument('--style',choices=['super-test-color','ink-monochrome'],default='super-test-color')
    a.add_argument('--out',default='output/story.json');x=a.parse_args()
    plan=compile_story(x.prompt,x.duration,x.ratio,x.style);Path(x.out).parent.mkdir(parents=True,exist_ok=True)
    Path(x.out).write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    print('PLAN_OK',plan['setting'],plan['character'],plan['prop'],[b['action'] for b in plan['beats']])
