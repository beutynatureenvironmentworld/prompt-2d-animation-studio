import importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mascot_loop',ROOT/'src'/'loop.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class TestMascotLoop(unittest.TestCase):
 def test_story_is_chronological(self):
  t=mod.storyboard('door');self.assertEqual([x['action'] for x in t],list(mod.GAGS['door']))
  self.assertGreater(t[-1]['end'],8)
 def test_running_has_real_spatial_travel(self):
  t=mod.storyboard('door');r=next(x for x in t if x['action']=='run');p={'contact_offset':0,'right_hand_offset':78}
  a=mod.state_at(r['start']+.03,t,p);b=mod.state_at(r['end']-.03,t,p)
  self.assertGreater(b['x']-a['x'],60)
 def test_knock_has_near_contact(self):
  t=mod.storyboard('door');r=next(x for x in t if x['action']=='knock');p={'contact_offset':7,'right_hand_offset':75}
  s=mod.state_at((r['start']+r['end'])/2,t,p)
  self.assertLessEqual(abs(245-(s['x']+p['right_hand_offset'])),18)
 def test_images_source_is_six_paired_original_poses(self):
  self.assertEqual(len(mod.NAMES),6)
 def test_gag_library_is_bounded(self):
  self.assertEqual(len(mod.GAGS),4)
  for g in mod.GAGS.values():self.assertTrue(set(g).issubset(mod.ACTIONS))
if __name__=='__main__':unittest.main()