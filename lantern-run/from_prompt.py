"""Author a fresh episode from prose with a configured OpenCode model."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('prompt');p.add_argument('project',type=Path)
p.add_argument('--model',required=True,help='A configured OpenCode provider/model')
a=p.parse_args()
if not a.prompt.strip():p.error('Provide a story.')
cli=shutil.which('opencode') or root.parent/'midnight-jar/node_modules/.bin/opencode'
if not Path(cli).is_file():p.error('OpenCode executable is missing')
env=os.environ.copy()
node=root.parent/'midnight-jar/runtime/node-v22.16.0-linux-x64/bin'
if node.is_dir():env['PATH']=str(node)+os.pathsep+env['PATH']
dst=a.project.resolve();dst.mkdir(parents=True,exist_ok=False)
for f in ('story.json','film.py','render.py','scene.cjs','art.cjs'):
    shutil.copy2(root/f,dst/f)
request="""Author a new episode for this prompt. Read all project files. Edit story.json
and art.cjs to draw the new story with recognizable full-body proportions, connected
limbs, ground contacts, expressive face and new props. Keep frame(t,story,amp)
and the film.py audio interface compatible. Keep dialogue within the duration.
Adjust the story timing and render code if the action requires a different setting.
Set story.json prompt to the exact supplied request. Story: """+a.prompt
subprocess.run([str(cli),'run','--model',a.model,request],cwd=dst,env=env,check=True)
if json.loads((dst/'story.json').read_text())['prompt'].strip()!=a.prompt.strip():raise ValueError('Episode author did not record this prompt')
if (dst/'art.cjs').read_bytes()==(root/'art.cjs').read_bytes():raise ValueError('No new staging generated')
subprocess.run([sys.executable,'film.py','story.json','episode.mp4'],cwd=dst,check=True)
