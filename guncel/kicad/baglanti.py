"""Kart dosyasındaki yolların bağlantı durumunu raporlar (net başına kopuk parça sayısı)."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sexp import parse, find, first
import gen_pcb as GP, pad_check as PC
from matplotlib.path import Path

def analyze(pcbfile):
    b = parse(open(pcbfile, encoding='utf-8').read())
    pads = [p for f in find(b, 'footprint') for p in GP.pad_world(f)]
    segs = []
    for s in find(b, 'segment'):
        a, e = first(s, 'start'), first(s, 'end'); n = first(s, 'net')
        segs.append(dict(a=(float(a[1]), float(a[2])), b=(float(e[1]), float(e[2])), w=float(first(s, 'width')[1]),
                         layer=first(s, 'layer')[1], net=n[1] if n else None))
    vias = find(b, 'via')
    parent = {}
    def f(x):
        while parent.setdefault(x, x) != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def u(x, y): parent[f(x)] = f(y)
    polys = [Path(PC.outline(p, 48)) for p in pads]
    def on_seg(p, s, tol=0.02):
        (x1, y1), (x2, y2) = s['a'], s['b']; dx, dy = x2 - x1, y2 - y1; L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((p[0] - x1) * dx + (p[1] - y1) * dy) / L))
        return math.hypot(p[0] - x1 - t * dx, p[1] - y1 - t * dy) <= tol
    for i, s in enumerate(segs):
        for end in (s['a'], s['b']):
            for j, p in enumerate(pads):
                if p['net'] == s['net'] and polys[j].contains_point(end, radius=0.01):
                    u(('s', i), ('p', j))
            for k, t in enumerate(segs):
                if k != i and t['net'] == s['net'] and on_seg(end, t):
                    u(('s', i), ('s', k))
    nets = {}
    for j, p in enumerate(pads):
        if p['net']: nets.setdefault(p['net'], []).append(j)
    open_ = {}
    for n, js in nets.items():
        comps = {f(('p', j)) for j in js}
        if len(comps) > 1: open_[n] = len(comps) - 1
    return dict(segs=len(segs), vias=len(vias), layers=sorted({s['layer'] for s in segs}),
                widths=sorted({s['w'] for s in segs}), open=open_, total_open=sum(open_.values()),
                length=sum(math.dist(s['a'], s['b']) for s in segs))

if __name__ == '__main__':
    r = analyze(sys.argv[-1])
    print({k: v for k, v in r.items() if k != 'open'}); print('kopuk:', r['open'])
