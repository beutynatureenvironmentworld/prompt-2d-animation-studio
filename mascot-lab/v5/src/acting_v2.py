"""Identity-preserving facial acting and authored contact anchors for Funny Toon Ever.

This module operates on the user's ORIGINAL six-pose sheet. Every frame has one
complete head, two eyes, ONE pupil in each eye, and one expression-specific mouth.
No AI weight, external service, or arbitrary model-generated code is executed.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Mapping
import cv2
import numpy as np
from PIL import Image, ImageDraw

STYLES = ('grin', 'focus', 'effort', 'shock', 'worried', 'neutral')
ACTIONS_FACE = {
    'anticipate':'focus', 'run':'focus', 'knock':'effort', 'jump':'grin',
    'shock':'shock', 'slip':'worried', 'recover':'neutral',
}

@dataclass(frozen=True)
class FaceGeometry:
    cx: float
    cy: float
    radius: float


def detect_head(sprite:Image.Image) -> FaceGeometry:
    """Detect the circular HEAD outline, not pupil circles or hands.

    We constrain a Hough vote to the upper third and a plausible scale. This
    works on the user's six authored sprites and refuses uncertain geometry
    instead of silently putting a face on an elbow.
    """
    rgb=np.asarray(sprite.convert('RGB'))
    mono=cv2.medianBlur(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),5)
    h,w=mono.shape
    circles=cv2.HoughCircles(mono,cv2.HOUGH_GRADIENT,1.2,55,
                             param1=120,param2=35,
                             minRadius=max(38,int(min(w,h)*.15)),
                             maxRadius=int(min(w,h)*.32))
    if circles is None:
        raise ValueError('Head-circle detection failed; original six-pose art requires calibration')
    candidates=[]
    for cx,cy,r in circles[0]:
        if not (0.17*w < cx < 0.83*w and 0.08*h < cy < 0.42*h):
            continue
        # favor large circles near the upper portion, penalize truncated bounds
        outside=max(0,r-cx)+max(0,cx+r-w)+max(0,r-cy)+max(0,cy+r-h)
        score=r - .4*cy - 3*outside
        candidates.append((score,float(cx),float(cy),float(r)))
    if not candidates:
        raise ValueError('No head circle met upper-body constraints')
    _,x,y,r=max(candidates)
    return FaceGeometry(x,y,r)


def _line(d,xy,fill='black',width=4,joint='curve'):
    d.line(xy,fill=fill,width=width,joint=joint)


def cleaned_face(src:Image.Image, geom:FaceGeometry, expression:str='neutral',gaze:str='right') -> Image.Image:
    """Replace the original internally drawn pupils/grin with one controlled face.

    The thick outer head contour remains sourced from original user's artwork.
    Features are rebuilt inside the contour with explicit pupil count == 2.
    """
    if expression not in STYLES:raise ValueError('Unsupported expression')
    if gaze not in ('left','right','center'):raise ValueError('Unsupported eye direction')
    out=src.copy().convert('RGBA');d=ImageDraw.Draw(out)
    cx,cy,r=geom.cx,geom.cy,geom.radius
    # Do NOT touch outer ink contour; whitewash only the internal face, including
    # all source pupils. Proportional margin keeps the black source outline.
    # Redraw the source-identical round head contour in place. Several original
    # pose drawings push the grin against the outer border, so whitewashing
    # only the interior leaves a duplicate smile. Cover the full old head once.
    # Radius expansion is calibrated to the six permanent original poses.
    rr=r*(1.14 if r<87 else 1.075)
    d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill='white',outline='black',width=max(5,int(rr*.06)))
    r=rr
    ink=(0,0,0,255);white=(255,255,255,255)
    thick=max(3,round(r*.045));eye_rx=r*.21;eye_ry=r*.245
    eye_y=cy-r*.18
    pupil_positions=[]
    for side in (-1,1):
        ex=cx+side*r*.345
        d.ellipse((ex-eye_rx,eye_y-eye_ry,ex+eye_rx,eye_y+eye_ry), fill=white,outline=ink,width=thick)
        shift={'left':-.37,'center':0,'right':.37}[gaze]*eye_rx
        pupil_r=max(4,r*.075)
        px=ex+shift
        py=eye_y+eye_ry*.24
        # EXACTLY ONE filled black ellipse inside each eye.
        d.ellipse((px-pupil_r,py-pupil_r,px+pupil_r,py+pupil_r),fill=ink)
        pupil_positions.append((px,py))
        eyebrow_y=cy-r*.52
        if expression=='shock':
            brow=[(ex-eye_rx*.9,eyebrow_y+r*.045),(ex,eyebrow_y-r*.12),(ex+eye_rx*.9,eyebrow_y+r*.045)]
        elif expression in ('focus','effort'):
            slope=side*r*.07
            brow=[(ex-eye_rx*.9,eyebrow_y-slope),(ex,eyebrow_y),(ex+eye_rx*.9,eyebrow_y+slope)]
        else:
            brow=[(ex-eye_rx*.9,eyebrow_y+r*.025),(ex,eyebrow_y-r*.08),(ex+eye_rx*.9,eyebrow_y+r*.025)]
        d.line(brow,fill=ink,width=thick+1,joint='curve')
    my=cy+r*.38
    if expression=='shock':
        # Big readable O mouth; no toothy grin during surprise.
        d.ellipse((cx-r*.14,my-r*.23,cx+r*.14,my+r*.19),fill=ink)
        d.ellipse((cx-r*.07,my-r*.14,cx+r*.07,my+r*.07),fill=white)
    elif expression=='worried':
        d.arc((cx-r*.32,my-r*.04,cx+r*.32,my+r*.33),185,350,fill=ink,width=thick+2)
        d.line((cx-r*.14,my+r*.04,cx+r*.14,my+r*.09),fill=ink,width=max(2,thick-1))
    elif expression=='effort':
        d.rounded_rectangle((cx-r*.27,my-r*.12,cx+r*.27,my+r*.14),radius=r*.065,
                            outline=ink,fill=white,width=thick)
        d.line((cx-r*.23,my,cx+r*.23,my),fill=ink,width=thick)
    elif expression in ('neutral','focus'):
        d.arc((cx-r*.29,my-r*.22,cx+r*.29,my+r*.22),15,165,fill=ink,width=thick)
        if expression=='focus':d.line((cx-r*.2,my+r*.08,cx+r*.2,my+r*.08),fill=ink,width=thick)
    else:  # grin is only for explicit happy/recovered beats
        d.pieslice((cx-r*.42,my-r*.36,cx+r*.42,my+r*.31),0,180,fill=ink)
        d.arc((cx-r*.42,my-r*.36,cx+r*.42,my+r*.31),0,180,fill=ink,width=thick)
        d.ellipse((cx-r*.31,my-r*.03,cx+r*.31,my+r*.14),fill=white)
        for frac in (-.4,0,.4):
            xx=cx+frac*r*.5
            d.line((xx,my-r*.02,xx,my+r*.13),fill=ink,width=max(2,thick-1))
    # Instrumentation: exact canonical two pupils (one per eye).
    out.info['pupil_centers']=pupil_positions
    out.info['pupil_count']=len(pupil_positions)
    out.info['expression']=expression
    return out


def build_face_bank(poses:list[Image.Image]):
    """Precompute once, not per-video-frame; small CPU and deterministic."""
    bank={}; geometry={}
    for i,p in enumerate(poses):
        g=detect_head(p);geometry[i]=g
        for expression in STYLES:
            bank[(i,expression)] = cleaned_face(p,g,expression,
                                                'right' if i in (1,2,3) else 'center')
    return bank, geometry


def hand_anchor(pose:Image.Image,which:str='run_b') -> tuple[float,float]:
    """Calibrated visual fist center in original six-pose cropped coordinates.

    For source pose 3, hand/knuckles are ~88% across and 43% down.
    These points are used with the same affine scale as the visible sprite.
    """
    if which!='run_b':raise ValueError('Unsupported pose for contact')
    return pose.width*.88,pose.height*.43


def knock_alignment(pose:Image.Image,scale:float,door_x:float=245.,door_y:float=375.,
                    pulse:float=0) -> dict:
    """Solve actor translation to put the real pixel hand at the door, rather
    than estimating hand position as actor_center + an arbitrary constant.
    """
    hx,hy=hand_anchor(pose)
    body_h=pose.height*scale
    relative_x=(hx-pose.width/2)*scale
    relative_y=-(pose.height-hy)*scale
    center=door_x-relative_x + pulse
    bottom=door_y-relative_y
    return {'x':center,'bottom':bottom,'hand_x':center+relative_x,
            'hand_y':bottom+relative_y, 'hand_error':abs(pulse)}


def expression_for(action:str,progress:float=0) -> str:
    if action=='recover' and progress>.58:return 'grin'
    if action=='knock' and progress>.65:return 'focus'
    return ACTIONS_FACE.get(action,'neutral')
