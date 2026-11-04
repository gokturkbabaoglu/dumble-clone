"""Off-board wiring diagram (inside-cabinet view)."""
import math
from layout import wires as PADS

O = []
def add(s): O.append(s)
def line(pts, col='#333', w=2.2, dash=None):
    d = ' '.join(f'{"M" if i == 0 else "L"}{x:.1f},{y:.1f}' for i, (x, y) in enumerate(pts))
    add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{f" stroke-dasharray=\"{dash}\"" if dash else ""}/>')
def text(x, y, s, size=12, anchor='start', weight=400, col='#1f2933'):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{col}">{s}</text>')
def twisted(p1, p2, cols, amp=4.5, period=16):
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
    n = len(cols); steps = max(int(L / 2), 2)
    for k, c in enumerate(cols):
        ph = 2 * math.pi * k / n
        pts = []
        for i in range(steps + 1):
            t = i / steps; s = t * L
            env = min(1, s / 10, (L - s) / 10)
            off = amp * env * math.sin(2 * math.pi * s / period + ph)
            pts.append((x1 + ux * s + nx * off, y1 + uy * s + ny * off))
        line(pts, c, 2.2)

# board geometry
BX, BY, PP = 300, 300, 17
def pad(i):
    x, y = PADS[i - 1][0], PADS[i - 1][1]
    return (BX + (x - 0.5) * PP, BY + (y - 0.5) * PP)

RED, BLK = '#c62828', '#222'
C = {'sig': '#1565c0', 'sig2': '#2e7d32', 'sig3': '#8e24aa', 'sig4': '#ef6c00', 'wh': '#9e9e9e'}

# ---------- board ----------
add(f'<rect x="{BX-8}" y="{BY-8}" width="{31*PP+16}" height="{14*PP+16}" rx="8" fill="#e8d3a6" stroke="#9c7c43"/>')
for c in range(1, 32):
    for r in range(1, 15):
        add(f'<circle cx="{BX+(c-0.5)*PP}" cy="{BY+(r-0.5)*PP}" r="1.6" fill="#b49460"/>')
text(BX + 31 * PP / 2, BY + 14 * PP / 2 + 5, 'KART (parça yüzü, üstten)', 15, 'middle', 700, '#8a6d3b')
text(BX + 31 * PP / 2, BY + 14 * PP / 2 + 24, 'Pedlerin yeri için yerleşim çizimine bak', 11, 'middle', 400, '#8a6d3b')

# ---------- component icons ----------
def pot_rear(cx, cy, name, val, note1, note2, col):
    """rear view: lug 3 left, 2 middle, 1 right. returns lug coords dict"""
    add(f'<circle cx="{cx}" cy="{cy}" r="32" fill="#f4f6f8" stroke="#555" stroke-width="2"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#ddd" stroke="#777"/>')
    lugs = {}
    for k, n in ((-22, 3), (0, 2), (22, 1)):
        x = cx + k; y = cy + 30
        add(f'<rect x="{x-5}" y="{y}" width="10" height="20" rx="2" fill="#cfd4d9" stroke="#555"/>')
        add(f'<circle cx="{x}" cy="{y+14}" r="2.6" fill="#fff" stroke="#555"/>')
        text(x, y + 34, str(n), 12, 'middle', 800, '#333')
        lugs[n] = (x, y + 14)
    text(cx, cy - 66, f'{name} · {val}', 14, 'middle', 800, col)
    text(cx, cy - 50, f'{note1} {note2}', 10.5, 'middle', 600, '#333')
    lugs['body'] = (cx + 30, cy - 10)
    return lugs

def slide_sw(cx, cy, name, col, labels=('', 'orta', '')):
    add(f'<rect x="{cx-34}" y="{cy-14}" width="68" height="28" rx="4" fill="#f4f6f8" stroke="#555" stroke-width="2"/>')
    add(f'<rect x="{cx-10}" y="{cy-6}" width="20" height="12" rx="2" fill="#bbb"/>')
    lugs = {}
    for k, key in ((-20, 'a'), (0, 'm'), (20, 'b')):
        x = cx + k; y = cy + 14
        add(f'<rect x="{x-3.5}" y="{y}" width="7" height="16" fill="#cfd4d9" stroke="#555"/>')
        add(f'<circle cx="{x}" cy="{y+11}" r="2.4" fill="#fff" stroke="#555"/>')
        lugs[key] = (x, y + 11)
    text(cx, cy - 22, name, 13, 'middle', 800, col)
    text(cx, cy + 44, labels[1], 9.5, 'middle', 600, '#555')
    return lugs

def lug_dot(x, y): add(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#fff" stroke="#333" stroke-width="1.6"/>')

# pots (top)
VR3 = pot_rear(450, 130, 'VR3 SHAPE', 'B22k', 'önden sol: Fender,', 'sağ: Marshall', '#0369a1')
VR2 = pot_rear(620, 130, 'VR2 VOLUME', 'B100k', 'saat yönü:', 'ses açılır', '#0369a1')
VR1 = pot_rear(790, 130, 'VR1 GAIN', 'B1k', 'saat yönü:', 'gain açılır', '#047857')

# J1 input jack (left)
def jack_mono(cx, cy):
    add(f'<rect x="{cx-30}" y="{cy-26}" width="60" height="52" rx="6" fill="#f4f6f8" stroke="#555" stroke-width="2"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#fff" stroke="#555"/>')
    t = (cx + 30, cy - 12); s = (cx + 30, cy + 12)
    lug_dot(*t); lug_dot(*s)
    text(cx + 22, cy - 15, 'uç', 9.5, 'end', 600); text(cx + 22, cy + 21, 'gövde', 9.5, 'end', 600)
    return {'tip': t, 'sl': s}
J1 = jack_mono(110, 420); text(110, 382, 'J1 GİRİŞ 6,35 mm', 13, 'middle', 800, '#c2410c')

S2 = slide_sw(150, 590, 'S2 BRIGHT/DARK', '#7c3aed')

# power (right top)
S1 = slide_sw(990, 300, 'S1 AÇ/KAPA', '#b91c1c')
def dcjack(cx, cy):
    add(f'<rect x="{cx-28}" y="{cy-24}" width="56" height="48" rx="6" fill="#f4f6f8" stroke="#555" stroke-width="2"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="9" fill="#fff" stroke="#555"/><circle cx="{cx}" cy="{cy}" r="2.5" fill="#555"/>')
    p = (cx - 28, cy - 10); m = (cx - 28, cy + 12)
    lug_dot(*p); lug_dot(*m)
    text(cx - 20, cy - 13, '+ merkez', 9, 'start', 600); text(cx - 20, cy + 22, '− gövde', 9, 'start', 600)
    return {'p': p, 'm': m}
J2 = dcjack(1135, 300); text(1135, 264, 'J2 12 V DC', 13, 'middle', 800, '#b91c1c')

# speaker + S3
S3 = slide_sw(990, 450, 'S3 HOPARLÖR', '#a16207')
add('<rect x="1100" y="425" width="22" height="50" fill="#f4f6f8" stroke="#555" stroke-width="2"/><path d="M1122,425 L1150,405 L1150,495 L1122,475 Z" fill="#f4f6f8" stroke="#555" stroke-width="2"/>')
SPp = (1100, 437); SPm = (1100, 463); lug_dot(*SPp); lug_dot(*SPm)
text(1094, 433, '+', 12, 'end', 800, RED); text(1094, 475, '−', 13, 'end', 800)
text(1125, 515, 'SP1 8 Ω', 13, 'middle', 800, '#a16207')

# J3 headphones
def jack_st(cx, cy):
    add(f'<rect x="{cx-34}" y="{cy-26}" width="68" height="52" rx="6" fill="#f4f6f8" stroke="#555" stroke-width="2"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="8" fill="#fff" stroke="#555"/>')
    L_ = (cx - 34, cy - 14); R_ = (cx - 34, cy); G_ = (cx - 34, cy + 14)
    for p, n in ((L_, 'L (uç)'), (R_, 'R (halka)'), (G_, 'gövde')):
        lug_dot(*p); text(p[0] + 8, p[1] + 3.5, n, 9, 'start', 600)
    return {'L': L_, 'R': R_, 'G': G_}
J3 = jack_st(1010, 620); text(1010, 582, 'J3 KULAKLIK 3,5 mm', 13, 'middle', 800, '#be185d')

# ---------- wiring ----------
def badge(i, col):
    x, y = pad(i)
    add(f'<circle cx="{x}" cy="{y}" r="8" fill="#fff" stroke="{col}" stroke-width="2.6"/>')
    text(x, y + 3.6, str(i), 9.5, 'middle', 800, col)

# B1 input (1 tip, 2 sleeve) -> J1
g = (262, 432); h = (172, 420)
line([pad(1), (pad(1)[0], 432), (g[0]+8, 432)], C['sig']); line([pad(2), (pad(2)[0], 440), (g[0]+8, 440)], BLK)
twisted((g[0]+8, 436), h, [C['sig'], BLK])
line([h, (150, 420), (150, J1['tip'][1]), J1['tip']], C['sig']); line([h, (155, 424), (155, J1['sl'][1]), J1['sl']], BLK)

# B2 S2 (3 Y, 4 GND)
line([pad(3), (pad(3)[0], 560), (440, 560)], C['sig3']); line([pad(4), (pad(4)[0]+6, 560), (440, 566)], BLK)
twisted((440, 563), (240, 620), [C['sig3'], BLK])
line([(240, 620), S2['m']], C['sig3']); line([(240, 620), (228, 640), (S2['b'][0], 640), S2['b']], BLK)
text(150, 668, 'orta + bir yan bacak; sürgü o yandayken = Dark', 9.5, 'middle', 600, '#7c3aed')
text(S2['a'][0], 668, '', 9)

# B3 shape (5 -> lug3, 6 -> lug1)
gs = (520, 280)
line([pad(5), (pad(5)[0], 286), (gs[0]-4, 286)], C['sig']); line([pad(6), (pad(6)[0], 280), (gs[0]+4, 280)], C['sig2'])
twisted(gs, (450, 205), [C['sig'], C['sig2']])
line([(450, 205), (VR3[3][0], 190), VR3[3]], C['sig']); line([(450, 205), (VR3[1][0], 190), VR3[1]], C['sig2'])
# jumper VR3 lug2 -> VR2 lug3
line([VR3[2], (VR3[2][0], 196), (VR2[3][0], 196), VR2[3]], C['sig4'], 2.6)
text((VR3[2][0] + VR2[3][0]) / 2, 191, 'kısa tel', 9.5, 'middle', 600, C['sig4'])

# B4 volume (7 -> lug2, 8 GND -> lug1)
gv = (682, 270)
line([pad(7), (pad(7)[0] - 3, gv[1] + 4)], C['sig']); line([pad(8), (pad(8)[0] + 4, gv[1] + 4)], BLK)
twisted((gv[0], gv[1] + 4), (630, 210), [C['sig'], BLK])
line([(630, 210), (VR2[2][0], 200), VR2[2]], C['sig']); line([(630, 210), (VR2[1][0], 204), VR2[1]], BLK)

# B5 gain (9 -> lug2, 10 -> lug3)
gg = (740, 262)
line([pad(9), (pad(9)[0], 330), (gg[0] - 4, 330), (gg[0] - 4, gg[1])], C['sig2']); line([pad(10), (pad(10)[0] + 34, pad(10)[1]), (gg[0] + 4, pad(10)[1]), (gg[0] + 4, gg[1])], C['sig'])
twisted(gg, (785, 210), [C['sig2'], C['sig']])
line([(785, 210), (VR1[2][0], 200), VR1[2]], C['sig2']); line([(785, 210), (VR1[3][0], 202), VR1[3]], C['sig'])
text(VR1[1][0] + 8, VR1[1][1] + 26, '1 boş', 9.5, 'start', 600, '#888')
text(VR3[2][0] + 10, VR3[2][1] + 26, '', 9)

text(620, 32, 'Pot gövdelerini çıplak telle birbirine ve VR2 1. bacağa (GND) bağla', 10, 'middle', 600, '#666')

# B6 power (11 +12 -> S1 side, 12 GND -> J2 −)
gp = (870, 330)
line([pad(11), (pad(11)[0], 286), (gp[0], 286), (gp[0], gp[1] - 4)], RED); line([pad(12), (pad(12)[0] + 30, pad(12)[1]), (gp[0] + 8, pad(12)[1]), (gp[0] + 8, gp[1] - 4)], BLK)
twisted((gp[0] + 4, gp[1] - 6), (985, 372), [RED, BLK])
line([(985, 372), S1['m']], RED)
line([(985, 372), (1085, 374), (1085, J2['m'][1]), J2['m']], BLK)
# D1 between J2+ and S1 middle
dx1, dx2 = 1040, 1075
line([J2['p'], (1090, J2['p'][1]), (1090, 225), (dx2 + 8, 225)], RED)
add(f'<path d="M{dx2},215 L{dx2},235 L{dx1+18},225 Z" fill="#222"/>'); line([(dx1 + 18, 213), (dx1 + 18, 237)], '#222', 2.6)
line([(dx1 + 18, 225), (944, 225), (944, 345), (S1['a'][0], 345), S1['a']], RED)
add(f'<rect x="{dx1+8}" y="207" width="44" height="36" rx="10" fill="none" stroke="#888" stroke-dasharray="3 3"/>')
text(1060, 200, 'D1 1N4007 (makaronlu)', 9.5, 'middle', 600)
text(1060, 256, 'çizgi S1 tarafında', 9, 'middle', 400, '#555')

# LED from S1 middle (switched +12) to J2 −
add('<circle cx="988" cy="350" r="3.3" fill="#c62828"/>')
line([(988, 350), (1010, 350)], RED)
add('<rect x="1010" y="344" width="28" height="12" fill="#fff" stroke="#555" stroke-width="1.6"/>')
line([(1038, 350), (1048, 350)], RED)
add('<path d="M1048,342 L1048,358 L1062,350 Z" fill="#facc15" stroke="#555" stroke-width="1.4"/>'); line([(1062, 342), (1062, 358)], '#555', 2)
line([(1062, 350), (1085, 350), (1085, 374)], BLK)
add('<circle cx="1085" cy="374" r="3.3" fill="#222"/>')
text(1024, 338, 'RLED 2,2k', 9, 'middle', 600); text(1055, 372, 'LED (uzun bacak sol)', 9, 'middle', 600, '#a16207')

# B7 speaker (13 -> S3 middle, 14 -> SP −)
gk = (870, 450)
line([pad(13), (pad(13)[0], 452), (gk[0], 452)], C['sig4']); line([pad(14), (pad(14)[0], 458), (gk[0], 458)], BLK)
twisted((gk[0], 455), (948, 495), [C['sig4'], BLK])
line([(948, 495), S3['m']], C['sig4']); line([(948, 495), (1070, 497), (1070, SPm[1]), SPm], BLK)
line([S3['b'], (S3['b'][0], 480), (1060, 480), (1060, SPp[1]), SPp], C['sig4'])

# B8 headphones (15 L, 16 R, 17 GND)
gh = (850, 560)
line([pad(15), (pad(15)[0], gh[1] - 6)], C['sig']); line([pad(16), (pad(16)[0], gh[1])], C['sig3']); line([pad(17), (pad(17)[0], gh[1] + 6)], BLK)
line([(pad(15)[0], gh[1] - 6), (gh[0], gh[1] - 6)], C['sig']); line([(pad(16)[0], gh[1]), (gh[0], gh[1])], C['sig3']); line([(pad(17)[0], gh[1] + 6), (gh[0], gh[1] + 6)], BLK)
twisted(gh, (945, 620), [C['sig'], C['sig3'], BLK], amp=5)
line([(945, 620), (955, J3['L'][1]), J3['L']], C['sig']); line([(945, 620), J3['R']], C['sig3']); line([(945, 620), (955, J3['G'][1]), J3['G']], BLK)

# badges on top
groups = {1: '#c2410c', 2: '#c2410c', 3: '#7c3aed', 4: '#7c3aed', 5: '#0369a1', 6: '#0369a1', 7: '#0369a1', 8: '#0369a1',
          9: '#047857', 10: '#047857', 11: '#b91c1c', 12: '#b91c1c', 13: '#a16207', 14: '#a16207', 15: '#be185d', 16: '#be185d', 17: '#be185d'}
for i, c in groups.items(): badge(i, c)

# legend
LY = 712
twisted((30, LY), (90, LY), ['#1565c0', '#222'])
text(98, LY + 4, '= burgulu (örülmüş) kablo grubu', 11.5, 'start', 600)
line([(330, LY), (370, LY)], RED); text(376, LY + 4, '+12 V', 11.5, 'start', 600)
line([(430, LY), (470, LY)], BLK); text(476, LY + 4, 'GND', 11.5, 'start', 600)
text(30, LY + 26, 'Potlar ARKADAN (lehim tarafından) çizildi: arkadan bakınca 3 solda, 1 sağda. Önden bakınca 1 solda, 3 sağda olur.', 11.5, 'start', 600, '#b45309')

def wiring_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 750" class="sch" font-family="Inter,Arial,sans-serif">'
            '<rect width="1200" height="750" fill="#fff"/>' + '\n'.join(O) + '</svg>')

if __name__ == '__main__':
    open('wiring.svg', 'w').write(wiring_svg()); print('ok')
