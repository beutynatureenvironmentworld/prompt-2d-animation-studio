"""Optional prompt -> declarative animation JSON using a locally running llama.cpp
or explicitly configured HTTPS OpenAI-compatible chat endpoint.

No prompt-generated Python/JS is ever executed. Invalid model response fails
closed or falls back to the deterministic offline planner if opted in.
"""
import argparse,json,os,pathlib,re,urllib.request,urllib.parse,sys
from story import compile_story,validate,ALLOWED,SETTINGS,CHARACTERS,PROPS

SYSTEM=(
 'You are the director for a funny 2D animation. Return ONLY a JSON object, '
 'with fields version=2, prompt, planner="opt-in-LLM-json-v2", '
 'setting among '+','.join(SETTINGS)+', character among '+','.join(CHARACTERS)+', '
 'prop among none,'+','.join(PROPS)+', cast a 1-2 element character list, '
 'ratio=9:16, style=super-test-color or ink-monochrome, fps=24, duration seconds, '
 'beats each with {action,start,end,strength}. '
 'Actions restricted to '+','.join(sorted(ALLOWED))+'. '
 'Timeline starts at 0 and fills duration without gaps. Choose expressive physical comedy '
 'and avoid smiling throughout the video. No source code, no markdown.'
)

def plan_llm(prompt,duration=9,ratio='9:16',style='super-test-color'):
    url=os.getenv('STORY_LLM_BASE','http://127.0.0.1:8080').rstrip('/')
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!='https' and not (parsed.scheme=='http' and parsed.hostname in ('localhost','127.0.0.1')):
        raise ValueError('Only HTTPS providers or local llama.cpp are allowed')
    if parsed.username or parsed.password or parsed.fragment:raise ValueError('Embedded URL credentials are forbidden')
    endpoint=url+'/chat/completions' if url.endswith('/v1') else url+'/v1/chat/completions'
    key=os.environ.get('STORY_LLM_API_KEY','')
    request={'model':os.environ.get('STORY_LLM_MODEL','local'),
             'temperature':0.05,'max_tokens':1050,
             'messages':[{'role':'system','content':SYSTEM},
                         {'role':'user','content':f'Prompt: {prompt[:650]}. Duration: {duration}s. Ratio: {ratio}; style: {style}. Return full JSON.'}]}
    headers={'Content-Type':'application/json'}
    if key:headers['Authorization']='Bearer '+key
    req=urllib.request.Request(endpoint,data=json.dumps(request).encode(),method='POST',headers=headers)
    with urllib.request.urlopen(req,timeout=80) as response:
        payload=json.load(response)
    text=payload['choices'][0]['message']['content'].strip()
    if text.startswith('```'):
        text=text.split('\n',1)[-1].rsplit('```',1)[0]
    obj=json.loads(text)
    obj['version']=2;obj['prompt']=prompt;obj['planner']='verified-LLM-json-v2';obj['ratio']=ratio
    obj['style']=style;obj['duration']=float(duration);obj['fps']=24
    return validate(obj)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('prompt');ap.add_argument('--duration',type=float,default=9)
    ap.add_argument('--ratio',default='9:16');ap.add_argument('--style',default='super-test-color')
    ap.add_argument('--fallback-offline',action='store_true');ap.add_argument('--output',default='output/ai-plan.json')
    a=ap.parse_args()
    try:p=plan_llm(a.prompt,a.duration,a.ratio,a.style)
    except (ValueError,KeyError,TimeoutError,urllib.error.URLError) as exc:
        if not a.fallback_offline:raise
        print('LLM_PLANNING_FAILED_USE_OFFLINE_FALLBACK',str(exc)[:150])
        p=compile_story(a.prompt,a.duration,a.ratio,a.style)
    pathlib.Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    pathlib.Path(a.output).write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
    print('VALIDATED',p['planner'],p['setting'],[b['action'] for b in p['beats']])
