"""Funny Toon Ever: reuse permanent asset and V4/V6 CPU cartoon motion methods.

Offline director creates a bounded validated script; source can be replaced by
approved Qwen3 JSON with identical schema, but no inference is claimed here.
"""
import json
from pathlib import Path
BEATS=[
 ('sly_show',0.0,1.35,'sly'),
 ('reach_bite',1.35,2.55,'bite'),
 ('suspicious',2.55,3.30,'suspicious'),
 ('burning',3.30,4.40,'shock'),
 ('panic',4.40,5.40,'panic'),
 ('flare_up',5.40,7.72,'fire'),
 ('smoke',7.72,8.73,'exhausted'),
 ('recover',8.73,10.20,'tired'),
 ('sly_finish',10.20,11.40,'sly')]
SCHEMA='fte-spicy-v1'
def make_plan(prompt='The permanent Funny Toon Ever mascot takes a tiny chili bite then breathes a rocket of fire'):
 return {'schema':SCHEMA,'director':'offline constrained beat planner (NOT live Qwen inference)',
         'prompt':prompt,'character':'funny_toon_ever_permanent','duration':11.4,'fps':24,'size':[540,960],
         'beats':[{'action':a,'start':s,'end':e,'face':f} for a,s,e,f in BEATS],
         'constraints':{'one_pupil_per_eye':True,'smooth_shoulder_join':True,'leg_crossing':False,
                        'default_mischievous_grin':True,'chili_contact':'hand_to_mouth','no_model_download':True}}
def validate(data):
 if data.get('schema')!=SCHEMA or data.get('character')!='funny_toon_ever_permanent':raise ValueError('Incorrect motion plan identity')
 if data.get('fps')!=24 or data.get('size')!=[540,960]:raise ValueError('Unexpected render format')
 if not 4<=data.get('duration',0)<=15:raise ValueError('Unsafe/unsupported duration')
 valid={x[0] for x in BEATS};prev=0
 for b in data['beats']:
  if b['action'] not in valid or not 0<=b['start']<b['end']<=data['duration']+.01 or abs(b['start']-prev)>.001:raise ValueError('Unsupported beat or discontinuity')
  prev=b['end']
 if abs(prev-data['duration'])>.001:raise ValueError('Timeline not complete')
 return data
def beat_at(plan,t):
 for b in plan['beats']:
  if t<b['end']:
   return b,max(0,min(1,(t-b['start'])/(b['end']-b['start'])))
 return plan['beats'][-1],1
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--prompt',default='Chili pepper prank');p.add_argument('--out',default='output/plan.json');a=p.parse_args()
 data=validate(make_plan(a.prompt));f=Path(a.out);f.parent.mkdir(exist_ok=True,parents=True);f.write_text(json.dumps(data,indent=2));print('DIRECTOR_VALIDATED',f)
