"""Dolgulu karttaki GND adaları için düz (yatay/dikey), kısa tel köprü yerleri bulur."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analiz as A

PAD_R = 1.0      # köprü padi yarıçapı (2.0 mm pad, 0.9 delik)
BOYLAR = [5.08, 7.62, 10.16, 12.7]

def polys_of(path):
    B = A.sexp(open(path, encoding='utf-8').read())
    out = []
    for z in A.find(B, 'zone'):
        nn = A.one(z, 'net'); nm = A.one(z, 'net_name')
        name = nm[1] if nm else (nn[1] if nn else '')
        if name != 'GND': continue
        for fp in A.find(z, 'filled_polygon'):
            out.append([(float(p[1]), float(p[2])) for p in A.one(fp, 'pts') if isinstance(p, list) and p[0] == 'xy'])
    return B, out

def inside(pt, P):
    x, y = pt; c = False
    for i in range(len(P)):
        (x1, y1), (x2, y2) = P[i], P[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def edist(pt, P):
    b = 1e9
    for i in range(len(P)):
        (ax, ay), (bx, by) = P[i - 1], P[i]; vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((pt[0] - ax) * vx + (pt[1] - ay) * vy) / L))
        b = min(b, math.dist(pt, (ax + t * vx, ay + t * vy)))
    return b

def courtyards(B):
    R = []
    for fp in A.find(B, 'footprint'):
        at = A.one(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0
        ref = [p[2] for p in A.find(fp, 'property') if p[1] == 'Reference'][0]
        for r in A.find(fp, 'fp_rect'):
            if A.one(r, 'layer')[1] != 'F.CrtYd': continue
            s = A.one(r, 'start'); e = A.one(r, 'end')
            pts = [A.rot(float(x), float(y), fr) for x, y in ((s[1], s[2]), (e[1], s[2]), (e[1], e[2]), (s[1], e[2]))]
            xs = [fx + p[0] for p in pts]; ys = [fy + p[1] for p in pts]
            R.append((ref, min(xs), min(ys), max(xs), max(ys)))
    return R

def bul(path, dikkat=('U1', 'U2', 'C1', 'C25', 'C7', 'C23', 'J1', 'J2', 'RV1', 'RV2', 'RV3', 'RV4', 'F1', 'D1', 'TB1', 'TB2')):
    B, polys = polys_of(path)
    D = A.load(path)
    adalar, _, _ = A.gnd_islands(path)
    # ana parça = en büyük alan
    def area(P): return abs(sum(P[i - 1][0] * P[i][1] - P[i][0] * P[i - 1][1] for i in range(len(P)))) / 2
    main = max(range(len(polys)), key=lambda k: area(polys[k]))
    crt = courtyards(B)
    pads = list(D['pads'])
    sonuc = []
    for padname, gap in adalar:
        ref, num = padname.split('.')
        p0 = [p for p in pads if p[4] == ref and p[5] == num][0]
        # adanın dolgu parçası(ları): padin değdiği parçalar
        own = [k for k, P in enumerate(polys) if k != main and (inside(p0[:2], P) or edist(p0[:2], P) <= p0[2] / 2 + 0.15)]
        aday = []
        # köprünün bir ucu doğrudan ada padine gelebilir (pad = köprü ucu) ya da ada dolgusu içinde bir nokta
        starts = []   # köprü ucu mevcut bir pad deliğine konmaz
        for k in own:
            P = polys[k]; xs = [q[0] for q in P]; ys = [q[1] for q in P]
            x = min(xs)
            while x <= max(xs):
                y = min(ys)
                while y <= max(ys):
                    if inside((x, y), P) and edist((x, y), P) >= PAD_R: starts.append((x, y, 'dolgu'))
                    y += 0.635
                x += 0.635
        for sx, sy, kind in starts:
            for L in BOYLAR:
                for dx, dy in ((L, 0), (-L, 0), (0, L), (0, -L)):
                    ex, ey = sx + dx, sy + dy
                    P = polys[main]
                    if not (inside((ex, ey), P) and edist((ex, ey), P) >= PAD_R): continue
                    # başka padlerle çakışma
                    ok = True
                    for q in pads:
                        for (cx, cy, k2) in ((sx, sy, kind), (ex, ey, 'dolgu')):
                            if k2 == 'pad' and (cx, cy) == (p0[0], p0[1]): continue
                            if math.dist((cx, cy), q[:2]) < PAD_R + q[2] / 2 + 0.5: ok = False
                    if not ok: continue
                    # büyük parça gövdesi üstünden geçmesin
                    x0, x1 = sorted((sx, ex)); y0, y1 = sorted((sy, ey))
                    # hiçbir parçanın avlusuyla çakışmasın (köprü gövdesi ±1.25 mm genişlikte); ada padinin kendi parçası hariç
                    m = PAD_R + 0.25
                    if any(not (x1 + m <= r[1] or x0 - m >= r[3] or y1 + m <= r[2] or y0 - m >= r[4]) and not (kind == 'pad' and r[0] == ref) for r in crt): continue
                    aday.append((L + (0 if kind == 'pad' else 0.5), L, (round(sx, 3), round(sy, 3)), (round(ex, 3), round(ey, 3)), kind))
                    break
        aday.sort()
        best = aday[0] if aday else None
        if best:   # seçilen köprünün padlerini engel listesine ekle
            for c in (best[2], best[3]):
                pads.append((c[0], c[1], 2 * PAD_R, 'GND', 'K', '0'))
        sonuc.append((padname, gap, best))
    return sonuc

if __name__ == '__main__':
    for r in bul(sys.argv[1]): print(r)
