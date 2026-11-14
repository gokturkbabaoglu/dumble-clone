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

LAYOUTS = {'K1': K1}

def legalize(P, prio=None, gap=1.5, rmax=40.0):
    """İstenen konumları sırayla (öncelik listesi) en yakın boş yere kaydırır; dönüş korunur."""
    import math
    fixed = GP.fixed()
    occ = [GP.rect_of(r, *P[r]) for r in fixed] + list(GP.keepouts())
    out = {r: P[r] for r in fixed}
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

PRIO = ['U2', 'C6', 'C7', 'R25', 'R26', 'R27', 'C22', 'TB1', 'TB2', 'D1', 'F1', 'C1', 'C25', 'U1', 'Q1', 'R5', 'R6', 'R1', 'C22', 'C6', 'C4', 'C12', 'R26', 'C23', 'C14']

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
    for name in (sys.argv[1:] or LAYOUTS):
        P, moved = legalize(LAYOUTS[name](), PRIO)
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
