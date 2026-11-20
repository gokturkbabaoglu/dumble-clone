"""Yönlendirilmiş .kicad_pcb -> alt bakır görselleri (PNG/SVG) ve lazer dosyaları.
Kullanım: python kicad/gorsel.py kart.kicad_pcb cikti_klasoru
Üretilenler: bakir_onizleme.png (renkli önizleme), lazer_*.png/svg (1:1, siyah = yakılacak / bakır)
"""
import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analiz as A
from PIL import Image, ImageDraw

def rot(x, y, r):
    c, s = math.cos(math.radians(r)), math.sin(math.radians(r))
    return x * c + y * s, -x * s + y * c

def oku(path):
    B = A.sexp(open(path, encoding='utf-8').read())
    edge = None
    for g in A.find(B, 'gr_rect'):
        if A.one(g, 'layer')[1] == 'Edge.Cuts':
            s, e = A.one(g, 'start'), A.one(g, 'end'); edge = (float(s[1]), float(s[2]), float(e[1]), float(e[2]))
    zones = []
    for z in A.find(B, 'zone'):
        for fp in A.find(z, 'filled_polygon'):
            if A.one(fp, 'layer') and A.one(fp, 'layer')[1] != 'B.Cu': continue
            zones.append([(float(p[1]), float(p[2])) for p in A.one(fp, 'pts') if isinstance(p, list) and p[0] == 'xy'])
    segs = []
    for sg in A.find(B, 'segment'):
        if A.one(sg, 'layer')[1] != 'B.Cu': continue
        s, e = A.one(sg, 'start'), A.one(sg, 'end')
        segs.append(((float(s[1]), float(s[2])), (float(e[1]), float(e[2])), float(A.one(sg, 'width')[1])))
    arcs = []
    for ar in A.find(B, 'arc'):
        if A.one(ar, 'layer')[1] != 'B.Cu': continue
        pts = [A.one(ar, k) for k in ('start', 'mid', 'end')]
        arcs.append(([(float(p[1]), float(p[2])) for p in pts], float(A.one(ar, 'width')[1])))
    pads = []   # (cx, cy, shape, w, h, ang, drill, ref, num)
    for fp in A.find(B, 'footprint'):
        at = A.one(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0
        ref = [p[2] for p in A.find(fp, 'property') if p[1] == 'Reference'][0]
        for p in A.find(fp, 'pad'):
            pa = A.one(p, 'at'); px, py = float(pa[1]), float(pa[2]); pr = float(pa[3]) if len(pa) > 3 else 0
            dx, dy = rot(px, py, fr)
            sz = A.one(p, 'size'); dr = A.one(p, 'drill')
            drill = float(dr[1]) if dr and len(dr) > 1 and dr[1] not in ('oval',) else 0
            pads.append((fx + dx, fy + dy, p[3], float(sz[1]), float(sz[2]), pr, drill, ref, p[1], p[2]))
    return dict(edge=edge, zones=zones, segs=segs, arcs=arcs, pads=pads)

def arc_pts(p, n=24):
    (x1, y1), (x2, y2), (x3, y3) = p
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(d) < 1e-9: return [p[0], p[2]]
    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
    r = math.dist((ux, uy), p[0])
    a1, a2, a3 = [math.atan2(y - uy, x - ux) for x, y in p]
    def norm(a): return a % (2 * math.pi)
    span = norm(a3 - a1); mid = norm(a2 - a1)
    if mid > span: span = span - 2 * math.pi
    return [(ux + r * math.cos(a1 + span * i / n), uy + r * math.sin(a1 + span * i / n)) for i in range(n + 1)]

def pad_poly(cx, cy, shape, w, h, ang, n=20):
    """Pad dış hattı (mm). KiCad: açı saat yönünün tersine, y aşağı."""
    if shape == 'circle':
        r = w / 2; return [(cx + r * math.cos(2 * math.pi * i / 32), cy + r * math.sin(2 * math.pi * i / 32)) for i in range(32)]
    if shape in ('rect', 'roundrect', 'trapezoid'):
        loc = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    else:   # oval
        loc = []
        if w >= h:
            r = h / 2; L = (w - h) / 2
            loc += [(L + r * math.cos(t), r * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / n for i in range(n + 1)]]
            loc += [(-L + r * math.cos(t), r * math.sin(t)) for t in [math.pi / 2 + math.pi * i / n for i in range(n + 1)]]
        else:
            r = w / 2; L = (h - w) / 2
            loc += [(r * math.cos(t), L + r * math.sin(t)) for t in [math.pi * i / n for i in range(n + 1)]]
            loc += [(r * math.cos(t), -L + r * math.sin(t)) for t in [math.pi + math.pi * i / n for i in range(n + 1)]]
    out = []
    for x, y in loc:
        dx, dy = rot(x, y, ang); out.append((cx + dx, cy + dy))
    return out

def ciz(K, dpi, renk=False, negatif=False, delik=0.6, kenar_pay=0.0):
    x0, y0, x1, y1 = K['edge']
    s = dpi / 25.4
    W, H = int(round((x1 - x0) * s)), int(round((y1 - y0) * s))
    if renk:
        im = Image.new('RGB', (W, H), (25, 60, 35)); cu = (205, 135, 70); hole = (15, 15, 15)
    else:
        im = Image.new('L', (W, H), 255); cu = 0; hole = 255
    d = ImageDraw.Draw(im)
    T = lambda p: ((p[0] - x0) * s, (p[1] - y0) * s)
    for z in K['zones']: d.polygon([T(p) for p in z], fill=cu)
    def kalem(a, b, w):
        d.line([T(a), T(b)], fill=cu, width=max(1, int(round(w * s))))
        for c in (a, b):
            X, Y = T(c); r = w * s / 2; d.ellipse([X - r, Y - r, X + r, Y + r], fill=cu)
    for a, b, w in K['segs']: kalem(a, b, w)
    for pts, w in K['arcs']:
        P = arc_pts(pts)
        for a, b in zip(P, P[1:]): kalem(a, b, w)
    for p in K['pads']:
        if p[2] == 'np_thru_hole': continue
        d.polygon([T(q) for q in pad_poly(p[0], p[1], p[2], p[3], p[4], p[5])], fill=cu)
    for p in K['pads']:
        if p[2] == 'np_thru_hole':
            r = p[6] / 2 * s
        elif delik:
            r = min(delik, p[6]) / 2 * s
        else: continue
        X, Y = T(p[:2]); d.ellipse([X - r, Y - r, X + r, Y + r], fill=hole)
    if negatif and not renk:
        im = Image.eval(im, lambda v: 255 - v)
    return im

def svg(K, path, negatif=False, delik=0.6, aynali=False):
    """Vektör: siyah dolgu = bakır (negatif=True ise siyah = yakılacak alan, bakır beyaz)."""
    x0, y0, x1, y1 = K['edge']; W, H = x1 - x0, y1 - y0
    fg, bg = ('#fff', '#000') if negatif else ('#000', '#fff')
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%gmm" height="%gmm" viewBox="0 0 %g %g">' % (W, H, W, H),
         '<rect x="0" y="0" width="%g" height="%g" fill="%s"/>' % (W, H, bg),
         ('<g transform="translate(%g 0) scale(-1 1)">' % W if aynali else '<g>') + '<g transform="translate(%g %g)">' % (-x0, -y0)]
    for z in K['zones']: o.append('<polygon fill="%s" points="%s"/>' % (fg, ' '.join('%.4f,%.4f' % p for p in z)))
    for a, b, w in K['segs']:
        o.append('<line x1="%.4f" y1="%.4f" x2="%.4f" y2="%.4f" stroke="%s" stroke-width="%g" stroke-linecap="round"/>' % (a[0], a[1], b[0], b[1], fg, w))
    for pts, w in K['arcs']:
        P = arc_pts(pts); o.append('<polyline fill="none" stroke="%s" stroke-width="%g" stroke-linecap="round" points="%s"/>' % (fg, w, ' '.join('%.4f,%.4f' % p for p in P)))
    for p in K['pads']:
        if p[2] == 'np_thru_hole': continue
        o.append('<polygon fill="%s" points="%s"/>' % (fg, ' '.join('%.4f,%.4f' % q for q in pad_poly(p[0], p[1], p[2], p[3], p[4], p[5]))))
    for p in K['pads']:
        r = p[6] / 2 if p[2] == 'np_thru_hole' else (min(delik, p[6]) / 2 if delik else 0)
        if r: o.append('<circle cx="%.4f" cy="%.4f" r="%.4f" fill="%s"/>' % (p[0], p[1], r, bg))
    o.append('</g></g></svg>')
    open(path, 'w').write('\n'.join(o))

def dxf(K, path):
    """Bakır dış hatları (kapalı LWPOLYLINE) — yollar dikdörtgen+daire olarak yaklaşık."""
    L = ['0', 'SECTION', '2', 'ENTITIES']
    x0, y0, x1, y1 = K['edge']
    def poly(P):
        L.extend(['0', 'LWPOLYLINE', '8', 'BAKIR', '90', str(len(P)), '70', '1'])
        for x, y in P: L.extend(['10', '%.4f' % (x - x0), '20', '%.4f' % (y1 - y)])
    for z in K['zones']: poly(z)
    def seg(a, b, w):
        dx, dy = b[0] - a[0], b[1] - a[1]; l = math.hypot(dx, dy) or 1e-9; nx, ny = -dy / l * w / 2, dx / l * w / 2
        ang = math.atan2(dy, dx)
        P = [(b[0] + w / 2 * math.cos(ang - math.pi / 2 + math.pi * i / 12), b[1] + w / 2 * math.sin(ang - math.pi / 2 + math.pi * i / 12)) for i in range(13)]
        P += [(a[0] + w / 2 * math.cos(ang + math.pi / 2 + math.pi * i / 12), a[1] + w / 2 * math.sin(ang + math.pi / 2 + math.pi * i / 12)) for i in range(13)]
        poly(P)
    for a, b, w in K['segs']: seg(a, b, w)
    for pts, w in K['arcs']:
        P = arc_pts(pts)
        for a, b in zip(P, P[1:]): seg(a, b, w)
    for p in K['pads']:
        if p[2] != 'np_thru_hole': poly(pad_poly(p[0], p[1], p[2], p[3], p[4], p[5]))
    for p in K['pads']:
        r = p[6] / 2
        if r: L.extend(['0', 'CIRCLE', '8', 'DELIK', '10', '%.4f' % (p[0] - x0), '20', '%.4f' % (y1 - p[1]), '40', '%.4f' % r])
    L.extend(['0', 'ENDSEC', '0', 'EOF'])
    open(path, 'w').write('\n'.join(L))

def ayna(im): return im.transpose(Image.FLIP_LEFT_RIGHT)

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    K = oku(src)
    ciz(K, 300, renk=True).save(os.path.join(out, 'bakir_onizleme.png'))
    if '--lazer' in sys.argv:
        DPI = 1000
        poz = ciz(K, DPI, delik=0.6)            # siyah = bakır, üstten bakış (KiCad görünümü)
        neg = ciz(K, DPI, negatif=True, delik=0.6)   # siyah = yakılacak (bakırsız) alan
        lz = os.path.join(out, 'lazer'); os.makedirs(lz, exist_ok=True)
        ayna(neg).save(os.path.join(lz, 'lazer_boya_yakma_AYNALI_1000dpi.png'), dpi=(DPI, DPI))
        ayna(poz).save(os.path.join(lz, 'lazer_bakir_siyah_AYNALI_1000dpi.png'), dpi=(DPI, DPI))
        poz.save(os.path.join(lz, 'toner_bakir_siyah_1000dpi.png'), dpi=(DPI, DPI))
        svg(K, os.path.join(lz, 'bakir_siyah_ustten.svg'))
        svg(K, os.path.join(lz, 'boya_yakma_negatif_ustten.svg'), negatif=True)
        svg(K, os.path.join(lz, 'lazer_boya_yakma_AYNALI.svg'), negatif=True, aynali=True)
        svg(K, os.path.join(lz, 'lazer_bakir_siyah_AYNALI.svg'), aynali=True)
        dxf(K, os.path.join(lz, 'bakir_hatlari_ustten.dxf'))
    print('tamam', len(K['segs']), 'yol', len(K['pads']), 'pad', K['edge'])
