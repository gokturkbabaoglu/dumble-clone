"""Perfboard (dot-pad pertinaks) layout for LM386 Dumble-style amp.
Component-side view. Copper-side solder trails drawn as lines.
Run: python3 layout.py  -> checks + writes layout.svg
"""
import math, sys
from collections import defaultdict

W, H = 31, 14  # columns x rows

# ---------- components ----------
# pads: (x, y, net, pinlabel)
# body: ('circle', cx, cy, r_pitch) | ('rect', cx, cy, w, h)   (pitch units, 1 pitch = 2.54 mm)
P = 2.54
comps = []
def comp(ref, val, pads, body, kind):
    comps.append(dict(ref=ref, val=val, pads=pads, body=body, kind=kind))

def r_stand(ref, val, a, b, na, nb, body_on='a'):
    bx, by = a if body_on == 'a' else b
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('circle', bx, by, 1.2 / P), 'r_stand')

def r_flat(ref, val, a, b, na, nb):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    horiz = a[1] == b[1]
    w, h = (6.3 / P, 2.4 / P) if horiz else (2.4 / P, 6.3 / P)
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('rect', cx, cy, w, h), 'r_flat')

def ecap(ref, val, plus, minus, np_, nm, dia_mm):
    cx, cy = (plus[0] + minus[0]) / 2, (plus[1] + minus[1]) / 2
    comp(ref, val, [(plus[0], plus[1], np_, '+'), (minus[0], minus[1], nm, '−')], ('circle', cx, cy, dia_mm / 2 / P), 'ecap')

def film(ref, val, a, b, na, nb, thick_mm=3.5):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    horiz = a[1] == b[1]
    L = 7.2 / P; t = thick_mm / P
    w, h = (L, t) if horiz else (t, L)
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('rect', cx, cy, w, h), 'film')

def ceram(ref, val, a, b, na, nb):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    horiz = a[1] == b[1]
    w, h = (5 / P, 2.5 / P) if horiz else (2.5 / P, 5 / P)
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('rect', cx, cy, w, h), 'ceram')

# ---------- placement ----------
SH = 7  # power-amp section shift (columns)
# Preamp supply
r_flat('Rf', '1k', (8, 1), (12, 1), 'VPRE', '+12V')
ecap('C6', '100µ', (3, 2), (3, 4), 'VPRE', 'GND', 10)
r_stand('Rd', '2k2', (7, 2), (7, 3), 'VPRE', 'DRAIN')
comp('Q1', 'BF245B', [(5, 8, 'GATE', 'G'), (6, 8, 'SRC', 'S'), (7, 8, 'DRAIN', 'D')], ('rect', 6, 8.15, 4.8 / P, 3.8 / P), 'to92')
r_flat('Rg', '1M', (4, 8), (4, 12), 'GATE', 'GND')
r_stand('Rs', '1k', (6, 10), (6, 11), 'SRC', 'GND')
# Bright/Dark: C8 source->Y ; Y->GND via Rb||C9 ; S2 shorts Y to GND (Dark)
ecap('C8', '10µ', (7, 10), (8, 10), 'SRC', 'Y', 5)
r_stand('Rb', '560', (9, 11), (9, 12), 'Y', 'GND')
ceram('C9', '104', (11, 11), (11, 12), 'Y', 'GND')
film('C7', '100n', (8, 6), (10, 6), 'DRAIN', 'A')
# Shape (bridged-T): A -CT1- M -CT2- B ; RT A-B ; RM M->GND
film('CT1', '47n', (12, 6), (14, 6), 'A', 'M', 3.0)
film('CT2', '47n', (15, 6), (17, 6), 'M', 'B', 3.0)
r_flat('RT', '10k', (12, 4), (17, 4), 'A', 'B')
r_stand('RM', '2k2', (14, 8), (14, 9), 'M', 'GND')
# LM386, notch left. top row (y=4): 8 7 6 5 ; bottom row (y=7): 1 2 3 4
ux, uyt, uyb = 14 + SH, 4, 7
comp('U1', 'LM386', [
    (ux, uyb, 'G1', '1'), (ux + 1, uyb, 'GND', '2'), (ux + 2, uyb, 'IN3', '3'), (ux + 3, uyb, 'GND', '4'),
    (ux + 3, uyt, 'OUT', '5'), (ux + 2, uyt, '+12V', '6'), (ux + 1, uyt, 'P7', '7'), (ux, uyt, 'G8', '8')],
    ('rect', ux + 1.5, (uyt + uyb) / 2, 9.8 / P, 6.4 / P), 'dip8')
film('C3', '100n', (14+SH, 8), (14+SH, 10), 'G1', 'GA')
film('C4', '100n', (12+SH, 8), (12+SH, 10), 'G1', 'GA')
r_stand('R1', '10R', (19+SH, 5), (19+SH, 4), 'ZOB', 'OUT', body_on='a')
film('C5', '47n', (19+SH, 6), (19+SH, 8), 'ZOB', 'GND', 3.0)
ecap('C2', '220µ', (22+SH, 5), (22+SH, 7), 'OUT', 'SPK', 8)
ecap('C1', '220µ', (22+SH, 2), (24+SH, 2), '+12V', 'GND', 8)
# pin 7 bypass and pin 6 HF decoupling (rev 4)
ecap('C11', '10µ', (22, 2), (24, 2), 'P7', 'GND', 5)
film('C12', '100n', (26, 1), (26, 3), '+12V', 'GND')
r_stand('R2', '1k', (20+SH, 10), (20+SH, 11), 'SPK', 'HPL')
r_stand('R3', '1k', (22+SH, 10), (22+SH, 11), 'SPK', 'HPR')

wires = [
    (3, 8, 'GATE', 'GİRİŞ uç', 'J1'), (1, 9, 'GND', 'GİRİŞ gövde', 'J1'),
    (10, 10, 'Y', 'S2', 'S2'), (10, 12, 'GND', 'S2 GND', 'S2'),
    (11, 5, 'A', 'SHAPE 3', 'VOL'), (18, 6, 'B', 'SHAPE 1', 'VOL'),
    (16+SH, 8, 'IN3', 'VOL 2', 'VOL'), (16+SH, 10, 'GND', 'VOL 1', 'VOL'),
    (13+SH, 4, 'G8', 'GAIN 2', 'GAIN'), (13+SH, 11, 'GA', 'GAIN 3', 'GAIN'),
    (21+SH, 1, '+12V', '+12V (S1)', 'PWR'), (24+SH, 5, 'GND', 'GND (DC jak)', 'PWR'),
    (21+SH, 8, 'SPK', 'S3 orta', 'SPK'), (24+SH, 9, 'GND', 'HOP −', 'SPK'),
    (20+SH, 12, 'HPL', 'KUL L', 'HP'), (22+SH, 12, 'HPR', 'KUL R', 'HP'), (24+SH, 12, 'GND', 'KUL gövde', 'HP'),
]

def hline(y, x0, x1): return [(x, y) for x in range(min(x0, x1), max(x0, x1) + 1)]
def vline(x, y0, y1): return [(x, y) for y in range(min(y0, y1), max(y0, y1) + 1)]
def sh(pts): return [(x + SH, y) for x, y in pts]
traces = [
    ('GND', hline(14, 1, 24+SH)), ('GND', vline(1, 4, 14)), ('GND', vline(24+SH, 2, 14)),
    ('+12V', hline(1, 12, 22+SH)), ('+12V', vline(22+SH, 1, 2)),
    ('VPRE', hline(1, 2, 8)), ('VPRE', vline(3, 1, 2)), ('VPRE', vline(7, 1, 2)),
    ('GND', [(3, 4), (2, 4), (1, 4)]),
    ('DRAIN', vline(7, 3, 8)), ('DRAIN', [(7, 6), (8, 6)]),
    ('GATE', hline(8, 3, 5)),
    ('GND', [(4, 12), (3, 12), (2, 12), (1, 12)]),
    ('SRC', vline(6, 8, 10)), ('SRC', [(6, 10), (7, 10)]),
    ('GND', vline(6, 11, 14)),
    ('Y', hline(10, 8, 11)), ('Y', vline(9, 10, 11)), ('Y', vline(11, 10, 11)),
    ('GND', vline(9, 12, 14)), ('GND', vline(11, 12, 14)), ('GND', vline(10, 12, 14)),
    ('A', hline(6, 10, 12)), ('A', vline(11, 5, 6)), ('A', vline(12, 4, 6)),
    ('M', [(14, 6), (15, 6)]), ('M', vline(14, 6, 8)),
    ('B', vline(17, 4, 6)), ('B', [(17, 6), (18, 6)]),
    ('GND', vline(14, 9, 14)),
    ('P7', vline(22, 2, 4)), ('GND', [(24, 2), (25, 2), (25, 3)]), ('GND', hline(3, 25, 31)),
    ('+12V', sh(vline(16, 1, 4))),
    ('GND', sh(vline(15, 7, 14))), ('GND', sh(vline(17, 7, 14))),
    ('IN3', sh(vline(16, 7, 8))), ('GND', sh([(15, 10), (16, 10)])),
    ('G1', sh(vline(14, 7, 8))), ('G1', sh(hline(8, 12, 14))), ('GA', sh(hline(10, 12, 14))), ('GA', sh(vline(13, 10, 11))),
    ('G8', sh([(14, 4), (13, 4)])),
    ('OUT', sh([(17, 4), (18, 4), (19, 4), (20, 4), (21, 4), (22, 4), (22, 5)])),
    ('ZOB', sh(vline(19, 5, 6))), ('GND', sh([(19, 8), (18, 8), (17, 8)])),
    ('SPK', sh(vline(22, 7, 10))), ('SPK', sh([(22, 8), (21, 8)])), ('SPK', sh([(22, 9), (21, 9), (20, 9), (20, 10)])),
    ('HPL', sh(vline(20, 11, 12))), ('HPR', sh(vline(22, 11, 12))),
]

# ---------- checks ----------
def check():
    errs = []
    used = {}
    pad_net = {}
    for c in comps:
        for (x, y, n, _) in c['pads']:
            if not (1 <= x <= W and 1 <= y <= H): errs.append(f'{c["ref"]} pad off board {x,y}')
            if (x, y) in used: errs.append(f'hole {x,y} used by {used[(x,y)]} and {c["ref"]}')
            used[(x, y)] = c['ref']
            pad_net[(x, y)] = n
    for (x, y, n, lab, g) in wires:
        if (x, y) in used: errs.append(f'wire {lab} hole {x,y} already used by {used[(x,y)]}')
        used[(x, y)] = 'wire:' + lab
        pad_net[(x, y)] = n
    # union find over traces
    parent = {}
    def f(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def u(a, b): parent[f(a)] = f(b)
    trace_net = {}
    for net, pts in traces:
        for i, p in enumerate(pts):
            if not (1 <= p[0] <= W and 1 <= p[1] <= H): errs.append(f'trace off board {p}')
            if p in trace_net and trace_net[p] != net: errs.append(f'trace conflict at {p}: {trace_net[p]} vs {net}')
            trace_net[p] = net
            if p in pad_net and pad_net[p] != net: errs.append(f'trace {net} hits pad of net {pad_net[p]} at {p}')
            if i:
                q = pts[i - 1]
                if abs(p[0] - q[0]) + abs(p[1] - q[1]) != 1: errs.append(f'non-adjacent trace step {q}->{p}')
                u(p, q)
            else:
                f(p)
    # under-body trace pads are fine; but trace through a hole that is under a component body and has a lead? handled above
    groups = defaultdict(set)
    for p, n in pad_net.items():
        groups[n].add(f(p))
    for n, g in groups.items():
        if len(g) > 1: errs.append(f'net {n} split into {len(g)} islands')
    # each trace island single net
    isl = defaultdict(set)
    for p, n in list(pad_net.items()) + list(trace_net.items()):
        isl[f(p)].add(n)
    for k, s in isl.items():
        if len(s) > 1: errs.append(f'island mixes nets {s}')
    # body overlap (approx)
    def bbox(b):
        if b[0] == 'circle': return ('c', b[1], b[2], b[3])
        return ('r', b[1], b[2], b[3], b[4])
    def overlap(a, b):
        if a[0] == 'c' and b[0] == 'c':
            return math.hypot(a[1] - b[1], a[2] - b[2]) - (a[3] + b[3])
        def rr(z):
            if z[0] == 'c': return (z[1] - z[3], z[2] - z[3], z[1] + z[3], z[2] + z[3])
            return (z[1] - z[3] / 2, z[2] - z[4] / 2, z[1] + z[3] / 2, z[2] + z[4] / 2)
        A, B = rr(a), rr(b)
        dx = max(B[0] - A[2], A[0] - B[2]); dy = max(B[1] - A[3], A[1] - B[3])
        if dx < 0 and dy < 0: return max(dx, dy)
        return max(dx, dy)
    warns = []
    for i in range(len(comps)):
        for j in range(i + 1, len(comps)):
            o = overlap(bbox(comps[i]['body']), bbox(comps[j]['body']))
            if o < -0.12: warns.append(f'body overlap {comps[i]["ref"]}-{comps[j]["ref"]}: {o:.2f} pitch')
    # wire pad covered by a body?
    for (x, y, n, lab, g) in wires:
        for c in comps:
            b = c['body']
            if b[0] == 'circle' and c['kind'] == 'ecap' and math.hypot(x - b[1], y - b[2]) < b[3] - 0.1:
                warns.append(f'wire pad {lab} under body of {c["ref"]}')
    # adjacency of different-net used pads (info)
    adj = []
    for (x, y), n in pad_net.items():
        for dx, dy in ((1, 0), (0, 1)):
            q = (x + dx, y + dy)
            m = pad_net.get(q) or trace_net.get(q)
            if m and m != n and not (q in trace_net and trace_net[q] == n):
                adj.append(f'{(x,y)}{n} ~ {q}{m}')
    return errs, warns, adj, trace_net, pad_net

if __name__ == '__main__':
    e, w, a, _, _ = check()
    print('ERRORS:', *e, sep='\n  ') if e else print('no errors')
    print('WARN:', *w, sep='\n  ') if w else print('no body warnings')
    print('adjacent diff-net pads:', len(a))
    for s in a: print('  ', s)
