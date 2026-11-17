"""Auditable analytic two-bone IK and stance/swing foot trajectory."""
import math

def clamp(x,lo,hi):return max(lo,min(hi,x))
def smooth(x):x=clamp(x,0,1);return x*x*(3-2*x)
def lerp(a,b,z):return a+(b-a)*z

def two_bone_ik(root,target,upper,lower,elbow_sign=1):
    dx=target[0]-root[0];dy=target[1]-root[1]; d=math.hypot(dx,dy)
    constrained=clamp(d,abs(upper-lower)+.01,upper+lower-.01)
    direction=math.atan2(dy,dx) if d>1e-9 else math.pi/2
    c=clamp((upper*upper+constrained*constrained-lower*lower)/(2*upper*constrained),-1,1)
    alpha=math.acos(c)
    elbow=(root[0]+upper*math.cos(direction+elbow_sign*alpha),root[1]+upper*math.sin(direction+elbow_sign*alpha))
    corrected=(root[0]+constrained*math.cos(direction),root[1]+constrained*math.sin(direction))
    return elbow,corrected,abs(d-constrained)

def planted_foot(t,motion_x,side,start,end,ground_y=833,cycle=.42,stance=.58):
    """Foot is world-space stationary for stance phase, lifted during swing.
    side=-1 left, +1 right; analytic phase avoids cumulative error between frames.
    """
    if t<start:return (motion_x(start)+side*23,ground_y),True
    if t>end:return (motion_x(end)+side*23,ground_y),True
    phase_offset=0 if side<0 else .5
    phase=(t-start)/cycle+phase_offset
    k=math.floor(phase);u=phase-k
    anchor_t=start+(k-phase_offset)*cycle
    next_t=anchor_t+cycle
    anchor_x=motion_x(clamp(anchor_t,start,end))+side*23
    next_x=motion_x(clamp(next_t,start,end))+side*23
    if u<stance:return (anchor_x,ground_y),True
    z=smooth((u-stance)/(1-stance))
    return (lerp(anchor_x,next_x,z),ground_y-28*math.sin(math.pi*z)),False
