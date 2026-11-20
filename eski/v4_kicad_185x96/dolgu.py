"""GND dolgusunun yaklaşık rasterle hesaplanıp bütün GND padlerinin tek parça olup olmadığının kontrolü."""
import math
import numpy as np, cv2
RES = 0.1   # mm/piksel
ARALIK = 0.5; KENAR = 1.0; MIN_KAL = 0.5

class Dolgu:
    def __init__(self, X0, Y0, X1, Y1, kopruler=()):
        self.X0, self.Y0, self.X1, self.Y1 = X0, Y0, X1, Y1
        self.W = int(math.ceil((X1 - X0) / RES)) + 1; self.H = int(math.ceil((Y1 - Y0) / RES)) + 1
        self.kopruler = kopruler   # [(refK)] köprü padleri aynı ref'te birleşir
        r = int(round(ARALIK / RES))
        self.kd = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
        m = max(1, int(round(MIN_KAL / 2 / RES)))
        self.km = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * m + 1, 2 * m + 1))
    def P(self, p): return (int(round((p[0] - self.X0) / RES)), int(round((p[1] - self.Y0) / RES)))
    def bagli(self, S, PADS, ret_detay=False):
        cu = np.zeros((self.H, self.W), np.uint8)
        for s in S:
            if s['net'] == 'GND': continue
            cv2.line(cu, self.P(s['a']), self.P(s['b']), 255, max(1, int(round(s['w'] / RES))), lineType=cv2.LINE_8)
            for c in (s['a'], s['b']): cv2.circle(cu, self.P(c), int(round(s['w'] / 2 / RES)), 255, -1)
        gp = []
        for p in PADS:
            pts = np.array([self.P(q) for q in p['poly']], np.int32)
            if p['net'] == 'GND' and p['typ'] != 'np_thru_hole': gp.append((p, pts)); continue
            cv2.fillPoly(cu, [pts], 255)
        obs = cv2.dilate(cu, self.kd)
        free = np.zeros_like(cu)
        e = int(round(KENAR / RES))
        free[e:self.H - e, e:self.W - e] = 255
        free[obs > 0] = 0
        free = cv2.morphologyEx(free, cv2.MORPH_OPEN, self.km)
        for p, pts in gp: cv2.fillPoly(free, [pts], 255)
        for s in S:
            if s['net'] == 'GND':
                cv2.line(free, self.P(s['a']), self.P(s['b']), 255, max(1, int(round(s['w'] / RES))))
        n, lab = cv2.connectedComponents(free, connectivity=8)
        comp = {}
        for p, pts in gp:
            x, y = self.P((p['x'], p['y']))
            comp.setdefault(int(lab[min(max(y, 0), self.H - 1), min(max(x, 0), self.W - 1)]), []).append(p)
        # köprüler: aynı ref'teki iki pad bileşenleri birleştirir
        par = {k: k for k in comp}
        def f(a):
            while par[a] != a: par[a] = par[par[a]]; a = par[a]
            return a
        byref = {}
        for k, L in comp.items():
            for p in L:
                if p['ref'] in self.kopruler: byref.setdefault(p['ref'], set()).add(k)
        for ks in byref.values():
            ks = list(ks)
            for k in ks[1:]: par[f(k)] = f(ks[0])
        roots = {f(k) for k in comp}
        if ret_detay: return len(roots), comp
        return len(roots)
