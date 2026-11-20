"""Arama zinciri (her çekirdekte bir tane çalışır). Arayüz kart_ara.py bunu başlatır."""
import os, sys, json, time, random, math, traceback, glob
DIR = os.path.dirname(os.path.abspath(__file__))
if DIR not in sys.path: sys.path.insert(0, DIR)
DURUM = os.path.join(DIR, 'durum')
SONUC = os.path.join(DIR, 'sonuclar')


def _yaz_json(yol, veri):
    tmp = yol + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(veri, f)
    os.replace(tmp, yol)


def puanla(pl, A):
    """(puan, bilgi, router). Düşük puan iyi."""
    from final2 import route_eval, orders, bad_jumps
    o = orders(pl, 1, 0)[0]
    r, f = route_eval(pl, o)
    if r is None:
        if f and set(f) == {'GND'}:
            ada = len(f) - 1
            return 300 + 80 * len(f), {'durum': f'GND {ada} ada bağlanamadı', 'kopru': None, 'kotu': None, 'tam': False}, None
        fs = sorted(set(f))
        return 1000 + 100 * len(f), {'durum': 'çizilemeyen: ' + ','.join(fs[:4]) + ('…' if len(fs) > 4 else ''), 'kopru': None, 'kotu': None, 'tam': False}, None
    nj = sum(len(v) for v in r.jumps.values())
    bj = bad_jumps(r)
    L = sum(len(p) for s in r.paths.values() for p in s)
    p = nj * A['kopru_agirlik'] + bj * A['kotu_kopru_agirlik'] + L * 0.02
    return p, {'durum': f'tam çizildi, {nj} köprü' + (f' ({bj} parça üstünden)' if bj else ''), 'kopru': nj, 'kotu': bj, 'tam': True}, r


def ciz(pl, r, yol_png, baslik):
    """Bakır + parça çerçeveleri + köprüler: önizleme resmi."""
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image
    from final2 import build_geom, pour, raster, verify, PX
    from geom import body_box_mm, pins_mm, C, BW, BH, U
    items, padpos = build_geom(pl, r)
    g = pour(items)
    sig = raster(items, lambda n: n != 'GND')
    err = verify(items, padpos, g)
    img = np.zeros(g.shape + (3,), np.uint8)
    img[:] = (245, 236, 220)
    img[g] = (226, 190, 140)
    img[sig] = (196, 120, 50)
    im = Image.fromarray(img).resize((int(BW * 6), int(BH * 6)))
    fig, ax = plt.subplots(figsize=(16, 16 * BH / BW + 0.6))
    ax.imshow(np.asarray(im), extent=[0, BW, BH, 0])
    for ref in pl:
        if C[ref][0].startswith('KO'):
            x0, x1, y0, y1 = body_box_mm(ref, pl)
            ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, color='#c0392b', lw=.8, ls='--'))
            continue
        x0, x1, y0, y1 = body_box_mm(ref, pl)
        ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, color='#1f3a68', lw=.7))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, ref, fontsize=6.5, ha='center', va='center', color='#1f3a68', fontweight='bold')
        for p in pins_mm(ref, pl): ax.plot(*p, 'o', ms=1.6, color='#333')
    k = 0
    for n, js in r.jumps.items():
        for a, b in js:
            k += 1
            ax.plot([a[0] * U, b[0] * U], [a[1] * U, b[1] * U], '-', color='#e01010', lw=2.5)
            L = math.hypot(a[0] - b[0], a[1] - b[1]) * U
            ax.text((a[0] + b[0]) / 2 * U, (a[1] + b[1]) / 2 * U - 1.5, f'K{k} {n} {L:.0f}mm', color='#e01010', fontsize=7, ha='center', fontweight='bold')
    ax.set_xlim(0, BW); ax.set_ylim(BH, 0); ax.set_aspect('equal')
    ax.set_title(baslik + ('' if not err else f'   HATA: {err[:3]}'), fontsize=10)
    ax.text(BW / 2, BH + 4, '▼ ön panel ▼', ha='center', fontsize=9, color='#555')
    fig.savefig(yol_png, dpi=90, bbox_inches='tight')
    plt.close(fig)
    return err


def calis(wid, seed, durdur, kuyruk):
    try:  # Windows: bilgisayar yavaşlamasın diye düşük öncelik
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass
    try:
        _calis(wid, seed, durdur, kuyruk)
    except Exception:
        kuyruk.put({'tip': 'hata', 'zincir': wid, 'metin': traceback.format_exc()})


def _calis(wid, seed, durdur, kuyruk):
    import ayarlar
    A = ayarlar.A
    imza = ayarlar.imza(A)
    os.makedirs(DURUM, exist_ok=True); os.makedirs(SONUC, exist_ok=True)
    from place2 import C, FIXED, run as yerlestir
    from rsa2 import legal
    dyol = os.path.join(DURUM, f'zincir_{wid}.json')
    random.seed(seed * 7919 + int(time.time()))
    movable = [r for r in C if r not in FIXED]

    st = None
    if os.path.exists(dyol):
        try:
            with open(dyol, encoding='utf-8') as f: st = json.load(f)
            if st.get('imza') != imza: st = None
        except Exception:
            st = None
    if st:
        pl = {k: tuple(v) for k, v in st['pl'].items()}
        best_pl = {k: tuple(v) for k, v in st['best_pl'].items()}
        k0, tur = st['k'], st['tur']
        kuyruk.put({'tip': 'bilgi', 'zincir': wid, 'metin': f'kayıttan devam (tur {tur}, deneme {k0})'})
    else:
        bas = sorted(glob.glob(os.path.join(DIR, 'baslangic', str(A['kart_eni']), '*.json')))
        if bas:
            yol = bas[wid % len(bas)]
            with open(yol, encoding='utf-8') as f: pl = {k: tuple(v) for k, v in json.load(f).items()}
            kuyruk.put({'tip': 'bilgi', 'zincir': wid, 'metin': 'başlangıç: ' + os.path.basename(yol)})
        else:
            kuyruk.put({'tip': 'bilgi', 'zincir': wid, 'metin': 'başlangıç yerleşimi üretiliyor (≈2 dk)…'})
            pl = yerlestir(seed, 40000)[1]
        for k, v in FIXED.items(): pl[k] = v
        best_pl = dict(pl); k0, tur = 0, 0

    cur, info, r = puanla(pl, A)
    best, binfo, _ = puanla(best_pl, A) if best_pl != pl else (cur, info, r)
    best_tam = st.get('best_tam', 1e18) if st else 1e18
    kuyruk.put({'tip': 'ilerleme', 'zincir': wid, 'tur': tur, 'k': k0, 'N': A['deneme'], 'cur': cur, 'best': best, 'durum': binfo['durum']})
    N = A['deneme']; T0, T1 = A['sicaklik_bas'], A['sicaklik_son']
    son_kayit = time.time()

    def kaydet():
        _yaz_json(dyol, {'imza': imza, 'pl': {a: list(b) for a, b in pl.items()},
                         'best_pl': {a: list(b) for a, b in best_pl.items()},
                         'k': k, 'tur': tur, 'best_tam': best_tam})

    k = k0
    while not durdur.is_set():
        if k >= N:  # yeni tur: en iyiden yeniden ısıtarak başla
            tur += 1; k = 0; pl = dict(best_pl); cur = best
            T0 = max(A['sicaklik_bas'] * 0.6, T1 * 2)
        T = T0 * (T1 / T0) ** (k / N)
        rr = random.choice(movable); old = pl[rr]; m = random.random(); r2 = None
        if m < 0.6: pl[rr] = (old[0] + random.randint(-3, 3), old[1] + random.randint(-3, 3), old[2])
        elif m < 0.8: pl[rr] = (old[0], old[1], random.choice([0, 90, 180, 270]))
        else:
            r2 = random.choice(movable); old2 = pl[r2]
            pl[rr], pl[r2] = (old2[0], old2[1], old[2]), (old[0], old[1], old2[2])
        k += 1
        if not legal(pl, rr) or (r2 and not legal(pl, r2)):
            pl[rr] = old
            if r2: pl[r2] = old2
            continue
        new, ninfo, nr = puanla(pl, A)
        if new < cur or random.random() < math.exp((cur - new) / T):
            cur = new
            if new < best:
                best, binfo, best_pl = new, ninfo, dict(pl)
                kuyruk.put({'tip': 'ilerleme', 'zincir': wid, 'tur': tur, 'k': k, 'N': N, 'cur': cur, 'best': best, 'durum': binfo['durum']})
            if ninfo['tam'] and new < best_tam - 0.5:
                best_tam = new
                ad = time.strftime('%Y%m%d_%H%M%S') + f'_z{wid}_k{ninfo["kopru"]}_p{int(new)}'
                _yaz_json(os.path.join(SONUC, ad + '.json'), {a: list(b) for a, b in pl.items()})
                err = ciz(pl, nr, os.path.join(SONUC, ad + '.png'),
                          f'{ad}   |   {ninfo["durum"]}   |   kart {A["kart_eni"]} mm')
                with open(os.path.join(SONUC, ad + '.txt'), 'w', encoding='utf-8') as f:
                    f.write(json.dumps({'puan': new, 'kopru': ninfo['kopru'], 'kotu': ninfo['kotu'], 'hata': err,
                                        'ayarlar': A}, ensure_ascii=False, indent=1))
                kaydet()
                kuyruk.put({'tip': 'sonuc', 'zincir': wid, 'ad': ad})
        else:
            pl[rr] = old
            if r2: pl[r2] = old2
        if time.time() - son_kayit > 20:
            kaydet(); son_kayit = time.time()
            kuyruk.put({'tip': 'ilerleme', 'zincir': wid, 'tur': tur, 'k': k, 'N': N, 'cur': cur, 'best': best, 'durum': binfo['durum']})
    kaydet()
    kuyruk.put({'tip': 'bitti', 'zincir': wid})
