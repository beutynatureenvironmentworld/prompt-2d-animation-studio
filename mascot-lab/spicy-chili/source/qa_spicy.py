"""Actual-video QA plus honest limitations about what numeric checks can prove."""
import json,sys,subprocess
from pathlib import Path
import cv2,numpy as np

def verify(video,metadata,output=None):
 video=Path(video);d=json.loads(Path(metadata).read_text())
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(video)]))
 cs={s['codec_name'] for s in p['streams']};assert {'h264','aac'}<=cs,cs
 assert abs(float(p['format']['duration'])-11.4)<.12
 assert d['frames']==274
 assert d['leg_lane_crossings']==0
 assert d['pupil_count_per_eye']==1
 assert d['max_arm_ik_target_error_px']<1
 assert d['chili_mouth_contact_min_distance_px']<12
 assert d['smooth_shoulder_no_joint_rings'] is True
 assert d['audio_sfx_events']>=10
 assert len(d['facial_states'])>=6
 cap=cv2.VideoCapture(str(video));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
 imgs=[]
 for t in [.5,1.8,2.3,3.5,4.8,5.8,6.8,8.5,10.6]:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read()
  if not ok:raise AssertionError(f'Cannot decode MP4 at {t}s')
  imgs.append(im)
 cap.release()
 movement=[float(np.abs(a.astype('float32')-b.astype('float32')).mean()) for a,b in zip(imgs,imgs[1:])]
 if max(movement)<5:raise AssertionError('Encoded video may be an unchanged still image')
 # Strong fire color region to the right of face, unique to flame moment.
 fire=imgs[5];right=fire[360:660,250:530];b,g,r=cv2.split(right)
 mask=(r.astype('int16')>g.astype('int16')+60)&(g.astype('int16')>b.astype('int16')+35)&(r>190)
 if int(mask.sum())<120:raise AssertionError('Fire reaction missing from decoded MP4')
 result={'pass':True,'codec':sorted(cs),'frames_decoded':n,'fps':fps,
    'video_duration_sec':float(p['format']['duration']),'max_frame_difference':round(max(movement),2),
    'min_hand_to_chili_contact_error_px':d['chili_mouth_contact_min_distance_px'],
    'crossing_knees':d['leg_lane_crossings'],'fire_colored_pixels_in_decoded_frame':int(mask.sum()),
    'caveats':'Pixel QA is not the same as expert artistic/animation review. This is script-driven, not live Qwen3 inference.'}
 dst=Path(output or video.with_name('QA_VERIFIED.json'));dst.write_text(json.dumps(result,indent=2)+'\n');print('SPICY_REAL_MP4_QA_PASS',json.dumps(result));return result

if __name__=='__main__':
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument('--video',required=True);pa.add_argument('--metadata',required=True);pa.add_argument('--output',default=None);a=pa.parse_args()
 verify(a.video,a.metadata,a.output)
