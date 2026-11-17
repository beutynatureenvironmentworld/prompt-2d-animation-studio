import unittest,sys,math,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from moon_garden import background,backplate
from garden_sound import vocal,make_audio
from front_arm_motion import front_arm_pose
from shoulder_guard import clean_shoulder_flecks,count_flecks
from render import body_illustration,KNOB
from face import crop_original_head
from v3_director import offline_plan,validate

class V6GardenTests(unittest.TestCase):
  def test_scene_color_and_contact_anchor(self):
    garden=background(4,'knock',.5)
    self.assertEqual(garden.size,(540,960))
    self.assertNotEqual(garden.getpixel((30,190))[:3],garden.getpixel((30,600))[:3])
    self.assertEqual(KNOB,(406,606))
  def test_single_subject_identity(self):
    b,_=crop_original_head(Image.open(ROOT/'assets'/'canonical_neutral_pose.png'))
    self.assertTrue({'sly','shock','grin','neutral'}.issubset(b))
  def test_shoulder_root_seam_is_embedded_not_outside_torso(self):
    b,_=crop_original_head(Image.open(ROOT/'assets'/'canonical_neutral_pose.png'))
    logs={'max_leg_ik_unreach_px':0,'max_hand_ik_unreach_px':0,'knock_contact_max_error_px':0,'knock_contact_frames':0,'planted_foot_samples':0,'stance_tracks':[],'expressions':set(),'leg_lane_crossings':0,'leg_samples':0,'run_pose_counts':{'contact':0,'down':0,'passing':0,'up':0},'frontal_arm_frames':0,'run_arm_swing_signs':{'-1':[],'1':[]},'run_arm_hand_y_samples':{'-1':[],'1':[]},'run_arm_screen_horizontal_max_px':0,'shoulder_specks_removed':0}
    for action,t in [('sneak',.4),('dash',1.4),('knock',3.7),('shock',5.5),('recover',8.9)]:
      sprite,*_=body_illustration(t,action,.4,b,logs)
      self.assertEqual(count_flecks(sprite),[0,0],action)
    self.assertEqual(logs['max_hand_ik_unreach_px'],0)
    self.assertGreater(logs['shoulder_specks_removed'],0)
  def test_formant_reaction_exists_without_narration(self):
    import numpy as np
    w=vocal(.8,[(0,440,900,.9),(.4,700,1500,1.4),(1,420,800,.8)])
    self.assertGreater(np.std(w),.06)
    self.assertTrue(np.isfinite(w).all())
  def test_front_arm_outward_silhouette_no_robot_elbow(self):
    a=front_arm_pose('dash',-1,(186,303),math.pi/2)
    self.assertGreater(a.hand[1],a.shoulder[1]+40)
    self.assertLess(abs(a.hand[0]-a.shoulder[0]),39)
  def test_original_storyboard_still_valid(self):
    p=validate(offline_plan('moon garden wish bell, three chimes and one bloom'))
    self.assertEqual(len(p['beats']),11)
if __name__=='__main__':unittest.main()
