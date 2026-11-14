"""Project a generated Blender skeleton onto the shared Cairo stage."""
import math
import paint


class MotionLayer:
    def __init__(self, clip, start):
        self.frames = clip["frames"]
        self.rate = clip["fps"]
        self.start = start
        first = self.frames[0]
        self.origin = first["pelvis"]
        self.floor = min(first[key][2] for key in ("r_foot", "l_foot", "r_ankle", "l_ankle"))
        self.scale = 112 / max(1, first["neck"][2] - self.floor)

    def draw(self, t, prop, plan, cue, amp, mouth=None):
        index = max(0, min(len(self.frames)-1, round((t-self.start)*self.rate)))
        joints = self.frames[index]
        def point(name):
            x, y, z = joints[name]
            return (186 + self.scale * (.95*(x-self.origin[0]) + .31*(y-self.origin[1])),
                    470 - self.scale * (z-self.floor))
        sides = sorted(("l_", "r_"), key=lambda s: joints[s+"shoulder"][1], reverse=True)
        def arm(side):
            a,b,c = [point(side+k) for k in ("shoulder","elbow","wrist")]
            paint.limb(a,b,5.8,4.3,"#d27565")
            paint.limb(b,c,4.4,3,"#edb695")
            paint.oval(*c,4.3,3.6,"#f0c4a0")
        for s in sides:
            a,b,c,d = [point(s+k) for k in ("hip","knee","ankle","foot")]
            paint.limb(a,b,8,6,"#43485f")
            paint.limb(b,c,6,4,"#555c71")
            paint.limb(c,d,4,4.6,"#413849")
        arm(sides[0])
        paint.path([point(n) for n in ("l_shoulder","r_shoulder","r_hip","l_hip")],"#df7865")
        paint.path([point("r_shoulder"),point("l_hip")],"#895160",2)
        hx,hy = point("head")
        hy -= 8
        paint.oval(hx,hy,16,19,paint.ink)
        paint.oval(hx,hy,15,18,"#f1c09f")
        paint.oval(hx-2,hy-13,15,7,"#393449")
        blink = max(.08,min(1,abs(t%2.8-1.65)*16))
        for dx in (-5,6):
            paint.oval(hx+dx,hy,3.4,3.7*blink,"#fff3df")
            paint.oval(hx+dx+math.copysign(1,prop[0]-hx),hy,1.6,2.2*blink,paint.ink)
        paint.oval(hx+1,hy+9,*(mouth or (3+amp,1+3*amp)),"#844c57")
        arm(sides[1])
