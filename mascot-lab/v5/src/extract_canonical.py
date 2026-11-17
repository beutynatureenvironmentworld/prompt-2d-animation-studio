"""Reproducibly extract the 1st reference pose from permanent six-pose sheet.

Maintains user artwork; no image generation/reinterpretation. Deterministic
OpenCV-connected silhouette extraction removes the sheet's soft floor shadow.
"""
import argparse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from acting_v2 import detect_head

def extract(source, output):
    image=Image.open(source).convert('RGB')
    w,h=image.size
    rgb=np.array(image.crop((0,0,w//3,h//2)))
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)
    # Only saturated dark ink contributes; this excludes the floor shadow.
    dark=np.uint8(gray<118)*255
    dark=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    contours,_=cv2.findContours(dark,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    candidates=[c for c in contours if cv2.contourArea(c)>max(800,gray.size*.009)]
    if not candidates:raise RuntimeError('Reference silhouette missing')
    largest=max(candidates,key=cv2.contourArea)
    mask=np.zeros_like(gray)
    cv2.drawContours(mask,[largest],-1,255,-1)
    mask=cv2.GaussianBlur(mask,(3,3),.7)
    ys,xs=np.where(mask>10)
    x0,x1=max(0,int(xs.min())-3),min(gray.shape[1],int(xs.max())+4)
    y0,y1=max(0,int(ys.min())-3),min(gray.shape[0],int(ys.max())+4)
    sprite=Image.fromarray(np.dstack([rgb,mask])[y0:y1,x0:x1],mode='RGBA')
    # Verify reference really includes a large upper circular mascot head.
    geo=detect_head(sprite)
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    sprite.save(output)
    print('CANONICAL_ORIGINAL_MASCOT_EXTRACTED',sprite.size,'head_radius',geo.radius,'=>',output)
    return sprite

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sheet',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();extract(a.sheet,a.output)
