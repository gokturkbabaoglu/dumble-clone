import math
from layout import comps, wires, traces, W, H, check

# ======================= PERFBOARD =======================
GROUP_COL = {'J1': '#c2410c', 'S2': '#7c3aed', 'VOL': '#0369a1', 'GAIN': '#047857',
             'PWR': '#b91c1c', 'SPK': '#a16207', 'HP': '#be185d'}
KIND_FILL = {'r_stand': '#e9d8b4', 'r_flat': '#e9d8b4', 'ecap': '#bcd3ee', 'film': '#f3e08a',
             'ceram': '#f6c879', 'to92': '#3a3a3a', 'dip8': '#2f2f2f'}
NET_COL = {'GND': '#5b6470', '+12V': '#c0392b', 'VPRE': '#e67e22'}

def board_svg(mirror=False, pitch=26, show_parts=True):
    m = 34
    Wpx, Hpx = W * pitch + 2 * m, H * pitch + 2 * m + 18
    def X(c): return m + ((W + 1 - c) if mirror else c) * pitch - pitch / 2
    def Y(r): return m + r * pitch - pitch / 2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wpx} {Hpx}" class="board" font-family="Inter,Arial,sans-serif">']
    o.append(f'<rect x="{m-10}" y="{m-10}" width="{W*pitch+20}" height="{H*pitch+20}" rx="8" fill="#c9a86a" stroke="#9c7c43"/>')
    # coordinate labels
    for c in range(1, W + 1):
        o.append(f'<text x="{X(c)}" y="{m-14}" font-size="9" text-anchor="middle" fill="#7a6a4a">{c}</text>')
    for r in range(1, H + 1):
        lx = m - 18 if not mirror else m + W * pitch + 18
        o.append(f'<text x="{lx}" y="{Y(r)+3}" font-size="9" text-anchor="middle" fill="#7a6a4a">{chr(64+r)}</text>')
    def draw_traces():
      for net, pts in traces:
        col = NET_COL.get(net, '#b87333')
        d = ' '.join(f'{"M" if i==0 else "L"}{X(x):.1f},{Y(y):.1f}' for i, (x, y) in enumerate(pts))
        op = 0.8 if mirror else 0.55
        o.append(f'<path d="{d}" stroke="{col}" stroke-width="{pitch*0.36:.1f}" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="{op}"/>')
    if not mirror: draw_traces()
    # holes
    for c in range(1, W + 1):
        for r in range(1, H + 1):
            o.append(f'<circle cx="{X(c)}" cy="{Y(r)}" r="{pitch*0.28:.1f}" fill="#d9b77a" stroke="#b08a4a" stroke-width="1"/>'
                     f'<circle cx="{X(c)}" cy="{Y(r)}" r="{pitch*0.1:.1f}" fill="#5a4a30"/>')
    if mirror: draw_traces()
    # components
    if show_parts:
        for cpt in comps:
            b = cpt['body']; k = cpt['kind']; fill = KIND_FILL[k]
            if b[0] == 'circle':
                cx, cy, rr = X(b[1]), Y(b[2]), b[3] * pitch
                o.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="{fill}" fill-opacity="{0.55 if not mirror else 0.12}" stroke="#334" stroke-width="1.3" stroke-dasharray="{"" if not mirror else "3 3"}"/>')
                if k == 'ecap' and not mirror:
                    # minus stripe marker near minus pad
                    mx, my = cpt['pads'][1][0], cpt['pads'][1][1]
                    o.append(f'<text x="{X(mx)}" y="{Y(my)+ (11 if cpt["pads"][1][1]>=cpt["pads"][0][1] else -6)}" font-size="11" font-weight="700" text-anchor="middle" fill="#123">−</text>')
                    px, py = cpt['pads'][0][0], cpt['pads'][0][1]
                    o.append(f'<text x="{X(px)+ (0 if cpt["pads"][0][0]==mx else -9)}" y="{Y(py)+(-7 if py<=my and px==mx else 4)}" font-size="11" font-weight="700" text-anchor="middle" fill="#b00">+</text>')
            else:
                cx, cy, w, h = X(b[1]), Y(b[2]), b[3] * pitch, b[4] * pitch
                fo = 0.9 if k in ('to92', 'dip8') else 0.6
                if mirror: fo = 0.1
                o.append(f'<rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{3 if k!="to92" else 2}" fill="{fill}" fill-opacity="{fo}" stroke="#334" stroke-width="1.3" stroke-dasharray="{"" if not mirror else "3 3"}"/>')
                if k == 'dip8' and not mirror:
                    o.append(f'<path d="M{cx-w/2:.1f},{cy-6} a6,6 0 0 1 0,12" fill="none" stroke="#ddd" stroke-width="1.5"/>')
                if k == 'to92' and not mirror:
                    o.append(f'<line x1="{cx-w/2:.1f}" y1="{cy-h/2:.1f}" x2="{cx+w/2:.1f}" y2="{cy-h/2:.1f}" stroke="#ffd34d" stroke-width="3"/>')
            # leads
            for (x, y, n, pl) in cpt['pads']:
                o.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{pitch*0.2:.1f}" fill="#9aa3ad" stroke="#222" stroke-width="1"/>')
                if pl and k in ('dip8', 'to92'):
                    o.append(f'<text x="{X(x)}" y="{Y(y)+3.5}" font-size="9" font-weight="700" text-anchor="middle" fill="#fff" stroke="#000" stroke-width="2" paint-order="stroke">{pl}</text>')
            # label
            if b[0] == 'circle':
                lx, ly = X(b[1]), Y(b[2])
            else:
                lx, ly = X(b[1]), Y(b[2])
            if k == 'dip8':
                txt = f'{cpt["ref"]} {cpt["val"]}'; ly2 = ly + 4; col = '#fff'
            elif k == 'to92':
                txt = cpt['ref']; ly2 = ly + 22; col = '#111'
            else:
                txt = cpt['ref']; ly2 = ly + 4; col = '#111'
            if k == 'r_stand':
                # put label beside
                side = -1 if cpt['ref'] in ('Rs',) else 1
                lx += side * (pitch * 0.62 if not mirror else -pitch * 0.62)
                ly2 = ly + 4
            o.append(f'<text x="{lx:.1f}" y="{ly2:.1f}" font-size="{10 if k!="dip8" else 11}" font-weight="700" text-anchor="middle" fill="{col}" stroke="{"#fff" if col=="#111" else "none"}" stroke-width="2.5" paint-order="stroke">{txt}</text>')
    # wire pads
    for i, (x, y, n, lab, g) in enumerate(wires, 1):
        col = GROUP_COL[g]
        o.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{pitch*0.34:.1f}" fill="#fff" stroke="{col}" stroke-width="3"/>')
        o.append(f'<text x="{X(x)}" y="{Y(y)+3.6}" font-size="10" font-weight="800" text-anchor="middle" fill="{col}">{i}</text>')
    title = 'BAKIR (LEHİM) YÜZÜ — ayna görüntüsü' if mirror else 'PARÇA YÜZÜ — üstten görünüm'
    o.append(f'<text x="{m-10}" y="{Hpx-8}" font-size="12" font-weight="700" fill="#333">{title}</text>')
    o.append('</svg>')
    return '\n'.join(o)

# ======================= SCHEMATIC =======================
S = []
def L(*pts, w=1.8, c='#1f2933'):
    d = ' '.join(f'{"M" if i==0 else "L"}{x},{y}' for i, (x, y) in enumerate(pts))
    S.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"/>')
def T(x, y, s, size=12, anchor='start', weight=400, c='#1f2933'):
    S.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{c}">{s}</text>')
def dot(x, y): S.append(f'<circle cx="{x}" cy="{y}" r="3.3" fill="#1f2933"/>')
def gnd(x, y):
    L((x, y), (x, y + 8)); L((x - 10, y + 8), (x + 10, y + 8)); L((x - 6, y + 12), (x + 6, y + 12)); L((x - 2, y + 16), (x + 2, y + 16))
def res_v(x, y1, y2, label=None, lx=None, fill='#fff'):
    S.append(f'<rect x="{x-7}" y="{y1}" width="14" height="{y2-y1}" fill="{fill}" stroke="#1f2933" stroke-width="1.8"/>')
def res_h(x1, x2, y):
    S.append(f'<rect x="{x1}" y="{y-7}" width="{x2-x1}" height="14" fill="#fff" stroke="#1f2933" stroke-width="1.8"/>')
def cap_v(x, y, pol=False):  # vertical current path, plates horizontal, centered y
    L((x - 12, y - 4), (x + 12, y - 4), w=2.4)
    if pol:
        S.append(f'<path d="M{x-12},{y+7} Q{x},{y+1} {x+12},{y+7}" fill="none" stroke="#1f2933" stroke-width="2.4"/>')
        T(x - 18, y - 6, '+', 12, 'middle', 700)
    else:
        L((x - 12, y + 4), (x + 12, y + 4), w=2.4)
def cap_h(x, y, pol=False):  # horizontal current path, plates vertical, centered x
    L((x - 4, y - 12), (x - 4, y + 12), w=2.4)
    if pol:
        S.append(f'<path d="M{x+7},{y-12} Q{x+1},{y} {x+7},{y+12}" fill="none" stroke="#1f2933" stroke-width="2.4"/>')
        T(x - 10, y - 14, '+', 12, 'middle', 700)
    else:
        L((x + 4, y - 12), (x + 4, y + 12), w=2.4)
def arrow(x1, y1, x2, y2, c='#1f2933'):
    ang = math.atan2(y2 - y1, x2 - x1); a = 8
    L((x1, y1), (x2, y2), c=c)
    p1 = (x2 - a * math.cos(ang - 0.4), y2 - a * math.sin(ang - 0.4)); p2 = (x2 - a * math.cos(ang + 0.4), y2 - a * math.sin(ang + 0.4))
    S.append(f'<path d="M{x2},{y2} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" fill="{c}"/>')
def term(x, y): S.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#fff" stroke="#1f2933" stroke-width="1.6"/>')
def cab(x, y, w, h):  # cabinet-mounted part highlight
    S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#eef4fb" stroke="#9bb8d6" stroke-dasharray="4 3"/>')

# cabinet highlights first (background)
cab(14, 168, 70, 92)     # J1
cab(336, 270, 30, 58)    # S2

# rails
L((200, 60), (268, 60)); res_h(268, 328, 60); L((328, 60), (410, 60))
T(298, 84, 'Rf 1k', 11, 'middle'); T(206, 46, 'V_pre ≈ 9–10 V', 11); T(430, 50, '+12 V', 12, 'middle', 700, '#b91c1c')
dot(235, 60); L((235, 60), (235, 96)); cap_v(235, 100, True); L((235, 104), (235, 122)); gnd(235, 122); T(252, 104, 'C6 100µ', 11)
# Rd
L((200, 60), (200, 88)); res_v(200, 88, 148); L((200, 148), (200, 190)); T(178, 112, 'Rd', 11, 'end', 700); T(178, 126, '2,2k', 11, 'end')
# JFET
L((185, 182), (185, 238), w=3)
L((185, 190), (200, 190)); L((185, 230), (200, 230)); L((200, 230), (200, 262))
arrow(120, 210, 184, 210)
T(146, 175, 'Q1 BF245B', 11, 'middle', 700); T(204, 200, 'D', 9); T(204, 244, 'S', 9); T(170, 222, 'G', 9)
dot(200, 180) if False else None
# input jack
S.append('<rect x="24" y="196" width="30" height="28" rx="3" fill="#fff" stroke="#1f2933" stroke-width="1.8"/>')
L((54, 204), (120, 204), (120, 210)); L((54, 218), (64, 218), (64, 230)); gnd(64, 230)
T(49, 186, 'J1 GİRİŞ', 11, 'middle', 700)
dot(100, 204); L((100, 204), (100, 232)); res_v(100, 232, 282); L((100, 282), (100, 296)); gnd(100, 296); T(112, 262, 'Rg 1M', 11)
# source
dot(200, 262); L((200, 262), (200, 282)); res_v(200, 282, 330); L((200, 330), (200, 344)); gnd(200, 344); T(212, 312, 'Rs 1k', 11)
L((200, 262), (250, 262)); cap_h(262, 262, True); L((266, 262), (352, 262)); dot(290, 262); dot(322, 262)
T(266, 238, 'C8 10µ', 10, 'middle')
L((290, 262), (290, 276)); res_v(290, 276, 314); L((290, 314), (290, 330)); gnd(290, 330)
T(290, 362, 'Rb 560', 10, 'middle')
L((322, 262), (322, 292)); cap_v(322, 296); L((322, 300), (322, 330)); gnd(322, 330); T(326, 376, 'C9 100n', 10, 'middle')
L((352, 262), (352, 280)); term(352, 283); term(352, 315); L((351, 286), (340, 312), w=2); L((352, 318), (352, 330)); gnd(352, 330)
T(352, 238, 'S2', 11, 'middle', 700, '#7c3aed'); T(368, 296, 'kapalı=Dark', 9, 'start', 400, '#7c3aed'); T(368, 308, 'açık=Bright', 9, 'start', 400, '#7c3aed')
# drain -> C7 -> node A
L((200, 180), (200, 190)); dot(200, 180); L((200, 180), (262, 180)); cap_h(266, 180); L((270, 180), (410, 180))
T(266, 160, 'C7 100n', 11, 'middle')
S.append('<g transform="translate(50,0)">')
cab(372, 262, 106, 56)
L((360, 60), (1086, 60)); L((360, 180), (380, 180))
dot(380, 180)
# Shape: bridged-T + VR3 crossfade
L((380, 180), (396, 180)); cap_h(400, 180); L((404, 180), (436, 180)); cap_h(440, 180); L((444, 180), (470, 180))
dot(420, 180); dot(470, 180)
L((420, 180), (420, 230)); res_v(420, 196, 228); gnd(420, 230); T(398, 162, 'CT1', 9, 'middle'); T(446, 162, 'CT2', 9, 'middle'); T(434, 214, 'RM 2,2k', 9, 'start')
L((380, 180), (380, 145), (392, 145)); res_h(392, 458, 145); L((458, 145), (470, 145), (470, 180)); T(425, 132, 'RT 10k', 10, 'middle')
L((420, 180), (420, 196)) if False else None
L((380, 180), (380, 280), (392, 280)); res_h(392, 458, 280); L((458, 280), (470, 280), (470, 180))
T(388, 270, '3', 9, 'middle', 700); T(462, 270, '1', 9, 'middle', 700)
arrow(425, 306, 425, 289); L((425, 306), (425, 318), (530, 318), (530, 180), (560, 180))
T(425, 336, 'VR3 SHAPE 22k', 10, 'middle', 700); T(425, 349, 'sol: Fender · sağ: Marshall', 9, 'middle', 400, '#555')
# RM from M down (drawn between caps area)
L((420, 186), (420, 222)) if False else None
S.append('<g transform="translate(90,0)">')
cab(455, 172, 78, 124); cab(628, 396, 72, 54); cab(892, 218, 128, 100); cab(806, 358, 112, 76); cab(946, 28, 218, 150)
# volume VR2
L((470, 180), (470, 196)); res_v(470, 196, 270); L((470, 270), (470, 284)); gnd(470, 284)
arrow(500, 240, 478, 240); L((500, 240), (560, 240))
T(486, 210, 'VR2', 11, 'start', 700); T(486, 223, 'VOLUME', 10); T(486, 235, '100k', 10)
# LM386 box
S.append('<rect x="560" y="170" width="140" height="160" rx="6" fill="#f7f7f2" stroke="#1f2933" stroke-width="2"/>')
T(630, 262, 'LM386', 15, 'middle', 700); T(630, 278, 'U1', 11, 'middle')
T(566, 236, '+3', 11, 'start', 700); T(566, 294, '−2', 11, 'start', 700)
L((560, 290), (536, 290), (536, 300)); gnd(536, 300)
T(636, 186, '6', 11, 'start', 700); L((630, 170), (630, 60)); dot(630, 60)
T(636, 326, '4', 11, 'start', 700); L((630, 330), (630, 346)); gnd(630, 346)
T(580, 326, '1', 11, 'start', 700); T(678, 326, '8', 11, 'end', 700)
T(694, 246, '5', 11, 'end', 700); T(664, 186, '7', 11, 'start', 700)
L((660, 170), (660, 146), (720, 146), (720, 156)); cap_v(720, 160, True); L((720, 164), (720, 178)); gnd(720, 178); T(734, 164, 'C11 10µ', 10)
dot(630, 118); L((630, 118), (598, 118), (598, 126)); cap_v(598, 130); L((598, 134), (598, 142)); gnd(598, 142); T(588, 134, 'C12 100n', 10, 'end')
# gain loop
L((575, 330), (575, 422)); L((575, 422), (590, 422))
L((590, 408), (590, 436)); L((590, 408), (606, 408)); cap_h(610, 408); L((614, 408), (630, 408))
L((590, 436), (606, 436)); cap_h(610, 436); L((614, 436), (630, 436)); L((630, 408), (630, 436))
L((630, 422), (640, 422)); res_h(640, 684, 422); arrow(648, 444, 678, 410)
L((684, 422), (690, 422), (690, 330))
T(610, 460, 'C3‖C4 2×100n', 10, 'middle'); T(662, 406, 'VR1 GAIN', 10, 'middle', 700)
# output
L((700, 250), (790, 250)); dot(740, 250)
L((740, 250), (740, 266)); res_v(740, 266, 300); L((740, 300), (740, 318)); cap_v(740, 322); L((740, 326), (740, 336)); gnd(740, 336)
T(754, 286, 'R1 10Ω', 10); T(754, 326, 'C5 47n', 10); T(754, 352, 'Zobel', 9, 'start', 400, '#666')
cap_h(794, 250, True); L((798, 250), (860, 250)); T(800, 226, 'C2 220µ', 11, 'middle')
dot(780, 60); L((780, 60), (780, 96)); cap_v(780, 100, True); L((780, 104), (780, 122)); gnd(780, 122); T(796, 104, 'C1 220µ', 11)
dot(860, 250)
# S3 + speaker
L((860, 250), (906, 250)); term(909, 250); term(947, 250); L((911, 249), (944, 236), w=2)
T(928, 228, 'S3 HOPARLÖR', 10, 'middle', 700, '#a16207')
L((950, 250), (978, 250), (978, 254)); S.append('<rect x="978" y="248" width="10" height="22" fill="#fff" stroke="#1f2933" stroke-width="1.8"/>')
S.append('<path d="M988,248 L1004,236 L1004,282 L988,270 Z" fill="#fff" stroke="#1f2933" stroke-width="1.8"/>')
L((978, 266), (962, 266), (962, 286)); gnd(962, 286); T(996, 304, 'SP1 8Ω', 10, 'middle')
# headphones
L((860, 250), (860, 296)); L((836, 296), (884, 296)); dot(860, 296)
L((836, 296), (836, 306)); res_v(836, 306, 346); L((884, 296), (884, 306)); res_v(884, 306, 346)
T(822, 330, 'R2', 10, 'end'); T(898, 330, 'R3', 10); T(822, 342, '1k', 10, 'end'); T(898, 342, '1k', 10)
L((836, 346), (836, 380)); L((884, 346), (884, 380))
S.append('<rect x="818" y="380" width="88" height="26" rx="3" fill="#fff" stroke="#1f2933" stroke-width="1.8"/>')
T(836, 397, 'L', 10, 'middle', 700); T(884, 397, 'R', 10, 'middle', 700); T(860, 397, 'G', 10, 'middle', 700)
L((860, 406), (860, 412)); gnd(860, 412); T(862, 376, 'J3 KULAKLIK', 10, 'middle', 700)
# power
dot(970, 60); L((970, 60), (970, 76)); res_v(970, 76, 106); L((970, 106), (970, 118))
S.append('<path d="M961,118 L979,118 L970,132 Z" fill="#fff" stroke="#1f2933" stroke-width="1.8"/>'); L((961, 132), (979, 132), w=2)
arrow(982, 122, 994, 112); arrow(984, 130, 996, 120); L((970, 132), (970, 146)); gnd(970, 146)
T(986, 94, 'RLED 2,2k', 9); T(1002, 136, 'LED1 sarı', 9)
L((996, 60), (1004, 60)); term(1007, 60); term(1045, 60); L((1009, 59), (1042, 46), w=2); T(1026, 40, 'S1 AÇ/KAPA', 10, 'middle', 700, '#b91c1c')
L((1048, 60), (1068, 60))
S.append('<path d="M1094,50 L1094,70 L1076,60 Z" fill="#1f2933"/>'); L((1076, 48), (1076, 72), w=2.4)
L((1068, 60), (1076, 60)); L((1094, 60), (1114, 60)); T(1085, 86, 'D1 1N4007', 10, 'middle')
S.append('<rect x="1114" y="46" width="34" height="34" rx="4" fill="#fff" stroke="#1f2933" stroke-width="1.8"/>')
T(1131, 60, '+', 12, 'middle', 700); T(1131, 75, '−', 12, 'middle', 700)
L((1148, 72), (1156, 72), (1156, 104)); gnd(1156, 104); T(1131, 40, 'J2 12V', 10, 'middle', 700)
S.append('</g>'); S.append('</g>')
# legend
S.append('<rect x="20" y="452" width="22" height="14" rx="4" fill="#eef4fb" stroke="#9bb8d6" stroke-dasharray="4 3"/>')
T(48, 463, 'Kesikli çerçeve = kabin üzerindeki parça (kart dışı). VR3 orta bacağı doğrudan VR2 3. bacağına bağlanır.', 11, 'start', 400, '#444')

def schematic_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 478" class="sch" font-family="Inter,Arial,sans-serif">'
            '<rect width="1320" height="478" fill="#fff"/>' + '\n'.join(S) + '</svg>')

if __name__ == '__main__':
    e, w, a, _, _ = check()
    assert not e, e
    open('schematic.svg', 'w').write(schematic_svg())
    open('board_top.svg', 'w').write(board_svg(False))
    open('board_bottom.svg', 'w').write(board_svg(True))
    print('ok')
