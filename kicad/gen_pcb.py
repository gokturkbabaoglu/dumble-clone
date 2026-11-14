"""PCB yerleşim üreticisi: sabit parçalar + bölgelere göre otomatik paketleme -> amfi_<v>.kicad_pcb
Yönlendirmeyi Freerouting yapar (KiCad eklentisi). Çalıştır: python kicad/gen_pcb.py A B C
"""
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_kicad as G
D = G.D
f, q, uid = G.f, G.q, G.uid

W = 185.0
H = float(os.environ.get('KART_H', '114.3'))   # kart derinliği (mm); ön kenar y = H
OX, OY = 30.0, 30.0           # KiCad sayfasındaki kayma
GAP = 2.54                    # avlular arası boşluk (aradan bir yol geçsin)
EDGE = 1.0
STRIP = 2.5                   # kenar GND şeridi (yol yok)
GND_RING = 0.0                # kenar GND yolu eksen uzaklığı (0 = yok)
RING_W = 1.5

# ------------------------------ sabit parçalar ------------------------------
FX = {'J1': 12, 'RV4': 34, 'RV1': 56, 'SW1': 77, 'RV2': 99, 'RV3': 123, 'J2': 145, 'D2': 160, 'SW2': 175}
def fixed(front=FX):
    P = {}
    for r in ('J1', 'RV4', 'RV1', 'RV2', 'RV3', 'J2', 'D2'):
        P[r] = (front[r], H, 0)
    sw1, sw2 = front['SW1'], front['SW2']
    P['P1'] = (sw1 - 4, H - 23, 0); P['P2'] = (sw1, H - 23, 0); P['P3'] = (sw1 + 4, H - 23, 0)
    P['P4'] = (sw2 - 2.5, H - 25, 0); P['P5'] = (sw2 + 2.5, H - 25, 0)
    P['MH1'] = (6, 6, 0); P['MH2'] = (W - 6, 6, 0); P['MH3'] = (92, 6, 0)
    P['MH4'] = (6, H - 34, 0); P['MH5'] = (W - 5.5, H - 39, 0)   # ön taraf (kullanıcı isteği)
    return P
# panel anahtar gövdeleri (kartın üstünde, parça konmaz): (x0,y0,x1,y1)
def keepouts(front=FX):
    return [(front['SW1'] - 7.5, H - 20, front['SW1'] + 7.5, H), (front['SW2'] - 8.5, H - 22, front['SW2'] + 8.5, H)]

# ------------------------------ gruplar ------------------------------
GROUPS = {
    'IN':   ['Q1', 'R5', 'R6', 'JP1', 'R4', 'TR1', 'C9', 'C10', 'R2', 'C5'],
    'GAIN': ['U1', 'R7', 'CB1', 'CD1', 'R8', 'C11', 'C12', 'R9', 'C13', 'C14', 'R1', 'C3', 'C8', 'C4'],
    'US':   ['R10', 'R11', 'C15', 'C26', 'C16', 'C17', 'R13', 'R14', 'R15', 'R16'],
    'UK':   ['R12', 'R17', 'R18', 'C18', 'C19', 'C20', 'R19', 'R20', 'R30', 'R21', 'R22', 'R31'],
    'VOL':  ['R23', 'R24', 'C21', 'C22'],
    'TDA':  ['U2', 'C6', 'C7', 'R25', 'R26', 'C23', 'R27', 'C24'],
    'OUT':  ['C25', 'R28', 'R29', 'TB2'],
    'PWR':  ['TB1', 'F1', 'D1', 'C1', 'C2', 'R3'],
}
_g = sum(GROUPS.values(), [])
assert sorted(_g + list(fixed())) == sorted(G.PARTS), set(G.PARTS) ^ set(_g + list(fixed()))

# Yerleşim varyantları: grup -> (bölge x0,y0,x1,y1, tarama 'top'|'bottom'|'left'|'right', eksenel yön 0|90)
VARIANTS = {
 'A': dict(order=['TDA', 'PWR', 'IN', 'GAIN', 'VOL', 'OUT', 'US', 'UK'], g={
    'IN':   ((2, 40, 48, H), 'bottom', 90),
    'GAIN': ((40, 40, 95, H), 'bottom', 90),
    'US':   ((40, 2, 110, 50), 'top', 90),
    'UK':   ((90, 40, 140, H), 'bottom', 90),
    'VOL':  ((115, 30, 150, H), 'bottom', 90),
    'TDA':  ((130, 2, 183, 40), 'top', 90),
    'PWR':  ((150, 25, 183, H), 'right', 90),
    'OUT':  ((130, 40, 183, H), 'bottom', 90)}),
 'B': dict(order=['TDA', 'PWR', 'IN', 'GAIN', 'VOL', 'OUT', 'UK', 'US'], g={
    'IN':   ((2, 2, 45, H), 'bottom', 0),
    'GAIN': ((35, 30, 92, H), 'bottom', 0),
    'US':   ((70, 2, 130, 60), 'top', 0),
    'UK':   ((85, 35, 140, H), 'bottom', 0),
    'VOL':  ((110, 30, 150, H), 'bottom', 0),
    'TDA':  ((130, 2, 183, 40), 'top', 0),
    'PWR':  ((150, 25, 183, H), 'right', 0),
    'OUT':  ((130, 40, 183, H), 'bottom', 0)}),
 'C': dict(order=['TDA', 'PWR', 'IN', 'GAIN', 'US', 'UK', 'VOL', 'OUT'], g={
    'IN':   ((2, 30, 50, H), 'bottom', 90),
    'GAIN': ((2, 2, 70, 60), 'top', 0),
    'US':   ((60, 2, 125, 55), 'left', 90),
    'UK':   ((60, 45, 135, H), 'left', 90),
    'VOL':  ((110, 40, 150, H), 'bottom', 90),
    'TDA':  ((128, 2, 183, 40), 'top', 0),
    'PWR':  ((150, 25, 183, H), 'right', 0),
    'OUT':  ((128, 40, 183, H), 'bottom', 0)}),
}
AXIAL = {'R', 'CF', 'CC', 'JMP', 'DO201', 'FUSE'}

# ------------------------------ geometri ------------------------------
def rect_of(ref, x, y, r):
    fp = G.PARTS[ref][0]
    x0, y0, x1, y1 = G.fp_extent(fp)
    pts = [G._rot(a, b, r) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs = [x + p[0] for p in pts]; ys = [y + p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
def overlap(a, b, g):
    return not (a[2] + g <= b[0] or b[2] + g <= a[0] or a[3] + g <= b[1] or b[3] + g <= a[1])
def pads_abs(ref, x, y, r):
    fp = G.PARTS[ref][0]
    return [(x + G._rot(px, py, r)[0], y + G._rot(px, py, r)[1]) for px, py in D.FP[fp]['pins']]

def place(vname, front=FX):
    V = VARIANTS[vname]
    P = fixed(front)
    occ = [rect_of(r, *P[r]) for r in P if not r.startswith('P') or True]
    occ += keepouts(front)
    # sabit güç parçaları (sağ kenar)
    for ref in V['order']:
        (x0, y0, x1, y1), scan, ax = V['g'][ref]
        for part in GROUPS[ref]:
            fp = G.PARTS[part][0]
            rots = [ax] if fp in AXIAL else [0]
            if part in ('TB1', 'TB2'): rots = [90]
            if part == 'U2': rots = [0]
            best = None
            step = 1.27
            xs = [x0 + i * step for i in range(int((x1 - x0) / step) + 1)]
            ys = [y0 + i * step for i in range(int((y1 - y0) / step) + 1)]
            if scan == 'bottom': order = [(x, y) for y in reversed(ys) for x in xs]
            elif scan == 'top': order = [(x, y) for y in ys for x in xs]
            elif scan == 'right': order = [(x, y) for x in reversed(xs) for y in ys]
            else: order = [(x, y) for x in xs for y in ys]
            for (x, y) in order:
                for r in rots:
                    rc = rect_of(part, x, y, r)
                    if rc[0] < EDGE or rc[1] < EDGE or rc[2] > W - EDGE or rc[3] > H - EDGE: continue
                    if rc[0] < x0 or rc[2] > x1 or rc[1] < y0 or rc[3] > y1: continue
                    if any(overlap(rc, o, GAP) for o in occ): continue
                    best = (x, y, r); break
                if best: break
            if not best:
                if (x0, y0, x1, y1) != (0, 0, W, H):
                    print('  uyarı: %s %s bölgesine sığmadı, bütün kartta aranıyor' % (vname, part))
                    V['g'][ref] = ((0, 0, W, H), scan, ax)
                    (x0, y0, x1, y1) = (0, 0, W, H)
                    xs = [x0 + i * step for i in range(int((x1 - x0) / step) + 1)]
                    ys = [y0 + i * step for i in range(int((y1 - y0) / step) + 1)]
                    order = [(x, y) for y in reversed(ys) for x in xs] if scan == 'bottom' else [(x, y) for y in ys for x in xs]
                    for (x, y) in order:
                        for r in rots:
                            rc = rect_of(part, x, y, r)
                            if rc[0] < EDGE or rc[1] < EDGE or rc[2] > W - EDGE or rc[3] > H - EDGE: continue
                            if any(overlap(rc, o, GAP) for o in occ): continue
                            best = (x, y, r); break
                        if best: break
                if not best: raise SystemExit('%s: %s yerleşmedi' % (vname, part))
            P[part] = best
            occ.append(rect_of(part, *best))
    return P

# ------------------------------ kalite ölçüleri ------------------------------
def nets_pads(P):
    N = {}
    for ref, (fp, val, nets) in G.PARTS.items():
        if fp == 'MH': continue
        for (x, y), n in zip(pads_abs(ref, *P[ref]), nets):
            N.setdefault(n, []).append((x, y, ref))
    return N
def mst(pts):
    if len(pts) < 2: return []
    used = [0]; E = []
    rest = list(range(1, len(pts)))
    while rest:
        b = min(((i, j) for i in used for j in rest), key=lambda e: math.dist(pts[e[0]][:2], pts[e[1]][:2]))
        E.append((pts[b[0]], pts[b[1]])); used.append(b[1]); rest.remove(b[1])
    return E
def seg_cross(a, b, c, d):
    def o(p, q_, r): return (q_[0] - p[0]) * (r[1] - p[1]) - (q_[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0
def metrics(P):
    N = nets_pads(P)
    E = {n: mst(p) for n, p in N.items() if not n.startswith('NC')}
    tot = sum(math.dist(a[:2], b[:2]) for e in E.values() for a, b in e)
    flat = [(n, a, b) for n, e in E.items() for a, b in e]
    cross = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i][0] != flat[j][0] and seg_cross(flat[i][1], flat[i][2], flat[j][1], flat[j][2]): cross += 1
    inlen = sum(math.dist(a[:2], b[:2]) for n in ('IN', 'GATE') for a, b in E[n])
    return dict(ratsnest_mm=round(tot), kesisme=cross, giris_mm=round(inlen, 1)), E

# ------------------------------ .kicad_pcb ------------------------------
LAYERS = '''\t(layers
\t\t(0 "F.Cu" signal) (31 "B.Cu" signal)
\t\t(32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive")
\t\t(34 "B.Paste" user) (35 "F.Paste" user)
\t\t(36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen")
\t\t(38 "B.Mask" user) (39 "F.Mask" user)
\t\t(40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments")
\t\t(42 "Eco1.User" user "User.Eco1") (43 "Eco2.User" user "User.Eco2")
\t\t(44 "Edge.Cuts" user) (45 "Margin" user)
\t\t(46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard")
\t\t(48 "B.Fab" user) (49 "F.Fab" user)
\t)
'''
def zone_rule(name, layer, pts, tracks=False, pour=True, fps=True, key=''):
    return ('\t(zone (net 0) (net_name "") (layer %s) (uuid %s) (name %s) (hatch edge 0.5)\n'
            '\t\t(connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no)\n'
            '\t\t(keepout (tracks %s) (vias not_allowed) (pads allowed) (copperpour %s) (footprints %s))\n'
            '\t\t(fill (thermal_gap 0.5) (thermal_bridge_width 0.5))\n'
            '\t\t(polygon (pts %s)))\n') % (q(layer), q(uid('zone', key, name)), q(name),
                                          'allowed' if tracks else 'not_allowed', 'allowed' if pour else 'not_allowed',
                                          'allowed' if fps else 'not_allowed',
                                          ' '.join('(xy %s %s)' % (f(x + OX), f(y + OY)) for x, y in pts))
def rectpts(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def write_pcb(vname, P, path, with_gnd_zone=False):
    netnames = sorted({n for v in G.PARTS.values() for n in v[2] if not n.startswith('NC')})
    netnum = {n: i + 1 for i, n in enumerate(netnames)}
    for n in {n for v in G.PARTS.values() for n in v[2] if n.startswith('NC')}: netnum[n] = 0
    s = '(kicad_pcb\n\t(version 20240108)\n\t(generator "amfi_gen")\n\t(generator_version "8.0")\n'
    s += '\t(general (thickness 1.6) (legacy_teardrops no))\n\t(paper "A3")\n'
    s += '\t(title_block (title %s) (date "2026-11-14") (rev %s))\n' % (q('12V Gitar Amfisi - tek yüz'), q(vname))
    s += LAYERS
    s += '\t(setup (pad_to_mask_clearance 0) (allow_soldermask_bridges_in_footprints no))\n'
    s += '\t(net 0 "")\n' + ''.join('\t(net %d %s)\n' % (netnum[n], q(n)) for n in netnames)
    for ref, (fp, val, nets) in sorted(G.PARTS.items()):
        x, y, r = P[ref]
        name = G.fpname(fp)
        x0, y0, x1, y1 = G.fp_extent(fp)
        s += '\t(footprint %s (layer "F.Cu") (uuid %s) (at %s %s %s)\n' % (q(G.PRJ + ':' + name), q(uid('fp', ref)), f(x + OX), f(y + OY), f(r))
        s += '\t\t(property "Reference" %s (at %s %s %s) (layer "F.SilkS") (uuid %s) (effects (font (size 1 1) (thickness 0.15))))\n' % (
            q(ref), f((x0 + x1) / 2), f(y0 - 0.8), f(r), q(uid('fpref', ref)))
        s += '\t\t(property "Value" %s (at %s %s %s) (layer "F.Fab") (uuid %s) (effects (font (size 1 1) (thickness 0.15))))\n' % (
            q(val), f((x0 + x1) / 2), f(y1 + 0.8), f(r), q(uid('fpval', ref)))
        s += '\t\t(property "Footprint" %s (at 0 0 %s) (layer "F.Fab") (hide yes) (uuid %s) (effects (font (size 1 1) (thickness 0.15))))\n' % (
            q(G.PRJ + ':' + name), f(r), q(uid('fpfp', ref)))
        s += '\t\t(path %s) (sheetname "Root") (sheetfile %s)\n' % (q('/' + G.uid('sym', ref)), q(G.PRJ + '.kicad_sch'))
        s += '\t\t(attr through_hole%s)\n' % (' exclude_from_bom' if fp == 'MH' else '')
        s += ''.join('\t\t' + it + '\n' for it in G.fp_items(fp, r, nets, netnum, key=ref))
        s += '\t)\n'
    s += '\t(gr_rect (start %s %s) (end %s %s) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts") (uuid %s))\n' % (
        f(OX), f(OY), f(OX + W), f(OY + H), q(uid('edge', vname)))
    # üst kat tamamen yasak (tek yüz): yol ve via yok
    s += zone_rule('ust_kat_yasak', 'F.Cu', rectpts(0, 0, W, H), tracks=False, pour=False, key=vname)
    # panel anahtar gövdeleri: parça yok (yol serbest)
    for i, k in enumerate(keepouts()):
        s += zone_rule('anahtar_govdesi_%d' % (i + 1), 'F.Cu', rectpts(*k), tracks=True, pour=True, fps=False, key=vname + str(i))
    # Kenarda kesintisiz GND yolu (kilitli; Freerouting dokunmaz). Ön kenarda J2'nin 1. pini kenara taştığı için
    # ön kenar şeridi J2'nin solunda biter; sağ ön köşe sağ kenardan beslenir.
    if GND_RING:
        g = GND_RING; wd = RING_W; jx = P['J2'][0]
        pts = [(jx - 6, H - g), (g, H - g), (g, g), (W - g, g), (W - g, H - g), (jx + 6, H - g)]
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            s += '\t(segment (start %s %s) (end %s %s) (width %s) (layer "B.Cu") (locked yes) (net %d) (uuid %s))\n' % (
                f(x1 + OX), f(y1 + OY), f(x2 + OX), f(y2 + OY), f(wd), netnum['GND'], q(uid('ring', vname, i)))
    if with_gnd_zone:
        s += ('\t(zone (net %d) (net_name "GND") (layer "B.Cu") (uuid %s) (name "GND") (hatch edge 0.5)\n'
              '\t\t(connect_pads (clearance 0.5)) (min_thickness 0.5) (filled_areas_thickness no)\n'
              '\t\t(fill yes (thermal_gap 0.5) (thermal_bridge_width 1.0) (island_removal_mode 1))\n'
              '\t\t(polygon (pts %s)))\n') % (netnum['GND'], q(uid('gndzone', vname)),
                                             ' '.join('(xy %s %s)' % (f(x + OX), f(y + OY)) for x, y in rectpts(EDGE, EDGE, W - EDGE, H - EDGE)))
    s += ')\n'
    open(path, 'w', encoding='utf-8').write(s)

# ------------------------------ önizleme ------------------------------
def preview(vname, P, E, m, path):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=110)
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.5))
    for k in keepouts(): ax.add_patch(Rectangle((k[0], k[1]), k[2] - k[0], k[3] - k[1], color='#ddd'))
    grp = {p: g for g, L in GROUPS.items() for p in L}
    col = {'IN': '#d62728', 'GAIN': '#ff7f0e', 'US': '#2ca02c', 'UK': '#17becf', 'VOL': '#9467bd', 'TDA': '#8c564b', 'OUT': '#e377c2', 'PWR': '#7f7f7f'}
    for ref in G.PARTS:
        rc = rect_of(ref, *P[ref]); c = col.get(grp.get(ref), 'k')
        ax.add_patch(Rectangle((rc[0], rc[1]), rc[2] - rc[0], rc[3] - rc[1], fill=False, ec=c, lw=0.8))
        ax.text((rc[0] + rc[2]) / 2, (rc[1] + rc[3]) / 2, ref, ha='center', va='center', fontsize=5.5, color=c)
        for x, y in pads_abs(ref, *P[ref]): ax.add_patch(Circle((x, y), 0.7, color='#b87333'))
    for n, e in E.items():
        c = '#d62728' if n in ('IN', 'GATE', 'SRC', 'DRAIN') else ('#1f77b4' if n in D.POWER_NETS else ('#2ca02c' if n == 'GND' else '#999'))
        for a, b in e: ax.plot([a[0], b[0]], [a[1], b[1]], lw=0.5, color=c)
    ax.set_xlim(-3, W + 3); ax.set_ylim(H + 3, -8); ax.set_aspect('equal')
    ax.set_title('Yerleşim %s — ratsnest %s mm, kesişme %s, giriş yolu %s mm  (alt kenar = ön panel)' % (vname, m['ratsnest_mm'], m['kesisme'], m['giris_mm']))
    ax.axis('off'); fig.tight_layout(); fig.savefig(path); plt.close(fig)

if __name__ == '__main__':
    out = os.path.join(HERE, 'amfi')
    res = {}
    for v in (sys.argv[1:] or list(VARIANTS)):
        P = place(v)
        m, E = metrics(P)
        res[v] = m
        write_pcb(v, P, os.path.join(out, 'amfi_%s.kicad_pcb' % v))
        preview(v, P, E, m, os.path.join(HERE, 'onizleme_%s.png' % v))
        json.dump({k: list(val) for k, val in P.items()}, open(os.path.join(HERE, 'yerlesim_%s.json' % v), 'w'), indent=0)
        print(v, m)
