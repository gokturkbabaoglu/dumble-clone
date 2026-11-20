"""Proje ayak izi kütüphanesi: kicad/yeni_kart/amfi_yeni.pretty

* KiCad standart ayak izlerinin kopyaları: ölçü/delik/yerleşim aynı, yalnız padler büyütüldü
  (lazerle boya kazıma + asit için). Ad aynı, açıklamaya not eklendi.
* Standardı olmayanlar (WH148 pot, 6,35 jak, PJ-324M, sigorta yuvası, 90° LED, tel köprü) özel çizim.
Kural: pad çapı = max(3,2 mm, delik + 2 mm); aynı ayak izindeki padler arası en az 0,6 mm bakır boşluk.
Çalıştır: python kicad/yeni_kart/gen_fp.py [KiCad_footprints_klasörü]
"""
import os, sys, math, copy, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexp import parse, dump, Sym as S, find, first

FPDIR = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('KICAD_FP', 'D:/kicad/share/kicad/footprints')
OUT = os.path.join(HERE, 'amfi_yeni.pretty')
LIB = 'amfi_yeni'
GAP = 0.6
NS = uuid.UUID('1f7e2c9a-55b1-4c0e-8a3d-77e1b0c4d2aa')
def uid(*k): return str(uuid.uuid5(NS, '/'.join(map(str, k))))
def F(v): return S(('%.4f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-9 else '0')

# (kütüphane, ad) -> pad kuralı: ('circle', d) | ('oval', w, h)  [w: x yönü, h: y yönü]
STD = {
    ('Resistor_THT', 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'): ('circle', 3.2),
    ('Capacitor_THT', 'C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'): ('circle', 3.2),
    ('Capacitor_THT', 'C_Disc_D5.0mm_W2.5mm_P5.00mm'): ('circle', 3.2),
    ('Capacitor_THT', 'CP_Radial_D5.0mm_P2.00mm'): ('oval', 1.4, 2.8),
    ('Capacitor_THT', 'CP_Radial_D6.3mm_P2.50mm'): ('oval', 1.9, 3.0),
    ('Capacitor_THT', 'CP_Radial_D8.0mm_P3.50mm'): ('circle', 2.9),
    ('Capacitor_THT', 'CP_Radial_D10.0mm_P5.00mm'): ('circle', 3.2),
    ('Capacitor_THT', 'CP_Radial_D12.5mm_P5.00mm'): ('circle', 3.4),
    ('Package_DIP', 'DIP-8_W7.62mm_Socket'): ('oval', 3.2, 1.9),
    ('Package_TO_SOT_THT', 'TO-92_Inline_Wide'): ('oval', 1.9, 3.0),
    ('Package_TO_SOT_THT', 'TO-220-5_P3.4x3.7mm_StaggerOdd_Lead3.8mm_Vertical'): ('circle', 2.8),
    ('Diode_THT', 'D_DO-201AD_P15.24mm_Horizontal'): ('circle', 3.6),
    ('TerminalBlock_Phoenix', 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'): ('circle', 3.6),
    ('Potentiometer_THT', 'Potentiometer_Bourns_3296W_Vertical'): ('oval', 1.9, 3.0),
    ('MountingHole', 'MountingHole_3.2mm_M3_Pad'): None,          # değişmez (6,4 mm halka)
    ('Connector_Wire', 'SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm'): ('circle', 3.2),
}

def set_pad(p, rule):
    shape = p[3]
    size = first(p, 'size')
    if rule[0] == 'circle':
        w = h = rule[1]
    else:
        w, h = rule[1], rule[2]
    size[1], size[2] = F(w), F(h)
    if str(shape) in ('rect', 'roundrect'):
        return                                   # 1. pin işareti (kare/yuvarlatılmış) korunur
    p[3] = S('circle' if w == h else 'oval')

def std_fp(lib, name, rule):
    t = parse(open(os.path.join(FPDIR, lib + '.pretty', name + '.kicad_mod'), encoding='utf-8').read())
    d = first(t, 'descr')
    note = ' | amfi_yeni: KiCad %s:%s kopyası, padler ev yapımı tek yüzlü kart için büyütüldü' % (lib, name)
    if d: d[1] = d[1] + note
    if rule:
        for p in find(t, 'pad'):
            set_pad(p, rule)
    return t

# ---------------------------------------------------------------- özel ayak izleri
def prop(key, val, x, y, layer, hide=False):
    e = [S('property'), key, val, [S('at'), F(x), F(y), S('0')], [S('layer'), layer]]
    if hide: e.append([S('hide'), S('yes')])
    e += [[S('uuid'), uid(key, val, x, y)], [S('effects'), [S('font'), [S('size'), S('1'), S('1')], [S('thickness'), S('0.15')]]]]
    return e

def rect(x1, y1, x2, y2, layer, w=0.12, dash=False):
    return [S('fp_rect'), [S('start'), F(x1), F(y1)], [S('end'), F(x2), F(y2)],
            [S('stroke'), [S('width'), F(w)], [S('type'), S('dash' if dash else 'solid')]], [S('fill'), S('no')],
            [S('layer'), layer], [S('uuid'), uid('r', x1, y1, x2, y2, layer)]]

def line(x1, y1, x2, y2, layer, w=0.12):
    return [S('fp_line'), [S('start'), F(x1), F(y1)], [S('end'), F(x2), F(y2)],
            [S('stroke'), [S('width'), F(w)], [S('type'), S('solid')]], [S('layer'), layer], [S('uuid'), uid('l', x1, y1, x2, y2, layer)]]

def text(s, x, y, layer):
    return [S('fp_text'), S('user'), s, [S('at'), F(x), F(y), S('0')], [S('layer'), layer], [S('uuid'), uid('t', s, x, y)],
            [S('effects'), [S('font'), [S('size'), S('0.8'), S('0.8')], [S('thickness'), S('0.12')]]]]

def pad(num, x, y, w, h, drill, rot=0, shape=None):
    shape = shape or ('circle' if w == h else 'oval')
    at = [S('at'), F(x), F(y)] + ([F(rot)] if rot else [])
    return [S('pad'), num, S('thru_hole'), S(shape), at, [S('size'), F(w), F(h)], [S('drill'), F(drill)],
            [S('layers'), '*.Cu', '*.Mask'], [S('remove_unused_layers'), S('no')], [S('uuid'), uid('pad', num, x, y)]]

def custom(name, descr, pads, body, extra=(), ref=(0, 2), val=(0, 3.5)):
    """body: (x1,y1,x2,y2) gövde dikdörtgeni (y=0 kartın ön kenarı, -y kartın içi)"""
    x1, y1, x2, y2 = body
    xs = [p[2] for p in pads] + [x1, x2]; ys = [p[3] for p in pads] + [y1, y2]
    cy = (min(ys) - 2.5, max(ys) + 2.5)
    e = [S('footprint'), name, [S('version'), S('20260206')], [S('generator'), 'amfi_gen'], [S('generator_version'), '10.0'],
         [S('layer'), 'F.Cu'], [S('descr'), descr], [S('tags'), 'amfi_yeni'],
         prop('Reference', 'REF**', ref[0], ref[1], 'F.SilkS'), prop('Value', name, val[0], val[1], 'F.Fab'),
         prop('Datasheet', '', 0, 0, 'F.Fab', True), prop('Description', descr, 0, 0, 'F.Fab', True),
         [S('attr'), S('through_hole')], [S('duplicate_pad_numbers_are_jumpers'), S('no')],
         rect(x1, y1, x2, y2, 'F.SilkS'), rect(x1, y1, x2, y2, 'F.Fab', 0.1)]
    e += list(extra)
    pd = [pad(*p[:1], *p[2:]) for p in pads]
    # avlu: gövde + padler
    bx1 = min([x1] + [p[2] - max(p[4], p[5]) / 2 for p in pads]) - 0.25
    bx2 = max([x2] + [p[2] + max(p[4], p[5]) / 2 for p in pads]) + 0.25
    by1 = min([y1] + [p[3] - max(p[4], p[5]) / 2 for p in pads]) - 0.25
    by2 = max([y2] + [p[3] + max(p[4], p[5]) / 2 for p in pads]) + 0.25
    e.append(rect(bx1, by1, bx2, by2, 'F.CrtYd', 0.05))
    e += pd
    e.append([S('embedded_fonts'), S('no')])
    return e

def customs():
    out = {}
    # WH148 16 mm pot, bacaklar 5 mm aralık, gövde ön yüzünden 5 mm geride (önceki kartla aynı)
    out['Pot_WH148_16mm_OnKenar'] = custom(
        'Pot_WH148_16mm_OnKenar',
        'WH148 16 mm döner pot, 3 bacak 5,0 mm aralık, ön kenara (y=0) dayalı; delik 1,3 mm',
        [('1', None, -5.0, -5.0, 3.6, 3.6, 1.3), ('2', None, 0.0, -5.0, 3.6, 3.6, 1.3), ('3', None, 5.0, -5.0, 3.6, 3.6, 1.3)],
        (-8.5, -9.5, 8.5, 0), [text('ön kenar', 0, 1.2, 'F.Fab')], ref=(0, -11), val=(0, 1.5))
    # 6,35 mm mono kesicili jak: pin şase(S) 7,5 / kesici(TN) 15 / uç(T) 22,5 mm geride
    out['Jak_6.35mm_Mono_Kesicili'] = custom(
        'Jak_6.35mm_Mono_Kesicili',
        '6,35 mm mono PCB jak, kesicili; S=şase, T=uç, TN=uç kesicisi; yassı bacak için 2,3 mm delik',
        [('S', None, 1.25, -7.5, 4.0, 4.0, 2.3), ('TN', None, -1.25, -15.0, 4.0, 4.0, 2.3), ('T', None, -1.25, -22.5, 4.0, 4.0, 2.3)],
        (-7, -25, 7, 0), ref=(0, -26.5), val=(0, 1.5))
    # PJ-324M 3,5 mm stereo kesicili jak (üstten bakış çizimi): S, RN, R, T, TN
    a = -math.degrees(math.atan2(1.0, 2.6))        # ovaller R-RN doğrultusuna dik uzun
    out['PJ-324M'] = custom(
        'PJ-324M',
        'PJ-324M 3,5 mm stereo jak, kesicili (T/TN, R/RN), ön kenara dayalı; delik 1,6 mm',
        [('S', None, 0.0, -1.7, 3.0, 3.0, 1.6),
         ('RN', None, -5.2, -9.6, 2.15, 3.2, 1.6, a),
         ('R', None, -2.6, -8.6, 2.15, 3.2, 1.6, a),
         ('T', None, 4.6, -13.0, 3.0, 3.0, 1.6),
         ('TN', None, 4.1, -5.9, 3.0, 3.0, 1.6)],
        (-5.75, -14.2, 5.75, 0), ref=(0, -16), val=(0, 1.5))
    # sigorta yuvası 23x9 mm, bacak aralığı 10 mm (önceki kartla aynı)
    out['Sigorta_Yuvasi_23x9mm_P10mm'] = custom(
        'Sigorta_Yuvasi_23x9mm_P10mm', '5x20 mm sigorta yuvası, gövde 23x9 mm, bacak aralığı 10 mm, delik 1,3 mm',
        [('1', None, 0.0, 0.0, 3.6, 3.6, 1.3), ('2', None, 10.0, 0.0, 3.6, 3.6, 1.3)],
        (-6.5, -4.5, 16.5, 4.5), ref=(5, -5.8), val=(5, 5.8))
    # 5 mm LED, bacaklar 90° bükülü, gövde ön kenardan dışarı bakar; 1=K, 2=A
    out['LED_D5.0mm_Dik90_OnKenar'] = custom(
        'LED_D5.0mm_Dik90_OnKenar', '5 mm LED, bacaklar 90° bükülü, ön kenara dayalı; 1=K (kısa bacak), 2=A; 2,54 mm aralık',
        [('1', None, 1.27, -5.0, 1.9, 3.0, 0.9), ('2', None, -1.27, -5.0, 1.9, 3.0, 0.9)],
        (-3, -3.5, 3, 0), [text('K', 1.27, -7.3, 'F.SilkS'), text('A', -1.27, -7.3, 'F.SilkS')], ref=(0, -8.8), val=(0, 1.5))
    # tel köprü 5,08 mm (JP1)
    out['Tel_Kopru_P5.08mm'] = custom(
        'Tel_Kopru_P5.08mm', 'Tel köprü / jumper, 5,08 mm, delik 0,9 mm',
        [('1', None, 0.0, 0.0, 3.2, 3.2, 0.9), ('2', None, 5.08, 0.0, 3.2, 3.2, 0.9)],
        (1.0, -0.5, 4.08, 0.5), ref=(2.54, -2.6), val=(2.54, 2.6))
    # TDA2003 için klipsli soğutucu izdüşümü: standart TO-220-5 kopyasına çizim olarak eklenir
    return out

# ---------------------------------------------------------------- pad açıklığı denetimi
def pad_geom(p):
    at = first(p, 'at'); x, y = float(at[1]), float(at[2]); rot = float(at[3]) if len(at) > 3 else 0
    sz = first(p, 'size'); w, h = float(sz[1]), float(sz[2])
    # kapsül: merkez doğrusu + yarıçap (dikdörtgenler için yaklaşık: köşegen yerine kısa kenar)
    r = min(w, h) / 2; L = (max(w, h) - min(w, h)) / 2
    ang = math.radians(rot) + (0 if w >= h else math.pi / 2)
    dx, dy = L * math.cos(ang), -L * math.sin(ang)
    shape = str(p[3])
    return (x - dx, y - dy), (x + dx, y + dy), r, shape, w, h

def seg_dist(a, b, c, d):
    def pt_seg(p, a, b):
        ax, ay = b[0] - a[0], b[1] - a[1]; L2 = ax * ax + ay * ay
        t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2))
        return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)
    return min(pt_seg(a, c, d), pt_seg(b, c, d), pt_seg(c, a, b), pt_seg(d, a, b))

def outline(p, n=240):
    at = first(p, 'at'); x, y = float(at[1]), float(at[2]); rot = math.radians(float(at[3]) if len(at) > 3 else 0)
    sz = first(p, 'size'); w, h = float(sz[1]), float(sz[2]); shape = str(p[3])
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n; c, s_ = math.cos(t), math.sin(t)
        if shape in ('rect', 'roundrect'):               # dikdörtgen (yuvarlatma ihmal: güvenli taraf)
            m = max(abs(c) / (w / 2), abs(s_) / (h / 2)); px, py = c / m, s_ / m
        else:                                            # daire / oval (kapsül)
            r = min(w, h) / 2; L = (max(w, h) - min(w, h)) / 2
            if w >= h: px, py = (L if c >= 0 else -L) + r * c, r * s_
            else: px, py = r * c, (L if s_ >= 0 else -L) + r * s_
        # KiCad: pozitif açı ekranda saat yönünün tersi (y aşağı)
        qx = px * math.cos(rot) + py * math.sin(rot); qy = -px * math.sin(rot) + py * math.cos(rot)
        pts.append((x + qx, y + qy))
    return pts

def check(name, t):
    pads = find(t, 'pad'); worst = 99
    outs = [outline(p) for p in pads]
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            g = min(math.hypot(a[0] - b[0], a[1] - b[1]) for a in outs[i] for b in outs[j])
            worst = min(worst, g)
    return worst

def build():
    os.makedirs(OUT, exist_ok=True)
    allfp = {}
    for (lib, name), rule in STD.items():
        allfp[name] = std_fp(lib, name, rule)
    allfp.update(customs())
    # TO-220-5'e soğutucu izdüşümü (Dwgs.User) ekle
    t = allfp['TO-220-5_P3.4x3.7mm_StaggerOdd_Lead3.8mm_Vertical']
    k = next(i for i, x in enumerate(t) if isinstance(x, list) and x[0] == 'pad')
    t[k:k] = [rect(3.4 - 11, -3.0 - 14, 3.4 + 11, -3.0, 'Dwgs.User', 0.1, True)]
    rep = []
    for name, t in allfp.items():
        g = check(name, t)
        sizes = sorted({tuple(first(p, 'size')[1:3]) for p in find(t, 'pad')})
        drills = sorted({first(p, 'drill')[1] for p in find(t, 'pad') if first(p, 'drill')})
        rep.append((name, g, sizes, drills))
        assert g >= GAP - 1e-6 or len(find(t, 'pad')) < 2, (name, g)
        open(os.path.join(OUT, name + '.kicad_mod'), 'w', encoding='utf-8', newline='\n').write(dump(t) + '\n')
    return rep

if __name__ == '__main__':
    for name, g, sizes, drills in build():
        print('%-62s boşluk %5.2f  pad %s  delik %s' % (name, g, ' '.join('x'.join(s) for s in sizes), ' '.join(drills)))
