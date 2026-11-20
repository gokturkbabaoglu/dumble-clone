"""KiCad proje üreticisi (şema + sembol/ayak izi kütüphanesi + kurallar).
Kaynak: tools/design2.py (netlist) ve tools/params.py (ölçüler). Çıktı: kicad/amfi/
Çalıştır:  python kicad/gen_kicad.py
"""
import os, sys, uuid, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'v2_v3', 'araclar'))
import design2 as D

OUT = os.path.join(HERE, 'amfi')
PRJ = 'amfi'
NS = uuid.UUID('6a1f2c3e-0000-4000-8000-0000000a3f1e')
def uid(*k): return str(uuid.uuid5(NS, '/'.join(map(str, k))))
def f(x): return ('%.4f' % x).rstrip('0').rstrip('.') if abs(x) > 1e-9 else '0'
def q(s): return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'

# ---------------- referans adları (KiCad'in sayı bekleyen adları için) ----------------
# a/b sonekli çiftler: KiCad harf sonekini çok birimli parça sanar -> yeni numara (kullanıcı kararı)
REN = {
       'CB': 'CB1', 'CD': 'CD1', 'P_SWB': 'P1', 'P_SWC': 'P2', 'P_SWD': 'P3', 'P_PW1': 'P4', 'P_PW2': 'P5'}
SKIP = {'KO_SW1', 'KO_SW2'}          # panel anahtar gövdeleri: PCB'de yasak bölge olarak çizilir
PARTS = {}
for ref, (fp, val, nets) in D.C.items():
    if ref in SKIP: continue
    PARTS[REN.get(ref, ref)] = (fp, val, nets)
# kullanıcı isteği: ön tarafa ek M3 vida delikleri (eskiler hep arka kenardaydı)
PARTS['MH4'] = ('MH', 'M3', ['NC_MH4'])
PARTS['MH5'] = ('MH', 'M3', ['NC_MH5'])
# Tel köprüler (GND adalarını ana dolguya bağlar). kicad/kopruler.json: [{"ref": "K1", "L": 5.08}, ...]
_kj = os.path.join(HERE, 'kopruler.json')
KOPRULER = json.load(open(_kj, encoding='utf-8')) if os.path.exists(_kj) else []
for _k in KOPRULER:
    _key = 'KOPRU%g' % _k['L']
    D.FP[_key] = dict(pins=[(0, 0), (_k['L'], 0)], body=('rect', _k['L'], 1.0), pad=2.0, hole=0.9, shape='rect')
    PARTS[_k['ref']] = (_key, 'tel köprü %g mm' % _k['L'], ['GND', 'GND'])

# ---------------- ayak izi adları ----------------
def fpname(fp):
    if fp.startswith('KOPRU'): return 'Kopru_P%s' % fp[5:]
    if fp.startswith('E'):
        d, p = D.ELKO[fp[1:]]
        return 'CP_D%s_P%s' % (f(d), f(p))
    return {'R': 'R_P10.16', 'CF': 'C_Film_P5.08', 'CC': 'C_Disc_P5.08', 'TO92': 'TO92_Inline_GSD',
            'TRIM': 'Trim_3296W', 'DIP8': 'DIP8_Socket', 'DO201': 'DO201_P15.24', 'PW5': 'Pentawatt_V',
            'PAD': 'Pad_Kablo', 'MH': 'MH_M3', 'JMP': 'Jumper_P5.08', 'J635': 'Jak_6.35_Mono',
            'PJ324': 'PJ-324M', 'POT': 'Pot_WH148_16mm', 'LED': 'LED_5mm_Dik90', 'FUSE': 'Sigorta_23x9_P10',
            'TB2': 'Klemens_2_P5.08'}[fp]

# ======================================================================================
#  AYAK İZLERİ (.kicad_mod) — pad koordinatları design2.FP'den (Y aşağı = PCB yönü)
# ======================================================================================
def body_box(fp):
    """Gövde dikdörtgeni (x0,y0,x1,y1) ya da daire ('c',cx,cy,r)."""
    d = D.FP[fp]; pins = d['pins']; b = d['body']
    xs = [p[0] for p in pins]; ys = [p[1] for p in pins]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    if b is None: return None
    k = b[0]
    if k == 'circ': return ('c', cx, cy, b[1] / 2)
    if k == 'front':   # ön yüz y=0, gövde -y yönüne uzanır
        w, dep = b[1], b[2]
        return (-w / 2, -dep, w / 2, 0)
    if k == 'pw':      # Pentawatt: gövde bacak sırasının arkasında (tab -y, arka kenara)
        w, dep = b[1], b[2]
        return (-w / 2, -dep + 1.0, w / 2, 1.0)
    w, h = b[1], b[2]
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

def _rot(x, y, r):
    """KiCad döndürmesi (Y aşağı, r derece saat yönünün tersine)."""
    c, sn = round(math.cos(math.radians(r)), 9), round(math.sin(math.radians(r)), 9)
    return x * c + y * sn, -x * sn + y * c

def fp_extent(fp):
    """Avlu dikdörtgeni (yerel): gövde ile pad halkalarının birleşimi + 0.25 mm."""
    d = D.FP[fp]; bb = body_box(fp); pins = d['pins']; r = d['pad'] / 2
    xs = [p[0] - r for p in pins] + [p[0] + r for p in pins]
    ys = [p[1] - r for p in pins] + [p[1] + r for p in pins]
    if bb:
        if bb[0] == 'c': xs += [bb[1] - bb[3], bb[1] + bb[3]]; ys += [bb[2] - bb[3], bb[2] + bb[3]]
        else: xs += [bb[0], bb[2]]; ys += [bb[1], bb[3]]
    m = 0.25
    return min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m

def fp_items(fp, rot=0, nets=None, netnum=None, key=''):
    """Ayak izi içeriği (KiCad 8 biçimi). nets: pad sırasına göre net adları (PCB'ye gömülürken)."""
    name = fpname(fp); d = D.FP[fp]; pins = d['pins']; K = key or name
    L = []
    def line(a, b, layer, w, tag):
        L.append('(fp_line (start %s %s) (end %s %s) (stroke (width %s) (type solid)) (layer %s) (uuid %s))' % (
            f(a[0]), f(a[1]), f(b[0]), f(b[1]), f(w), q(layer), q(uid(K, tag))))
    def rct(x0, y0, x1, y1, layer, w, tag, typ='solid'):
        L.append('(fp_rect (start %s %s) (end %s %s) (stroke (width %s) (type %s)) (fill none) (layer %s) (uuid %s))' % (
            f(x0), f(y0), f(x1), f(y1), f(w), typ, q(layer), q(uid(K, tag))))
    bb = body_box(fp)
    if bb:
        for lay, w in (('F.SilkS', 0.12), ('F.Fab', 0.1)):
            if bb[0] == 'c':
                L.append('(fp_circle (center %s %s) (end %s %s) (stroke (width %s) (type solid)) (fill none) (layer %s) (uuid %s))' % (
                    f(bb[1]), f(bb[2]), f(bb[1] + bb[3]), f(bb[2]), f(w), q(lay), q(uid(K, lay, 'body'))))
            else:
                rct(bb[0], bb[1], bb[2], bb[3], lay, w, lay + 'body')
    if fp.startswith('E'):
        x, y = pins[0]
        line((x - 1.6, y - 2.2), (x - 0.4, y - 2.2), 'F.SilkS', 0.15, 'p1')
        line((x - 1.0, y - 2.8), (x - 1.0, y - 1.6), 'F.SilkS', 0.15, 'p2')
    if fp == 'DO201':
        line((bb[2] - 1.5, bb[1]), (bb[2] - 1.5, bb[3]), 'F.SilkS', 0.4, 'band')
    if fp == 'PW5':
        hw, hd = D.HS_KEEPOUT
        rct(-hw / 2, bb[1] - hd + 2, hw / 2, bb[1], 'Dwgs.User', 0.1, 'hs', 'dash')
    if fp == 'DIP8':
        L.append('(fp_circle (center 0 -2.2) (end 0.4 -2.2) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS") (uuid %s))' % q(uid(K, 'dot')))
    x0, y0, x1, y1 = fp_extent(fp)
    rct(x0, y0, x1, y1, 'F.CrtYd', 0.05, 'crt')
    for i, (x, y) in enumerate(pins, 1):
        if fp in ('KO1', 'KO2'): continue
        if fp == 'MH':
            L.append('(pad "" np_thru_hole circle (at %s %s %s) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask") (uuid %s))' % (
                f(x), f(y), f(rot), q(uid(K, 'pad', i))))
            continue
        shape = 'rect' if (i == 1 and (fp in ('DIP8', 'TO92', 'TRIM') or fp.startswith('E'))) else 'circle'
        net = ''
        if nets is not None:
            n = nets[i - 1]
            net = ' (net %d %s)' % (netnum[n], q(n))
        L.append('(pad %s thru_hole %s (at %s %s %s) (size %s %s) (drill %s) (layers "*.Cu" "*.Mask") (remove_unused_layers no)%s (uuid %s))' % (
            q(i), shape, f(x), f(y), f(rot), f(d['pad']), f(d['pad']), f(d['hole']), net, q(uid(K, 'pad', i))))
    return L

def footprint(fp):
    name = fpname(fp)
    x0, y0, x1, y1 = fp_extent(fp)
    s = '(footprint %s\n\t(version 20240108)\n\t(generator "amfi_gen")\n\t(generator_version "8.0")\n\t(layer "F.Cu")\n' % q(name)
    s += '\t(descr %s)\n' % q('amfi: ' + fp)
    s += '\t(property "Reference" "REF**" (at %s %s 0) (layer "F.SilkS") (uuid %s) (effects (font (size 1 1) (thickness 0.15))))\n' % (
        f((x0 + x1) / 2), f(y0 - 1.0), q(uid(name, 'ref')))
    s += '\t(property "Value" %s (at %s %s 0) (layer "F.Fab") (uuid %s) (effects (font (size 1 1) (thickness 0.15))))\n' % (
        q(name), f((x0 + x1) / 2), f(y1 + 1.0), q(uid(name, 'val')))
    s += '\t(attr through_hole)\n'
    s += ''.join('\t' + it + '\n' for it in fp_items(fp))
    return name, s + ')\n'

# ======================================================================================
#  SEMBOLLER (.kicad_sym) — bütün pinler pasif (ERC'de güç bayrağı gerekmez)
# ======================================================================================
FONT = '(effects (font (size 1.27 1.27)))'
FONTH = '(effects (font (size 1.27 1.27)) (hide yes))'
def pin(num, name, x, y, ang, L=2.54):
    return '\t\t\t(pin passive line (at %s %s %d) (length %s) (name %s %s) (number %s %s))\n' % (
        f(x), f(y), ang, f(L), q(name), FONT, q(num), FONT)
def poly(pts, w=0.254, fill='none'):
    return '\t\t\t(polyline (pts %s) (stroke (width %s) (type default)) (fill (type %s)))\n' % (
        ' '.join('(xy %s %s)' % (f(a), f(b)) for a, b in pts), f(w), fill)
def rect(x0, y0, x1, y1, fill='none'):
    return '\t\t\t(rectangle (start %s %s) (end %s %s) (stroke (width 0.254) (type default)) (fill (type %s)))\n' % (
        f(x0), f(y0), f(x1), f(y1), fill)

# her sembol: (çizim, pinler[(num,name,x,y,ang)], show_pin_names, ref_prefix, ref_pos, val_pos)
SYM = {}
SYM['R'] = (rect(-1.016, -2.54, 1.016, 2.54), [('1', '~', 0, 5.08, 270), ('2', '~', 0, -5.08, 90)], False, 'R')
SYM['C'] = (poly([(-2.032, 0.762), (2.032, 0.762)], 0.508) + poly([(-2.032, -0.762), (2.032, -0.762)], 0.508) +
            poly([(0, 2.54), (0, 0.762)]) + poly([(0, -2.54), (0, -0.762)]),
            [('1', '~', 0, 5.08, 270), ('2', '~', 0, -5.08, 90)], False, 'C')
SYM['CP'] = (rect(-2.286, 0.508, 2.286, 1.016) + rect(-2.286, -0.508, 2.286, -1.016, 'outline') +
             poly([(-1.778, 2.286), (-0.762, 2.286)]) + poly([(-1.27, 2.794), (-1.27, 1.778)]) +
             poly([(0, 2.54), (0, 1.016)]) + poly([(0, -2.54), (0, -1.016)]),
             [('1', '+', 0, 5.08, 270), ('2', '-', 0, -5.08, 90)], False, 'C')
SYM['D'] = (poly([(-1.27, 1.27), (-1.27, -1.27), (1.27, 0), (-1.27, 1.27)]) + poly([(1.27, 1.27), (1.27, -1.27)]) +
            poly([(-2.54, 0), (2.54, 0)]),
            [('1', 'A', -5.08, 0, 0), ('2', 'K', 5.08, 0, 180)], False, 'D')
SYM['LED'] = (SYM['D'][0] + poly([(0, 1.778), (1.016, 3.048)]) + poly([(1.016, 1.778), (2.032, 3.048)]),
              SYM['D'][1], False, 'D')
SYM['POT'] = (rect(-1.016, -2.54, 1.016, 2.54) + poly([(2.54, 0), (1.524, 0)]) +
              poly([(1.016, 0), (1.778, 0.508), (1.778, -0.508), (1.016, 0)], 0.254, 'outline'),
              [('1', '1', 0, 5.08, 270), ('3', '3', 0, -5.08, 90), ('2', '2', 5.08, 0, 180)], False, 'RV')
SYM['NJFET'] = (poly([(0.254, 1.905), (0.254, -1.905)], 0.508) + poly([(0.254, 1.27), (2.54, 1.27), (2.54, 2.54)]) +
                poly([(0.254, -1.27), (2.54, -1.27), (2.54, -2.54)]) + poly([(-2.54, 0), (0.254, 0)]) +
                poly([(-0.762, 0.508), (0, 0), (-0.762, -0.508)]) +
                '\t\t\t(circle (center 1.27 0) (radius 2.794) (stroke (width 0.254) (type default)) (fill (type none)))\n',
                [('1', 'G', -5.08, 0, 0), ('2', 'S', 2.54, -5.08, 90), ('3', 'D', 2.54, 5.08, 270)], True, 'Q')
def ic(pl, pr, w=7.62):
    """pl/pr: [(num,name)] sol/sağ, yukarıdan aşağı"""
    n = max(len(pl), len(pr)); h = (n + 1) * 2.54 / 2
    h = math.ceil(h / 1.27) * 1.27
    body = rect(-w, h, w, -h, 'background')
    pins = []
    for side, lst in ((-1, pl), (1, pr)):
        y0 = (len(lst) - 1) * 2.54 / 2
        for k, (num, name) in enumerate(lst):
            y = y0 - k * 2.54
            pins.append((num, name, side * (w + 2.54), y, 0 if side < 0 else 180))
    return body, pins
b, p = ic([('3', '+IN'), ('2', '-IN'), ('7', 'BYP'), ('1', 'G1'), ('8', 'G8')], [('6', 'VS'), ('5', 'OUT'), ('4', 'GND')])
SYM['LM386'] = (b, p, True, 'U')
b, p = ic([('1', 'IN+'), ('2', 'IN-'), ('3', 'GND')], [('5', 'VS'), ('4', 'OUT')])
SYM['TDA2003'] = (b, p, True, 'U')
b, p = ic([('3', 'UÇ'), ('2', 'KESİCİ'), ('1', 'ŞASE')], [], 5.08)
SYM['JACK3'] = (b, p, True, 'J')
b, p = ic([('4', 'TIP'), ('5', 'TIP-NC'), ('3', 'RING'), ('2', 'RING-NC'), ('1', 'SLEEVE')], [], 5.08)
SYM['PJ324'] = (b, p, True, 'J')
b, p = ic([('1', '1'), ('2', '2')], [], 2.54)
SYM['TB2'] = (b, p, False, 'TB')
SYM['FUSE'] = (rect(-2.54, 0.762, 2.54, -0.762) + poly([(-2.54, 0), (2.54, 0)]),
               [('1', '~', -5.08, 0, 0), ('2', '~', 5.08, 0, 180)], False, 'F')
SYM['PAD'] = ('\t\t\t(circle (center 0 0) (radius 0.762) (stroke (width 0.254) (type default)) (fill (type none)))\n',
              [('1', '~', 0, -2.54, 90)], False, 'P')
SYM['JMP'] = (poly([(-1.27, 0.762), (1.27, 0.762)]) +
              '\t\t\t(circle (center -1.778 0) (radius 0.508) (stroke (width 0.254) (type default)) (fill (type none)))\n'
              '\t\t\t(circle (center 1.778 0) (radius 0.508) (stroke (width 0.254) (type default)) (fill (type none)))\n',
              [('1', '~', -5.08, 0, 0), ('2', '~', 5.08, 0, 180)], False, 'JP')
SYM['MH'] = ('\t\t\t(circle (center 0 0) (radius 1.524) (stroke (width 0.254) (type default)) (fill (type none)))\n'
             '\t\t\t(circle (center 0 0) (radius 0.762) (stroke (width 0.254) (type default)) (fill (type none)))\n',
             [], False, 'MH')

def symtype(ref, fp, val):
    if fp.startswith('E'): return 'CP'
    if fp.startswith('KOPRU'): return 'JMP'
    return {'R': 'R', 'CF': 'C', 'CC': 'C', 'TO92': 'NJFET', 'TRIM': 'POT', 'POT': 'POT', 'DIP8': 'LM386',
            'PW5': 'TDA2003', 'DO201': 'D', 'LED': 'LED', 'J635': 'JACK3', 'PJ324': 'PJ324', 'TB2': 'TB2',
            'FUSE': 'FUSE', 'PAD': 'PAD', 'JMP': 'JMP', 'MH': 'MH'}[fp]

def symbol_def(name, prefix_lib=''):
    draw, pins, shownames, refp = SYM[name]
    full = prefix_lib + name
    s = '\t(symbol %s\n' % q(full)
    s += '\t\t(pin_numbers (hide %s))\n' % ('no' if shownames else 'yes')
    s += '\t\t(pin_names (offset %s)%s)\n' % ('1.016' if shownames else '0', '' if shownames else ' (hide yes)')
    s += '\t\t(exclude_from_sim no) (in_bom %s) (on_board yes)\n' % ('no' if name == 'MH' else 'yes')
    s += '\t\t(property "Reference" %s (at 3.81 1.27 0) (effects (font (size 1.27 1.27)) (justify left)))\n' % q(refp)
    s += '\t\t(property "Value" %s (at 3.81 -1.27 0) (effects (font (size 1.27 1.27)) (justify left)))\n' % q(name)
    for k in ('Footprint', 'Datasheet', 'Description'):
        s += '\t\t(property %s "" (at 0 0 0) %s)\n' % (q(k), FONTH)
    s += '\t\t(symbol %s\n%s\t\t)\n' % (q(name + '_0_1'), draw)
    s += '\t\t(symbol %s\n%s\t\t)\n' % (q(name + '_1_1'), ''.join(pin(*pp) for pp in pins))
    s += '\t\t(embedded_fonts no)\n\t)\n'
    return s

# ======================================================================================
#  ŞEMA (.kicad_sch) — parçalar bloklar halinde; bağlantılar net etiketleriyle
# ======================================================================================
BLOCKS = [
    ('BESLEME', ['TB1', 'F1', 'P4', 'P5', 'D1', 'C1', 'C2', 'C7', 'C6', 'R1', 'C3', 'C8', 'C4', 'R2', 'C5', 'R3', 'D2']),
    ('GİRİŞ / JFET (Q1 BF245B Fairchild: 1=G 2=S 3=D)', ['J1', 'JP1', 'R5', 'R6', 'Q1', 'R4', 'TR1', 'C9', 'RV4', 'C10']),
    ('GAIN + SW1 (panel) + LM386', ['RV1', 'R7', 'CB1', 'CD1', 'P1', 'P2', 'P3', 'U1', 'R8', 'C11', 'C12', 'R9', 'C13', 'C14']),
    ('US TON YIĞINI (Fender)', ['R10', 'R11', 'C15', 'C26', 'C16', 'C17', 'R13', 'R14', 'R15', 'R16']),
    ('UK TON YIĞINI (Marshall)', ['R12', 'R17', 'R18', 'C18', 'C19', 'C20', 'R19', 'R20', 'R30', 'R21', 'R22', 'R31']),
    ('ISF + VOLUME + TDA2003 GİRİŞİ', ['RV2', 'RV3', 'R23', 'R24', 'C21', 'C22']),
    ('TDA2003 GÜÇ KATI', ['U2', 'R25', 'R26', 'C23', 'R27', 'C24']),
    ('ÇIKIŞ: HOPARLÖR / KULAKLIK', ['C25', 'J2', 'R28', 'R29', 'TB2']),
    ('MONTAJ DELİKLERİ', ['MH1', 'MH2', 'MH3', 'MH4', 'MH5']),
]
if KOPRULER:
    BLOCKS.append(('TEL KÖPRÜLER (GND dolgu adaları)', [k['ref'] for k in KOPRULER]))
_all = sum((b[1] for b in BLOCKS), [])
assert sorted(_all) == sorted(PARTS), set(PARTS) ^ set(_all)

ROOT = uid('root')
def lib_pins(name): return SYM[name][1]

def build_sch():
    # netlerin kullanım sayısı: tek pinli netlere etiket yerine "bağlantı yok" işareti
    cnt = {}
    for ref, (fp, val, nets) in PARTS.items():
        for n in nets: cnt[n] = cnt.get(n, 0) + 1
    used = sorted({symtype(r, *PARTS[r][:2]) for r in PARTS})
    s = '(kicad_sch\n\t(version 20250114)\n\t(generator "amfi_gen")\n\t(generator_version "9.0")\n'
    s += '\t(uuid %s)\n\t(paper "A2")\n' % q(ROOT)
    s += '\t(title_block (title "12V Gitar Amfisi (dumble-clone)") (date "2026-11-14") (rev "KiCad-1")\n'
    s += '\t\t(comment 1 "Kaynak: tools/design2.py netlisti (kart-v3). Bağlantılar net etiketleriyle.")\n'
    s += '\t\t(comment 2 "SW1 ve güç anahtarı panelde; kartta P1-P5 kablo padleri."))\n'
    s += '\t(lib_symbols\n' + ''.join(symbol_def(n, PRJ + ':') for n in used) + '\t)\n'
    body = ''
    CW, X0 = 27.94, 25.4
    y = 30.48
    for title, refs in BLOCKS:
        body += '\t(text %s (exclude_from_sim no) (at %s %s 0) (effects (font (size 2.032 2.032) (bold yes)) (justify left bottom)) (uuid %s))\n' % (
            q(title), f(X0 - 5.08), f(y - 7.62), q(uid('txt', title)))
        x = X0
        rowh = 0
        for ref in refs:
            fp, val, nets = PARTS[ref]
            st = symtype(ref, fp, val)
            pins = lib_pins(st)
            wide = st in ('LM386', 'TDA2003', 'JACK3', 'PJ324')
            if wide: x += 7.62
            if x > 540:
                x = X0; y += rowh + 12.7; rowh = 0
            sx, sy = round(x / 1.27) * 1.27, round((y + 5.08) / 1.27) * 1.27
            ext = max([abs(pp[3]) for pp in pins] + [5.08])
            rowh = max(rowh, 2 * ext + 5.08)
            s_ref = ref
            fpn = fpname(fp)
            body += '\t(symbol (lib_id %s) (at %s %s 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board yes) (dnp no) (fields_autoplaced yes) (uuid %s)\n' % (
                q(PRJ + ':' + st), f(sx), f(sy), 'no' if st == 'MH' else 'yes', q(uid('sym', ref)))
            body += '\t\t(property "Reference" %s (at %s %s 0) (effects (font (size 1.27 1.27)) (justify left)))\n' % (q(s_ref), f(sx + 2.54), f(sy - 1.27))
            body += '\t\t(property "Value" %s (at %s %s 0) (effects (font (size 1.27 1.27)) (justify left)))\n' % (q(val), f(sx + 2.54), f(sy + 1.27))
            body += '\t\t(property "Footprint" %s (at %s %s 0) %s)\n' % (q(PRJ + ':' + fpn), f(sx), f(sy), FONTH)
            body += '\t\t(property "Datasheet" "" (at %s %s 0) %s)\n' % (f(sx), f(sy), FONTH)
            body += '\t\t(property "Description" "" (at %s %s 0) %s)\n' % (f(sx), f(sy), FONTH)
            for pp in pins:
                body += '\t\t(pin %s (uuid %s))\n' % (q(pp[0]), q(uid('pin', ref, pp[0])))
            body += '\t\t(instances (project %s (path %s (reference %s) (unit 1))))\n\t)\n' % (q(PRJ), q('/' + ROOT), q(s_ref))
            # etiketler
            for (num, name, px, py, ang) in pins:
                net = nets[int(num) - 1]
                ex, ey = sx + px, sy - py
                if cnt[net] == 1:
                    body += '\t(no_connect (at %s %s) (uuid %s))\n' % (f(ex), f(ey), q(uid('nc', ref, num)))
                    continue
                la = (ang + 180) % 360
                just = {0: 'left bottom', 180: 'right bottom', 90: 'left bottom', 270: 'right bottom'}[la]
                body += '\t(label %s (at %s %s %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid %s))\n' % (
                    q(net), f(ex), f(ey), la, just, q(uid('lbl', ref, num)))
            x += CW + (7.62 if wide else 0)
        y += rowh + 20.32
    s += body
    s += '\t(sheet_instances (path "/" (page "1")))\n\t(embedded_fonts no)\n)\n'
    return s, y

# ======================================================================================
#  PROJE + KURALLAR
# ======================================================================================
POWER = sorted(D.POWER_NETS)
def project():
    return {
        "board": {"design_settings": {
            "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2},
            "rules": {"min_clearance": 0.5, "min_track_width": 0.5, "min_copper_edge_clearance": 0.5,
                      "min_through_hole_diameter": 0.6, "min_hole_to_hole": 0.5, "min_hole_clearance": 0.25,
                      "min_via_diameter": 2.0, "min_via_annular_width": 0.3, "min_connection": 0.5,
                      "allow_blind_buried_vias": False, "allow_microvias": False, "solder_mask_to_copper_clearance": 0.0},
            "track_widths": [0.0, 1.0, 1.3, 2.0], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}],
        }},
        "meta": {"filename": PRJ + ".kicad_pro", "version": 3},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": 0.5, "track_width": 1.0, "via_diameter": 2.0, "via_drill": 0.8,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647},
                {"name": "Guc", "clearance": 0.5, "track_width": 1.3, "via_diameter": 2.0, "via_drill": 0.8,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 0},
                {"name": "GND", "clearance": 0.5, "track_width": 1.3, "via_diameter": 2.0, "via_drill": 0.8,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 1},
            ],
            "meta": {"version": 4},
            "netclass_patterns": [{"netclass": "Guc", "pattern": n} for n in POWER] + [{"netclass": "GND", "pattern": "GND"}],
        },
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [[ROOT, "Root"]],
        "text_variables": {},
    }

DRU = '''(version 1)
# Tek yüzlü ev yapımı kart: bakır yalnız B.Cu (alt). Üst katta yol/via/dolgu yasak.
(rule "tek_yuz_ust_yasak"
\t(layer "F.Cu")
\t(condition "A.Type == 'track' || A.Type == 'arc' || A.Type == 'zone'")
\t(constraint disallow track zone))
(rule "via_yok"
\t(constraint disallow via))
# Toner transfer: en küçük bakır aralığı 0.5 mm (dolgu dahil)
(rule "aralik"
\t(constraint clearance (min 0.5mm)))
(rule "kenar"
\t(constraint edge_clearance (min 0.5mm)))
# arka/sol/sağ kenarda 1 mm şerit kural alanlarıyla korunur; ön kenarda potların altından geçen yollar için 0.5 mm
'''

def main():
    os.makedirs(os.path.join(OUT, PRJ + '.pretty'), exist_ok=True)
    seen = set()
    for ref, (fp, val, nets) in PARTS.items():
        if fp in seen: continue
        seen.add(fp)
        name, txt = footprint(fp)
        open(os.path.join(OUT, PRJ + '.pretty', name + '.kicad_mod'), 'w', encoding='utf-8').write(txt)
    lib = '(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "amfi_gen")\n\t(generator_version "9.0")\n'
    lib += ''.join(symbol_def(n) for n in SYM) + ')\n'
    open(os.path.join(OUT, PRJ + '.kicad_sym'), 'w', encoding='utf-8').write(lib)
    sch, _ = build_sch()
    open(os.path.join(OUT, PRJ + '.kicad_sch'), 'w', encoding='utf-8').write(sch)
    json.dump(project(), open(os.path.join(OUT, PRJ + '.kicad_pro'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    open(os.path.join(OUT, PRJ + '.kicad_dru'), 'w', encoding='utf-8').write(DRU)
    open(os.path.join(OUT, 'sym-lib-table'), 'w').write(
        '(sym_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.kicad_sym")(options "")(descr "amfi projesi"))\n)\n' % (PRJ, PRJ))
    open(os.path.join(OUT, 'fp-lib-table'), 'w').write(
        '(fp_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.pretty")(options "")(descr "amfi projesi"))\n)\n' % (PRJ, PRJ))
    print('parça', len(PARTS), 'ayak izi', len(seen), 'net', len({n for v in PARTS.values() for n in v[2]}))

if __name__ == '__main__':
    main()
