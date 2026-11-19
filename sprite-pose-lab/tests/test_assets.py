from pathlib import Path
from PIL import Image
from sprite_factory import POSES,generate
from render import validate
import json

def test_generator(tmp_path):
    generate(tmp_path)
    for who in ('pip','luma'):
        for pose in POSES:
            im=Image.open(tmp_path/'characters'/who/(pose+'.png'))
            assert im.mode=='RGBA'
            assert im.getbbox()
    assert Image.open(tmp_path/'props'/'ball.png').mode=='RGBA'

def test_timeline():
    root=Path(__file__).resolve().parents[1]
    t=json.loads((root/'config'/'demo_story.json').read_text())
    assert validate(t,root/'assets')
