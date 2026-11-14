"""Elle tasarlanmış yerleşimler (sinyal akışı: sol ön -> orta -> sağ arka güç katı).
Koordinat: mm, x sağa, y aşağı (arka kenar y=0, ön kenar y=H). (x, y, dönüş); konum = ayak izinin 1. pini.
Dönüş: 0 = 2. pin sağda, 90 = 2. pin yukarıda (arkaya), 180 = solda, 270 = aşağıda (öne).
"""
import gen_pcb as GP
H, W = GP.H, GP.W

def base():
    """Bütün varyantlarda ortak: ön panel, TDA2003 ve sağ kenar besleme/hoparlör."""
    P = GP.fixed()
    P.update({
        # --- TDA2003 güç katı (arka sağ; soğutucu arka kenardan taşar) ---
        'U2':  (156, 8.5, 0),       # pinler: 1 TIN (152.6) 2 TNEG 3 GND (156) 4 TOUT 5 V12 (159.4)
        'C6':  (167, 7, 270),     # V12 dekuplaj, 5. bacak yanında
        'C7':  (168, 23, 0),       # 1000µ V12
        'R27': (161, 15, 270),      # TOUT -> ZOB2
        'C24': (161, 29, 270),      # ZOB2 -> GND
        'R25': (153, 15, 270),      # TNEG -> TOUT
        'R26': (149, 15, 270),      # TNEG -> TRC
        'C23': (140, 18, 0),        # TRC -> GND (470µ)
        'C25': (152, 34, 270),      # TOUT -> SPK (2200µ)
        # --- besleme girişi ve hoparlör (sağ kenar) ---
        'TB2': (178.3, 30, 90),     # SPKT / GND
        'TB1': (178.3, 50, 90),     # DCIN / GND
        'F1':  (167.5, 50, 270),    # DCIN -> FUSED
        'D1':  (180, 80, 180),      # VIN -> V12
        'C1':  (150, 70, 0),        # 2200µ V12
        'C2':  (160, 86, 0),        # 100n V12
        'R3':  (158, 98, 90),       # V12 -> LED
        # --- kulaklık L-pad ---
        'R28': (140, 94, 0),        # SPK -> HPS
        'R29': (134, 98, 0),        # HPS -> GND
    })
    return P

def K1():
    """Giriş sol önde; LM386 sol-orta; ton yığınları ortada (US üstte, UK altta); TIN zinciri sağ-orta sütunda,
    R1 bu sütunun üstüne köprü gibi oturur (tel köprü gerekmesin)."""
    P = base()
    P.update({
        # --- giriş / JFET ---
        'R5':  (4, 84, 0),          # IN -> GATE
        'Q1':  (18, 80, 0),         # G S D
        'R6':  (16, 74, 180),       # GATE -> GND
        'JP1': (22, 101, 90),       # INDET -> GND (giriş susturma)
        'TR1': (5, 66, 0),          # SRC -> GND
        'C9':  (27, 86, 270),       # SRC -> DRV
        'R4':  (25, 56, 270),       # V3 -> DRAIN
        'C10': (30, 74, 0),         # DRAIN -> GAININ
        'C5':  (32, 58, 0),         # V3
        'R2':  (48, 50, 180),       # V2 -> V3
        # --- gain + LM386 ---
        'U1':  (62, 82, 0),
        'R7':  (46, 98, 90),        # GAINW -> GND
        'CB1': (65, 98, 0),         # GAININ -> SWB
        'CD1': (84, 88, 0),         # SWD -> GND
        'R8':  (59, 85, 180),       # G1 -> G1C
        'C11': (46, 76, 0),         # G1C -> G8
        'C12': (56, 68, 0),         # BYP -> GND
        'R9':  (74, 76, 0),         # O386 -> ZOB1
        'C13': (86, 70, 90),        # ZOB1 -> GND
        'C14': (74, 66, 0),         # O386 -> X
        'C4':  (66, 62, 0),         # V2 100n (6. bacak)
        'C8':  (60, 58, 0),         # V2 100µ
        'C3':  (52, 58, 0),         # V2 220µ
        'R1':  (140, 44, 180),      # V12 -> V2 (TIN/Z sütununun üstünden köprü)
        # --- US ton yığını (üst orta) ---
        'R10': (82, 46, 90), 'R11': (86, 46, 90), 'C15': (90, 50, 90), 'C26': (94, 50, 90),
        'C16': (86, 24, 0), 'C17': (86, 30, 0), 'R13': (98, 46, 90), 'R14': (102, 46, 90),
        'R15': (106, 46, 90), 'R16': (110, 46, 90),
        # --- UK ton yığını (alt orta) ---
        'R12': (90, 78, 90), 'R17': (94, 78, 90), 'R18': (98, 78, 90), 'C18': (102, 74, 90),
        'C19': (106, 74, 90), 'C20': (110, 74, 90), 'R19': (114, 78, 90), 'R20': (118, 78, 90),
        'R30': (122, 78, 90), 'R21': (98, 94, 0), 'R22': (110, 98, 0), 'R31': (110, 92, 0),
        # --- volume -> TDA girişi ---
        'R23': (130, 72, 90),       # VOLW -> Z
        'R24': (134, 30, 90),       # Z -> GND
        'C21': (138, 32, 0),        # Z -> GND
        'C22': (145, 12, 180),      # TIN(+) -> Z
    })
    return P

def K2():
    """Küçültülmüş kart (H ortam değişkeniyle, örn. 100 mm). Giriş katı J1'in hemen sağında sıkı küme;
    LM386 Gain potunun arkasında; ton yığınları ortada iki sıra; TDA arka sağ; besleme sağ kenar."""
    P = GP.fixed()
    h = H
    P.update({
        # giriş / JFET
        'R5': (14, h - 26, 0), 'Q1': (26, h - 32, 0), 'R6': (20, h - 30, 90), 'TR1': (14, h - 40, 0),
        'C9': (38, h - 28, 270), 'R4': (31, h - 48, 270), 'C10': (36, h - 36, 0), 'JP1': (22, h - 20, 270),
        'C5': (26, h - 52, 0), 'R2': (44, h - 54, 180),
        # gain + LM386
        'U1': (58, h - 28, 0), 'R7': (66, h - 20, 0), 'CB1': (64, h - 14, 0), 'CD1': (86, h - 22, 90),
        'R8': (56, h - 24, 180), 'C11': (50, h - 36, 0), 'C12': (60.5, h - 40, 90), 'C4': (64, h - 40, 90),
        'C8': (67, h - 44, 0), 'C3': (72, h - 48, 0), 'R9': (68, h - 34, 0), 'C13': (80, h - 38, 90), 'C14': (70, h - 38, 0),
        # US (arka sıra) / UK (ön sıra)
        'R10': (84, 40, 90), 'R11': (88, 40, 90), 'C15': (92, 40, 90), 'C26': (96, 40, 90), 'C16': (86, 16, 0),
        'C17': (86, 22, 0), 'R13': (100, 40, 90), 'R14': (104, 40, 90), 'R15': (108, 40, 90), 'R16': (112, 40, 90),
        'R12': (90, h - 26, 90), 'R17': (94, h - 26, 90), 'R18': (98, h - 26, 90), 'C18': (102, h - 30, 90),
        'C19': (106, h - 30, 90), 'C20': (110, h - 30, 90), 'R19': (114, h - 26, 90), 'R20': (118, h - 26, 90),
        'R30': (122, h - 26, 90), 'R21': (96, h - 16, 0), 'R22': (108, h - 16, 0), 'R31': (108, 44, 0),
        # volume -> TDA
        'R23': (126, h - 20, 90), 'R24': (134, 30, 90), 'C21': (138, 32, 0), 'C22': (145, 12, 180),
        'R1': (140, 44, 180),
        # TDA
        'U2': (156, 8.5, 0), 'C6': (167, 7, 270), 'C7': (168, 23, 0), 'R27': (161, 15, 270), 'C24': (161, 29, 270),
        'R25': (153, 15, 270), 'R26': (149, 15, 270), 'C23': (140, 18, 0), 'C25': (152, 34, 270),
        # besleme / hoparlör (sağ kenar)
        'TB2': (178.3, 28, 90), 'TB1': (178.3, 46, 90), 'F1': (168, 42, 270), 'D1': (180, h - 42, 180),
        'C1': (150, h - 40, 0), 'C2': (160, h - 30, 0), 'R3': (158, h - 14, 90),
        'R28': (136, h - 22, 0), 'R29': (136, h - 27, 0),
    })
    return P

H0 = 114.3
def olcekle(P, h):
    """K1 tohumlarını (H0 derinlik) yeni derinliğe taşır: ön bölge öne yapışık, arka bölge sabit, orta ölçekli."""
    Q = {}
    for r, (x, y, a) in P.items():
        if y >= H0 - 40: y2 = y + (h - H0)
        elif y <= 30: y2 = y
        else: y2 = 30 + (y - 30) * ((h - 40) - 30) / ((H0 - 40) - 30)
        Q[r] = (x, y2, a)
    return Q

def K3():
    """K1'in ton yığınları yer değiştirmiş hali: UK arkada, US önde; ton parçaları daha sıkı."""
    P = K1()
    us = ['R10', 'R11', 'C15', 'C26', 'C16', 'C17', 'R13', 'R14', 'R15', 'R16']
    uk = ['R12', 'R17', 'R18', 'C18', 'C19', 'C20', 'R19', 'R20', 'R30', 'R21', 'R22', 'R31']
    for r in us: x, y, a = P[r]; P[r] = (x, y + 34, a)
    for r in uk: x, y, a = P[r]; P[r] = (x, y - 40, a)
    return P

def K4():
    """Ton yığınları yatay (eksenel parçalar 0°) iki blok; LM386 biraz sağda."""
    P = K1()
    for r in ['R10', 'R11', 'C15', 'C26', 'R13', 'R14', 'R15', 'R16', 'R12', 'R17', 'R18', 'C18', 'C19', 'C20', 'R19', 'R20', 'R30']:
        x, y, a = P[r]; P[r] = (x, y, 0)
    x, y, a = P['U1']; P['U1'] = (x + 4, y, a)
    return P

def K5():
    """K4 + ön pot düğümleri sabitlendi: VOLW (R23) RV3 silecinin hemen arkasında, USOUT (R14) ve UKOUT (R20)
    RV2'nin uç pinlerinin hemen arkasında. Yüksek empedanslı ton çıkışları kısa kalır."""
    P = K4()
    h = H0
    P.update({'R23': (123, h - 13, 90), 'R14': (94, h - 13, 90), 'R20': (104, h - 13, 90),
              'R13': (90, h - 13, 90), 'R19': (108, h - 13, 90)})
    return P

LAYOUTS = {'K1': K1, 'K2': K2, 'K3': K3, 'K4': K4, 'K5': K5}

def legalize(P, prio=None, gap=1.5, rmax=40.0):
    """İstenen konumları sırayla (öncelik listesi) en yakın boş yere kaydırır; dönüş korunur."""
    import math
    fixed = GP.fixed()
    occ = [GP.rect_of(r, *fixed[r]) for r in fixed] + list(GP.keepouts())
    out = dict(fixed)
    order = list(dict.fromkeys([r for r in (prio or []) if r not in fixed] + [r for r in P if r not in fixed]))
    step = 0.635
    offs = sorted({(i * step, j * step) for i in range(-int(rmax / step), int(rmax / step) + 1)
                   for j in range(-int(rmax / step), int(rmax / step) + 1)}, key=lambda d: (d[0] ** 2 + d[1] ** 2, abs(d[1])))
    moved = {}
    for r in order:
        x, y, a = P[r]
        for dx, dy in offs:
            rc = GP.rect_of(r, x + dx, y + dy, a)
            if rc[0] < 0.8 or rc[1] < 0.8 or rc[2] > W - 0.8 or rc[3] > H + 2: continue
            g = [gap] * len(occ)
            if any(GP.overlap(rc, o, gp) for o, gp in zip(occ, g)): continue
            out[r] = (round(x + dx, 3), round(y + dy, 3), a); occ.append(rc)
            if dx or dy: moved[r] = round(math.hypot(dx, dy), 1)
            break
        else:
            raise SystemExit('yerleşmedi: ' + r)
    return out, moved

PRIO = ['R23', 'R14', 'R20', 'R13', 'R19', 'U2', 'C6', 'C7', 'R25', 'R26', 'R27', 'C22', 'TB1', 'TB2', 'D1', 'F1', 'C1', 'C25', 'U1', 'Q1', 'R5', 'R6', 'R1', 'C22', 'C6', 'C4', 'C12', 'R26', 'C23', 'C14']

def check(P, gap=0.6):
    R = {r: GP.rect_of(r, *P[r]) for r in P}
    bad = []
    keys = sorted(R)
    for i, a in enumerate(keys):
        ra = R[a]
        if a not in GP.fixed() or a.startswith('P'):
            if ra[0] < 0.5 or ra[1] < 0.5 or ra[2] > W - 0.5 or ra[3] > H + 2: bad.append(('kenar', a))
        for b in keys[i + 1:]:
            if GP.overlap(ra, R[b], gap - 1e-6): bad.append((a, b))
        for k in GP.keepouts():
            if a not in GP.fixed() and GP.overlap(ra, k, 0): bad.append(('anahtar', a))
    missing = set(GP.G.PARTS) - set(P)
    return bad, missing

if __name__ == '__main__':
    import sys, os
    for arg in (sys.argv[1:] or LAYOUTS):
        arg, _, rs = arg.partition('#')
        base_name, _, hs = arg.partition('@')
        seed = LAYOUTS[base_name]()
        if hs: seed = olcekle(seed, float(hs))
        name = base_name + ('_%s' % hs.replace('.', '') if hs else '') + ('s%s' % rs if rs else '')
        if rs:   # rastgele küçük oynatma (aynı tohumla tekrar üretilebilir)
            import random
            rnd = random.Random(int(rs)); fx = GP.fixed()
            seed = {r: (x + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4), a) if r not in fx and r not in ('R23', 'R14', 'R20', 'R13', 'R19') else (x, y, a) for r, (x, y, a) in seed.items()}
        P, moved = legalize(seed, PRIO)
        print('kaydırılan:', moved)
        bad, miss = check(P, 1.4)
        print(name, 'eksik:', sorted(miss), 'çakışma:', bad)
        m, E = GP.metrics(P)
        GP.preview(name, P, E, m, os.path.join(GP.HERE, 'onizleme_%s.png' % name))
        print(m)
        GP.write_pcb(name, P, os.path.join(GP.HERE, 'amfi', 'amfi_%s.kicad_pcb' % name))
        import json, shutil
        d = json.load(open(os.path.join(GP.HERE, 'amfi', 'amfi.kicad_pro'), encoding='utf-8')); d['meta']['filename'] = 'amfi_%s.kicad_pro' % name
        json.dump(d, open(os.path.join(GP.HERE, 'amfi', 'amfi_%s.kicad_pro' % name), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        shutil.copy(os.path.join(GP.HERE, 'amfi', 'amfi.kicad_dru'), os.path.join(GP.HERE, 'amfi', 'amfi_%s.kicad_dru' % name))
