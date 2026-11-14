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
for f in ('story.json','episode.py','room.py','staging.py'):
    shutil.copy2(root/f,dst/f)
request="""Create a new episode based on the user's prompt. Read story.json, staging.py,
room.py and episode.py. Rewrite story.json and staging.py for the requested external
objects, physical interactions and environment. Preserve the room.py face rig and
episode.py rendering interface. Keep shot keys compatible, transitions continuous,
dialogue short enough to fit each shot, English voices, no third-party images or
network calls in generated drawing code. Use as many shots as the requested length
requires. Put the user's original prompt in story.json under prompt.
Story: """+a.prompt
subprocess.run([str(cli),'run','--model',a.model,request],cwd=dst,env=env,check=True)
if json.loads((dst/'story.json').read_text())['prompt'].strip()!=a.prompt.strip():raise ValueError('Episode author did not record this prompt')
if (dst/'staging.py').read_bytes()==(root/'staging.py').read_bytes():raise ValueError('No new staging generated')
subprocess.run([sys.executable,'episode.py','story.json','build'],cwd=dst,check=True)
