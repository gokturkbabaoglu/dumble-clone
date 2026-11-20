"""Üretilen şemadan bağlantıları geometriyle yeniden çıkarır, design2 netlistiyle karşılaştırır
ve şemanın PNG önizlemesini çizer.  python kicad/yeni_kart/check_sch.py [semboller] [png]"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexp import parse, find, first
import gen_sch as G
import gen_sema as GS

sch = parse(open(os.path.join(HERE, G.PRJ + '.kicad_sch'), encoding='utf-8').read())
libs = {s[1]: s for s in find(first(sch, 'lib_symbols'), 'symbol')}

parent = {}
def fnd(a):
    while parent.setdefault(a, a) != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def uni(a, b): parent[fnd(a)] = fnd(b)
def P(x, y): return (round(float(x), 2), round(float(y), 2))

pinpts = {}      # (ref,num) -> point
wires = []
for w in find(sch, 'wire'):
    a, b = [P(x[1], x[2]) for x in find(first(w, 'pts'), 'xy')]
    wires.append((a, b)); uni(('pt', a), ('pt', b))
for l in find(sch, 'label'):
    at = first(l, 'at'); uni(('pt', P(at[1], at[2])), ('net', l[1]))
power = []
for s in find(sch, 'symbol'):
    libid = first(s, 'lib_id')[1]; at = first(s, 'at')
    X, Y, r = float(at[1]), float(at[2]), int(float(at[3]))
    ref = [p for p in find(s, 'property') if p[1] == 'Reference'][0][2]
    val = [p for p in find(s, 'property') if p[1] == 'Value'][0][2]
    mir = first(s, 'mirror'); mir = mir[1] if mir else None
    for num, (px, py, pa) in G.pins_of(libs[libid]).items():
        (dx, dy), _ = GS.xf(px, py, pa, r, mir)
        pt = P(X + dx * 1.27, Y + dy * 1.27)
        pinpts[(ref, num)] = pt
        if libid == 'power:GND':
            uni(('pt', pt), ('net', 'GND'))
# tellerin ortasına düşen uçlar (T bağlantısı) — bu şemada yok ama kontrol et
allpts = {p for (k, p) in [x for x in parent if x[0] == 'pt']}
for (a, b) in wires:
    for p in allpts:
        if p not in (a, b) and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]):
            if (a[0] == b[0] == p[0]) or (a[1] == b[1] == p[1]):
                uni(('pt', p), ('pt', a))

def grp(ref, num):
    return fnd(('pt', pinpts[(ref, num)]))
def names(root):
    return sorted(k[1] for k in parent if k[0] == 'net' and fnd(k) == root)
bad = 0
net2grp, grp2net = {}, {}
for ref, p in G.PARTS.items():
    for num, net in p['pins'].items():
        g = grp(ref, num)
        if net in net2grp and net2grp[net] != g:
            print('KOPUK', net, ref, num); bad += 1
        net2grp.setdefault(net, g)
        if g in grp2net and grp2net[g] != net:
            print('KISA DEVRE', net, grp2net[g], ref, num); bad += 1
        grp2net.setdefault(g, net)
for net, g in net2grp.items():
    nm = names(g)
    if nm and nm != [net]:
        print('ETİKET UYUŞMAZ', net, nm); bad += 1
# yalnız tek pine bağlı tel/etiket grupları (sarkan uç) kontrolü
cnt = {}
for (ref, num), pt in pinpts.items():
    cnt[fnd(('pt', pt))] = cnt.get(fnd(('pt', pt)), 0) + 1
for (a, b) in wires:
    if fnd(('pt', a)) not in cnt: print('SARKAN TEL', a, b); bad += 1
# şemadaki her bileşen pini bağlı mı?
for (ref, num), pt in pinpts.items():
    if ref.startswith('#'): continue
    if ref in G.PARTS and num not in G.PARTS[ref]['pins']:
        print('BOŞTA PIN', ref, num)
# netlist özetini design2 ile karşılaştır (bağlantı kümesi olarak)
import design2 as D
exp = {}
for ref, (fp, val, nets) in D.C.items():
    if ref in G.SKIP: continue
    for n in nets:
        if not n.startswith('NC'): exp.setdefault(n, 0); exp[n] += 1
got = {}
for ref, p in G.PARTS.items():
    for num, net in p['pins'].items(): got.setdefault(net, 0); got[net] += 1
for n in sorted(set(exp) | set(got)):
    if exp.get(n) != got.get(n): print('NET SAYISI FARKLI', n, exp.get(n), got.get(n)); bad += 1
print('kontrol edilen pin', sum(len(p['pins']) for p in G.PARTS.values()), 'net', len(got), 'hata', bad)

# ------------------------------------------------------------------ önizleme
if len(sys.argv) > 2:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Arc
    fig, ax = plt.subplots(figsize=(594 / 25.4 * 1.6, 420 / 25.4 * 1.6), dpi=110)
    ax.set_xlim(0, 594); ax.set_ylim(420, 0); ax.set_aspect('equal'); ax.axis('off')
    MIR = [None]
    def T(X, Y, r, x, y):
        if MIR[0] == 'x': y = -y
        if MIR[0] == 'y': x = -x
        a, b = G.rot(x, y, r); return X + a, Y - b
    def draw_sym(sym, X, Y, r, mir=None):
        MIR[0] = mir
        for u in find(sym, 'symbol'):
            for g in u:
                if not isinstance(g, list): continue
                k = g[0]
                if k == 'rectangle':
                    s, e = first(g, 'start'), first(g, 'end')
                    pts = [(float(s[1]), float(s[2])), (float(e[1]), float(s[2])), (float(e[1]), float(e[2])), (float(s[1]), float(e[2])), (float(s[1]), float(s[2]))]
                    xs, ys = zip(*[T(X, Y, r, *p) for p in pts]); ax.plot(xs, ys, 'firebrick', lw=0.6)
                elif k == 'polyline':
                    pts = [(float(x[1]), float(x[2])) for x in find(first(g, 'pts'), 'xy')]
                    xs, ys = zip(*[T(X, Y, r, *p) for p in pts]); ax.plot(xs, ys, 'firebrick', lw=0.6)
                elif k == 'circle':
                    c = first(g, 'center'); rad = float(first(g, 'radius')[1])
                    cx, cy = T(X, Y, r, float(c[1]), float(c[2]))
                    ax.add_patch(plt.Circle((cx, cy), rad, fill=False, color='firebrick', lw=0.6))
                elif k == 'arc':
                    pts = [T(X, Y, r, float(first(g, t)[1]), float(first(g, t)[2])) for t in ('start', 'mid', 'end')]
                    (x1, y1), (x2, y2), (x3, y3) = pts
                    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
                    if abs(d) < 1e-9: continue
                    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
                    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
                    R = math.hypot(x1 - ux, y1 - uy)
                    a1, a2, a3 = [math.degrees(math.atan2(y - uy, x - ux)) for x, y in pts]
                    # yönü orta noktaya göre seç
                    def between(a, s, e): return (a - s) % 360 <= (e - s) % 360
                    s, e = (a1, a3) if between(a2, a1, a3) else (a3, a1)
                    ax.add_patch(Arc((ux, uy), 2 * R, 2 * R, theta1=s, theta2=e, color='firebrick', lw=0.6))
                elif k == 'pin':
                    at = first(g, 'at'); L = float(first(g, 'length')[1])
                    px, py, pa = float(at[1]), float(at[2]), float(at[3])
                    qx, qy = px + L * math.cos(math.radians(pa)), py + L * math.sin(math.radians(pa))
                    (a, b), (c, d) = T(X, Y, r, px, py), T(X, Y, r, qx, qy)
                    ax.plot([a, c], [b, d], 'firebrick', lw=0.6)
    for s in find(sch, 'symbol'):
        libid = first(s, 'lib_id')[1]; at = first(s, 'at')
        X, Y, r = float(at[1]), float(at[2]), int(float(at[3]))
        mir = first(s, 'mirror'); draw_sym(libs[libid], X, Y, r, mir[1] if mir else None)
        for p in find(s, 'property'):
            if p[1] not in ('Reference', 'Value'): continue
            eff = first(p, 'effects')
            if first(eff, 'hide') is not None: continue
            pa = first(p, 'at'); j = first(eff, 'justify')
            ha = 'left' if j and 'left' in j else ('right' if j and 'right' in j else 'center')
            ax.text(float(pa[1]), float(pa[2]), p[2], fontsize=5, ha=ha, va='center',
                    rotation=float(pa[3]), color='teal' if p[1] == 'Reference' else 'black')
    for (a, b) in wires:
        ax.plot([a[0], b[0]], [a[1], b[1]], 'green', lw=0.6)
    for l in find(sch, 'label'):
        at = first(l, 'at'); ang = float(at[3])
        ha = 'left' if ang in (0, 90) else 'right'
        ax.text(float(at[1]), float(at[2]) - 0.3, l[1], fontsize=4.5, ha=ha, va='bottom',
                rotation=(ang if ang in (0, 90) else ang - 180), rotation_mode='anchor', color='navy')
    for jn in find(sch, 'junction'):
        at = first(jn, 'at'); ax.add_patch(plt.Circle((float(at[1]), float(at[2])), 0.5, color='green'))
    for t in find(sch, 'text'):
        at = first(t, 'at'); ax.text(float(at[1]), float(at[2]), t[1], fontsize=7, weight='bold', va='bottom')
    for rc in find(sch, 'rectangle'):
        s, e = first(rc, 'start'), first(rc, 'end')
        x1, y1, x2, y2 = map(float, (s[1], s[2], e[1], e[2]))
        ax.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], color='gray', lw=0.5, ls='--')
    ax.plot([0, 594, 594, 0, 0], [0, 0, 420, 420, 0], 'k', lw=0.5)
    fig.savefig(sys.argv[2], bbox_inches='tight')
    print('png', sys.argv[2])
