"""Yeni KiCad projesi: netlist (design2) ve KiCad standart sembol yardımcıları.

Devre: tools/design2.py netlisti (kicad/amfi/amfi.kicad_sch ile aynı), aynı referans adları
ve değerler. K1/K2 tel köprüleri ve KO_SW* yasak bölgeleri devrenin parçası olmadığı için alınmadı.

Çalıştır:  python kicad/yeni_kart/gen_sch.py [KiCad_semboller_klasörü]
           (varsayılan: D:/kicad/share/kicad/symbols ya da KICAD_SYM ortam değişkeni)
"""
import os, sys, math, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.append(os.path.join(HERE, '..', '..', 'tools'))
from sexp import parse, dump, Sym, find, first
import design2 as D

PRJ = 'amfi_yeni'
SYMDIR = (sys.argv[1] if len(sys.argv) > 1 else
          os.environ.get('KICAD_SYM', 'D:/kicad/share/kicad/symbols'))
NS = uuid.UUID('9b3c1d52-7e4a-4f0e-9d21-5a7c0e11a2b4')
def uid(*k): return str(uuid.uuid5(NS, '/'.join(map(str, k))))
ROOT = uid('root')
S = Sym

# ------------------------------------------------------------------ netlist
REN = {'CB': 'CB1', 'CD': 'CD1', 'P_SWB': 'P1', 'P_SWC': 'P2', 'P_SWD': 'P3', 'P_PW1': 'P4', 'P_PW2': 'P5'}
SKIP = {'KO_SW1', 'KO_SW2'}
LIB = {'R': 'Device:R', 'CF': 'Device:C', 'CC': 'Device:C', 'TO92': 'Device:Q_NJFET_GSD',
       'TRIM': 'Device:R_Potentiometer_Trim', 'POT': 'Device:R_Potentiometer',
       'DIP8': 'Amplifier_Audio:LM386', 'DO201': 'Diode:1N5822', 'PW5': 'Amplifier_Audio:TDA2003',
       'PAD': 'Connector_Generic:Conn_01x01', 'MH': 'Mechanical:MountingHole', 'JMP': 'Jumper:Jumper_2_Open',
       'J635': 'Connector_Audio:AudioJack2_SwitchT', 'PJ324': 'Connector_Audio:AudioJack3_SwitchTR',
       'LED': 'Device:LED', 'FUSE': 'Device:Fuse', 'TB2': 'Connector:Screw_Terminal_01x02'}

PARTS = {}   # ref -> dict(lib, value, pins{num: net}, kind)
for ref, (fp, val, nets) in D.C.items():
    if ref in SKIP:
        continue
    r = REN.get(ref, ref)
    lib = 'Device:C_Polarized' if fp.startswith('E') else LIB[fp]
    if fp == 'MH':
        pins = {}
    elif fp == 'DO201':            # eski sembol 1=A 2=K ; standart 1=K 2=A
        pins = {'2': nets[0], '1': nets[1]}
    elif fp == 'LED':              # eski 1=A 2=K ; standart 1=K 2=A
        pins = {'2': nets[0], '1': nets[1]}
    elif fp == 'J635':             # eski 1=şase 2=kesici 3=uç
        pins = {'S': nets[0], 'TN': nets[1], 'T': nets[2]}
    elif fp == 'PJ324':            # eski 1 sleeve, 2 ring-NC, 3 ring, 4 tip, 5 tip-NC
        pins = {'S': nets[0], 'RN': nets[1], 'R': nets[2], 'T': nets[3], 'TN': nets[4]}
    else:
        pins = {str(i + 1): n for i, n in enumerate(nets)}
    PARTS[r] = dict(lib=lib, value=val, pins=pins, fp=fp)
FPN = {'R': 'R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'CF': 'C_Rect_L7.2mm_W3.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2',
       'CC': 'C_Disc_D5.0mm_W2.5mm_P5.00mm', 'TO92': 'TO-92_Inline_Wide', 'TRIM': 'Potentiometer_Bourns_3296W_Vertical',
       'POT': 'Pot_WH148_16mm_OnKenar', 'DIP8': 'DIP-8_W7.62mm_Socket', 'DO201': 'D_DO-201AD_P15.24mm_Horizontal',
       'PW5': 'TO-220-5_P3.4x3.7mm_StaggerOdd_Lead3.8mm_Vertical', 'PAD': 'SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm',
       'MH': 'MountingHole_3.2mm_M3_Pad', 'JMP': 'Tel_Kopru_P5.08mm', 'J635': 'Jak_6.35mm_Mono_Kesicili',
       'PJ324': 'PJ-324M', 'LED': 'LED_D5.0mm_Dik90_OnKenar', 'FUSE': 'Sigorta_Yuvasi_23x9mm_P10mm',
       'TB2': 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'}
ELKO_FP = {(5.0, 2.0): 'CP_Radial_D5.0mm_P2.00mm', (6.3, 2.5): 'CP_Radial_D6.3mm_P2.50mm', (8.0, 3.5): 'CP_Radial_D8.0mm_P3.50mm',
           (10.0, 5.0): 'CP_Radial_D10.0mm_P5.00mm', (12.5, 5.0): 'CP_Radial_D12.5mm_P5.00mm'}
def footprint(fp):
    n = ELKO_FP[D.ELKO[fp[1:]]] if fp.startswith('E') else FPN[fp]
    return 'amfi_yeni:' + n
PARTS['MH4'] = dict(lib='Mechanical:MountingHole', value='M3', pins={}, fp='MH')
PARTS['MH5'] = dict(lib='Mechanical:MountingHole', value='M3', pins={}, fp='MH')
for _p in PARTS.values():
    _p['footprint'] = footprint(_p['fp'])

# ------------------------------------------------------------------ sembol kütüphanesi
_libcache = {}
def libtree(lib):
    if lib not in _libcache:
        _libcache[lib] = parse(open(os.path.join(SYMDIR, lib + '.kicad_sym'), encoding='utf-8').read())
    return _libcache[lib]

def raw_sym(lib, name):
    for s in find(libtree(lib), 'symbol'):
        if s[1] == name:
            return s
    raise KeyError(lib + ':' + name)

def rename_units(e, old, new):
    for x in e:
        if isinstance(x, list) and x and x[0] == 'symbol' and isinstance(x[1], str) and x[1].startswith(old + '_'):
            x[1] = new + x[1][len(old):]

def get_sym(libid):
    """Gömülü (lib_symbols) biçimde sembol: extends düzleştirilir."""
    import copy
    lib, name = libid.split(':')
    s = copy.deepcopy(raw_sym(lib, name))
    ext = first(s, 'extends')
    if ext:
        parent = get_sym(lib + ':' + ext[1])
        pname = ext[1]
        props = find(s, 'property')
        out = [S('symbol'), libid]
        for x in parent[2:]:
            if isinstance(x, list) and x[0] == 'property':
                continue
            out.append(x)
        # özellikleri unit'lerden önce koy
        k = next(i for i, x in enumerate(out) if isinstance(x, list) and x[0] == 'symbol')
        out[k:k] = props
        rename_units(out, pname, name)
        return out
    s[1] = libid
    return s

def pins_of(sym):
    res = {}
    for u in find(sym, 'symbol'):
        for p in find(u, 'pin'):
            at = first(p, 'at'); num = first(p, 'number')[1]
            res[num] = (float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0)
    return res

def prop(sym, key):
    for p in find(sym, 'property'):
        if p[1] == key:
            return p
    return None

# ------------------------------------------------------------------ geometri
def rot(x, y, r):
    c, s = round(math.cos(math.radians(r))), round(math.sin(math.radians(r)))
    return x * c - y * s, x * s + y * c

def pin_world(X, Y, r, px, py, pa):
    x, y = rot(px, py, r)
    a = (pa + r) % 360
    body = (round(math.cos(math.radians(a))), -round(math.sin(math.radians(a))))
    return (round(X + x, 3), round(Y - y, 3)), (-body[0], -body[1])

def F(v): return S(('%.3f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-9 else '0')

def font(size=1.27, bold=False):
    f = [S('font'), [S('size'), F(size), F(size)]]
    if bold:
        f.append([S('bold'), S('yes')])
    return f

def effects(justify=None, hide=False, size=1.27, bold=False):
    e = [S('effects'), font(size, bold)]
    if justify:
        e.append([S('justify')] + [S(j) for j in justify.split()])
    if hide:
        e.append([S('hide'), S('yes')])
    return e

ITEMS = []
SYMS_USED = {}
NPWR = [0]

def sym_instance(ref, libid, value, X, Y, r, pins, refpos=None, valpos=None, fpname='', hide_ref=False):
    sym = SYMS_USED.setdefault(libid, get_sym(libid))
    def ppos(key, given):
        if given:
            return given
        p = prop(sym, key); at = first(p, 'at')
        x, y = rot(float(at[1]), float(at[2]), r)
        ang = float(at[3]) if len(at) > 3 else 0
        if r in (90, 270):
            ang = (ang + 90) % 180
        hide = first(p, 'hide') is not None or any(isinstance(x, list) and x[0] == 'effects' and first(x, 'hide') for x in p)
        j = None
        eff = first(p, 'effects')
        if eff is not None and first(eff, 'justify') is not None:
            j = ' '.join(first(eff, 'justify')[1:])
        if r == 180 and j:
            j = j.replace('left', 'TMP').replace('right', 'left').replace('TMP', 'right')
        return (X + x, Y - y, ang, j)
    rp = ppos('Reference', refpos); vp = ppos('Value', valpos)
    e = [S('symbol'), [S('lib_id'), libid], [S('at'), F(X), F(Y), F(r)], [S('unit'), S('1')],
         [S('exclude_from_sim'), S('no')], [S('in_bom'), S('no' if ref.startswith('#') else 'yes')],
         [S('on_board'), S('no' if ref.startswith('#') else 'yes')], [S('dnp'), S('no')],
         [S('uuid'), uid('sym', ref)]]
    def P(key, val, pos, hide=False):
        x, y, a, j = pos
        return [S('property'), key, val, [S('at'), F(x), F(y), F(a)], effects(j, hide)]
    e.append(P('Reference', ref, rp, hide_ref))
    e.append(P('Value', value, vp))
    e.append(P('Footprint', fpname, (X, Y, 0, None), True))
    e.append(P('Datasheet', '~', (X, Y, 0, None), True))
    e.append(P('Description', '', (X, Y, 0, None), True))
    for num in pins_of(sym):
        e.append([S('pin'), num, [S('uuid'), uid('pin', ref, num)]])
    e.append([S('instances'), [S('project'), PRJ, [S('path'), '/' + ROOT, [S('reference'), ref], [S('unit'), S('1')]]]])
    ITEMS.append(e)
    return {num: pin_world(X, Y, r, *v) for num, v in pins_of(sym).items()}

def wire(a, b):
    ITEMS.append([S('wire'), [S('pts'), [S('xy'), F(a[0]), F(a[1])], [S('xy'), F(b[0]), F(b[1])]],
                  [S('stroke'), [S('width'), S('0')], [S('type'), S('default')]], [S('uuid'), uid('w', a, b)]])

def label(name, p, d):
    ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[d]
    j = 'left bottom' if ang in (0, 90) else 'right bottom'
    ITEMS.append([S('label'), name, [S('at'), F(p[0]), F(p[1]), F(ang)], effects(j), [S('uuid'), uid('lbl', name, p)]])

def gnd(p, up=False):
    NPWR[0] += 1
    ref = '#PWR%03d' % NPWR[0]
    r = 180 if up else 0
    sym_instance(ref, 'power:GND', 'GND', p[0], p[1], r, None,
                 refpos=(p[0], p[1] + (-6.35 if up else 6.35), 0, None),
                 valpos=(p[0], p[1] + (-3.81 if up else 3.81), 0, None), hide_ref=True)

def text(s, x, y, size=2.0, bold=True):
    ITEMS.append([S('text'), s, [S('exclude_from_sim'), S('no')], [S('at'), F(x), F(y), S('0')],
                  effects('left bottom', size=size, bold=bold), [S('uuid'), uid('txt', s, x, y)]])

def rect(x1, y1, x2, y2):
    ITEMS.append([S('rectangle'), [S('start'), F(x1), F(y1)], [S('end'), F(x2), F(y2)],
                  [S('stroke'), [S('width'), F(0.15)], [S('type'), S('dash')]], [S('fill'), [S('type'), S('none')]],
                  [S('uuid'), uid('rect', x1, y1)]])

STUB = 2.54
def connect(pinmap, nets, stub=STUB):
    for num, net in nets.items():
        (p, d) = pinmap[num]
        e = (round(p[0] + stub * d[0], 3), round(p[1] + stub * d[1], 3))
        wire(p, e)
        if net == 'GND':
            gnd(e, up=(d == (0, -1)))
        else:
            label(net, e, d)

# Şemanın çizimi (tellerle) gen_sema.py'de. Bu dosya netlist + sembol yardımcılarını sağlar.

if __name__ == '__main__':
    import runpy; runpy.run_path(os.path.join(HERE, 'gen_sema.py'), run_name='__main__')
