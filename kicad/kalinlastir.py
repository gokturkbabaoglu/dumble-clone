"""Mevcut (yönlendirilmiş) kartta yolları ve padleri, bakır aralığını bozmadan sığdığı kadar büyütür.
Kullanım: python kicad/kalinlastir.py girdi.kicad_pcb cikti.kicad_pcb
Kurallar: başka netin bakırına >= ARALIK; arka/sol/sağ kenarda 1 mm yol yasağı şeridi; ön kenarda 0.5 mm.
GND dolgusu sonra KiCad'de yeniden doldurulmalı.
"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analiz as A
import gorsel as G
from genislet import seg_seg, poly_seg, G_inside
import dolgu as DG

ARALIK = 0.5
GUC = {'DCIN', 'FUSED', 'SPK', 'SPKT', 'TNEG', 'TOUT', 'TRC', 'V12', 'VIN', 'ZOB2'}

def pt_seg(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]; L = vx * vx + vy * vy
    t = 0 if L == 0 else max(0, min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L))
    return math.dist(p, (a[0] + t * vx, a[1] + t * vy))

def poly_poly(P, Q):
    if G_inside(P[0], Q) or G_inside(Q[0], P): return 0.0
    return min(seg_seg(P[i - 1], P[i], Q[j - 1], Q[j]) for i in range(len(P)) for j in range(len(Q)))

def main(src, dst, koru=()):
    """koru: [(x, y, r)] — bu dairelere değen yol ve padler eski boyunda kalır (dolgu bağlantısı için)."""
    txt = open(src, encoding='utf-8').read()
    B = A.sexp(txt)
    edge = [g for g in A.find(B, 'gr_rect') if A.one(g, 'layer')[1] == 'Edge.Cuts'][0]
    s0, e0 = A.one(edge, 'start'), A.one(edge, 'end')
    X0, Y0, X1, Y1 = float(s0[1]), float(s0[2]), float(e0[1]), float(e0[2])
    # padler (metindeki yerleriyle)
    PADS = []
    for fm in re.finditer(r'\t\(footprint "[^"]*"\n(?:\t\t[^\n]*\n|\t\t\t[^\n]*\n|\t\t\t\t[^\n]*\n|\t\t\t\t\t[^\n]*\n)*?\t\)\n', txt):
        ft = fm.group(0)
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', ft)
        fx, fy, fr = float(at.group(1)), float(at.group(2)), float(at.group(3) or 0)
        ref = re.search(r'\(property "Reference" "([^"]*)"', ft).group(1)
        for pm in re.finditer(r'\t\t\(pad "([^"]*)" (\w+) (\w+)\n((?:\t\t\t[^\n]*\n|\t\t\t\t[^\n]*\n)*?)\t\t\)\n', ft):
            body = pm.group(4)
            pa = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', body)
            px, py, pr = float(pa.group(1)), float(pa.group(2)), float(pa.group(3) or 0)
            sz = re.search(r'\(size ([\d.]+) ([\d.]+)\)', body); dr = re.search(r'\(drill ([\d.]+)', body)
            net = re.search(r'\(net "([^"]*)"\)', body)
            dx, dy = G.rot(px, py, fr)
            PADS.append(dict(ref=ref, num=pm.group(1), typ=pm.group(2), shape=pm.group(3), x=fx + dx, y=fy + dy, ang=pr,
                             w=float(sz.group(1)), h=float(sz.group(2)), drill=float(dr.group(1)) if dr else 0,
                             net=net.group(1) if net else '', span=(fm.start() + pm.start(), fm.start() + pm.end()), text=pm.group(0)))
    for p in PADS:
        p['poly'] = G.pad_poly(p['x'], p['y'], p['shape'] if p['typ'] != 'np_thru_hole' else 'circle', p['w'], p['h'], p['ang'])
    # yollar
    S = []
    for m in re.finditer(r'\t\(segment\n(?:\t\t[^\n]*\n)+?\t\)\n', txt):
        b = m.group(0)
        st = re.search(r'\(start ([-\d.]+) ([-\d.]+)\)', b); en = re.search(r'\(end ([-\d.]+) ([-\d.]+)\)', b)
        S.append(dict(span=m.span(), text=b, a=(float(st.group(1)), float(st.group(2))), b=(float(en.group(1)), float(en.group(2))),
                      w0=float(re.search(r'\(width ([\d.]+)\)', b).group(1)), net=re.search(r'\(net "([^"]*)"\)', b).group(1)))
    for s in S: s['w'] = s['w0']

    def kenar_ok(s, w):
        r = w / 2
        for p in (s['a'], s['b']):
            if p[0] - r < X0 + 1.0 - 1e-6 or p[0] + r > X1 - 1.0 + 1e-6 or p[1] - r < Y0 + 1.0 - 1e-6 or p[1] + r > Y1 - 0.5 + 1e-6:
                return False
        return True
    def korunur(a, b):
        return any(pt_seg((x, y), a, b) < r for x, y, r in koru)
    def ok(i, w):
        s = S[i]
        if korunur(s['a'], s['b']): return False
        if not kenar_ok(s, w) and w > s['w0']: return False
        need = w / 2 + ARALIK - 1e-6
        for p in PADS:
            if p['net'] == s['net'] and p['typ'] != 'np_thru_hole': continue
            if abs(p['x'] - s['a'][0]) > 25 and abs(p['x'] - s['b'][0]) > 25: continue
            if poly_seg(p['poly'], s['a'], s['b']) < need: return False
        for j, t in enumerate(S):
            if j == i or t['net'] == s['net']: continue
            if seg_seg(s['a'], s['b'], t['a'], t['b']) < need + t['w'] / 2: return False
        return True
    KOP = tuple(sorted({p['ref'] for p in PADS if re.fullmatch(r'K\d+', p['ref'])}))
    DOL = DG.Dolgu(X0, Y0, X1, Y1, kopruler=KOP)
    TABAN = DOL.bagli(S, PADS)          # mevcut GND dolgu parça sayısı (artmamalı)
    def dolgu_ok(): return DOL.bagli(S, PADS) <= TABAN
    # kademeli büyütme: önce herkes 1.5'e kadar, sonra güç 2.0, sonra sinyal 2.0, güç 2.5
    plan = [1.2, 1.3, 1.4, 1.5, ('G', 1.75), ('G', 2.0), ('S', 1.75), ('S', 2.0), ('G', 2.5)]
    for st in plan:
        kind, w = (None, st) if not isinstance(st, tuple) else st
        for i, s in enumerate(S):
            if s['w'] >= w: continue
            g = s['net'] in GUC
            if kind == 'G' and not g: continue
            if kind == 'S' and g: continue
            if ok(i, w):
                eski = s['w']; s['w'] = w
                if not dolgu_ok(): s['w'] = eski
    # padler: delik + 2*halka; en büyük halka 1.0 mm, adımlarla
    def pad_ok(p, w, h):
        poly = G.pad_poly(p['x'], p['y'], p['shape'], w, h, p['ang'])
        for q in PADS:
            if q is p or (q['net'] == p['net'] and q['net'] and q['typ'] != 'np_thru_hole'): continue
            if abs(q['x'] - p['x']) > 12 or abs(q['y'] - p['y']) > 12: continue
            if poly_poly(poly, q['poly']) < ARALIK - 1e-6: return None
        for t in S:
            if t['net'] == p['net']: continue
            if min(abs(t['a'][0] - p['x']), abs(t['b'][0] - p['x'])) > 20 and abs((t['a'][0] + t['b'][0]) / 2 - p['x']) > 20: continue
            if poly_seg(poly, t['a'], t['b']) < t['w'] / 2 + ARALIK - 1e-6: return None
        return poly
    padbuyu = 0
    for p in PADS:
        if p['typ'] != 'thru_hole' or p['ref'].startswith('MH'): continue
        if any(math.dist((p['x'], p['y']), (x, y)) < r for x, y, r in koru): continue
        hedef = p['drill'] + 2.0       # 1 mm halka
        for k in (1.0, 0.8, 0.6, 0.4, 0.2):
            w, h = p['w'], p['h']
            nw = min(max(w, w + k), max(w, hedef)) if True else w
            nh = min(max(h, h + k), max(h, hedef))
            if nw <= w + 1e-6 and nh <= h + 1e-6: break
            poly = pad_ok(p, nw, nh)
            if poly:
                eski = p['poly']; p['poly'] = poly
                if not dolgu_ok(): p['poly'] = eski; continue
                p['nw'], p['nh'] = nw, nh; padbuyu += 1; break
    # metni yeniden yaz
    edits = []
    for s in S:
        if s['w'] != s['w0']:
            edits.append((s['span'], re.sub(r'\(width [\d.]+\)', '(width %g)' % s['w'], s['text'])))
    for p in PADS:
        if 'nw' in p:
            edits.append((p['span'], re.sub(r'\(size [\d.]+ [\d.]+\)', '(size %g %g)' % (round(p['nw'], 3), round(p['nh'], 3)), p['text'], count=1)))
    edits.sort()
    out = []; last = 0
    for (a, b), t in edits:
        out.append(txt[last:a]); out.append(t); last = b
    out.append(txt[last:])
    open(dst, 'w', encoding='utf-8').write(''.join(out))
    from collections import Counter
    print('GND dolgu parça sayısı: önce', TABAN, 'sonra', DOL.bagli(S, PADS))
    return Counter(round(s['w'], 2) for s in S), padbuyu, S, PADS

if __name__ == '__main__':
    koru = [tuple(float(v) for v in a.split(',')) for a in sys.argv[3:]]
    c, n, S, P = main(sys.argv[1], sys.argv[2], koru)
    print('yol genişlikleri:', dict(sorted(c.items())))
    print('büyütülen pad:', n)
    dar = [(s['net'], s['w'], s['a'], s['b']) for s in S if s['w'] < 1.5]
    print('1.5 altında kalan yol:', len(dar), 'toplam uzunluk %.1f mm' % sum(math.dist(d[2], d[3]) for d in dar))
    for d in dar: print('  ', d[0], d[1], d[2], d[3], '%.1f mm' % math.dist(d[2], d[3]))
