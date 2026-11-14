"""Yönlendirilmiş .kicad_pcb dosyasını okur: bağlanmamış bağlantılar, yol uzunlukları, gürültü ölçütleri, görsel.
Kullanım: python kicad/analiz.py kart.kicad_pcb [cikti.png]
"""
import sys, re, math, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

def sexp(txt):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt)
    st = [[]]
    for t in tok:
        if t == '(': st.append([])
        elif t == ')': x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1] if t.startswith('"') else t)
    return st[0][0]
def find(node, key): return [c for c in node if isinstance(c, list) and c and c[0] == key]
def one(node, key):
    r = find(node, key); return r[0] if r else None

def rot(x, y, r):
    c, s = math.cos(math.radians(r)), math.sin(math.radians(r))
    return x * c + y * s, -x * s + y * c

def load(path):
    B = sexp(open(path, encoding='utf-8').read())
    nets = {int(n[1]): n[2] for n in find(B, 'net') if len(n) > 2}
    def nn(n):
        if not n: return ''
        return n[2] if len(n) > 2 else (nets.get(int(n[1]), n[1]) if n[1].isdigit() else n[1])
    pads = []   # (x,y,size,net,ref,num)
    fps = {}
    for fp in find(B, 'footprint'):
        at = one(fp, 'at'); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0
        ref = [p[2] for p in find(fp, 'property') if p[1] == 'Reference'][0]
        fps[ref] = (fx, fy, fr)
        for p in find(fp, 'pad'):
            pa = one(p, 'at'); px, py = float(pa[1]), float(pa[2])
            dx, dy = rot(px, py, fr)
            sz = float(one(p, 'size')[1]); n = one(p, 'net')
            pads.append((fx + dx, fy + dy, sz, nn(n), ref, p[1]))
    segs = []
    for s in find(B, 'segment'):
        a = one(s, 'start'); b = one(s, 'end')
        segs.append(((float(a[1]), float(a[2])), (float(b[1]), float(b[2])), float(one(s, 'width')[1]), one(s, 'layer')[1], nn(one(s, 'net'))))
    vias = find(B, 'via')
    edge = [g for g in find(B, 'gr_rect') if one(g, 'layer')[1] == 'Edge.Cuts']
    e = edge[0]; ex0, ey0 = float(one(e, 'start')[1]), float(one(e, 'start')[2]); ex1, ey1 = float(one(e, 'end')[1]), float(one(e, 'end')[2])
    return dict(pads=pads, segs=segs, vias=len(vias), fps=fps, edge=(ex0, ey0, ex1, ey1))

def connectivity(D):
    """Her net için kopuk ada sayısı (pad + yol uçları; yol uçları pad içinde ya da başka yol üstünde)."""
    par = {}
    def fnd(a):
        while par.setdefault(a, a) != a: par[a] = par[par[a]]; a = par[a]
        return a
    def uni(a, b): par[fnd(a)] = fnd(b)
    bynet = {}
    for i, p in enumerate(D['pads']):
        if p[3]: bynet.setdefault(p[3], {'pads': [], 'segs': []})['pads'].append(i)
    for j, s in enumerate(D['segs']): bynet.setdefault(s[4], {'pads': [], 'segs': []})['segs'].append(j)
    def on_seg(pt, s, tol):
        (ax, ay), (bx, by) = s[0], s[1]
        vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((pt[0] - ax) * vx + (pt[1] - ay) * vy) / L))
        return math.dist(pt, (ax + t * vx, ay + t * vy)) <= tol
    res = {}
    for n, d in bynet.items():
        for j in d['segs']:
            s = D['segs'][j]; uni(('s', j), ('s', j))
            for k in d['pads']:
                p = D['pads'][k]
                for e in (s[0], s[1]):
                    if math.dist(e, p[:2]) <= p[2] / 2: uni(('s', j), ('p', k))
                if on_seg(p[:2], s, 0.05): uni(('s', j), ('p', k))
            for j2 in d['segs']:
                if j2 <= j: continue
                s2 = D['segs'][j2]
                if any(on_seg(e, s2, 0.02) for e in (s[0], s[1])) or any(on_seg(e, s, 0.02) for e in (s2[0], s2[1])): uni(('s', j), ('s', j2))
        groups = {fnd(('p', k)) for k in d['pads']}
        res[n] = len(groups) - 1 if d['pads'] else 0
    return res

def score(D, conn):
    """Raporlardaki gürültü ölçütlerine göre sayısal göstergeler."""
    P = {}
    for p in D['pads']: P.setdefault((p[4], p[5]), p)
    def pad(ref, num): return P[(ref, str(num))]
    def netlen(*names): return sum(math.dist(s[0], s[1]) for s in D['segs'] if s[4] in names)
    out = {}
    out['kopuk_baglanti'] = sum(conn.values())
    out['kopuk_netler'] = sorted(n for n, v in conn.items() if v)
    out['via'] = D['vias']
    out['ust_kat_yol'] = sum(1 for s in D['segs'] if s[3] != 'B.Cu')
    out['toplam_yol_mm'] = round(sum(math.dist(s[0], s[1]) for s in D['segs']))
    out['giris_yolu_mm'] = round(netlen('IN', 'GATE'), 1)
    out['giris_kati_mm'] = round(netlen('IN', 'GATE', 'SRC', 'DRAIN', 'DRV'), 1)
    # giriş katının güç katına uzaklığı
    q1 = pad('Q1', 1); u2 = pad('U2', 4)
    out['Q1_TDA_mesafe_mm'] = round(math.dist(q1[:2], u2[:2]), 1)
    # giriş netlerine en yakın güç/çıkış yolu
    hot = [s for s in D['segs'] if s[4] in ('TOUT', 'SPK', 'SPKT', 'V12', 'VIN', 'DCIN', 'FUSED')]
    inp = [s for s in D['segs'] if s[4] in ('IN', 'GATE')] + [((p[0], p[1]), (p[0], p[1]), p[2], 'B.Cu', p[3]) for p in D['pads'] if p[3] in ('IN', 'GATE')]
    def segdist(a, b):
        def pd(p, s):
            (ax, ay), (bx, by) = s[0], s[1]; vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy
            t = 0 if L == 0 else max(0, min(1, ((p[0] - ax) * vx + (p[1] - ay) * vy) / L))
            return math.dist(p, (ax + t * vx, ay + t * vy))
        return min(pd(a[0], b), pd(a[1], b), pd(b[0], a), pd(b[1], a))
    out['giris_guc_en_yakin_mm'] = round(min((segdist(a, b) for a in inp for b in hot), default=99), 1)
    # büyük akım döngüsü: TDA çıkışı -> C25 -> hoparlör (TB2) -> GND dönüşü (TB2 GND pad - TDA GND pin)
    loop = [pad('U2', 4), pad('C25', 1), pad('C25', 2), pad('TB2', 1), pad('TB2', 2), pad('U2', 3)]
    a = 0
    for i in range(len(loop)):
        x1, y1 = loop[i][:2]; x2, y2 = loop[(i + 1) % len(loop)][:2]; a += x1 * y2 - x2 * y1
    out['hoparlor_dongu_alani_mm2'] = round(abs(a) / 2)
    out['TIN_yolu_mm'] = round(netlen('TIN', 'Z'), 1)
    # dekuplaj mesafeleri
    out['C4_LM386_6_mm'] = round(math.dist(pad('C4', 1)[:2], pad('U1', 6)[:2]), 1)
    out['C6_TDA_5_mm'] = round(math.dist(pad('C6', 1)[:2], pad('U2', 5)[:2]), 1)
    out['C12_LM386_7_mm'] = round(math.dist(pad('C12', 1)[:2], pad('U1', 7)[:2]), 1)
    out['C23_TDA_2_mm'] = round(min(math.dist(pad('R26', k)[:2], pad('U2', 2)[:2]) for k in (1, 2)), 1)
    out['ton_yuksek_emp_mm'] = round(netlen('USOUT', 'UKOUT', 'ISFW', 'VOLW'), 1)
    out['V2_V3_yol_mm'] = round(netlen('V2', 'V3'), 1)
    return out

def draw(D, path, title=''):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    x0, y0, x1, y1 = D['edge']
    fig, ax = plt.subplots(figsize=(13, 8.5), dpi=120)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=True, fc='#f4ead5', ec='k'))
    col = lambda n: '#c0392b' if n in ('IN', 'GATE', 'SRC', 'DRAIN', 'DRV') else ('#2471a3' if n in ('V12', 'VIN', 'DCIN', 'FUSED', 'V2', 'V3') else ('#7d3c98' if n in ('TOUT', 'SPK', 'SPKT', 'TNEG', 'TRC', 'ZOB2', 'HPS') else ('#1e8449' if n == 'GND' else '#b9770e')))
    for s in D['segs']:
        ax.plot([s[0][0], s[1][0]], [s[0][1], s[1][1]], color=col(s[4]), lw=s[2] * 2.2, solid_capstyle='round')
    for p in D['pads']:
        ax.add_patch(Circle(p[:2], p[2] / 2, color=col(p[3]) if p[3] else '#888', zorder=3))
    for ref, (fx, fy, fr) in D['fps'].items():
        ax.text(fx, fy - 2.2, ref, fontsize=5, ha='center', zorder=4)
    ax.set_xlim(x0 - 2, x1 + 2); ax.set_ylim(y1 + 2, y0 - 2); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title + '  (parça yüzünden bakış; alt kenar = ön panel)  kırmızı: giriş, mavi: besleme, mor: çıkış, yeşil: GND', fontsize=8)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)

if __name__ == '__main__':
    D = load(sys.argv[1]); c = connectivity(D); s = score(D, c)
    print(json.dumps(s, ensure_ascii=False, indent=1))
    if len(sys.argv) > 2: draw(D, sys.argv[2], os.path.basename(sys.argv[1]))
