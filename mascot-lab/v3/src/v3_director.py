"""Reusable safe creative director. AI reasoning outputs JSON, not runnable code.

Current offline template targets the user-provided 'locked restroom' physical comedy;
`--plan` supports AI-authored plans using the same validated actions. This code
never claims to have run Qwen unless the caller provides a verified LLM plan.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import json,re

ACTIONS=('sneak','dash','brake','knock','shock','jump','slip','fall','recover','reveal','celebrate')
FACE_STATES=('sly','focus','effort','shock','worried','grin','neutral')
TEMPLATE=[
    ('sneak',0.00,.90,'sly'),
    ('dash',.90,2.70,'sly'),
    ('brake',2.70,3.40,'focus'),
    ('knock',3.40,5.28,'effort'),
    ('shock',5.28,5.96,'shock'),
    ('jump',5.96,6.68,'shock'),
    ('slip',6.68,7.45,'worried'),
    ('fall',7.45,8.20,'worried'),
    ('recover',8.20,9.26,'focus'),
    ('reveal',9.26,10.25,'sly'),
    ('celebrate',10.25,11.50,'grin')]


def offline_plan(prompt='Mascot sneaks toward the locked restroom, knocks, falls and discovers PULL'):
    return {'schema':'fte-motion-v3','title':'THE LOCKED DOOR','input_prompt':prompt[:500],
       'director':'offline deterministic action grammar; not an LLM inference result',
       'character':'funny_toon_ever_permanent','duration':11.5,'fps':24,
       'width':540,'height':960,'location':'bathroom_hallway',
       'beats':[{'action':a,'start':s,'end':e,'expression':face} for a,s,e,face in TEMPLATE],
       'objects':{'door':{'handle_x':406,'handle_y':606,'frame_left':371},
                  'floor':{'y':833}},
       'sound_cues':['footsteps','three_knocks','panic','slip','comedy_ding']}


def validate(plan):
    if not isinstance(plan,dict) or plan.get('schema')!='fte-motion-v3':raise ValueError('Plan schema must be fte-motion-v3')
    if plan.get('character')!='funny_toon_ever_permanent':raise ValueError('Only canonical mascot character supported')
    if not 4<=float(plan.get('duration',0))<=18:raise ValueError('Duration outside 4..18 seconds')
    if not 12<=int(plan.get('fps',0))<=30:raise ValueError('Invalid fps')
    if len(plan.get('beats',[]))<3 or len(plan['beats'])>32:raise ValueError('3..32 beats required')
    prev=0
    for i,b in enumerate(plan['beats']):
        if b.get('action') not in ACTIONS or b.get('expression') not in FACE_STATES:raise ValueError(f'Beat {i}: invalid action/expression')
        s,e=float(b['start']),float(b['end'])
        if abs(s-prev)>.021 or e<=s or e>plan['duration']+.02:raise ValueError(f'Beat {i}: invalid timeline or gap')
        prev=e
    if abs(prev-plan['duration'])>.025:raise ValueError('Timeline must cover duration')
    door=plan.get('objects',{}).get('door',{})
    if not (355<=door.get('handle_x',0)<=515 and 450<=door.get('handle_y',0)<=750):raise ValueError('Handle off the authored door')
    if plan.get('width')!=540 or plan.get('height')!=960:raise ValueError('This calibrated rig requires 540x960 output')
    return plan


def load_or_compile(prompt='',path=None):
    if path:
        result=json.loads(Path(path).read_text(encoding='utf-8'))
    else:result=offline_plan(prompt or 'A sneaky mascot runs toward the toilet door, knocks, slips, and recovers')
    return validate(result)


def active_beat(plan,t):
    for b in plan['beats']:
        if t<float(b['end']):return b,max(0,min(1,(t-b['start'])/(b['end']-b['start'])))
    return plan['beats'][-1],1.

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--prompt',default='A sneaky mascot knocks on a bathroom door and slips');p.add_argument('--output',default='output/story_motion.json');a=p.parse_args()
    plan=offline_plan(a.prompt);validate(plan);path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n');print('MOTION_JSON_VALIDATED',path)