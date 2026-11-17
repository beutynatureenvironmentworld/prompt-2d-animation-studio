import json, unittest
from pathlib import Path
from story_engine import parse_prompt, load_poses, state
ROOT=Path(__file__).resolve().parent
class StoryTests(unittest.TestCase):
 def test_prompt_understood(self):
  v=parse_prompt('දුවගෙන දොරට තට්ටු කර බය වෙනවා')
  self.assertTrue(v['matched_keywords']['run'])
  self.assertTrue(v['matched_keywords']['door'])
  self.assertTrue(v['matched_keywords']['knock'])
 def test_persistent_original_six_poses(self):
  p=load_poses(ROOT.parent/'config/permanent_mascot.webp' if (ROOT.parent/'config/permanent_mascot.webp').exists() else ROOT/'source/permanent_mascot_original_sheet.png')
  self.assertEqual(len(p),6)
  self.assertTrue(all(im.width>80 and im.height>100 for im in p))
 def test_real_displacement(self):
  s0=state(.86);s1=state(2.64)
  self.assertGreater(s1['x']-s0['x'],70)
if __name__=='__main__':unittest.main()