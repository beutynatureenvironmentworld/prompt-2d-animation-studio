import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'src'))
from story import compile_story,validate,SETTINGS,CHARACTERS
from draw import ik,render_frame
import cairo
class StoryTests(unittest.TestCase):
 def test_sinhala_toilet(self):
  p=compile_story('ළමයා ටොයිලට් එකට දුවලා දොරට තට්ටු කරලා බය වෙලා ලිස්සලා වැටෙනවා')
  self.assertEqual(p['setting'],'toilet')
  self.assertIn('knock',[x['action'] for x in p['beats']]);self.assertIn('sprint',[x['action'] for x in p['beats']])
 def test_varied_place(self):
  self.assertEqual(compile_story('Cat jumps over ball on a beach')['setting'],'beach')
 def test_many_characters(self):
  self.assertEqual(compile_story('Robot dances in school')['character'],'robot')
 def test_action_order(self):
  p=compile_story('Girl runs then jumps, slips and recovers')
  arr=[b['action'] for b in p['beats']]
  self.assertTrue(arr.index('sprint')<arr.index('jump')<arr.index('slip'))
 def test_arbitrary_executable_code_rejected(self):
  p=compile_story('Funny cat sprints then falls')
  p['beats'][0]['action']='subprocess.Popen'
  with self.assertRaises(ValueError):validate(p)
 def test_ik_lengths(self):
  h,f=(0.,0.),(35.,81.);k=ik(h,f,53,55,1)
  self.assertAlmostEqual(((k[0]-h[0])**2+(k[1]-h[1])**2)**.5,53,delta=.1)
  self.assertAlmostEqual(((k[0]-f[0])**2+(k[1]-f[1])**2)**.5,55,delta=.1)
 def test_render_every_environment(self):
  surface=cairo.ImageSurface(cairo.FORMAT_RGB24,96,160)
  for place in SETTINGS:
   p=compile_story('Funny boy runs',4);p['setting']=place
   self.assertIsInstance(render_frame(cairo.Context(surface),p,0.9,96,160),str)
 def test_all_characters_render(self):
  surface=cairo.ImageSurface(cairo.FORMAT_RGB24,96,160)
  for k in CHARACTERS:
   p=compile_story('Funny boy runs',4);p['character']=k
   self.assertIsInstance(render_frame(cairo.Context(surface),p,.8,96,160),str)
if __name__=='__main__':unittest.main()
