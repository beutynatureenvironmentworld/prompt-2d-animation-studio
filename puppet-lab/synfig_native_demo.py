"""Create original Synfig-native 2D animation with actual animated circle layers.
No imported still-image animation. Head, eyes, body, pupils and nose move as
native Synfig vector primitives on timed animated vector waypoints.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
out=Path("puppet-lab/output/synfig")
out.mkdir(parents=True,exist_ok=True)
canvas=ET.Element("canvas",{"version":"0.1","width":"480","height":"640",
"xres":"2834.645752","yres":"2834.645752","view-box":"-3.0 4.0 3.0 -4.0",
"antialias":"1","fps":"24.000","begin-time":"0f","end-time":"143f",
"bgcolor":"0.925 0.914 0.850 1.0"})
ET.SubElement(canvas,"name").text="Original funny bouncing 2D puppet — Synfig animated vector test"
def param(layer,name):return ET.SubElement(layer,"param",{"name":name})
def real(p,n):ET.SubElement(p,"real",{"value":str(n)})
def vec(p,x,y):
    v=ET.SubElement(p,"vector");ET.SubElement(v,"x").text=str(x);ET.SubElement(v,"y").text=str(y)
def circle(name,radius,color,track):
    layer=ET.SubElement(canvas,"layer",{"type":"circle","active":"true","version":"0.1","desc":name})
    real(param(layer,"z_depth"),0)
    real(param(layer,"amount"),1)
    ET.SubElement(param(layer,"blend_method"),"integer",{"value":"0"})
    c=ET.SubElement(param(layer,"color"),"color")
    for k,n in zip(("r","g","b","a"),color):ET.SubElement(c,k).text=str(n)
    real(param(layer,"radius"),radius)
    real(param(layer,"feather"),0)
    p=param(layer,"pos")
    a=ET.SubElement(p,"animated",{"type":"vector"})
    for frame,x,y in track:
        wp=ET.SubElement(a,"waypoint",{"time":f"{frame}f","before":"clamped","after":"clamped"})
        vec(wp,x,y)
    ET.SubElement(param(layer,"invert"),"bool",{"value":"false"})
    ET.SubElement(param(layer,"falloff"),"integer",{"value":"2"})
def track(x,y,dx=0,dy=0):
    return [(0,x-1.1,y),(24,x-.6,y+.13),(48,x+.2,y+.08),
            (66,x+.65,y+dy),(80,x+.5,y+dy-.15),
            (104,x-.5,y+.3),(128,x+dx,y-.25),(143,x,y)]
# Background and character are native vector layers, not PNGs.
# Synfig layers are composited in reverse insertion order: face above body.
circle("Golden torso",.87,(.89,.69,.28,1),track(0,-1.05))
circle("Cream face",.99,(1,.92,.77,1),track(0,.52,dy=.6))
circle("Black hair cap",.89,(.12,.12,.16,1),track(0,1.03,dy=.6))
circle("Left eye white",.22,(1,1,1,1),track(-.39,.53,dy=.6))
circle("Right eye white",.22,(1,1,1,1),track(.39,.53,dy=.6))
circle("Left pupil",.085,(.11,.11,.14,1),track(-.34,.52,dy=.6))
circle("Right pupil",.085,(.11,.11,.14,1),track(.44,.52,dy=.6))
circle("Comic open mouth",.17,(.25,.12,.17,1),track(.03,.02,dy=.6))
circle("Funny round nose",.12,(.95,.65,.52,1),track(0,.33,dy=.6))
# Bouncing prop: its own separate motion track with independent timing.
circle("Escaping cookie",.24,(.52,.28,.11,1),[(0,2.3,-2),(24,1.6,-1.1),(48,.9,-.7),(66,.4,1.0),
(80,-.8,1.6),(104,-1.7,-.4),(128,1.4,-1.5),(143,2.3,-2)])
file=out/"original-native-synfig-animated-puppet.sif"
ET.indent(canvas)
ET.ElementTree(canvas).write(file,encoding="utf-8",xml_declaration=True)
print("NATIVE_SYNFIG_SIF_GENERATED",file)
