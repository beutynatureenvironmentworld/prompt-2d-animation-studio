"""Canonical face cut from user's six-pose sheet, with exact one pupil per eye."""
import sys,math
from pathlib import Path
from PIL import Image,ImageDraw
from acting_v2 import detect_head,cleaned_face

FACES=('sly','focus','effort','shock','worried','grin','neutral')

def crop_original_head(original):
    g=detect_head(original)
    r=g.radius*1.19
    # Preserve the real original exterior head contour with safe transparent cut.
    bank={}
    for state in FACES:
        use='neutral' if state in ('sly','grin') else state
        face=cleaned_face(original,g,use,'right' if state not in ('shock','worried') else 'center')
        ink=ImageDraw.Draw(face)
        cx,cy=g.cx,g.cy
        rr=g.radius*(1.14 if g.radius<87 else 1.075)
        # Keep the EXACT original author's broad toothy grin for normal/sly beats.
        # Restore only the lower face art from the original reference; keep the
        # upper face re-rendered so every eye has precisely one controlled pupil.
        if state in ('sly','grin'):
            restore=Image.new('L',original.size,0)
            rd=ImageDraw.Draw(restore)
            rr0=rr*.97
            rd.ellipse((cx-rr0,cy-rr0,cx+rr0,cy+rr0),fill=255)
            # Mask the upper eye area. The authored teeth stay literally original.
            block=Image.new('L',original.size,0)
            bd=ImageDraw.Draw(block)
            bd.rectangle((0,cy+rr*.10,original.width,original.height),fill=255)
            import PIL.ImageChops
            restore=PIL.ImageChops.multiply(restore,block)
            face.paste(original,(0,0),restore)
            ink=ImageDraw.Draw(face)
            if state=='sly':
                ink.line((cx-rr*.67,cy-rr*.54,cx-rr*.31,cy-rr*.62),fill='black',width=4)
        left=int(round(cx-r));top=int(round(cy-r));right=int(round(cx+r));bottom=int(round(cy+r))
        box=face.crop((left,top,right,bottom))
        mask=Image.new('L',box.size,0);m=ImageDraw.Draw(mask)
        # The circle mask includes the outer black contour and excludes existing torso.
        mid=box.width/2;rr0=rr+4
        m.ellipse((mid-rr0,mid-rr0,mid+rr0,mid+rr0),fill=255)
        box.putalpha(mask)
        bank[state]=box
    return bank,{'center':(g.cx,g.cy),'radius_source':g.radius,'one_pupil_per_eye':True,
                 'source_dimensions':original.size}