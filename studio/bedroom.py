"""Hand-authored expressive stick-figure bedroom. Reference-inspired, not AI auto-rigging.

Procedural keyframed face, blankets, limbs, snore Zs, window and props.
Returns a fresh Pillow RGB frame; no source images or network required.
"""
from __future__ import annotations
import math
from PIL import Image, ImageDraw

INK = (22, 22, 39)


def draw_bedroom(time: float, action: str, width: int, height: int) -> Image.Image:
    k = 2
    canvas = Image.new("RGB", (640 * k, 360 * k), "#202742")
    d = ImageDraw.Draw(canvas)
    def p(points):
        return [(round(x*k), round(y*k)) for x, y in points]
    def poly(points, fill, outline=INK, stroke=2):
        d.polygon(p(points), fill=fill)
        if outline:
            d.line(p(points + [points[0]]), fill=outline, width=round(stroke*k), joint="curve")
    def rect(box, fill, outline=INK, stroke=2):
        d.rectangle(tuple(round(q*k) for q in box), fill=fill, outline=outline,
                    width=round(stroke*k) if outline else 1)
    def oval(box, fill, outline=INK, stroke=2):
        d.ellipse(tuple(round(q*k) for q in box), fill=fill, outline=outline,
                  width=round(stroke*k) if outline else 1)
    def line(points, color=INK, stroke=3):
        d.line(p(points), fill=color, width=round(stroke*k), joint="curve")
    def arc(box, start, end, color=INK, stroke=2):
        d.arc(tuple(round(q*k) for q in box), start, end, fill=color, width=round(stroke*k))
    for y in range(360):
        frac = y / 360
        d.line([(0, y*k), (640*k, y*k)],
               fill=(int(34+frac*26), int(42+frac*22), int(77+frac*27)), width=k)
    oval((75, 2, 548, 475), (73, 81, 126), None)
    poly([(0,275), (640,276), (640,360), (0,360)], (53,54,88), None)
    line([(108,0), (110,274)], (24,28,48), 2)
    line([(533,0), (531,277)], (24,28,48), 2)
    rect((538,36,645,211), (25,31,55), INK, 3)
    rect((544,43,638,204), (89,122,171), None)
    oval((603,55,650,103), (218,232,247), None)
    for x,y in ((558,62), (590,96), (576,134), (616,150), (566,185)):
        oval((x,y,x+2,y+2), (241,240,214), None)
    line([(588,43), (588,204)], INK, 5)
    line([(544,124), (638,124)], INK, 5)
    line([(530,208), (647,208)], INK, 5)
    poly([(530,208), (648,208), (652,219), (526,218)], (88,91,137), INK, 2)

    # Family portrait: independently authored doodle rig.
    poly([(274,53), (363,51), (368,115), (276,119)], (27,29,53), INK, 3)
    poly([(283,59), (357,57), (361,106), (283,111)], (143,153,187), INK, 2)
    line([(310,52), (320,39), (329,51)], INK, 2)
    for cx, cy, radius in ((302,79,8), (327,73,9), (347,78,7), (319,94,6)):
        oval((cx-radius,cy-radius,cx+radius,cy+radius), None, INK, 2)
        oval((cx-3,cy-1,cx-2,cy), INK, None)
        oval((cx+2,cy-1,cx+3,cy), INK, None)
        arc((cx-4,cy-2,cx+5,cy+5), 15, 165, INK, 1)
        line([(cx,cy+radius), (cx,cy+radius+12)], INK, 2)

    # Beds and shadows are separate editable objects/layers.
    poly([(36,185), (235,173), (244,308), (31,321)], (20,22,49), None)
    poly([(365,176), (574,174), (604,323), (353,312)], (25,27,56), None)
    poly([(56,160), (86,151), (239,161), (250,265), (57,269)], (107,99,139), INK, 3)
    poly([(362,165), (391,154), (552,158), (565,270), (364,272)], (109,107,146), INK, 3)
    for b in ((55,154,70,277), (232,156,245,274), (359,158,373,277), (551,152,564,280)):
        rect(b, (107,96,136), INK, 3)
    poly([(67,224), (242,218), (246,282), (57,292)], (161,170,203), INK, 3)
    poly([(373,221), (557,221), (578,284), (365,288)], (161,171,204), INK, 3)
    poly([(114,185), (206,179), (218,218), (123,230)], (180,188,220), INK, 2)
    poly([(383,191), (483,183), (515,225), (396,237)], (178,190,218), INK, 2)
    arc((121,187,188,227), 100, 240, (125,135,174), 2)
    arc((392,191,491,235), 96, 190, (125,135,174), 2)

    snoring = action in ("snore", "stand", "look")
    reacting = action in ("annoyed", "wake", "react")
    sleeping = math.sin(time*2.5)
    blanket_lift = 1.9*sleeping
    nx = 158 + (2*math.sin(time*3.2) if reacting else 0)
    ny = 184 + 1.5*math.sin(time*1.8)
    line([(nx-3,ny+21), (nx-14,246), (nx-11,277), (nx+11,282)], INK, 5)
    line([(nx+2,ny+27), (nx+20,250), (nx+25,271), (nx+40,274)], INK, 5)
    if reacting:
        hand_y=156+12*math.sin(time*7)
        line([(nx+15,ny+25), (nx+34,ny+9), (nx+45,hand_y)], INK, 5)
        oval((nx+40,hand_y-4,nx+49,hand_y+5), (170,177,207), INK, 2)
    else:
        line([(nx+15,ny+18), (nx+34,ny-2), (nx+32,ny-22)], INK, 5)
    line([(nx-15,ny+22), (nx-31,ny+8), (nx-26,ny-17)], INK, 5)
    poly([(nx-24,ny-16), (nx-23,ny-48), (nx+8,ny-68), (nx+21,ny-20)],
         (121,130,176), INK, 3)
    oval((nx-29,ny-52,nx+18,ny-20), (132,140,181), INK, 2)
    line([(nx-26,ny-43), (nx+8,ny-57)], (74,81,131), 2)
    oval((nx-29,ny-53,nx-18,ny-41), (166,172,208), INK, 2)
    oval((nx-27,ny-28,nx+25,ny+24), (211,219,233), INK, 3)
    line([(nx-17,ny-4), (nx-2,ny-7)], INK, 3)
    line([(nx+7,ny-8), (nx+20,ny-4)], INK, 3)
    if reacting:
        oval((nx-15,ny-1,nx-5,ny+3), (34,39,59), None)
        oval((nx+10,ny-1,nx+19,ny+3), (34,39,59), None)
        arc((nx-12,ny+6,nx+15,ny+18), 190, 345, INK, 3)
    else:
        line([(nx-16,ny+1), (nx-4,ny+3)], INK, 3)
        line([(nx+8,ny+3), (nx+20,ny+1)], INK, 3)
        arc((nx-13,ny+7,nx+13,ny+17), 185, 344, INK, 2)

    sx = 456 + 2*math.sin(time)
    sy = 201 + 2.5*sleeping
    line([(sx+5,sy+27), (sx+24,252), (sx+43,282)], INK, 5)
    line([(sx-5,sy+29), (sx-31,245), (sx-35,270)], INK, 5)
    line([(sx+32,246), (sx+63,242), (sx+87,263)], INK, 5)
    oval((sx-27,sy-27,sx+26,sy+27), (220,227,240), INK, 3)
    arc((sx-20,sy-12,sx-4,sy+1), 0, 165, INK, 3)
    arc((sx+6,sy-12,sx+21,sy+1), 0, 165, INK, 3)
    mouth = 5.5 + 3.6*((1+math.sin(time*2.7))*.5) if snoring else 3
    oval((sx-12,sy+4,sx+12,sy+4+mouth*2), (20,22,32), INK, 2)
    oval((sx-3,sy+7+mouth,sx+6,sy+7+mouth*1.7), (183,99,135), None)
    if reacting:
        line([(sx-17,sy-7), (sx-5,sy-9)], INK, 2)

    poly([(51,243), (126,230), (181,234), (249,267), (249,319), (51,327)],
         (130,140,184), INK, 3)
    poly([(366,240+blanket_lift), (416,230+blanket_lift),
          (479,233+blanket_lift), (576,270), (590,325), (363,327)],
         (136,149,194), INK, 3)
    for x, yy in ((108,249),(178,254),(404,262),(496,257)):
        arc((x-22,yy-7,x+27,yy+14), 210, 337, (95,106,154), 2)
    poly([(42,291),(241,297),(244,333),(43,334)], (95,89,128), INK, 3)
    poly([(365,296),(589,299),(594,339),(364,336)], (91,88,128), INK, 3)
    for b in ((43,309,51,344),(239,312,246,344),(363,319,371,354),(585,322,594,354)):
        rect(b, (89,85,121), INK, 2)

    poly([(282,214),(343,213),(352,229),(274,232)], (120,113,151), INK, 3)
    rect((284,230,344,291), (99,91,126), INK, 3)
    rect((293,238,335,259), (130,122,157), INK, 2)
    rect((292,264,336,287), (111,106,141), INK, 2)
    oval((310,246,316,252), (55,54,81), INK, 1)

    if snoring:
        for i in range(3):
            phase = ((time*.26) + i/3) % 1
            zx = 504 + phase*51 + i*6
            zy = 176 - phase*83 + 2*math.sin(time*1.7+i)
            size = 9+i*5
            line([(zx,zy),(zx+size,zy),(zx,zy+size),(zx+size,zy+size)],
                 (20,19,40), 2+i//2)
        arc((530,147,578,189), 198, 343, (153,165,207), 2)
    return canvas.resize((width,height), Image.Resampling.LANCZOS)
