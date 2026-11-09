import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design2 import *
W, H = int(round(BW/U)), int(round(BH/U))
def rotp(p, r):
    x, y = p
    for _ in range((r//90) % 4): x, y = -y, x
    return x, y
def pins_mm(ref, pl):
    fp = FP[C[ref][0]]; x, y, r = pl[ref]
    return [(x*U + rotp(p, r)[0], y*U + rotp(p, r)[1]) for p in fp['pins']]
def pins_cell(ref, pl):
    return [(int(round(px/U)), int(round(py/U))) for px, py in pins_mm(ref, pl)]
def body_box_mm(ref, pl):
    """bounding box (x0,x1,y0,y1) of body+pads in mm"""
    fp = FP[C[ref][0]]; x, y, r = pl[ref]; ps = pins_mm(ref, pl)
    pr = fp['pad']/2
    xs = [p[0] for p in ps]; ys = [p[1] for p in ps]
    x0, x1, y0, y1 = min(xs)-pr, max(xs)+pr, min(ys)-pr, max(ys)+pr
    b = fp['body']
    if b:
        cx = (min(xs)+max(xs))/2; cy = (min(ys)+max(ys))/2
        if b[0] == 'circ':
            w = h = b[1]
        elif b[0] == 'front':
            # body sits from the front face (anchor y) backwards by depth
            w, d = b[1], b[2]; ax, ay = x*U, y*U
            bx0, bx1, by0, by1 = ax-w/2, ax+w/2, ay-d, ay
            return (min(x0,bx0), max(x1,bx1), min(y0,by0), max(y1,by1))
        elif b[0] == 'pw':
            w, h = b[1], b[2]; ax, ay = x*U, y*U
            hw, hd = HS_KEEPOUT
            bx0, bx1, by0, by1 = ax-max(w,hw)/2, ax+max(w,hw)/2, ay-0.8-hd, ay-0.3
            return (min(x0,bx0), max(x1,bx1), min(y0,by0), max(y1,by1))
        else:
            w, h = b[1], b[2]
            if r % 180 == 90: w, h = h, w
        bx0, bx1, by0, by1 = cx-w/2, cx+w/2, cy-h/2, cy+h/2
        x0, x1, y0, y1 = min(x0,bx0), max(x1,bx1), min(y0,by0), max(y1,by1)
    return (x0, x1, y0, y1)
def court(ref, pl, m=0.45):
    x0,x1,y0,y1 = body_box_mm(ref, pl)
    return ((x0-m)/U, (x1+m)/U, (y0-m)/U, (y1+m)/U)
nets = {}
for ref, (fp, v, ns) in C.items():
    for i, n in enumerate(ns): nets.setdefault(n, []).append((ref, i))
