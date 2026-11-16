import tempfile, unittest, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageChops
from asset_pack import load_asset_pack, AssetError
from shortgpt_supertest import draw_actor, procedural_background

class AssetPackTests(unittest.TestCase):
    def test_style_memory_and_character_colors(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'settings.json').write_text(json.dumps({'character':{'shirt':'#FF0033'},'layout':{'door_x':.78,'start_x':.14}}))
            (root/'style.md').write_text('sharp ink style and golden lighting')
            (root/'memory.md').write_text('Locked door is on the right')
            pack=load_asset_pack(root)
            self.assertEqual(pack.character['shirt'],'#FF0033')
            self.assertEqual(pack.layout['door_x'],.78)
            self.assertIn('golden lighting',pack.notes)
            self.assertIn('Locked door',pack.notes)
            im=procedural_background('toilet')
            colored=draw_actor(im,'notice',.1,True,pack.character,pack.layout)
            original=draw_actor(im,'notice',.1,True)
            self.assertIsNotNone(ImageChops.difference(colored,original).getbbox())

    def test_background_injection_real_image(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            Image.new('RGB',(480,640),'#aabbcc').save(root/'background_toilet.png')
            p=load_asset_pack(root)
            img=p.background('toilet',(360,640))
            self.assertEqual(img.size,(360,640))
            self.assertEqual(img.getpixel((180,200)),(170,187,204))

    def test_background_rejects_wrong_file_type(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'background_toilet.png').write_text('<script>fake image</script>')
            p=load_asset_pack(root)
            with self.assertRaises(Exception):p.background('toilet',(360,640))

    def test_character_config_rejects_unknown_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'settings.json').write_text(json.dumps({'character':{'eval':'oops'}}))
            with self.assertRaises(AssetError):load_asset_pack(root)

    def test_run_visibly_approaches_door(self):
        im=procedural_background('toilet')
        start=draw_actor(im,'run',0.1,True,progress=0.0)
        end=draw_actor(im,'run',0.1,True,progress=1.0)
        self.assertIsNotNone(ImageChops.difference(start,end).getbbox())
        # At least one visible change must involve head location, not just footsteps.
        self.assertNotEqual(start.getpixel((65,304)),end.getpixel((65,304)))

class QualityWarnings(unittest.TestCase):
    def test_story_voice_quality_flags(self):
        from quality_audit import review_plan
        story={'scenes':[{'action':'run','location':'toilet','duration':.8,'narration':'I have to run as fast as I possibly can'},
                         {'action':'knock','location':'toilet','duration':.6,'narration':'Please open up quickly'}]}
        warnings=review_plan(story)
        self.assertTrue(any('cut off' in w for w in warnings))
        self.assertTrue(any('under 8 seconds' in w for w in warnings))

    def test_good_comedy_plan_has_no_narration_warning(self):
        from quality_audit import review_plan
        story={'scenes':[{'action':'run','location':'toilet','duration':2.5,'narration':'I need it!'},
                         {'action':'knock','location':'toilet','duration':2.0,'narration':'Hello?'},
                         {'action':'shock','location':'toilet','duration':2.5,'narration':'Locked!'},
                         {'action':'recover','location':'toilet','duration':1.5,'narration':'Oops.'}]}
        warnings=review_plan(story)
        self.assertFalse(any('cut off' in w for w in warnings))

if __name__=='__main__':unittest.main()
