"""Izgara yollarındaki merdiven görünümünü düzeltir: her yol zincirinde, bakır boşluğu korunarak
uzak noktalara doğrudan kestirme yapar.  python smooth.py GİRİŞ.kicad_pcb ÇIKIŞ.kicad_pcb C"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sexp import parse, dump, Sym as S, find, first
import gen_pcb as GP, pad_check as PC
from yk_drc import sd, ss
import padgeom as geom

def key(p): return (round(p[0], 4), round(p[1], 4))

def main(src, dst, C):
    b = parse(open(src, encoding='utf-8').read())
    pads = [p for fp in find(b, 'footprint') for p in GP.pad_world(fp)]
    outs = [PC.outline(p, 72) for p in pads]
    padc = {key((p['x'], p['y'])) for p in pads}
    segs = [(key((float(first(s, 'start')[1]), float(first(s, 'start')[2]))), key((float(first(s, 'end')[1]), float(first(s, 'end')[2]))),
             float(first(s, 'width')[1]), first(s, 'net')[1]) for s in find(b, 'segment')]
    W = segs[0][2]
    # T bağlantıları: başka segmentin ortasına düşen uçlarda segmenti böl
    ends = {}
    for a, c, w, n in segs: ends.setdefault(n, set()).update((a, c))
    out = []
    for a, c, w, n in segs:
        pts = [p for p in ends[n] if p not in (a, c) and sd(p, a, c) < 1e-3]
        ch = sorted([a, c] + pts, key=lambda p: math.dist(p, a))
        out += [(u, v, w, n) for u, v in zip(ch, ch[1:])]
    segs = out
    # zincirler
    adj = {}
    for a, c, w, n in segs:
        adj.setdefault((n, a), []).append(c); adj.setdefault((n, c), []).append(a)
    used = set(); chains = []
    def is_end(n, p): return len(adj[(n, p)]) != 2 or p in padc
    for (n, p), nb in adj.items():
        if not is_end(n, p): continue
        for q in nb:
            e = frozenset((p, q))
            if (n, e) in used: continue
            ch = [p, q]; used.add((n, e))
            while not is_end(n, ch[-1]):
                nxt = [r for r in adj[(n, ch[-1])] if (n, frozenset((ch[-1], r))) not in used]
                if not nxt: break
                used.add((n, frozenset((ch[-1], nxt[0])))); ch.append(nxt[0])
            chains.append((n, ch))
    # kalan kapalı halkalar (olmamalı)
    others = {}                         # net -> segment listesi (güncel)
    for n, ch in chains: others.setdefault(n, []).append(ch)
    def ok(a, c, n):
        for p, o in zip(pads, outs):
            if p['net'] == n: continue
            if sd((p['x'], p['y']), a, c) > math.hypot(p['w'], p['h']) / 2 + W / 2 + C + 0.3: continue
            if geom.seg_pad(a, c, p) - W / 2 < C + 0.01: return False
        for m, chs in others.items():
            if m == n: continue
            for ch in chs:
                for u, v in zip(ch, ch[1:]):
                    if min(u[0], v[0]) > max(a[0], c[0]) + 2 or max(u[0], v[0]) < min(a[0], c[0]) - 2: continue
                    if min(u[1], v[1]) > max(a[1], c[1]) + 2 or max(u[1], v[1]) < min(a[1], c[1]) - 2: continue
                    if ss(a, c, u, v) - W < C + 0.06: return False
        m = 1.0 + W / 2                 # kenar payı
        for p in (a, c):
            if not (GP.X0 + m <= p[0] <= GP.X0 + GP.W - m and GP.Y0 + m <= p[1] <= GP.Y0 + GP.H - m):
                if p not in padc: return False
        return True
    for idx, (n, ch) in enumerate(chains):
        lst = others[n]; k = lst.index(ch)
        out = [ch[0]]; i = 0
        while i < len(ch) - 1:
            j = len(ch) - 1
            while j > i + 1 and not ok(ch[i], ch[j], n): j -= 1
            out.append(ch[j]); i = j
        lst[k] = out; chains[idx] = (n, out)
    # onarım: boşluk ihlali olan segmentleri L biçiminde (köşe noktası üzerinden) dene
    def viol(a, c, n):
        others_n = others[n]; others[n] = []
        r = not ok(a, c, n); others[n] = others_n
        return r
    for idx, (n, ch) in enumerate(chains):
        k = others[n].index(ch); new = [ch[0]]
        for a, c in zip(ch, ch[1:]):
            if viol(a, c, n):
                for m in ((a[0], c[1]), (c[0], a[1])):
                    if not viol(a, m, n) and not viol(m, c, n):
                        new.append(m); print('onarıldı', n, a, c, '->', m); break
            new.append(c)
        others[n][k] = new; chains[idx] = (n, new)
    b = [x for x in b if not (isinstance(x, list) and x and x[0] == 'segment')]
    new = []
    for n, ch in chains:
        for a, c in zip(ch, ch[1:]):
            new.append([S('segment'), [S('start'), GP.F(a[0]), GP.F(a[1])], [S('end'), GP.F(c[0]), GP.F(c[1])],
                        [S('width'), GP.F(W)], [S('layer'), 'B.Cu'], [S('net'), n], [S('uuid'), GP.uid('sm', n, a, c)]])
    b[len(b) - 1:len(b) - 1] = new
    open(dst, 'w', encoding='utf-8', newline='\n').write(dump(b) + '\n')
    print('segment', len(segs), '->', len(new))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]))
