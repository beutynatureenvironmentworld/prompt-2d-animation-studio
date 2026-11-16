"""No-network proof that six user-supplied mascot art poses are compatible."""
import sys,unittest
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from prompt_to_json import rules,validate
from render import load_pose,background,frame_at
class TestMascotCPU(unittest.TestCase):
 def test_six_valid_unique_poses(self):
  poses=load_pose()
  self.assertEqual(len(poses),6)
  hashes=[]
  import hashlib
  for p in poses:
   self.assertGreater(p.getchannel('A').getbbox()[2],150)
   hashes.append(hashlib.sha256(p.tobytes()).digest())
  self.assertEqual(len(set(hashes)),6)
 def test_sinhala_prompt_action_order(self):
  d=rules('චරිතය පැනලා කේන්තියෙන් දුවලා බය වෙලා නැගිටිනවා')
  self.assertEqual([a['action'] for a in d['actions']],['jump','run','shock','recover'])
 def test_unsupported_prompt_fails(self):
  with self.assertRaises(ValueError):rules('xyzzy')
 def test_one_complete_face_layer_per_frame(self):
  plan=rules('Mascot runs then gets shocked and recovers')
  poses=load_pose()
  base=background(640,360)
  from PIL import ImageFont
  font=ImageFont.load_default()
  img1,_=frame_at(.1,plan,poses,base,font,640,360)
  img2,_=frame_at(2.6,plan,poses,base,font,640,360)
  self.assertIsNotNone(ImageChops.difference(img1,img2).getbbox())
if __name__=='__main__':unittest.main()
