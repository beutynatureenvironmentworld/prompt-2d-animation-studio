"""Prompt => strictly validated JSON beat sheet for black/white cutout animation.

Default mode is deterministic/offline/CPU and free. --llm activates OpenAI Responses
JSON-schema conversion only if user explicitly supplies OPENAI_API_KEY; charges may apply.
"""
import argparse,json,os,re,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ALIASES={
 'idle':['idle','wait','stand','look','notice','බල','සිට','ඉන්න'],
 'crouch':['crouch','prepare','ready','squat','duck','නැවෙ','පහත්','සූදානම්'],
 'run':['sprint','running','run','chase','dash','දුව','පස්සෙන්','හඹා'],
 'knock':['knock','tap','door','තට්ටු','දොර'],
 'jump':['jump','leap','hop','bounce','පැන','පනින','උඩ'],
 'shock':['scared','scare','shock','surprise','panic','fright','බය','පුදුම','තැති'],
 'slip':['slip','trip','fall','stumble','වැට','ලිස්','පැටල'],
 'recover':['recover','stand up','smile','laugh','relax','නැගිට','හිනා','සිනහ','සතුට'],
}
POSES={
 'idle':0,'crouch':1,'run':2,'knock':1,'jump':4,'shock':4,'slip':4,'recover':5
}
DURATIONS={'idle':0.65,'crouch':0.7,'run':2.15,'knock':1.35,'jump':1.25,'shock':.85,'slip':1.0,'recover':1.0}
EFFECTS={'idle':['blink'],'crouch':['squash'],'run':['speed_lines','dust','bounce'],
 'knock':['knock_sfx','arm_punch'],'jump':['stretch','airborne'],'shock':['screen_shake','camera_zoom'],
 'slip':['squash','screen_shake'],'recover':['gentle_bounce']}
ALLOWED=set(POSES)

def validate(obj):
    if not isinstance(obj,dict) or not isinstance(obj.get('actions'),list):raise ValueError('JSON must have actions array')
    a=obj['actions']
    if not 1<=len(a)<=20:raise ValueError('actions must have 1..20 items')
    total=0.0
    out=[]
    for item in a:
        key=item.get('action')
        if key not in ALLOWED:raise ValueError('Unsupported action '+str(key))
        duration=float(item.get('duration',DURATIONS[key]))
        if not 0.18<=duration<=5:raise ValueError('Action duration out of bounds')
        out.append({'action':key,'pose':POSES[key], 'start':round(total,3),
            'duration':round(duration,3),'effects':EFFECTS[key]})
        total+=duration
    if total>55:raise ValueError('Use at most 55 seconds per render')
    return {'schema':'funnytoon-cutout-v1','input_prompt':obj.get('input_prompt',''),
       'compiler':obj.get('compiler','rules'), 'fps':24,'actions':out,
       'duration':round(total,3),'estimated_frames':int(round(total*24)),
       'note':'A six-pose cutout animator with transforms: not full limb rigging or AI video diffusion.'}

def rules(prompt):
    prompt=prompt.strip().lower()
    if not 2<len(prompt)<800:raise ValueError('Prompt must be 3–799 characters')
    hits=[]
    for action,patterns in ALIASES.items():
        cand=[]
        for w in patterns:
            for m in re.finditer(re.escape(w),prompt,re.IGNORECASE):cand.append(m.start())
        if cand:hits.append((min(cand),action))
    hits.sort()
    actions=[{'action':name} for _,name in hits]
    if not actions:raise ValueError('No supported action found. Try run, knock, jump, shock, slip, recover.')
    # Avoid duplicate keywords within each action; order follows prompt terms.
    return validate({'actions':actions,'input_prompt':prompt,'compiler':'offline-keyword-rules'})

def llm(prompt):
    key=os.environ.get('OPENAI_API_KEY','').strip()
    if not key:raise RuntimeError('--llm requires OPENAI_API_KEY; never place your key in the prompt or GitHub source')
    schema={'type':'object','properties':{'actions':{'type':'array','minItems':1,'maxItems':15,
       'items':{'type':'object','properties':{'action':{'type':'string','enum':sorted(ALLOWED)},
                                            'duration':{'type':'number'}},
                'required':['action','duration'],'additionalProperties':False}}},
        'required':['actions'],'additionalProperties':False}
    payload={
      'model':os.environ.get('PROMPT_LLM_MODEL','gpt-4.1-mini'),
      'input':[{'role':'system','content':'Turn a user supplied cartoon action prompt into concise sequence JSON. Use only defined actions. Choose durations 0.2 to 5 seconds. No unsafe content. A character should not be smiling constantly.'},
               {'role':'user','content':prompt}],
      'text':{'format':{'type':'json_schema','name':'animation_timeline','strict':True,'schema':schema}},
      'max_output_tokens':800
    }
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload).encode(),
                headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=35) as response:data=json.load(response)
    text=[]
    for output in data.get('output',[]):
        for c in output.get('content',[]):
            if c.get('type')=='output_text':text.append(c.get('text',''))
    if not text:raise RuntimeError('No JSON output from LLM; no video rendered')
    parsed=json.loads(''.join(text))
    parsed['input_prompt']=prompt;parsed['compiler']='remote-llm-structured-json'
    return validate(parsed)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--prompt',default='The mascot crouches, runs quickly, jumps, gets shocked, slips, recovers.')
    p.add_argument('--llm',action='store_true',help='Calls paid remote API only with explicit flag and OPENAI_API_KEY')
    p.add_argument('--output',type=Path,default=ROOT/'output/timeline.json')
    a=p.parse_args()
    plan=llm(a.prompt) if a.llm else rules(a.prompt)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    print('PROMPT_JSON_COMPILED',plan['compiler'],len(plan['actions']),plan['duration'],str(a.output))
if __name__=='__main__':main()
