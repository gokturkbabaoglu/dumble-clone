"""Tek katlı (B.Cu) ızgara yönlendirici — PathFinder (müzakereli tıkanıklık) yöntemi.

Yol genişliği W, bakır boşluğu C. Padler sabit engel; farklı netlerin yol merkezleri arası >= W + C.
Çalıştır: python router.py KART.kicad_pcb ÇIKTI.kicad_pcb [W] [C]
"""
import os, sys, math, heapq, time, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sexp import parse, dump, Sym as S, find, first
import gen_pcb as GP, pad_check as PC
from matplotlib.path import Path

G = float(os.environ.get('GRID', 0.5))   # ızgara adımı (mm)

def build_grid(pads, W, C, edge=1.0):
    nx = int(round(GP.W / G)) + 1; ny = int(round(GP.H / G)) + 1
    xs = GP.X0 + np.arange(nx) * G; ys = GP.Y0 + np.arange(ny) * G
    XX, YY = np.meshgrid(xs, ys, indexing='ij')
    pts = np.stack([XX.ravel(), YY.ravel()], 1)
    block = np.zeros((nx, ny), bool)              # her net için engel (kenar)
    m = edge + W / 2
    block |= (XX < GP.X0 + m) | (XX > GP.X0 + GP.W - m) | (YY < GP.Y0 + m) | (YY > GP.Y0 + GP.H - m)
    padnear = np.full((nx, ny), -1, int)          # bu hücre hangi pada (W/2+C) yakın; -2: birden fazla
    inside = {}                                   # pad indeksi -> içindeki hücreler
    for i, p in enumerate(pads):
        o = np.array(PC.outline(p, 48))
        path = Path(o)
        r = max(p['w'], p['h']) / 2 + C + W / 2 + G
        ix0 = max(0, int((p['x'] - r - GP.X0) / G)); ix1 = min(nx - 1, int((p['x'] + r - GP.X0) / G) + 1)
        iy0 = max(0, int((p['y'] - r - GP.Y0) / G)); iy1 = min(ny - 1, int((p['y'] + r - GP.Y0) / G) + 1)
        sub = np.stack(np.meshgrid(xs[ix0:ix1 + 1], ys[iy0:iy1 + 1], indexing='ij'), -1).reshape(-1, 2)
        ins = path.contains_points(sub, radius=-0.15)     # pad içinde (biraz içeride)
        # pad kenarına uzaklık
        import padgeom as geom
        d = np.array([geom.seg_pad((a, b), (a, b), p) for a, b in sub])
        near = d < C + W / 2 + 0.02
        cells = []
        for k, (a, b) in enumerate(sub):
            ix = ix0 + k // (iy1 - iy0 + 1); iy = iy0 + k % (iy1 - iy0 + 1)
            if near[k]:
                padnear[ix, iy] = i if padnear[ix, iy] in (-1, i) else -2
            if ins[k]:
                cells.append((ix, iy))
        if not cells:                              # çok küçük pad: en yakın hücre
            cells = [(int(round((p['x'] - GP.X0) / G)), int(round((p['y'] - GP.Y0) / G)))]
        inside[i] = cells
    return nx, ny, block, padnear, inside

NB = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
      (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]

class Router:
    def __init__(self, pads, W, C):
        self.pads = pads; self.W = W; self.C = C
        self.nx, self.ny, self.block, self.padnear, self.inside = build_grid(pads, W, C)
        self.padnet = [p['net'] for p in pads]
        # yol merkezleri arası en az W+C: bu yarıçap içindeki hücreler "komşu"
        R = W + C - 1e-6
        k = int(math.ceil(R / G))
        self.halo = [(dx, dy) for dx in range(-k, k + 1) for dy in range(-k, k + 1) if math.hypot(dx, dy) * G < R]
        self.use = {}                              # hücre -> {net: sayı}  (yol merkezi + halo)
        self.hist = np.zeros((self.nx, self.ny), float)
        self.routes = {}                           # net -> [yol hücre listeleri]
        self.nets = {}
        for i, p in enumerate(pads):
            if p['net']: self.nets.setdefault(p['net'], []).append(i)
        self.nets = {n: v for n, v in self.nets.items() if len(v) > 1}

    def allowed(self, c, net):
        ix, iy = c
        if self.block[ix, iy]: return False
        pn = self.padnear[ix, iy]
        if pn == -1: return True
        if pn == -2: return False
        return self.padnet[pn] == net

    def add(self, net, path, sign=1):
        for (x, y) in path:
            for dx, dy in self.halo:
                c = (x + dx, y + dy)
                d = self.use.setdefault(c, {})
                d[net] = d.get(net, 0) + sign
                if d[net] <= 0: del d[net]

    def cost(self, c, net, pf):
        d = self.use.get(c)
        other = 0
        if d:
            other = sum(1 for n in d if n != net)
        return (1.0 + self.hist[c]) * (1.0 + pf * other), other

    def astar(self, net, srcs, tgts, tgt_pts, pf):
        tg = set(tgts)
        best = {}
        h0 = lambda c: min(math.hypot(c[0] - t[0], c[1] - t[1]) for t in tgt_pts)
        pq = []
        for s in srcs:
            if s in best: continue
            best[s] = 0.0; heapq.heappush(pq, (h0(s), 0.0, s, None))
        prev = {}
        while pq:
            f, g, c, pr = heapq.heappop(pq)
            if g > best.get(c, 1e18) + 1e-9: continue
            if pr is not None: prev[c] = pr
            if c in tg:
                path = [c]
                while path[-1] in prev: path.append(prev[path[-1]])
                return path[::-1]
            for dx, dy, L in NB:
                n = (c[0] + dx, c[1] + dy)
                if not (0 <= n[0] < self.nx and 0 <= n[1] < self.ny): continue
                if not self.allowed(n, net): continue
                if dx and dy:                       # köşeden geçerken iki yan hücre de geçilebilir olmalı
                    if not (self.allowed((c[0] + dx, c[1]), net) or self.allowed((c[0], c[1] + dy), net)): continue
                k, _ = self.cost(n, net, pf)
                ng = g + L * k
                if ng < best.get(n, 1e18) - 1e-9:
                    best[n] = ng; heapq.heappush(pq, (ng + h0(n), ng, n, c))
        return None

    def route_net(self, net, pf):
        pins = self.nets[net]
        # en yakın komşu sırası (Prim)
        pts = {i: (self.pads[i]['x'], self.pads[i]['y']) for i in pins}
        done = [pins[0]]; rest = set(pins[1:]); paths = []
        tree = set(self.inside[pins[0]])
        while rest:
            i = min(rest, key=lambda j: min(math.dist(pts[j], pts[k]) for k in done))
            k = min(done, key=lambda kk: math.dist(pts[i], pts[kk]))
            tp = [((pts[k][0] - GP.X0) / G, (pts[k][1] - GP.Y0) / G)]
            path = self.astar(net, self.inside[i], tree, tp, pf)
            if path is None:
                rest.discard(i); paths.append(None); continue
            paths.append(path); tree |= set(path); tree |= set(self.inside[i])
            done.append(i); rest.discard(i)
        return paths

    def overused(self):
        bad = set()
        for net, paths in self.routes.items():
            for p in paths:
                if not p: continue
                for c in p:
                    d = self.use.get(c, {})
                    if any(n != net for n in d):
                        bad.add(net); break
        return bad

    def run(self, iters=40, tlimit=1500):
        t0 = time.time(); pf = 0.5
        order = sorted(self.nets, key=lambda n: -len(self.nets[n]))
        for net in order:
            self.routes[net] = self.route_net(net, pf); [self.add(net, p) for p in self.routes[net] if p]
        for it in range(iters):
            bad = self.overused()
            fails = sum(1 for ps in self.routes.values() for p in ps if p is None)
            print('tur %d: çakışan net %d, bulunamayan %d, %.0f s' % (it, len(bad), fails, time.time() - t0), flush=True)
            if not bad and not fails: break
            if time.time() - t0 > tlimit: break
            # tarihçe cezası
            for net in bad:
                for p in self.routes[net]:
                    if not p: continue
                    for c in p:
                        if any(n != net for n in self.use.get(c, {})): self.hist[c] += 0.6
            pf *= float(os.environ.get('PFG', 1.6))
            redo = list(bad) + [n for n, ps in self.routes.items() if any(p is None for p in ps)]
            random.shuffle(redo)
            for net in dict.fromkeys(redo):
                for p in self.routes[net]:
                    if p: self.add(net, p, -1)
                self.routes[net] = self.route_net(net, pf)
                for p in self.routes[net]:
                    if p: self.add(net, p)
        return self.routes

    def final_fix(self):
        """çakışmalı kalan bağlantıları sök (kopuk bırak) — kart temiz kalsın"""
        removed = []
        for _ in range(200):
            bad = self.overused()
            if not bad: break
            # en uzun çakışan yolu sök
            worst = None
            for net in bad:
                for j, p in enumerate(self.routes[net]):
                    if p and any(any(n != net for n in self.use.get(c, {})) for c in p):
                        if worst is None or len(p) > worst[2]: worst = (net, j, len(p))
            net, j, _ = worst
            self.add(net, self.routes[net][j], -1); self.routes[net][j] = None; removed.append(net)
        return removed

def simplify(path):
    if len(path) < 3: return path
    out = [path[0]]
    for a, b, c in zip(path, path[1:], path[2:]):
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]): out.append(b)
    out.append(path[-1]); return out

def segments(router, W):
    segs = []
    for net, paths in router.routes.items():
        for p in paths:
            if not p: continue
            q = simplify(p)
            pts = [(GP.X0 + x * G, GP.Y0 + y * G) for x, y in q]
            # uçları pad merkezine bağla (uç hücre pad içindeyse)
            for end in (0, -1):
                cell = p[end]
                for i in router.nets[net]:
                    if cell in router.inside[i]:
                        c = (router.pads[i]['x'], router.pads[i]['y'])
                        if end == 0: pts.insert(0, c)
                        else: pts.append(c)
                        break
            for a, b in zip(pts, pts[1:]):
                if math.dist(a, b) > 1e-6: segs.append((net, a, b))
    return segs

def write(pcb_in, pcb_out, segs, W):
    b = parse(open(pcb_in, encoding='utf-8').read())
    b = [x for x in b if not (isinstance(x, list) and x and x[0] in ('segment', 'via', 'arc'))]
    k = len(b) - 1
    new = []
    for i, (net, a, c) in enumerate(segs):
        new.append([S('segment'), [S('start'), GP.F(a[0]), GP.F(a[1])], [S('end'), GP.F(c[0]), GP.F(c[1])],
                    [S('width'), GP.F(W)], [S('layer'), 'B.Cu'], [S('net'), net], [S('uuid'), GP.uid('seg', i, a, c)]])
    b[k:k] = new
    open(pcb_out, 'w', encoding='utf-8', newline='\n').write(dump(b) + '\n')

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    W = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    C = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
    b = parse(open(src, encoding='utf-8').read())
    pads = [p for f in find(b, 'footprint') for p in GP.pad_world(f)]
    r = Router(pads, W, C)
    print('ızgara hazır', flush=True)
    random.seed(int(os.environ.get('SEED', 1)))
    r.run(iters=int(os.environ.get('ITERS', 40)), tlimit=float(os.environ.get('TLIM', 1500)))
    rem = r.final_fix()
    print('sökülen:', rem)
    write(src, dst, segments(r, W), W)
