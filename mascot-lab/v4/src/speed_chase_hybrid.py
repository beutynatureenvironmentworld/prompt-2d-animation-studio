"""Hybrid 2D cartoon motion inspired by verified speed-chase reference.

Use a staggered, pose-driven running foot cycle with world-space stance and
lateral lane constraints, never intersecting knees. Non-running actions retain
arm IK but use calm non-crossing FK legs. No elbow/knee ring is drawn.
"""
import math
from ik import clamp,smooth,lerp

CONTACT_PHASES=("contact","down","passing","up")

def chase_foot(t, movement_x, side, start=.9, end=2.7, ground_y=833, cycle=.40, stance=.56, lane=55):
    """World-locked foot contact and lifted inbetweens; separated screen lanes.

    Returns (world-foot target x,y), planted flag, named four-stage run pose.
    Side: -1 far/left, +1 near/right. Foot positions deliberately live on
    opposite sides of pelvis center to avoid the crossing-X look.
    """
    if side not in (-1,1):raise ValueError('Side must be -1 or 1')
    if not start <= end:raise ValueError('Invalid action interval')
    if t < start:return ((movement_x(start)+side*lane,ground_y),True,'contact')
    if t >= end:return ((movement_x(end)+side*lane,ground_y),True,'contact')
    offset=0 if side==-1 else .5
    cyc=(t-start)/cycle+offset
    integer=math.floor(cyc)
    u=cyc-integer
    ta=clamp(start+(integer-offset)*cycle,start,end)
    tb=clamp(start+(integer+1-offset)*cycle,start,end)
    ax=movement_x(ta)+side*lane
    bx=movement_x(tb)+side*lane
    if u<stance:
        return ((ax,ground_y),True,'contact' if u <stance*.52 else 'down')
    v=(u-stance)/(1-stance)
    # Explicit inbetween stage: far toe swings forward then reaches contact.
    z=smooth(v)
    lift=43*math.sin(math.pi*z)**.86
    return ((lerp(ax,bx,z),ground_y-lift),False,'passing' if v<.5 else 'up')


def leg_control(hip,foot,side,phase='contact'):
    """Outward-bending knee with no x crossover; stylized rubber-hose FK.

    Called in original 430x500 actor-local coordinates. Return knee only;
    hand/arm IK remains V3 exactly as before.
    """
    hx,hy=hip;fx,fy=foot
    # Lateral offset keeps the leg silhouette away from the body's center.
    additional=5 if phase in ('passing','up') else 0
    kx=(hx+fx)*.5+side*(14+additional)
    ky=hy+(fy-hy)*(.54 if phase in ('contact','down') else .47)-additional*.5
    return (kx,ky)


def lane_ok(left_hip,left_knee,left_foot,right_hip,right_knee,right_foot,center=215,margin=7):
    # Only x alignment relevant; this deliberately allows readable fore/aft
    # foot movement while preventing the crossed-X silhouette in front view.
    return (left_knee[0]<center-margin and right_knee[0]>center+margin
            and left_foot[0]<center-margin and right_foot[0]>center+margin
            and left_knee[0]<right_knee[0])


def rounded_joint_path(a,b,c,corner=.20,segments=8):
    """Invisible 2-bone joint: continuous rounded path, no elbow circles.

    Preserve V3 endpoint and arm IK, only smooth the visual stroke at joint.
    """
    x0=(lerp(a[0],b[0],1-corner),lerp(a[1],b[1],1-corner))
    x1=(lerp(b[0],c[0],corner),lerp(b[1],c[1],corner))
    points=[tuple(a),x0]
    for k in range(1,segments):
        v=k/segments;inv=1-v
        points.append((inv*inv*x0[0]+2*inv*v*b[0]+v*v*x1[0],
                       inv*inv*x0[1]+2*inv*v*b[1]+v*v*x1[1]))
    points.extend([x1,tuple(c)])
    return points
