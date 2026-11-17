import math,sys,unittest,tempfile,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ik import two_bone_ik,planted_foot
from v3_director import offline_plan,validate,active_beat
from face import crop_original_head
from extract_canonical import extract

class TestDirector(unittest.TestCase):
    def test_complete_template(self):
        p=validate(offline_plan('A funny sneaky mascot runs to the toilet door'))
        self.assertEqual(p['schema'],'fte-motion-v3')
        self.assertEqual(p['character'],'funny_toon_ever_permanent')
        self.assertEqual(p['beats'][0]['action'],'sneak')
        self.assertEqual(p['beats'][-1]['action'],'celebrate')
        self.assertEqual(active_beat(p,3.8)[0]['action'],'knock')
    def test_reject_arbitrary_code_or_unrecognized_action(self):
        p=offline_plan('door')
        p['beats'][2]['action']='__import__("os").system("echo unsafe")'
        with self.assertRaises(ValueError):validate(p)
    def test_no_unintended_actor(self):
        p=offline_plan('door');p['character']='someone_else'
        with self.assertRaises(ValueError):validate(p)

class TestIK(unittest.TestCase):
    def test_arm_hand_exact_when_reachable(self):
        joint,end,err=two_bone_ik((255,294),(335,229),66,66,1)
        self.assertLess(err,.01)
        self.assertLess(math.dist(end,(335,229)),.01)
        self.assertAlmostEqual(math.dist((255,294),joint),66,places=5)
        self.assertAlmostEqual(math.dist(joint,end),66,places=5)
    def test_unreachable_is_reported_not_silently_pretended(self):
        joint,end,err=two_bone_ik((0,0),(1000,0),66,66,1)
        self.assertGreater(err,850)
    def test_foot_world_lock_during_stance(self):
        def x(t):return 120+85*t
        a,locked=planted_foot(1.0,x,-1,.9,2.7)
        b,locked2=planted_foot(1.03,x,-1,.9,2.7)
        self.assertTrue(locked and locked2)
        self.assertAlmostEqual(a[0],b[0],places=6)
        self.assertEqual(a[1],833)

class TestReference(unittest.TestCase):
    def test_head_crop_from_original_reference(self):
        p=ROOT/'assets'/'canonical_neutral_pose.png'
        if not p.exists():self.skipTest('Needs extracted source pose')
        bank,meta=crop_original_head(Image.open(p))
        self.assertIn('sly',bank)
        self.assertIn('shock',bank)
        self.assertTrue(meta['one_pupil_per_eye'])
        self.assertGreater(bank['sly'].width,100)
        # Full original toothy grin is restored for normal mascot expression.
        self.assertNotEqual(bank['sly'].tobytes(),bank['shock'].tobytes())
    def test_reproducible_source_from_sixframe(self):
        p=ROOT/'assets'/'permanent_mascot_reference.png'
        if not p.exists():self.skipTest('Needs source sheet')
        with tempfile.TemporaryDirectory() as temp:
            sprite=extract(p,Path(temp)/'pose.png')
            self.assertGreater(sprite.width,200)
            self.assertGreater(sprite.height,200)

if __name__=='__main__':unittest.main()
