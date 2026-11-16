"""Optional local llama.cpp or OpenAI-compatible model as a *JSON planner only*.

Zero API-key mode: connect to a locally running llama.cpp/OpenAI-compatible
server at http://127.0.0.1:8080/v1/chat/completions.
Remote HTTPS (including Hugging Face routing) requires explicit URL, model,
optional secret from environment and consent to any provider's billing terms.
No downloaded model / arbitrary model-generated source code is executed.
"""
import argparse,json,os,pathlib,urllib.parse,urllib.request
from plan import ACTIONS,SETTINGS,CHARACTERS,validate

SYSTEM=(
 'You are a strict 2D-animation director. Reply only with JSON matching the schema: '
 '{"version":1,"prompt":"...","planner":"local-json-llm",'
 '"setting":"park|toilet|school|street|office|bedroom|kitchen",'
 '"character":"boy|girl|cat|robot|mascot",'
 '"ratio":"9:16|16:9|1:1","style":"super-test","duration":9,'
 '"beats":[{"action":"notice|sprint|jump|knock|point|speak|slip|panic|laugh|recover|dance|wave",'
 '"start":0,"end":1}, ...],"fps":24}. '
 'Use actions to tell a coherent joke. Timeline must be contiguous, no overlaps, and end at duration. '
 'Return at most 12 action beats. No executable code, no markdown. '
 'Cartoon character must move with distinct poses; most frames show a neutral mouth.'
)
def llm_plan(prompt,ratio='9:16',duration=9):
    raw_url=os.environ.get('STORY_LLM_BASE','http://127.0.0.1:8080').rstrip('/')
    parsed=urllib.parse.urlparse(raw_url)
    if parsed.scheme!='https' and not (parsed.scheme=='http' and parsed.hostname in ('127.0.0.1','localhost')):
        raise ValueError('Only HTTPS remote APIs and localhost LLMs allowed')
    endpoint=raw_url+'/v1/chat/completions' if not raw_url.endswith('/v1') else raw_url+'/chat/completions'
    model=os.environ.get('STORY_LLM_MODEL','local')
    key=os.environ.get('STORY_LLM_API_KEY','')
    headers={'Content-Type':'application/json'}
    if key:headers['Authorization']='Bearer '+key
    request={'model':model,'temperature':0,'max_tokens':850,'messages':[
        {'role':'system','content':SYSTEM},{'role':'user','content':f'{prompt[:800]}\nratio={ratio};duration={duration} seconds'}]}
    req=urllib.request.Request(endpoint,data=json.dumps(request).encode(),headers=headers,method='POST')
    with urllib.request.urlopen(req,timeout=80) as response:payload=json.load(response)
    answer=payload['choices'][0]['message']['content'].strip()
    if answer.startswith('```'):
        answer=answer.split('\n',1)[-1].rsplit('```',1)[0]
    p=json.loads(answer)
    p['planner']='opt-in-LLM-json-validated'
    p['prompt']=prompt
    p['ratio']=ratio;p['duration']=float(duration)
    p['fps']=24
    p['style']='super-test'
    p['version']=1
    return validate(p)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('prompt');p.add_argument('--ratio',default='9:16');p.add_argument('--duration',type=float,default=9);p.add_argument('--out',default='out/ai-plan.json');a=p.parse_args()
    out=llm_plan(a.prompt,a.ratio,a.duration)
    f=pathlib.Path(a.out);f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print('VALIDATED_LLM_JSON',f)