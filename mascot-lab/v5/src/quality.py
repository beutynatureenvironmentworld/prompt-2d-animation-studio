"""Deterministic MP4 integrity + QA gates; no claim of human-level art review."""
import json,subprocess,argparse
from pathlib import Path
import cv2,numpy as np

def assess(mp4,report_file,output=None):
    mp4=Path(mp4);d=json.loads(Path(report_file).read_text())
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height','-of','json',str(mp4)]))
    codecs={s.get('codec_name') for s in info['streams']}
    if {'h264','aac'}-codecs:raise RuntimeError('Missing H264/AAC')
    if abs(float(info['format']['duration'])-d['duration'])>.1:raise RuntimeError('Wrong duration')
    if d['knock_contact_frames']<3 or d['knock_contact_max_error_px']>9:raise RuntimeError('Bad authored wrist contact')
    if d['foot_stance_max_drift_px']>3:raise RuntimeError('World-space foot stance slipped')
    if len(d['face_states_used'])<5 or not d['one_pupil_per_eye']:raise RuntimeError('Face variety/pupil gate failed')
    cap=cv2.VideoCapture(str(mp4))
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    samples=[];fr=[]
    for sec in (.5,1.5,2.4,4.05,5.57,6.4,7.6,8.8,10.5):
        cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
        ret,image=cap.read()
        if not ret:raise RuntimeError('Decoded video missing frame at '+str(sec))
        samples.append(image)
        fr.append(sec)
    cap.release()
    diffs=[float(np.mean(np.abs(a.astype('float32')-b.astype('float32')))) for a,b in zip(samples,samples[1:])]
    # ensure different temporal poses rather than a 12-second still image
    if max(diffs)<4:raise RuntimeError('No perceptible motion differences across decoded frames')
    result={'passed':True,'duration':round(float(info['format']['duration']),2),'frames':n,'fps':round(fps,2),
            'codecs':sorted(codecs),'contact_error_px':d['knock_contact_max_error_px'],
            'foot_stance_max_drift_px':d['foot_stance_max_drift_px'],
            'unique_facial_states':d['face_states_used'],
            'decoded_frame_difference_max':round(max(diffs),2),'decoded_frame_difference_min':round(min(diffs),2),
            'notes':'Numeric QA is not a substitute for human inspection of acting/contact/limb shape.'}
    path=Path(output) if output else mp4.with_name('QUALITY_REPORT.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print('FUNNY_TOON_MASCOT_CPU_VIDEO_QA_PASS',json.dumps(result))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--video',required=True);p.add_argument('--report',required=True);p.add_argument('--output',default=None)
    a=p.parse_args();assess(a.video,a.report,a.output)
