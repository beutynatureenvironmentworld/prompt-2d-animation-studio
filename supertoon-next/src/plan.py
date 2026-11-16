"""Safe prompt -> timed story scenes. Offline deterministic and optional validated AI JSON.

One prompt, original settings, characters and events. No generated Python/JS execution.
Extend ACTION_MAP/SETTINGS to teach motions/places. Sinhala & English supported.
"""
from __future__ import annotations
import json,re,argparse
from pathlib import Path

ACTIONS={
 'notice':['notice','look','see','wake','spot','බල','දැක','සිට'],
 'sprint':['sprint','run','dash','race','rush','chase','flee','දුව','දිව','හඹා','පැන දුව'],
 'jump':['jump','leap','hop','vault','පැන','උඩ පැන'],
 'knock':['knock','tap','bang','තට්ටු','දොරට'],
 'point':['point','show','අඟව','පෙන්ව'],
 'speak':['speak','talk','shout','yell','කතා','කෑ','බනි'],
 'slip':['slip','stumble','fall','trip','ලිස්','වැට','පැටල'],
 'panic':['scare','scared','shock','surprise','fright','panic','බය','පුදුම','තැති'],
 'laugh':['laugh','giggle','chuckle','හිනා','සිනා'],
 'recover':['recover','stand up','return','stand again','නැගිට','නැගී','යථා'],
 'dance':['dance','celebrate','නට','රඟ'],
 'wave':['wave','hello','අත වන'],
}
SETTINGS={
 'toilet':['toilet','bathroom','washroom','restroom','වැසිකි','ටොයිලට්','නාන කාමර'],
 'school':['school','classroom','teacher','පාසල','පන්ති'],
 'park':['park','garden','tree','field','garden','උද්‍යා','වත්ත','ගස','ගෙවත්ත'],
 'street':['road','street','traffic','city','පාර','නගර','වීථි'],
 'office':['office','work','desk','කාර්යාල','මේස'],
 'bedroom':['bed','room','sleep','නිදන','කාමර'],
 'kitchen':['kitchen','cook','food','කුස්සි','කෑම','උය'],
}
CHARACTERS={
 'cat':['cat','kitten','kitty','puss','පූස','බළල'],
 'robot':['robot','android','රොබෝ'],
 'girl':['girl','sister','දැරිය','ගැහැණු','ළමයින්'],
 'boy':['boy','kid','child','man','human','person','මිනිස','ළමයා','කොල්ල','පුතා'],
 'mascot':['mascot','stickman','logo','funny toon','කළු සුදු'],
}
ALLOWED=set(ACTIONS)
DEFAULT_DUR={'notice':.65,'sprint':1.7,'jump':.85,'knock':1.0,'point':.75,'speak':1.15,'slip':.95,'panic':.65,'laugh':.9,'recover':.8,'dance':1.3,'wave':.7}

def occurrences(s,variants):
    hits=[]
    for term in variants:
        if len(term)<3:continue
        for m in re.finditer(re.escape(term),s):hits.append(m.start())
    return sorted(hits)

def detect(s,labels,default):
    scored=[(occurences[0],k) for k,v in labels.items() if (occurences:=occurrences(s,v))]
    return sorted(scored)[0][1] if scored else default

def validate(plan):
    if not isinstance(plan,dict):raise ValueError('Plan must be a JSON object')
    if plan.get('version')!=1:raise ValueError('Unsupported plan schema')
    if plan.get('setting') not in SETTINGS:raise ValueError('Unsupported setting')
    if plan.get('character') not in CHARACTERS:raise ValueError('Unsupported character')
    ratio=plan.get('ratio')
    if ratio not in ('9:16','16:9','1:1'):raise ValueError('Invalid ratio')
    duration=float(plan.get('duration',0))
    if not 2<=duration<=18:raise ValueError('Duration out of range (2..18 seconds)')
    beats=plan.get('beats')
    if not isinstance(beats,list) or not 1<=len(beats)<=16:raise ValueError('Invalid beat count')
    last=0.0
    for b in beats:
        if b.get('action') not in ALLOWED:raise ValueError('Invalid action')
        start=float(b.get('start',-1));end=float(b.get('end',-1))
        if abs(start-last)>0.04 or end<=start or end>duration+.04:raise ValueError('Invalid timeline')
        last=end
    if abs(last-duration)>.04:raise ValueError('Timeline must fill duration')
    if 'props' in plan:
        from props import validate_props
        validate_props(plan['props'],duration)
    return plan

def compile_story(prompt,duration=9.0,ratio='9:16',style='super-test'):
    raw=prompt.strip()
    if not 3<=len(raw)<=900:raise ValueError('Prompt must contain 3-900 characters')
    s=raw.casefold()
    setting=detect(s,SETTINGS,'park')
    character=detect(s,CHARACTERS,'boy')
    hits=[]
    for act,words in ACTIONS.items():
        for index in occurrences(s,words):hits.append((index,act))
    # Collect action words in order rather than a fixed canned joke.
    hits.sort(key=lambda x:x[0])
    acts=[]
    for _,a in hits:
        if not acts or acts[-1]!=a:acts.append(a)
    if not acts:acts=['notice','sprint','panic','recover']
    else:
        if acts[0]!='notice':acts.insert(0,'notice')
        if acts[-1] not in ('recover','laugh','dance','wave'):acts.append('recover')
    acts=acts[:12]
    duration=min(18,max(2,float(duration)))
    total=sum(DEFAULT_DUR[a] for a in acts)
    t=0.;beats=[]
    for i,a in enumerate(acts):
        end=duration if i==len(acts)-1 else min(duration,sum(DEFAULT_DUR[x] for x in acts[:i+1])*duration/total)
        beats.append({'action':a,'start':round(t,3),'end':round(end,3)})
        t=beats[-1]['end']
    plan={'version':1,'prompt':raw,'planner':'offline-pattern-v2','setting':setting,'character':character,
          'ratio':ratio,'style':style,'duration':duration,'beats':beats,
          'fps':24,'limits':'built-in environment and action vocabulary; not arbitrary generated animation'}
    return validate(plan)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('prompt',nargs='?',default='ටොයිලට් එකට දුවගෙන ගිහින් දොරට තට්ටු කරලා බය වෙලා ලිස්සලා වැටෙන 2D විහිළුවක්');p.add_argument('--duration',type=float,default=9);p.add_argument('--ratio',choices=['9:16','16:9','1:1'],default='9:16');p.add_argument('--out',default='out/story.json');a=p.parse_args()
    result=compile_story(a.prompt,a.duration,a.ratio)
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('PLAN',result['setting'],result['character'],[x['action'] for x in result['beats']])