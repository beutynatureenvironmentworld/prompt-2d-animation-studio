#!/usr/bin/env python3
"""Decode MP4 and verify actually moving pictures rather than encoded stills."""
import argparse, json, subprocess
from pathlib import Path
import cv2
import numpy as np

def inspect(video):
    p=Path(video)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error',
        '-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration',
        '-of','json',str(p)]))
    s=next(st for st in probe['streams'] if st.get('codec_name')=='h264')
    assert (s['width'],s['height'],s['r_frame_rate'])==(720,720,'24/1'),s
    assert abs(float(probe['format']['duration'])-12)<.05
    cap=cv2.VideoCapture(str(p));samples=[];times=[];count=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        if count%6==0:
            samples.append(cv2.cvtColor(cv2.resize(frame,(120,120)),cv2.COLOR_BGR2GRAY))
            times.append(count/24)
        count+=1
    cap.release();assert count==288,count
    changes=[float(np.abs(samples[i].astype(np.float32)-samples[i-1]).mean()) for i in range(1,len(samples))]
    assert sum(x>0.20 for x in changes)>27,changes
    street=[change for i,change in enumerate(changes,1) if 3.5<=times[i]<=5.75]
    assert sum(x>0.50 for x in street)>=6,street
    return {'frames':count,'fps':24,'size':'720x720','duration_seconds':12,
        'codec':'h264','sampled_frame_changes':sum(x>0.20 for x in changes),
        'street_samples_moving':sum(x>0.50 for x in street),'passed':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('video')
    parser.add_argument('--report',default=None)
    args=parser.parse_args();result=inspect(args.video)
    if args.report:Path(args.report).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
