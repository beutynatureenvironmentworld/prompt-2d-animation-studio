"""Surgical repair of tiny disconnected ink flecks inside shoulder sockets.

V5's front arm stroke was rooted outside the rounded torso: a visible broken
shoulder gap, plus one-pixel internal black islands at (239,294)/(240,299).
V6 embeds shoulder origins 11px within body, then suppresses only isolated
ink islands, never entire lines/eyes or exterior silhouette.
"""
import numpy as np
import cv2
from PIL import Image

SOCKET_ROIS=((216,280,253,325),(177,280,214,325))

def count_flecks(image):
    rgba=np.asarray(image.convert('RGBA'));counts=[]
    for x0,y0,x1,y1 in SOCKET_ROIS:
        roi=rgba[y0:y1,x0:x1]
        dark=np.uint8((roi[:,:,3]>240)&(np.max(roi[:,:,:3],axis=2)<93))*255
        _,labels,stats,_=cv2.connectedComponentsWithStats(dark,8)
        n=0
        for k in range(1,len(stats)):
            xx,yy,w,h,area=stats[k]
            if area<=9 and xx>2 and yy>2 and xx+w<x1-x0-2 and yy+h<y1-y0-2:
                n+=1
        counts.append(n)
    return counts

def clean_shoulder_flecks(image):
    a=np.asarray(image.convert('RGBA')).copy();fixed=0
    for x0,y0,x1,y1 in SOCKET_ROIS:
        roi=a[y0:y1,x0:x1]
        dark=np.uint8((roi[:,:,3]>240)&(np.max(roi[:,:,:3],axis=2)<93))*255
        _,labels,stats,_=cv2.connectedComponentsWithStats(dark,8)
        for k in range(1,len(stats)):
            xx,yy,w,h,area=stats[k]
            if not (area<=9 and xx>2 and yy>2 and xx+w<x1-x0-2 and yy+h<y1-y0-2):continue
            # 1px safety margin so compression doesn't reintroduce an isolated speck.
            mask=(labels==k).astype(np.uint8)
            mask=cv2.dilate(mask,np.ones((3,3),np.uint8),iterations=1).astype(bool)
            roi[mask,:]=(255,255,255,255)
            fixed+=1
    return Image.fromarray(a,'RGBA'),fixed
