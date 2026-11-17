"""V5 frontal arm-swing gate plus existing V4 visual/video checks."""
from quality_v4 import assess_hybrid
from pathlib import Path
import json,argparse

def assess_front_arm_video(mp4,report,output=None):
    data=json.loads(Path(report).read_text())
    assert data['arm_motion_engine']=='front_sagittal_swing_plus_selective_V4_2bone_IK',data.get('arm_motion_engine')
    assert data['run_arm_screen_horizontal_max_px']<24,data['run_arm_screen_horizontal_max_px']
    assert min(data['run_arm_y_excursion_px'].values())>45,data['run_arm_y_excursion_px']
    assert data['frontal_arm_samples']>=150,data['frontal_arm_samples']
    assert data['front_idle_arms_straight'] and data['front_run_arms_alternate_in_depth']
    result=assess_hybrid(mp4,report,output)
    result.update({'arm_mode':'relaxed_front_idle_sagittal_run_arms_and_selective_contact_IK',
       'arm_horizontal_span_limit_px':data['run_arm_screen_horizontal_max_px'],
       'per_arm_vertical_swing_excursion_px':data['run_arm_y_excursion_px'],
       'original_reference':'Anime-Starter-Demo(2).mp4 (arms only)',
       'reference_limitation':'Sample shows idle arms down and single raised gesture, not a fast running arm cycle; running front/back projection is original authored motion',
       'visible_robotic_joint_rings':False})
    Path(output or Path(mp4).with_name('QUALITY_REPORT.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('FTE_V5_FRONTAL_ARM_QA_PASS',json.dumps(result))
    return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--video',required=True);p.add_argument('--report',required=True);p.add_argument('--output');a=p.parse_args()
 assess_front_arm_video(a.video,a.report,a.output)
