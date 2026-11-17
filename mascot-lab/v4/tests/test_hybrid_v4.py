"""Regression tests, including natural non-crossing running legs and legacy arms."""
import sys,math,unittest
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from speed_chase_hybrid import chase_foot,leg_control,lane_ok,rounded_joint_path
from render import anchor_x,draw_limb,body_illustration,FLOOR
from ik import two_bone_ik
from face import crop_original_head

class HybridV4Tests(unittest.TestCase):
    def test_all_frames_non_crossed_knees_and_feet(self):
        # Samples every animation frame across full dash, plus split pose stages.
        seen=set();pos={}
        for i in range(round(1.8*24)):
            t=.9+i/24
            frame={}
            for side in (-1,1):
                (x,y),plant,pose=chase_foot(t,anchor_x,side)
                seen.add(pose)
                local=(x-(anchor_x(t)-215),y-(FLOOR-455))
                hip=(190,366) if side==-1 else (240,366)
                knee=leg_control(hip,local,side,pose)
                frame[side]=(hip,knee,local)
                if plant:
                    if side in pos and t-pos[side][0]<=1/24+.001:
                        self.assertLess(abs(x-pos[side][1]),1e-4)
                    pos[side]=(t,x)
                else:
                    pos.pop(side,None)
            self.assertTrue(lane_ok(*(frame[-1]+frame[1])),f'X crossing at t={t:.2f}: {frame}')
        self.assertEqual(seen,{'contact','down','passing','up'})

    def test_smooth_tube_keeps_arm_ik_endpoint_and_has_no_joint_ring(self):
        root=(255,294);dest=(335,229)
        mid,end,unreach=two_bone_ik(root,dest,66,66,1)
        pts=rounded_joint_path(root,mid,end)
        self.assertEqual(pts[0],root)
        self.assertEqual(pts[-1],end)
        self.assertGreaterEqual(len(pts),8)
        self.assertLess(unreach,.02)
        # Draw has continuous tube strokes, not the V3 donut ellipse.
        from PIL import ImageDraw
        class Spy:
            def __init__(self):self.shapes=[]
            def line(self,*args,**kw):self.shapes.append(('line',args,kw))
            def ellipse(self,*args,**kw):self.shapes.append(('ellipse',args,kw))
        spy=Spy();draw_limb(spy,root,mid,end,28)
        self.assertEqual([p[0] for p in spy.shapes],['line','line'])

    def test_static_idle_legs_do_not_form_x(self):
        feet={}
        for side in (-1,1):
            hip=(190 if side<0 else 240,366)
            foot=(215+side*51,455)
            feet[side]=(hip,leg_control(hip,foot,side),foot)
        self.assertTrue(lane_ok(*(feet[-1]+feet[1])))

    def test_v3_arms_door_contact_and_original_head_kept(self):
        bank,meta=crop_original_head(Image.open(ROOT/'assets'/'canonical_neutral_pose.png'))
        logs={'max_leg_ik_unreach_px':0.,'max_hand_ik_unreach_px':0.,
          'knock_contact_max_error_px':0.,'knock_contact_frames':0,
          'planted_foot_samples':0,'stance_tracks':[],'expressions':set(),
          'leg_lane_crossings':0,'leg_samples':0,
          'run_pose_counts':{k:0 for k in ('contact','down','passing','up')}}
        for i in range(8):
            t=3.4+i/24
            body_illustration(t,'knock',i/8,bank,logs)
        self.assertTrue(meta['one_pupil_per_eye'])
        self.assertLess(logs['max_hand_ik_unreach_px'],.01)
        self.assertEqual(logs['leg_lane_crossings'],0)

if __name__=='__main__':unittest.main()
