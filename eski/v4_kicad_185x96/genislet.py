"""Freerouting'in pin yanlarında daralttığı (neckdown) yolları 1.5 mm'ye genişletir.
Kural: genişletilen yol, başka netlerin pad/yollarına >= ARALIK uzak kalmalı. Kalamayanlar raporlanır.
Kullanım: python kicad/genislet.py girdi.kicad_pcb cikti.kicad_pcb [en_az=1.5] [aralik=0.5]
Not: GND dolgusu bu betikten sonra KiCad'de yeniden doldurulmalı (B tuşu / ZONE_FILLER).
"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analiz as A
import gorsel as G

def seg_seg(a, b, c, d):
    def ps(p, s0, s1):
        vx, vy = s1[0] - s0[0], s1[1] - s0[1]; L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((p[0] - s0[0]) * vx + (p[1] - s0[1]) * vy) / L))
        return math.dist(p, (s0[0] + t * vx, s0[1] + t * vy))
    def o(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0: return 0.0
    return min(ps(a, c, d), ps(b, c, d), ps(c, a, b), ps(d, a, b))

def poly_seg(P, a, b):
    """poligon kenarı ile parça arası en kısa mesafe (içerideyse 0)."""
    if G_inside(a, P) or G_inside(b, P): return 0.0
    return min(seg_seg(P[i - 1], P[i], a, b) for i in range(len(P)))
def G_inside(pt, P):
    x, y = pt; c = False
    for i in range(len(P)):
        (x1, y1), (x2, y2) = P[i], P[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def main(src, dst, wmin=1.5, gap=0.5):
    txt = open(src, encoding='utf-8').read()
    K = G.oku(src)
    B = A.sexp(txt)
    nets = {}
    pads = []
    for fp in A.find(B, 'footprint'):
        at = A.one(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0
        for p in A.find(fp, 'pad'):
            pa = A.one(p, 'at'); px, py = float(pa[1]), float(pa[2]); pr = float(pa[3]) if len(pa) > 3 else 0
            dx, dy = G.rot(px, py, fr); sz = A.one(p, 'size'); n = A.one(p, 'net')
            nn = n[-1] if n else ''
            if p[2] == 'np_thru_hole':
                d = float(A.one(p, 'drill')[1]); pads.append((G.pad_poly(fx + dx, fy + dy, 'circle', d, d, 0), '__NP'))
            else:
                pads.append((G.pad_poly(fx + dx, fy + dy, p[3], float(sz[1]), float(sz[2]), pr), nn))
    # segment blokları (metin içinde yerinde değiştirmek için)
    blocks = list(re.finditer(r'\t\(segment\n(?:\t\t[^\n]*\n)+?\t\)\n', txt))
    S = []
    for m in blocks:
        b = m.group(0)
        s = re.search(r'\(start ([-\d.]+) ([-\d.]+)\)', b); e = re.search(r'\(end ([-\d.]+) ([-\d.]+)\)', b)
        w = float(re.search(r'\(width ([\d.]+)\)', b).group(1)); n = re.search(r'\(net "([^"]*)"\)', b) or re.search(r'\(net (\d+)\)', b)
        S.append(dict(m=m, a=(float(s.group(1)), float(s.group(2))), b=(float(e.group(1)), float(e.group(2))), w=w, net=n.group(1)))
    ok, bad = 0, []
    for i, s in enumerate(S):
        if s['w'] >= wmin - 1e-6: continue
        need = wmin / 2 + gap
        clash = None
        for P, nn in pads:
            if nn == s['net']: continue
            if poly_seg(P, s['a'], s['b']) < need - 1e-6: clash = 'pad'; break
        if not clash:
            for j, t in enumerate(S):
                if j == i or t['net'] == s['net']: continue
                if seg_seg(s['a'], s['b'], t['a'], t['b']) < need + t['w'] / 2 - 1e-6: clash = 'yol ' + t['net']; break
        if clash:
            bad.append((s['net'], s['w'], s['a'], s['b'], clash))
        else:
            s['new'] = wmin; ok += 1
    out = []; last = 0
    for s in S:
        if 'new' in s:
            out.append(txt[last:s['m'].start()]); out.append(re.sub(r'\(width [\d.]+\)', '(width %g)' % s['new'], s['m'].group(0))); last = s['m'].end()
    out.append(txt[last:])
    open(dst, 'w', encoding='utf-8').write(''.join(out))
    return ok, bad

if __name__ == '__main__':
    a = sys.argv
    ok, bad = main(a[1], a[2], float(a[3]) if len(a) > 3 else 1.5, float(a[4]) if len(a) > 4 else 0.5)
    print('genişletilen', ok, 'genişletilemeyen', len(bad))
    for b in bad: print(' ', b)
