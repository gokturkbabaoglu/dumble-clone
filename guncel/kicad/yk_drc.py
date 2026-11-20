"""Basit DRC: farklı netli yol-pad ve yol-yol bakır boşluğu, kenar payı."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sexp import parse, find, first
import gen_pcb as GP, pad_check as PC
def sd(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
def ss(a, b, c, d):
    def ccw(p, q, r): return (r[1] - p[1]) * (q[0] - p[0]) - (q[1] - p[1]) * (r[0] - p[0])
    if (ccw(a, b, c) * ccw(a, b, d) < 0) and (ccw(c, d, a) * ccw(c, d, b) < 0): return 0
    return min(sd(a, c, d), sd(b, c, d), sd(c, a, b), sd(d, a, b))
def run(f, C):
    b = parse(open(f, encoding='utf-8').read())
    pads = [p for fp in find(b, 'footprint') for p in GP.pad_world(fp)]
    outs = [PC.outline(p, 48) for p in pads]
    segs = [((float(first(s, 'start')[1]), float(first(s, 'start')[2])), (float(first(s, 'end')[1]), float(first(s, 'end')[2])),
             float(first(s, 'width')[1]), first(s, 'net')[1]) for s in find(b, 'segment')]
    viol = []
    for a, c, w, n in segs:
        for p, o in zip(pads, outs):
            if p['net'] == n: continue
            if sd((p['x'], p['y']), a, c) > math.hypot(p['w'], p['h']) / 2 + w / 2 + C + 0.5: continue
            import padgeom as geom
            g = geom.seg_pad(a, c, p) - w / 2
            if g < C - 0.01: viol.append(('yol-pad', round(g, 3), n, p['ref'] + '.' + p['pad']))
    for i in range(len(segs)):
        a, c, w, n = segs[i]
        for j in range(i + 1, len(segs)):
            a2, c2, w2, n2 = segs[j]
            if n == n2: continue
            if min(a[0], c[0]) - 3 > max(a2[0], c2[0]) or min(a2[0], c2[0]) - 3 > max(a[0], c[0]): continue
            if min(a[1], c[1]) - 3 > max(a2[1], c2[1]) or min(a2[1], c2[1]) - 3 > max(a[1], c[1]): continue
            g = ss(a, c, a2, c2) - w / 2 - w2 / 2
            if g < C - 0.01: viol.append(('yol-yol', round(g, 3), n, n2))
    return viol
if __name__ == '__main__':
    v = run(sys.argv[1], float(sys.argv[2]))
    print('ihlal', len(v)); [print(' ', x) for x in sorted(v, key=lambda x: x[1])[:30]]
