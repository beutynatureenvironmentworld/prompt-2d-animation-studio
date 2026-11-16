import sys,unittest, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shortgpt_supertest import offline_plan,safe_plan,PipelineError,procedural_background,draw_actor
class Checks(unittest.TestCase):
    def test_story_english(self):
        d=offline_plan('The boy runs to the toilet then knocks on door and gets shocked')
        actions=[x['action'] for x in d['scenes']]
        self.assertIn('run',actions);self.assertIn('knock',actions)
        self.assertEqual(d['scenes'][0]['location'],'toilet')
    def test_sinhala(self):
        d=offline_plan('ටොයිලට් එකට දුවගෙන ගිහින් දොරට තට්ටු කරන්න')
        self.assertIn('run',[x['action'] for x in d['scenes']])
        self.assertIn('knock',[x['action'] for x in d['scenes']])
    def test_reject_arbitrary_code(self):
        with self.assertRaises(PipelineError):safe_plan({'scenes':[{'action':'exec','location':'park','duration':1}]})
    def test_six_scene_limit(self):
        with self.assertRaises(PipelineError):safe_plan({'scenes':[{'action':'run','location':'park','duration':1}]*7})
    def test_frame_motion(self):
        from PIL import ImageChops
        p=procedural_background('garden')
        a=draw_actor(p,'run',.1,True)
        b=draw_actor(p,'run',.3,True)
        self.assertIsNotNone(ImageChops.difference(a,b).getbbox())
if __name__=='__main__':unittest.main()
