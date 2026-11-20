"""Pad - yol arası tam (örneklemesiz) bakır mesafesi."""
import math
import gen_pcb as GP
from yk_drc import sd, ss

def pad_shape(p):
    """('cap', a, b, r) ya da ('poly', [köşeler])"""
    w, h = p['w'], p['h']
    if p['shape'] in ('rect', 'roundrect'):
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        return ('poly', [(p['x'] + GP.rot(x, y, p['ang'])[0], p['y'] + GP.rot(x, y, p['ang'])[1]) for x, y in pts])
    r = min(w, h) / 2; L = (max(w, h) - min(w, h)) / 2
    ax, ay = (L, 0) if w >= h else (0, L)
    dx, dy = GP.rot(ax, ay, p['ang'])
    return ('cap', (p['x'] - dx, p['y'] - dy), (p['x'] + dx, p['y'] + dy), r)

def inside_poly(pt, poly):
    s = 0
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        s += 1 if (b[0] - a[0]) * (pt[1] - a[1]) - (b[1] - a[1]) * (pt[0] - a[0]) > 0 else -1
    return abs(s) == len(poly)

def seg_pad(a, c, p):
    """segment merkez çizgisinden pad bakırına mesafe (içindeyse 0)"""
    sh = pad_shape(p)
    if sh[0] == 'cap':
        return max(0.0, ss(a, c, sh[1], sh[2]) - sh[3])
    poly = sh[1]
    if inside_poly(a, poly) or inside_poly(c, poly): return 0.0
    return min(ss(a, c, poly[i], poly[(i + 1) % 4]) for i in range(4))
