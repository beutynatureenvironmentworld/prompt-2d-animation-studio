"""Turn a natural-language brief into scene parameters using local llama.cpp grammar decoding."""
import json,os,socket,subprocess,time,urllib.request
from pathlib import Path
FIELDS={'place':['workshop','garden','rooftop'],'prop':['parcel','ball','clock'],'move':['bounce','slide','drop'],'reaction':['duck','jump','reach'],'camera':['wide','close'],'tone':['warm','night']}
def plan(prompt):
    if not prompt.strip() or len(prompt)>1500: raise ValueError('Enter a short scene description, up to 1500 characters')
    runtime=Path(os.environ.get('MOTION_RUNTIME',Path(__file__).resolve().parents[1]/'free-motion/runtime'))
    server=next(runtime.rglob('llama-server'));model=runtime/'motion.gguf'
    grammar='root ::= '+' " " '.join(FIELDS)+'\n'+'\n'.join(k+' ::= '+' | '.join(json.dumps(v) for v in vs) for k,vs in FIELDS.items())
    instruction='Read the brief and select the closest scene. Output location object motion reaction camera lighting separated by spaces. '+str(FIELDS)+'.'
    chat='<|im_start|>system\n'+instruction+'<|im_end|>\n<|im_start|>user\n'+prompt+'<|im_end|>\n<|im_start|>assistant\n'
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    url=f'http://127.0.0.1:{port}'
    with open(os.devnull,'w') as null:
        proc=subprocess.Popen([str(server),'-m',str(model),'--host','127.0.0.1','--port',str(port),'-c','768','-t','2','-b','32','-ub','16','-np','1','--no-warmup'],stdout=null,stderr=null)
        try:
            for _ in range(100):
                if proc.poll() is not None:raise RuntimeError('Local inference worker exited')
                try:
                    with urllib.request.urlopen(url+'/health',timeout=2):break
                except OSError:time.sleep(.4)
            body=dict(prompt=chat,grammar=grammar,temperature=0,n_predict=30,seed=17)
            req=urllib.request.Request(url+'/completion',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=220) as response:words=json.load(response)['content'].strip().split()
        finally:
            proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
    if len(words)!=len(FIELDS) or any(v not in opts for v,opts in zip(words,FIELDS.values())):raise ValueError('Incomplete scene plan')
    return {'prompt':prompt,**dict(zip(FIELDS,words))}
if __name__=='__main__':
    import sys
    result=plan(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,indent=2,ensure_ascii=False))
