"""Yeni kartın PCB dosyasını üretir: 185 x 96 mm kart, yalnız B.Cu, amfi_yeni.pretty ayak izleri.

Yerleşim: önceki kartın (kicad/amfi/amfi.kicad_pcb, kalin-yollar) parça konumları başlangıç alınır;
her parça, pad konumları eski karttakine en iyi oturacak açıyla yerleştirilir. Yollar bu betikte yok
(Freerouting ya da elle).  Çalıştır: python kicad/yeni_kart/gen_pcb.py ESKI_KART.kicad_pcb
"""
import os, sys, math, uuid, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexp import parse, dump, Sym as S, find, first
import gen_sch as G

OLD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'amfi', 'amfi.kicad_pcb')
LIBDIR = os.path.join(HERE, 'amfi_yeni.pretty')
NS = uuid.UUID('4d0c2b7e-2a61-4f39-9b7c-3c1e6f0a9d55')
def uid(*k): return str(uuid.uuid5(NS, '/'.join(map(str, k))))
def F(v): return S(('%.4f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-9 else '0')
X0, Y0, W, H = 30.0, 30.0, 185.0, 96.0          # kart: (30,30)-(215,126), ön kenar y=126

# eski pad adı -> yeni pad adı
PADMAP = {'J1': {'1': 'S', '2': 'TN', '3': 'T'}, 'J2': {'1': 'S', '2': 'RN', '3': 'R', '4': 'T', '5': 'TN'},
          'D1': {'1': '2', '2': '1'}, 'D2': {'1': '2', '2': '1'}}
FIT_ONLY = {'U2': {'1', '3', '5'}}                # Pentawatt: tek sıra bacaklarla hizala (kademeli sıra standartta ters)

def rot(x, y, a):
    """KiCad: y aşağı, pozitif açı ekranda saat yönünün tersi"""
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return x * c + y * s, -x * s + y * c

def old_positions():
    b = parse(open(OLD, encoding='utf-8').read())
    res = {}
    for f in find(b, 'footprint'):
        ref = [p for p in find(f, 'property') if p[1] == 'Reference'][0][2]
        at = first(f, 'at'); fx, fy = float(at[1]), float(at[2]); fa = float(at[3]) if len(at) > 3 else 0
        pads = {}
        for p in find(f, 'pad'):
            pa = first(p, 'at'); dx, dy = rot(float(pa[1]), float(pa[2]), fa)
            pads[PADMAP.get(ref, {}).get(p[1], p[1])] = (fx + dx, fy + dy)
        res[ref] = (fx, fy, fa, pads)
    return res

def load_fp(name):
    return parse(open(os.path.join(LIBDIR, name + '.kicad_mod'), encoding='utf-8').read())

def fit(ref, fp, old):
    """eski pad konumlarına en iyi oturan (x, y, açı)"""
    fx, fy, fa, opads = old
    lp = {p[1]: (float(first(p, 'at')[1]), float(first(p, 'at')[2])) for p in find(fp, 'pad')}
    keys = [k for k in lp if k in opads and (ref not in FIT_ONLY or k in FIT_ONLY[ref])]
    if not keys:                                    # padsız eşleşme (MH): eski konum
        return fx, fy, fa, 0
    best = None
    for a in (0, 90, 180, 270):
        rp = {k: rot(*lp[k], a) for k in keys}
        tx = sum(opads[k][0] - rp[k][0] for k in keys) / len(keys)
        ty = sum(opads[k][1] - rp[k][1] for k in keys) / len(keys)
        err = sum(math.hypot(opads[k][0] - rp[k][0] - tx, opads[k][1] - rp[k][1] - ty) for k in keys) / len(keys)
        if best is None or err < best[3] - 1e-6:
            best = (tx, ty, a, err)
    return best

def place_fp(ref, part, x, y, a, sym_uuid):
    name = part['footprint'].split(':')[1]
    fp = load_fp(name)
    out = [S('footprint'), part['footprint'], [S('layer'), 'F.Cu'], [S('uuid'), uid('fp', ref)],
           [S('at'), F(x), F(y)] + ([F(a)] if a else [])]
    for e in fp[2:]:
        if not isinstance(e, list): continue
        k = e[0]
        if k in ('version', 'generator', 'generator_version', 'layer', 'tags'):
            continue
        e = copy.deepcopy(e)
        if k == 'property':
            if e[1] == 'Reference': e[2] = ref
            if e[1] == 'Value': e[2] = part['value']
            at = first(e, 'at')
            if at is not None and a:
                ang = (float(at[3]) if len(at) > 3 else 0) + a
                del at[3:]; at.append(F(ang % 360))
        if k == 'pad':
            at = first(e, 'at')
            if a:
                ang = (float(at[3]) if len(at) > 3 else 0) + a
                del at[3:]; at.append(F(ang % 360))
            net = part['pins'].get(e[1])
            if net:
                e.append([S('net'), net])
            u = first(e, 'uuid')
            if u is None: e.append([S('uuid'), uid('pad', ref, e[1])])
            else: u[1] = uid('pad', ref, e[1])
        elif isinstance(e, list) and first(e, 'uuid') is not None:
            first(e, 'uuid')[1] = uid(ref, k, len(out))
        if k == 'attr':
            out += [[S('path'), '/' + sym_uuid], [S('sheetname'), 'Root'], [S('sheetfile'), G.PRJ + '.kicad_sch']]
        out.append(e)
    return out

def pad_world(fpe):
    at = first(fpe, 'at'); fx, fy = float(at[1]), float(at[2]); fa = float(at[3]) if len(at) > 3 else 0
    ref = [p for p in find(fpe, 'property') if p[1] == 'Reference'][0][2]
    res = []
    for p in find(fpe, 'pad'):
        pa = first(p, 'at'); dx, dy = rot(float(pa[1]), float(pa[2]), fa)
        sz = first(p, 'size'); net = first(p, 'net')
        res.append(dict(ref=ref, pad=p[1], x=fx + dx, y=fy + dy, w=float(sz[1]), h=float(sz[2]),
                        ang=float(pa[3]) if len(pa) > 3 else 0, shape=str(p[3]), net=net[1] if net else None,
                        drill=float(first(p, 'drill')[1])))
    return res

def build(positions=None, extra=()):
    old = old_positions()
    syms = {}
    sch = parse(open(os.path.join(HERE, G.PRJ + '.kicad_sch'), encoding='utf-8').read())
    for s in find(sch, 'symbol'):
        r = [p for p in find(s, 'property') if p[1] == 'Reference']
        if r: syms[r[0][2]] = first(s, 'uuid')[1]
    fps, placed = [], {}
    for ref, part in G.PARTS.items():
        fp = load_fp(part['footprint'].split(':')[1])
        if positions and ref in positions:
            x, y, a = positions[ref]; err = 0
        else:
            x, y, a, err = fit(ref, fp, old[ref])
        placed[ref] = (round(x, 3), round(y, 3), a, err)
        fps.append(place_fp(ref, part, round(x, 3), round(y, 3), a, syms[ref]))
    b0 = parse(open(OLD, encoding='utf-8').read())
    board = [S('kicad_pcb'), [S('version'), S('20260206')], [S('generator'), 'pcbnew'], [S('generator_version'), '10.0'],
             first(b0, 'general'), [S('paper'), 'A4'],
             [S('title_block'), [S('title'), '12 V Gitar Amfisi — yeni kart'], [S('date'), '2026-11-19'], [S('rev'), 'v4']],
             first(b0, 'layers'), first(b0, 'setup')] + fps
    board.append([S('gr_rect'), [S('start'), F(X0), F(Y0)], [S('end'), F(X0 + W), F(Y0 + H)],
                  [S('stroke'), [S('width'), S('0.1')], [S('type'), S('default')]], [S('fill'), S('no')],
                  [S('layer'), 'Edge.Cuts'], [S('uuid'), uid('edge')]])
    # önceki karttaki kural alanları: panel anahtar gövdeleri + üst katta yol yasağı (tek yüzlü kart)
    for z in find(b0, 'zone'):
        if first(z, 'keepout') is not None:
            board.append(z)
    board += list(extra)
    board.append([S('embedded_fonts'), S('no')])
    return board, placed, fps

if __name__ == '__main__':
    board, placed, fps = build()
    for r, (x, y, a, e) in sorted(placed.items()):
        if e > 0.3: print('uyum hatası %-5s %.2f mm' % (r, e))
    open(os.path.join(HERE, G.PRJ + '.kicad_pcb'), 'w', encoding='utf-8', newline='\n').write(dump(board) + '\n')
    print('yazıldı', len(placed))
