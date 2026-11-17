import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from spicy_motion_director import make_plan,validate,beat_at
from render_spicy import solve2,curve_points,face_variant,make_head_assets

class SpicyAnimationRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.face=make_head_assets((ROOT/'assets/permanent_mascot_reference.png') if (ROOT/'assets/permanent_mascot_reference.png').exists() else ROOT.parent/'config'/'permanent_mascot.webp')
 def test_planner_schema_and_fps(self):
  plan=validate(make_plan());self.assertEqual(plan['duration'],11.4);self.assertEqual(plan['fps'],24)
 def test_reject_unknown_animation(self):
  plan=make_plan();plan['beats'][3]['action']='run_unknown_generated_code'
  with self.assertRaises(ValueError):validate(plan)
 def test_end_of_timeline(self):
  p=make_plan();self.assertEqual(beat_at(p,6)[0]['action'],'flare_up');self.assertEqual(beat_at(p,11.3)[0]['action'],'sly_finish')
 def test_ik_preserves_endpoints(self):
  start=(276,336);dest=(265,243)
  knee,hand,err=solve2(start,dest)
  self.assertLess(err,.001);self.assertAlmostEqual(hand[0],dest[0],places=3);self.assertAlmostEqual(hand[1],dest[1],places=3)
 def test_smooth_shoulders_no_inserted_joint_shape(self):
  a=(276,336);b=(330,300);c=(300,263);p=curve_points(a,b,c)
  self.assertEqual(p[0],a);self.assertEqual(p[-1],c);self.assertGreater(len(p),9)
 def test_original_sly_grin_preserved(self):
  self.assertEqual(face_variant(self.face,'sly').tobytes(),self.face.tobytes())
 def test_face_variation(self):
  shocked=face_variant(self.face,'shock',.8)
  self.assertNotEqual(shocked.tobytes(),self.face.tobytes())
 def test_tongue_face(self):
  self.assertNotEqual(face_variant(self.face,'tired',1).tobytes(),face_variant(self.face,'panic',1).tobytes())

if __name__=='__main__':unittest.main()
