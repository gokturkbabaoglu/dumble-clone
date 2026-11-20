"""Yeni KiCad şeması — tellerle açık çizilmiş sürüm (images/1_devre_semasi.png düzenine benzer).

Devre: tools/design2.py netlisti (gen_sch.PARTS), aynı referanslar ve değerler.
Çalıştır:  python kicad/yeni_kart/gen_sema.py [KiCad_semboller_klasörü]
Koordinatlar 1,27 mm'lik ızgara birimi (u) cinsinden; y aşağı doğru.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_sch as G
from gen_sch import S, F, uid, effects, get_sym, pins_of, prop, first, find, dump

U = 1.27
OX, OY = 30, 30                     # sayfa kenar boşluğu (u)
ITEMS, SYMS, PIN, WIRES, NC = [], {}, {}, [], []
POINTS = set()                      # elektriksel uç noktalar (pin uçları, etiket, güç sembolü)
NPWR = [0]
PLACED = set()

def mm(p): return ((p[0] + OX) * U, (p[1] + OY) * U)

def xf(px, py, pa, r, mir):
    """kütüphane koordinatı (mm, y yukarı) -> şema ofseti (u, y aşağı), pin yönü"""
    x, y, a = px, py, pa
    if mir == 'x': y, a = -y, -a
    if mir == 'y': x, a = -x, 180 - a
    c, s = round(math.cos(math.radians(r))), round(math.sin(math.radians(r)))
    x, y = x * c - y * s, x * s + y * c
    return (round(x / U), round(-y / U)), (a + r) % 360

def place(ref, libid, value, c, r=0, mir=None, refpos=None, valpos=None, hide_ref=False, hide_val=False, fpname=''):
    sym = SYMS.setdefault(libid, get_sym(libid))
    X, Y = mm(c)
    def ppos(key, given):
        if given:
            x, y = mm((c[0] + given[0], c[1] + given[1]))
            return (x, y, given[3] if len(given) > 3 else 0, given[2])
        p = prop(sym, key); at = first(p, 'at')
        (dx, dy), _ = xf(float(at[1]), float(at[2]), 0, r, mir)
        x, y = X + float(at[1]) if False else None, None
        # konumu mm hassasiyetinde dönüştür
        lx, ly = float(at[1]), float(at[2])
        if mir == 'x': ly = -ly
        if mir == 'y': lx = -lx
        cc, ss = round(math.cos(math.radians(r))), round(math.sin(math.radians(r)))
        rx, ry = lx * cc - ly * ss, lx * cc * 0 + lx * ss + ly * cc
        ang = float(at[3]) if len(at) > 3 else 0
        if r in (90, 270): ang = (ang + 90) % 180
        eff = first(p, 'effects'); j = None
        if eff is not None and first(eff, 'justify') is not None:
            j = ' '.join(first(eff, 'justify')[1:])
        return (X + rx, Y - ry, ang, j)
    rp, vp = ppos('Reference', refpos), ppos('Value', valpos)
    e = [S('symbol'), [S('lib_id'), libid], [S('at'), F(X), F(Y), F(r)]]
    if mir: e.append([S('mirror'), S(mir)])
    e += [[S('unit'), S('1')], [S('exclude_from_sim'), S('no')],
          [S('in_bom'), S('no' if ref.startswith('#') else 'yes')],
          [S('on_board'), S('no' if ref.startswith('#') else 'yes')], [S('dnp'), S('no')], [S('uuid'), uid('sym', ref)]]
    def P(key, val, pos, hide=False):
        x, y, a, j = pos
        return [S('property'), key, val, [S('at'), F(x), F(y), F(a)], effects(j, hide)]
    e += [P('Reference', ref, rp, hide_ref), P('Value', value, vp, hide_val),
          P('Footprint', fpname, (X, Y, 0, None), True), P('Datasheet', '~', (X, Y, 0, None), True),
          P('Description', '', (X, Y, 0, None), True)]
    pins = pins_of(sym)
    for num in pins:
        e.append([S('pin'), num, [S('uuid'), uid('pin', ref, num)]])
    e.append([S('instances'), [S('project'), G.PRJ, [S('path'), '/' + G.ROOT, [S('reference'), ref], [S('unit'), S('1')]]]])
    ITEMS.append(e)
    out = {}
    for num, (px, py, pa) in pins.items():
        (dx, dy), a = xf(px, py, pa, r, mir)
        pt = (c[0] + dx, c[1] + dy)
        out[num] = pt; POINTS.add(pt)
    PIN[ref] = out
    if not ref.startswith('#'): PLACED.add(ref)
    return out

def part(ref, c, r=0, mir=None, **kw):
    p = G.PARTS[ref]
    return place(ref, p['lib'], p['value'], c, r, mir, fpname=p['footprint'], **kw)

def two(ref, A, B, side=1):
    """İki bacaklı parça: 1. pin A tarafında, A-B arası düz (yatay/dikey); kalan kısım tel."""
    p = G.PARTS[ref]; sym = SYMS.setdefault(p['lib'], get_sym(p['lib']))
    pins = pins_of(sym)
    horiz = A[1] == B[1]
    d = (B[0] - A[0], B[1] - A[1]); L = abs(d[0]) + abs(d[1]); ux, uy = d[0] // L, d[1] // L
    sg = lambda v: (v > 0) - (v < 0)
    for r in (0, 90, 180, 270):
        (x1, y1), _ = xf(*pins['1'], r, None); (x2, y2), _ = xf(*pins['2'], r, None)
        if (sg(x2 - x1), sg(y2 - y1)) == (ux, uy):
            break
    span = abs(x2 - x1) + abs(y2 - y1)
    assert L >= span, (ref, L, span)
    k = (L - span) // 2
    p1 = (A[0] + ux * k, A[1] + uy * k)
    c = (p1[0] - x1, p1[1] - y1)
    if horiz:
        rp, vp = (0, -3, None), (0, 3, None)
    else:
        rp, vp = ((2, -1, 'left'), (2, 1, 'left')) if side > 0 else ((-2, -1, 'right'), (-2, 1, 'right'))
    pm = place(ref, p['lib'], p['value'], c, r, None, refpos=rp, valpos=vp, fpname=p['footprint'])
    if pm['1'] != A: w(A, pm['1'])
    if pm['2'] != B: w(pm['2'], B)
    return pm

def w(*pts):
    for a, b in zip(pts, pts[1:]):
        assert a[0] == b[0] or a[1] == b[1], (a, b)
        if a != b: WIRES.append((a, b))

def gnd(p, up=False):
    NPWR[0] += 1
    place('#PWR%03d' % NPWR[0], 'power:GND', 'GND', p, 180 if up else 0,
          refpos=(0, 5, None), valpos=(0, 3, None), hide_ref=True, hide_val=True)

def flag(p):
    NPWR[0] += 1
    place('#FLG%03d' % NPWR[0], 'power:PWR_FLAG', 'PWR_FLAG', p, 0,
          refpos=(0, -4, None), valpos=(0, -3, None), hide_ref=True)

def label(name, p, d):
    ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[d]
    j = 'left bottom' if ang in (0, 90) else 'right bottom'
    x, y = mm(p); POINTS.add(p)
    ITEMS.append([S('label'), name, [S('at'), F(x), F(y), F(ang)], effects(j), [S('uuid'), uid('lbl', name, p)]])

def vl(p, name, up=True):
    q = (p[0], p[1] - 3 if up else p[1] + 3); w(p, q); label(name, q, (0, -1) if up else (0, 1))

def nc(p):
    x, y = mm(p); NC.append(p)
    ITEMS.append([S('no_connect'), [S('at'), F(x), F(y)], [S('uuid'), uid('nc', p)]])

def text(s, p, size=1.5, bold=False, color=None):
    x, y = mm(p)
    ITEMS.append([S('text'), s, [S('exclude_from_sim'), S('no')], [S('at'), F(x), F(y), S('0')],
                  effects('left bottom', size=size, bold=bold), [S('uuid'), uid('txt', s, p)]])

def box(a, b, title=None):
    (x1, y1), (x2, y2) = mm(a), mm(b)
    ITEMS.append([S('rectangle'), [S('start'), F(x1), F(y1)], [S('end'), F(x2), F(y2)],
                  [S('stroke'), [S('width'), F(0.15)], [S('type'), S('dash')]], [S('fill'), [S('type'), S('none')]],
                  [S('uuid'), uid('rect', a, b)]])
    if title: text(title, (a[0] + 1, a[1] + 2), size=1.27)

# ====================================================================== ÇİZİM
def draw():
    # ---------------- GİRİŞ + JFET ----------------
    text('GİRİŞ + JFET TAMPON', (4, 62), 2.0, True)
    j1 = part('J1', (10, 100), 0, 'x', refpos=(-2, -6, None), valpos=(-2, -4, None))
    w(j1['T'], (20, 100)); two('R5', (20, 100), (32, 100))
    w((32, 100), (44, 100))
    w(j1['TN'], (18, 98), (18, 88), (20, 88)); two('JP1', (20, 88), (28, 88))
    w((28, 88), (30, 88), (30, 90)); gnd((30, 90))
    w(j1['S'], (18, 102), (18, 106)); gnd((18, 106))
    two('R6', (36, 100), (36, 112)); gnd((36, 112))
    q1 = part('Q1', (48, 100), refpos=(5, -1, 'left'), valpos=(5, 1, 'left'))
    w(q1['3'], (50, 86)); two('R4', (50, 74), (50, 86)); vl((50, 74), 'V3')
    two('C10', (50, 86), (64, 86))
    w(q1['2'], (50, 110))
    tr = part('TR1', (50, 117), refpos=(-3, -1, 'right'), valpos=(-3, 1, 'right'))
    w((50, 110), tr['1']); w(tr['3'], (50, 124)); w(tr['2'], (55, 117), (55, 122), (50, 122)); gnd((50, 124))
    w((50, 110), (62, 110)); two('C9', (62, 110), (62, 120))
    rv4 = part('RV4', (62, 127), 0, 'x', refpos=(-3, -1, 'right'), valpos=(-3, 1, 'right'))
    w((62, 120), rv4['3']); w(rv4['1'], (62, 134)); w(rv4['2'], (67, 127), (67, 132), (62, 132)); gnd((62, 134))
    text('TR1 ile V(drain) ≈ 7 V', (30, 132), 1.27)
    text('RV4 DRIVE: saat yönü → kazanç ↑', (40, 140), 1.27)
    # ---------------- GAIN + SW1 ----------------
    text('GAIN + SW1', (68, 62), 2.0, True)
    rv1 = part('RV1', (72, 96), 0, 'x', refpos=(-3, -1, 'right'), valpos=(-3, 1, 'right'))
    w((64, 86), (72, 86), rv1['3']); w(rv1['1'], (72, 104)); gnd((72, 104))
    w((72, 86), (76, 86)); two('CB1', (76, 86), (88, 86))
    p1 = part('P1', (92, 86), refpos=(2, -2, 'left'), valpos=(2, 2, 'left')); w((88, 86), p1['1'])
    w(rv1['2'], (80, 96)); w((80, 96), (80, 92), (88, 92))
    p2 = part('P2', (92, 92), refpos=(2, -2, 'left'), valpos=(2, 2, 'left')); w((88, 92), p2['1'])
    p3 = part('P3', (92, 72), refpos=(2, -2, 'left'), valpos=(2, 2, 'left'))
    w(p3['1'], (84, 72)); two('CD1', (84, 72), (84, 80)); gnd((84, 80))
    text('SW1 ON-OFF-ON panelde (kabloyla):', (68, 66), 1.27)
    text('orta = P2, B = P1 (470p), A = P3 (3.3n)', (68, 69), 1.27)
    # ---------------- LM386 ----------------
    text('LM386 KAZANÇ KATI', (98, 62), 2.0, True)
    u1 = part('U1', (112, 98))
    w((80, 96), u1['3'])
    two('R7', (98, 96), (98, 108), side=-1); gnd((98, 108))
    w(u1['2'], (104, 100), (104, 104)); gnd((104, 104))
    vl(u1['6'], 'V2')
    gnd(u1['4'])
    w(u1['7'], (112, 84), (122, 84)); two('C12', (122, 84), (122, 92)); gnd((122, 92))
    w(u1['1'], (112, 110), (104, 110)); two('R8', (104, 110), (104, 118), side=-1)
    w((104, 118), (104, 120), (120, 120)); two('C11', (120, 120), (120, 112))
    w(u1['8'], (114, 108), (120, 108), (120, 112))
    w(u1['5'], (126, 98)); two('R9', (126, 98), (126, 108)); two('C13', (126, 108), (126, 116)); gnd((126, 116))
    w((126, 98), (130, 98)); two('C14', (130, 98), (142, 98))
    # ---------------- TON YIĞINLARI ----------------
    X = (152, 98)
    w((142, 98), X)
    two('R10', (146, 98), (146, 110), side=-1); gnd((146, 110))
    # US
    text('US yığını (Fender tipi)', (158, 14), 2.0, True)
    w(X, (152, 24))
    two('C15', (152, 24), (190, 24))
    w((156, 24), (156, 32)); two('C26', (156, 32), (186, 32)); w((186, 32), (186, 24))
    two('R13', (190, 24), (190, 36)); two('R14', (190, 36), (190, 48))
    two('R15', (190, 48), (190, 62)); two('R16', (190, 62), (190, 74)); gnd((190, 74))
    two('R11', (152, 52), (166, 52)); w((166, 52), (168, 52)); w((168, 48), (168, 62))
    two('C16', (168, 48), (190, 48)); two('C17', (168, 62), (190, 62))
    # UK
    text('UK yığını (Marshall tipi)', (158, 184), 2.0, True)
    two('R12', X, (152, 110))
    two('R17', (152, 114), (164, 114)); w((164, 114), (166, 114), (166, 116)); gnd((166, 116))
    w((152, 110), (152, 154))
    two('C18', (152, 124), (190, 124))
    two('R19', (190, 124), (190, 132)); two('R20', (190, 132), (190, 140)); two('R30', (190, 140), (190, 148))
    two('R21', (190, 148), (190, 160)); two('R22', (190, 160), (190, 168)); two('R31', (190, 168), (190, 176)); gnd((190, 176))
    two('R18', (152, 154), (166, 154)); w((166, 154), (168, 154)); w((168, 148), (168, 160))
    two('C19', (168, 148), (190, 148)); two('C20', (168, 160), (190, 160))
    # ---------------- ISF + VOLUME ----------------
    text('ISF + VOLUME', (204, 62), 2.0, True)
    rv2 = part('RV2', (212, 84), refpos=(-3, -1, 'right'), valpos=(-3, 1, 'right'))
    w((190, 36), (212, 36), rv2['1']); w((190, 132), (212, 132), rv2['3'])
    text('US ↑', (213, 74), 1.27); text('UK ↓', (213, 96), 1.27)
    rv3 = part('RV3', (230, 80), 0, 'x', refpos=(-3, -1, 'right'), valpos=(-3, 1, 'right'))
    w(rv2['2'], (220, 84), (220, 72), (230, 72), rv3['3']); w(rv3['1'], (230, 88)); gnd((230, 88))
    w(rv3['2'], (238, 80)); two('R23', (238, 80), (250, 80))
    w((250, 80), (262, 80))
    two('R24', (254, 80), (254, 92), side=-1); gnd((254, 92))
    two('C21', (262, 80), (262, 92)); gnd((262, 92))
    w((262, 80), (264, 80)); two('C22', (278, 80), (264, 80))
    # ---------------- TDA2003 ----------------
    text('TDA2003 GÜÇ KATI', (270, 54), 2.0, True)
    u2 = part('U2', (288, 82))
    w((278, 80), u2['1'])
    w(u2['2'], (276, 84), (276, 96))
    two('R26', (276, 96), (276, 106), side=-1); two('C23', (276, 106), (276, 116), side=-1); gnd((276, 116))
    two('R25', (276, 96), (298, 96)); w((298, 96), (298, 82))
    gnd(u2['3'])
    w(u2['5'], (286, 68)); vl((286, 68), 'V12'); w((286, 68), (302, 68))
    two('C6', (294, 68), (294, 76)); gnd((294, 76))
    two('C7', (302, 68), (302, 76)); gnd((302, 76))
    text('C6/C7: TDA 5. bacağın yanına', (290, 62), 1.27)
    w(u2['4'], (310, 82))
    two('R27', (306, 82), (306, 92)); two('C24', (306, 92), (306, 100)); gnd((306, 100))
    two('C25', (310, 82), (322, 82))
    # ---------------- KULAKLIK / HOPARLÖR ----------------
    text('KULAKLIK / HOPARLÖR', (318, 54), 2.0, True)
    j2 = part('J2', (344, 82), 180, refpos=(-2, -9, None), valpos=(-2, -11, None))
    w((322, 82), j2['R'])
    two('R28', (326, 82), (326, 92), side=-1); two('R29', (326, 92), (326, 104), side=-1); gnd((326, 104))
    w(j2['T'], (336, 78), (336, 82))
    w((326, 92), (338, 92), (338, 84), j2['S'])
    nc(j2['RN'])
    tb2 = part('TB2', (328, 66), 0, 'y', refpos=(0, -4, None), valpos=(0, 5, None))
    w(j2['TN'], (334, 76), (334, 66), tb2['1'])
    w(tb2['2'], (334 - 2, 68), (332, 72))
    gnd((332, 72))
    text('TB2 → hoparlör 4 Ω 6,5" (kabloyla)', (300, 112), 1.27)
    text('Fiş takılınca J2 TN açılır, hoparlör susar', (300, 115), 1.27)
    # ---------------- BESLEME ----------------
    text('BESLEME', (4, 222), 2.0, True)
    tb1 = part('TB1', (10, 240), 0, 'y', refpos=(0, -4, None), valpos=(0, 6, None))
    w(tb1['1'], (20, 240)); two('F1', (20, 240), (32, 240))
    p4 = part('P4', (40, 240), refpos=(0, -3, None), valpos=(0, 3, None)); w((32, 240), p4['1'])
    p5 = part('P5', (52, 240), 0, 'y', refpos=(0, -3, None), valpos=(0, 3, None))
    w(p5['1'], (62, 240))
    text('SW2 güç anahtarı panelde: P4 = orta, P5 = uç', (30, 230), 1.27)
    two('D1', (76, 240), (62, 240))
    w(tb1['2'], (18, 242), (18, 250)); gnd((18, 250)); w((18, 246), (22, 246)); flag((22, 246))
    w((76, 240), (100, 240))
    two('C1', (80, 240), (80, 250)); gnd((80, 250))
    two('C2', (88, 240), (88, 250)); gnd((88, 250))
    vl((94, 240), 'V12'); w((98, 240), (98, 237)); flag((98, 237))
    two('R1', (100, 240), (112, 240)); w((112, 240), (146, 240))
    two('C3', (116, 240), (116, 250)); gnd((116, 250))
    two('C8', (124, 240), (124, 250)); gnd((124, 250))
    two('C4', (132, 240), (132, 250)); gnd((132, 250))
    vl((138, 240), 'V2'); w((142, 240), (142, 237)); flag((142, 237))
    two('R2', (146, 240), (158, 240)); w((158, 240), (168, 240))
    two('C5', (162, 240), (162, 250)); gnd((162, 250))
    vl((168, 240), 'V3')
    w((94, 240), (94, 258), (98, 258)); two('R3', (98, 258), (110, 258))
    two('D2', (122, 258), (110, 258)); w((122, 258), (126, 258), (126, 260)); gnd((126, 260))
    text('LED (ön kenar)', (108, 264), 1.27)
    # ---------------- MEKANİK ----------------
    text('MONTAJ DELİKLERİ (M3)', (200, 222), 2.0, True)
    for i, r in enumerate(['MH1', 'MH2', 'MH3', 'MH4', 'MH5']):
        part(r, (204 + i * 14, 236), refpos=(3, -1, 'left'), valpos=(3, 1, 'left'))

def finish():
    # telleri özel noktalarda böl, bağlantı noktalarına junction koy
    pts = set(POINTS)
    for a, b in WIRES: pts.add(a); pts.add(b)
    segs = []
    for a, b in WIRES:
        inner = [p for p in pts if p not in (a, b) and
                 ((a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1])) or
                  (a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0])))]
        chain = sorted([a, b] + inner, key=lambda p: abs(p[0] - a[0]) + abs(p[1] - a[1]))
        segs += list(zip(chain, chain[1:]))
    deg = {}
    for a, b in segs:
        deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
    for p in POINTS:
        if p in deg: deg[p] += 1
    for a, b in segs:
        (x1, y1), (x2, y2) = mm(a), mm(b)
        ITEMS.append([S('wire'), [S('pts'), [S('xy'), F(x1), F(y1)], [S('xy'), F(x2), F(y2)]],
                      [S('stroke'), [S('width'), S('0')], [S('type'), S('default')]], [S('uuid'), uid('w', a, b)]])
    for p, n in sorted(deg.items()):
        if n >= 3:
            x, y = mm(p)
            ITEMS.append([S('junction'), [S('at'), F(x), F(y)], [S('diameter'), S('0')], [S('color'), S('0'), S('0'), S('0'), S('0')],
                          [S('uuid'), uid('j', p)]])
    missing = set(G.PARTS) - PLACED
    assert not missing, missing

def build():
    draw(); finish()
    ls = [S('lib_symbols')] + [SYMS[k] for k in sorted(SYMS)]
    return [S('kicad_sch'), [S('version'), S('20250114')], [S('generator'), 'eeschema'], [S('generator_version'), '9.0'],
            [S('uuid'), G.ROOT], [S('paper'), 'A2'],
            [S('title_block'), [S('title'), '12 V Gitar Amfisi — devre şeması (yeni kart)'], [S('date'), '2026-11-19'],
             [S('rev'), 'v4'],
             [S('comment'), S('1'), 'BF245B tampon → LM386 → ISF (US↔UK) ton yığınları → Volume → TDA2003 → 4 Ω hoparlör / kulaklık'],
             [S('comment'), S('2'), 'Kaynak: tools/design2.py netlisti (kicad/amfi/amfi.kicad_sch ile aynı devre)']],
            ls] + ITEMS + [[S('sheet_instances'), [S('path'), '/', [S('page'), '1']]], [S('embedded_fonts'), S('no')]]

if __name__ == '__main__':
    sch = build()
    open(os.path.join(HERE, G.PRJ + '.kicad_sch'), 'w', encoding='utf-8', newline='\n').write(dump(sch) + '\n')
    print('parça', len(PLACED), 'tel', len(WIRES))
