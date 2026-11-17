"""Validated story manifest for a selective GPU/CPU animation pipeline.

No untrusted prompts are executed as shell code. GPU results are never silently
substituted for CPU shots without explicit manifest declarations.
"""
from __future__ import annotations
import json,hashlib,re
from pathlib import Path

SCHEMA='fte.hybrid.story.v1'
ID=re.compile(r'^scene_[0-9]{2}$')
KINDS={'cpu','gpu_candidate'}


def read_story(path):
    p=Path(path); data=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or data.get('schema')!=SCHEMA:raise ValueError('Story schema mismatch')
    if data.get('project')!='funny-toon-ever':raise ValueError('Wrong character project')
    if data.get('character_ref')!='mascot-lab/config/permanent_mascot.webp':raise ValueError('Permanent character reference changed')
    if data.get('output_fps') not in (24,30):raise ValueError('Unsupported output FPS')
    clips=data.get('clips')
    if not isinstance(clips,list) or not 1<=len(clips)<=15:raise ValueError('Expected 1–15 clips')
    names=set()
    for c in clips:
        if not isinstance(c,dict) or not ID.fullmatch(str(c.get('id',''))):raise ValueError('Invalid scene identifier')
        if c['id'] in names:raise ValueError('Duplicate scene identifier')
        names.add(c['id'])
        if c.get('kind') not in KINDS:raise ValueError('Unsupported scene engine')
        if not isinstance(c.get('duration_s'),(int,float)) or not 0.5<=c['duration_s']<=5:raise ValueError('Shot duration out of range')
        if not isinstance(c.get('prompt'),str) or not 16<=len(c['prompt'])<=1800:raise ValueError('Prompt length invalid')
    if sum(x['duration_s'] for x in clips)>60:raise ValueError('Storyboard duration > 60 seconds')
    return data


def select_gpu(data,max_gpu_shots=2,max_gpu_seconds=10):
    if max_gpu_shots not in (0,1,2) or not 0<=max_gpu_seconds<=10:raise ValueError('Unsafe GPU cap')
    shots=[];used=0.0
    for c in data['clips']:
        if c['kind']!='gpu_candidate':continue
        if len(shots)>=max_gpu_shots or used+c['duration_s']>max_gpu_seconds:continue
        shots.append({k:c[k] for k in ('id','prompt','duration_s')});used+=c['duration_s']
    return shots


def make_batch(story_file,out,max_gpu_shots=2):
    data=read_story(story_file); selected=select_gpu(data,max_gpu_shots)
    manifest={'schema':'fte.gpu.jobs.v1','project':data['project'],
       'character_ref':data['character_ref'],'model_mode':'wan21-t2v-1.3b',
       'caption':'Generated clips require human identity review before publishing',
       'shots':selected,'story_sha256':hashlib.sha256(Path(story_file).read_bytes()).hexdigest()}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


def validate_batch(path):
    a=json.loads(Path(path).read_text())
    if a.get('schema')!='fte.gpu.jobs.v1' or a.get('character_ref')!='mascot-lab/config/permanent_mascot.webp':raise ValueError('Invalid batch')
    shots=a.get('shots')
    if not isinstance(shots,list) or len(shots)>2:raise ValueError('GPU batch over cap')
    used=set()
    for s in shots:
        if not ID.fullmatch(str(s.get('id',''))) or s['id'] in used:raise ValueError('Bad shot id')
        used.add(s['id'])
        if not isinstance(s.get('prompt'),str) or not 16<=len(s['prompt'])<=1800:raise ValueError('Bad shot prompt')
        if not isinstance(s.get('duration_s'),(int,float)) or not .5<=s['duration_s']<=5:raise ValueError('Bad shot duration')
    return a

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('story');p.add_argument('--out',default='output/gpu_jobs.json');p.add_argument('--gpu-shots',type=int,default=1);a=p.parse_args()
 print(json.dumps(make_batch(a.story,a.out,a.gpu_shots),indent=2))
