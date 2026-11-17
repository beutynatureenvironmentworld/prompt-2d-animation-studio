"""Reference-grounded front-view rubber-hose arm acting for Funny Toon Ever V5.

The supplied Anime-Starter-Demo(2).mp4 shows front-facing arms mostly DOWN,
with a deliberate single-hand raised gesture in later frames. It does NOT show
high-speed running. Running uses an authored screen-depth projection: hands
alternate chest-forward/hip-back, never swinging sideways like windmills.

No neural model or joint rings: arm silhouette is a smooth line, with upper
and lower control points invisible. V4 IK still serves contact gestures.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class FrontArmPose:
    shoulder:tuple[float,float]
    elbow:tuple[float,float]
    hand:tuple[float,float]
    swing:float
    depth:str
    kind:str


def front_arm_pose(action:str,side:int,shoulder:tuple[float,float],gait_phase:float,progress:float=0.0)->FrontArmPose:
    """Project a sagittal swing into near-vertical screen-space motion.

    +ve swing: wrist shortened and raised in front of the chest; -ve swing:
    hand extended downward behind hip. Opposite arms have opposite phase.
    For idle/rest, three centers are collinear so no visible elbow kink.
    """
    if side not in (-1,1): raise ValueError('side is -1 or +1')
    sx,sy=shoulder
    if action not in ('sneak','dash','brake','recover'):
        raise ValueError('Only frontal locomotion/resting actions supported')
    phase=math.sin(gait_phase+(math.pi if side==1 else 0.0))
    amplitude=1.0 if action=='dash' else (1.0-min(1.0,max(0.0,progress))) if action=='brake' else 0.0
    swing=phase*amplitude
    # The arm occupies a narrow silhouette outside the white body: no large
    # X-direction run swings. Front stroke can overlap the torso to convey depth.
    # Back stroke remains visible below torso, rather than rotating sideways.
    forward=max(0.0,swing)
    backward=max(0.0,-swing)
    # The forward-pumping wrist comes IN to the chest; the opposite wrist
    # drops near the hip behind the torso. Neither reaches sideways.
    hand_off_x=31.0-18.0*forward+5.0*backward
    hand_x=sx+side*hand_off_x
    hand_y=sy+107.0-60.0*forward+18.0*backward
    # Relaxed arms: collinear vertical rubber-hose. During the forward phase
    # the elbow bends invisibly, bringing the hand naturally toward the chest.
    elbow_x=sx+side*(hand_off_x*0.50+(10.0+5.0*forward)*abs(swing))
    elbow_y=sy+(hand_y-sy)*0.50+12.0*forward
    depth='front' if swing>0.04 else 'behind' if swing<-.04 else 'neutral'
    return FrontArmPose((sx,sy),(elbow_x,elbow_y),(hand_x,hand_y),swing,depth,'front_sagittal_projection')


def is_front_motion(action:str)->bool:
    return action in ('sneak','dash','brake','recover')


def near_arm_side(action:str,gait_phase:float)->int:
    """Dynamic draw-order: the arm swinging forward overlays the torso."""
    if action in ('dash','brake'):
        return -1 if math.sin(gait_phase)>=0 else 1
    return 1
