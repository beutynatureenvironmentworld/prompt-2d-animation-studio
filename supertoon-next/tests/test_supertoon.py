import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from plan import compile_story,validate
from draw import ik

class Tests(unittest.TestCase):
 def test_sinhala_toilet_and_actions(self):
  s=compile_story('ටොයිලට් එකට දුවලා දොරට තට්ටු කරලා බය වුණා',9)
  self.assertEqual(s['setting'],'toilet')
  self.assertIn('knock',[x['action'] for x in s['beats']])
  self.assertIn('sprint',[x['action'] for x in s['beats']])
 def test_cat_park(self):
  s=compile_story('Orange cat runs and jumps in garden',6,'16:9')
  self.assertEqual((s['setting'],s['character'],s['ratio']),('park','cat','16:9'))
 def test_other_scenes(self):
  s=compile_story('Robot dances in classroom and laughs',7)
  self.assertEqual((s['setting'],s['character']),('school','robot'))
 def test_json_bad_action_rejected(self):
  s=compile_story('Funny boy running',5)
  s['beats'][0]['action']='arbitrary_python_exec'
  with self.assertRaises(ValueError):validate(s)
 def test_no_timeline_overlap(self):
  s=compile_story('cat runs then jumps',6)
  s['beats'][-1]['start']=0
  with self.assertRaises(ValueError):validate(s)
 def test_ik_joint_reaches_foot(self):
  a=(0,0);ankle=(28,80);k=ik(a,ankle,46,47,-1)
  self.assertAlmostEqual(sum((k[i]-a[i])**2 for i in range(2))**.5,46,delta=.1)
  self.assertAlmostEqual(sum((ankle[i]-k[i])**2 for i in range(2))**.5,47,delta=.1)
 def test_sinhala_unknown_short_fails(self):
  with self.assertRaises(ValueError):compile_story('hi')

if __name__=='__main__':unittest.main()

class VectorPropsTests(unittest.TestCase):
 def test_safe_flying_prop_is_accepted(self):
  from props import validate_props,motion_at
  props=[{'kind':'ellipse','x':300,'y':125,'w':80,'h':80,'fill':'#ff9933',
    'motions':[{'t':0,'dx':150,'dy':0,'angle':0,'scale':1},{'t':7,'dx':-170,'dy':-20,'angle':200,'scale':1.1}]}]
  self.assertEqual(len(validate_props(props,8)),1)
  self.assertNotEqual(motion_at(props[0]['motions'],2)['dx'],motion_at(props[0]['motions'],5)['dx'])
 def test_reject_javascript_in_json(self):
  from props import validate_props
  with self.assertRaises(ValueError):
   validate_props([{'kind':'rect','x':4,'y':4,'w':10,'h':10,'onClick':'evil()'}],5)
 def test_reject_remote_resource_field(self):
  from props import validate_props
  with self.assertRaises(ValueError):
   validate_props([{'kind':'rect','x':4,'y':4,'w':10,'h':10,'url':'http://example.com/x'}],5)