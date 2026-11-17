"""Safety and geometry checks on real encoded V4 hybrid MP4 plus motion report."""
from quality import assess
import argparse,json
from pathlib import Path

def assess_hybrid(mp4,report,output=None):
    data=json.loads(Path(report).read_text())
    if data['leg_motion_engine']!='hybrid_speed_chase_fk_with_world_locked_stance':
        raise RuntimeError('Unexpected leg engine: not speed chase hybrid')
    if data['visible_elbow_knee_circles'] is not False:
        raise RuntimeError('Joint rings were not removed')
    if data['leg_lane_crossings']!=0 or data['leg_samples']<200:
        raise RuntimeError('Crossed-leg silhouette detected or insufficient samples')
    if min(data['run_pose_counts'].values()) < 1:
        raise RuntimeError('Run cycle missing one or more fundamental key poses')
    if data['knock_contact_max_error_px']>9:
        raise RuntimeError('V3 IK door contact regressed')
    result=assess(mp4,report,output)
    result.update({'leg_mode':'pose_driven_FK_speed_chase_plus_V3_arm_IK',
                   'noncrossed_leg_samples':data['leg_samples'],
                   'continuous_rubber_hose_arms':True,
                   'run_pose_counts':data['run_pose_counts'],
                   'verified_legacy_arm_ik_contact':True,
                   'visual_review_required':'A zero crossing count is geometric pre-transform validation, not human perceptual validation.'})
    Path(output or Path(mp4).with_name('QUALITY_REPORT.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('FTE_V4_NON_CROSSING_HYBRID_QA_PASS',json.dumps(result))
    return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--video',required=True);p.add_argument('--report',required=True);p.add_argument('--output');a=p.parse_args()
 assess_hybrid(a.video,a.report,a.output)
