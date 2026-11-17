import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from acting_v2 import build_face_bank, knock_alignment, expression_for

spec = importlib.util.spec_from_file_location('mascot_loop_v2', ROOT/'src'/'loop.py')
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class TestPermanentMascotActingV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sheet = ROOT/'config'/'permanent_mascot.webp'
        cls.poses = loop.load_poses(cls.sheet)
        cls.bank, cls.geometry = build_face_bank(cls.poses)

    def test_each_of_six_puppet_poses_has_six_explicit_expressions(self):
        self.assertEqual(len(self.bank), 36)
        self.assertEqual(len(self.geometry), 6)

    def test_one_pupil_per_eye_all_36_variations(self):
        for p in self.bank.values():
            self.assertEqual(p.info['pupil_count'], 2)
            self.assertEqual(len(set(tuple(v) for v in p.info['pupil_centers'])), 2)

    def test_expression_changes_at_dramatic_beats(self):
        self.assertEqual(expression_for('run', .5), 'focus')
        self.assertEqual(expression_for('knock', .2), 'effort')
        self.assertEqual(expression_for('shock', .5), 'shock')
        self.assertEqual(expression_for('slip', .5), 'worried')
        self.assertEqual(expression_for('recover', .1), 'neutral')
        self.assertEqual(expression_for('recover', .8), 'grin')

    def test_face_is_actually_changed_not_just_metadata(self):
        from PIL import ImageChops
        a = self.bank[(3,'shock')].convert('RGB')
        b = self.bank[(3,'grin')].convert('RGB')
        self.assertIsNotNone(ImageChops.difference(a,b).getbbox())

    def test_contact_sprite_fist_matches_target(self):
        p = self.poses[3]
        q = knock_alignment(p, 236/p.height,245,375)
        self.assertAlmostEqual(q['hand_x'],245,delta=.02)
        self.assertAlmostEqual(q['hand_y'],375,delta=.02)

    def test_rendered_knock_pose_uses_authored_fist_not_idle_open_hand(self):
        timeline=loop.storyboard('door')
        beat=next(b for b in timeline if b['action']=='knock')
        params={'contact_offset':14,'right_hand_offset':72,'start_x':110,'slip_x':175}
        backdrop=loop.backdrop('door')
        im, st=loop.frame(beat['start']+.38,self.poses,backdrop,timeline,params,face_bank=self.bank)
        self.assertEqual(st['pose'],3)
        self.assertEqual(st['expression'],'effort')
        self.assertLess(st['hand_contact_error_px'],3)
        self.assertEqual(im.size,(360,640))

if __name__=='__main__':
    unittest.main()
