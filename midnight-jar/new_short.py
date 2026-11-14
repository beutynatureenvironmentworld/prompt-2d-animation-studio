"""Author a new episode in a fresh folder using an already configured OpenCode model."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import json
p=argparse.ArgumentParser()
p.add_argument('story',help='Your story in Sinhala or English')
p.add_argument('destination',type=Path)
p.add_argument('--model',required=True,help='A model ID listed by opencode models')
p.add_argument('--width',choices=[360,540,720,1080],type=int,default=1080)
a=p.parse_args()
if not a.story.strip(): p.error('Give a story to animate.')
root=Path(__file__).resolve().parent
cli=shutil.which('opencode') or str(root/'node_modules/.bin/opencode')
if not Path(cli).is_file(): p.error('Install opencode-ai and configure a model first.')
dest=a.destination.resolve();dest.mkdir(parents=True,exist_ok=False)
for name in ['DIRECTOR.md','art.cjs','story.json','scene.cjs','render.py','index.jsx','build_blender.py','package.json']:
    shutil.copy2(root/name,dest/name)
original_art=(dest/'art.cjs').read_bytes()
prompt='Read DIRECTOR.md. Implement this original story in art.cjs and story.json. Use new visible staging for the prompt. Keep the renderer interface unchanged. Story:\n'+a.story
subprocess.run([cli,'run','--model',a.model,prompt],cwd=dest,check=True)
if (dest/'art.cjs').read_bytes()==original_art: raise SystemExit('No new artwork or motion code was produced. Inspect the episode before rendering.')
story=json.loads((dest/'story.json').read_text())
if not story.get('shots'): raise SystemExit('Generated scene has no shots.')
subprocess.run([sys.executable,'render.py','story.json','short.mp4','--width',str(a.width)],cwd=dest,check=True)
