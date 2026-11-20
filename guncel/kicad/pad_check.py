"""Kart üzerindeki farklı netli padler arası en küçük bakır boşluğunu ve kenar payını raporlar."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sexp import parse, find, first
import gen_pcb as GP

def outline(p, n=72):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n; c, s_ = math.cos(t), math.sin(t); w, h = p['w'], p['h']
        if p['shape'] in ('rect', 'roundrect'):
            m = max(abs(c) / (w / 2), abs(s_) / (h / 2)); px, py = c / m, s_ / m
        else:
            r = min(w, h) / 2; L = (max(w, h) - min(w, h)) / 2
            if w >= h: px, py = (L if c >= 0 else -L) + r * c, r * s_
            else: px, py = r * c, (L if s_ >= 0 else -L) + r * s_
        dx, dy = GP.rot(px, py, p['ang'])
        pts.append((p['x'] + dx, p['y'] + dy))
    return pts

def check(fps, lim=0.6):
    pads = [p for f in fps for p in GP.pad_world(f)]
    outs = [outline(p) for p in pads]
    bad = []
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            a, b = pads[i], pads[j]
            if a['net'] and a['net'] == b['net']: continue
            if math.hypot(a['x'] - b['x'], a['y'] - b['y']) > (max(a['w'], a['h']) + max(b['w'], b['h'])) / 2 + lim + 0.1: continue
            g = min(math.hypot(p[0] - q[0], p[1] - q[1]) for p in outs[i] for q in outs[j])
            if g < lim: bad.append((round(g, 2), a['ref'] + '.' + a['pad'], b['ref'] + '.' + b['pad']))
    edge = []
    for p, o in zip(pads, outs):
        m = min(min(q[0] - GP.X0, GP.X0 + GP.W - q[0], q[1] - GP.Y0, GP.Y0 + GP.H - q[1]) for q in o)
        if m < 0.5: edge.append((round(m, 2), p['ref'] + '.' + p['pad']))
    return sorted(bad), sorted(edge)

if __name__ == '__main__':
    b = parse(open(os.path.join(HERE, 'amfi_yeni.kicad_pcb'), encoding='utf-8').read())
    bad, edge = check(find(b, 'footprint'))
    print('yakın pad çiftleri:', len(bad)); [print(' ', x) for x in bad]
    print('kenara yakın:', edge)
