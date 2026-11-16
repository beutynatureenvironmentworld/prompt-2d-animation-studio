"""Extract 6 complete full-body black-and-white mascot poses from the supplied six-pose board.

No face overlays, no fake skeletal rig. The whole drawn pose is one stable layer.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import cv2

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/official_six_pose_sheet.png'
DEST=ROOT/'assets/poses'
NAMES=['idle_neutral','crouch_anticipation','sprint_angry','sprint_surprise','jump_shock','recover_soft_smile']

def extract():
    DEST.mkdir(parents=True,exist_ok=True)
    (ROOT/'output').mkdir(parents=True,exist_ok=True)
    original=Image.open(SOURCE).convert('RGB')
    ww,hh=original.size
    previews=[]
    for i,name in enumerate(NAMES):
        col,row=i%3,i//3
        xa=ww*col//3; xb=ww*(col+1)//3
        ya=hh*row//2; yb=hh*(row+1)//2
        rgb=np.asarray(original.crop((xa,ya,xb,yb)))
        gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
        # dark ink outlines give a connected silhouette; ignore separate gray drop-shadows
        threshold=(gray<120).astype('uint8')*255
        count,labels,stats,_=cv2.connectedComponentsWithStats(threshold,8)
        # Join close parts, keeping the mascot (largest connected contour) separate from accents.
        solid=cv2.morphologyEx(threshold,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
        contours,_=cv2.findContours(solid,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        candidates=[q for q in contours if cv2.contourArea(q)>3000]
        if not candidates:raise ValueError('No mascot contour on pose '+str(i))
        mascot=max(candidates,key=cv2.contourArea)
        canvas=np.zeros_like(gray)
        cv2.drawContours(canvas,[mascot],-1,255,-1)
        # include nearby ink detached by a few pixels if inside body bounding rectangle
        canvas=cv2.GaussianBlur(canvas,(3,3),0.6)
        yy,xx=np.where(canvas>8)
        x0,x1=max(0,int(xx.min())-4),min(gray.shape[1],int(xx.max())+5)
        y0,y1=max(0,int(yy.min())-4),min(gray.shape[0],int(yy.max())+5)
        # preserve natural black strokes and white negative space without background bleed
        fg=np.concatenate([rgb,canvas[:,:,None]],axis=2)
        pose=Image.fromarray(fg,'RGBA').crop((x0,y0,x1,y1))
        # upsample just once while saving, keep source fidelity
        pose.save(DEST/f'{i}_{name}.png',optimize=True)
        thumb=pose.copy();thumb.thumbnail((255,245))
        previews.append(thumb)
        print('EXTRACTED_POSE',i,name,pose.size,'alpha_bbox',pose.getchannel('A').getbbox(),flush=True)
    sheet=Image.new('RGB',(870,680),'#f3f3f1');d=ImageDraw.Draw(sheet)
    for i,im in enumerate(previews):
        x=(i%3)*290+18;y=(i//3)*340+30
        sheet.paste(im,(x+(255-im.width)//2,y),im)
        d.text((x,y+260),f'{i}: {NAMES[i]}',fill='black')
    sheet.save(ROOT/'output/real_six_extracted_poses.jpg',quality=88)
if __name__=='__main__':extract()
