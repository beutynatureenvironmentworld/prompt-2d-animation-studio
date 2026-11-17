"""V6 inherits V5 frontal swing with slightly outward wrists to fix shoulder seams."""
import math, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from front_arm_motion import front_arm_pose,near_arm_side,is_front_motion

class ArmReferenceV5Tests(unittest.TestCase):
    def test_idle_hands_down_and_elbows_collinear(self):
        for side,sx in [(-1,175),(1,255)]:
            a=front_arm_pose('sneak',side,(sx,294),0)
            self.assertGreater(a.hand[1]-a.shoulder[1],100)
            self.assertLess(abs(a.hand[0]-a.shoulder[0]),39)
            x1=a.elbow[0]-a.shoulder[0];y1=a.elbow[1]-a.shoulder[1]
            x2=a.hand[0]-a.shoulder[0];y2=a.hand[1]-a.shoulder[1]
            cross=abs(x1*y2-y1*x2)
            self.assertLess(cross,0.001)
            self.assertAlmostEqual(a.swing,0)

    def test_run_arms_alternate_front_back_not_lateral(self):
        excursions={-1:[],1:[]}
        for i in range(120):
            phase=i/120*4*math.pi
            left=front_arm_pose('dash',-1,(175,294),phase)
            right=front_arm_pose('dash',1,(255,294),phase)
            self.assertAlmostEqual(left.swing,-right.swing,places=5)
            for arm in [left,right]:
                self.assertLess(abs(arm.hand[0]-arm.shoulder[0]),39)
                self.assertGreater(arm.hand[1],arm.shoulder[1]+40)
                self.assertLess(arm.hand[1],arm.shoulder[1]+135)
                excursions[-1 if arm.shoulder[0]==175 else 1].append(arm.hand[1])
        self.assertGreater(max(excursions[-1])-min(excursions[-1]),45)
        self.assertGreater(max(excursions[1])-min(excursions[1]),45)

    def test_running_forward_arm_pumps_toward_chest_and_back_arm_stretches(self):
        near=front_arm_pose('dash',-1,(175,294),math.pi/2)
        far=front_arm_pose('dash',1,(255,294),math.pi/2)
        # Raised wrist near chest on the forward beat, trailing wrist lower.
        self.assertLess(near.hand[1],350)
        self.assertGreater(far.hand[1],405)
        self.assertGreater(far.hand[1]-near.hand[1],65)
        # At rest the elbow is straight, while forward pumping has a bend.
        idle=front_arm_pose('sneak',-1,(175,294),0)
        def bend_cross(a):
            x1=a.elbow[0]-a.shoulder[0];y1=a.elbow[1]-a.shoulder[1]
            x2=a.hand[0]-a.shoulder[0];y2=a.hand[1]-a.shoulder[1]
            return abs(x1*y2-y1*x2)
        self.assertGreater(bend_cross(near),150)
        self.assertLess(bend_cross(idle),.01)

    def test_brake_swing_eases_to_resting_down(self):
        p=front_arm_pose('brake',-1,(175,294),math.pi/2,1.0)
        idle=front_arm_pose('sneak',-1,(175,294),0)
        self.assertAlmostEqual(p.hand[1],idle.hand[1])
        self.assertAlmostEqual(p.hand[0],idle.hand[0])

    def test_dynamic_front_depth_switches_at_half_stride(self):
        self.assertEqual(near_arm_side('dash',math.pi/2),-1)
        self.assertEqual(near_arm_side('dash',3*math.pi/2),1)
        self.assertEqual(near_arm_side('knock',math.pi/2),1)
        self.assertTrue(is_front_motion('recover'))
        self.assertFalse(is_front_motion('knock'))

if __name__=='__main__':unittest.main()
