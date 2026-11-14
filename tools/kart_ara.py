"""12V gitar amfisi — kart yerleşim arama programı (grafik arayüz).
Çalıştırma: baslat.bat ya da  python kart_ara.py
"""
import os, sys, json, glob, time, shutil, random
import multiprocessing as mp
DIR = os.path.dirname(os.path.abspath(__file__))
if DIR not in sys.path: sys.path.insert(0, DIR)
import ayarlar
import arama

ALANLAR = [  # (anahtar, etiket, tür, açıklama)
    ('kart_eni', 'Kart eni (mm)', ('165', '185'), '185: v2 düzeni + RV4 için 20 mm geniş; 165: sıkıştırılmış'),
    ('zincir', 'Zincir sayısı', int, 'aynı anda çalışan arama (Ryzen 5 2600 için 10 önerilir)'),
    ('deneme', 'Tur başına deneme', int, 'bir tur bitince zincir en iyi sonuçtan yeniden başlar'),
    ('jcost', 'Köprü maliyeti (yol çizici)', int, 'yüksek = yol çizici köprüden daha çok kaçınır'),
    ('jmax', 'En uzun köprü (hücre)', int, '1 hücre = 1.27 mm; 8 ≈ 10 mm'),
    ('ring', 'Kenar GND şeridi (hücre)', int, '0 = yok; 2 önerilir (arka/sol/sağ kenar)'),
    ('kopru_agirlik', 'Köprü cezası (puan)', int, 'her köprünün puandaki cezası'),
    ('kotu_kopru_agirlik', 'Parça üstü köprü cezası', int, ''),
    ('sicaklik_bas', 'Başlangıç sıcaklığı', float, 'yüksek = daha cesur denemeler'),
    ('sicaklik_son', 'Bitiş sıcaklığı', float, ''),
]


def main():
    import tkinter as tk
    from tkinter import ttk, messagebox
    from PIL import Image, ImageTk
    try:
        import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    ctx = mp.get_context('spawn')
    S = {'q': ctx.Queue(), 'ev': None, 'procs': [], 'img': None, 'secili': None, 'kapaniyor': False}
    SON = arama.SONUC; os.makedirs(SON, exist_ok=True); os.makedirs(arama.DURUM, exist_ok=True)

    root = tk.Tk(); root.title('Amfi Kart Arama — 12V gitar amfisi'); root.geometry('1500x950')
    style = ttk.Style()
    try: style.theme_use('vista')
    except Exception: pass

    # ---------------- ayarlar ----------------
    fa = ttk.LabelFrame(root, text='Ayarlar'); fa.pack(fill='x', padx=8, pady=6)
    A = ayarlar.oku(); deg = {}
    for i, (k, et, tur, ack) in enumerate(ALANLAR):
        r, c = i % 5, (i // 5) * 3
        ttk.Label(fa, text=et).grid(row=r, column=c, sticky='e', padx=4, pady=2)
        v = tk.StringVar(value=str(A[k])); deg[k] = v
        if isinstance(tur, tuple):
            w = ttk.Combobox(fa, textvariable=v, values=tur, width=8, state='readonly')
        else:
            w = ttk.Entry(fa, textvariable=v, width=9)
        w.grid(row=r, column=c + 1, sticky='w', padx=2)
        ttk.Label(fa, text=ack, foreground='#666').grid(row=r, column=c + 2, sticky='w', padx=(2, 18))

    fb = ttk.Frame(root); fb.pack(fill='x', padx=8)
    durum_lbl = ttk.Label(fb, text='Hazır.'); durum_lbl.pack(side='right')

    def ayar_topla():
        d = ayarlar.oku()
        for k, et, tur, _ in ALANLAR:
            s = deg[k].get().strip().replace(',', '.')
            try:
                d[k] = int(s) if (tur is int or isinstance(tur, tuple)) else float(s)
            except ValueError:
                raise ValueError(f'"{et}" geçerli bir sayı değil: {s}')
        if d['zincir'] < 1 or d['zincir'] > 64: raise ValueError('Zincir sayısı 1–64 olmalı')
        if d['jmax'] < 3: raise ValueError('En uzun köprü en az 3 hücre olmalı')
        return d

    def calisiyor(): return any(p.is_alive() for p in S['procs'])

    def baslat():
        if calisiyor(): return
        try: d = ayar_topla()
        except ValueError as e: messagebox.showerror('Ayar hatası', str(e)); return
        ayarlar.yaz(d)
        S['ev'] = ctx.Event(); S['procs'] = []
        tree.delete(*tree.get_children())
        for i in range(d['zincir']):
            tree.insert('', 'end', iid=str(i), values=(i, '', '', '', '', 'başlıyor…'))
            p = ctx.Process(target=arama.calis, args=(i, random.randint(1, 10 ** 6), S['ev'], S['q']), daemon=True)
            p.start(); S['procs'].append(p)
        durum_lbl.config(text=f'{d["zincir"]} zincir çalışıyor (kart {d["kart_eni"]} mm).')
        b_bas.config(state='disabled'); b_dur.config(state='normal')

    def durdur():
        if S['ev']: S['ev'].set()
        durum_lbl.config(text='Durduruluyor: zincirler son denemeyi bitirip kaydediyor…')
        b_dur.config(state='disabled')

    def sifirla():
        if calisiyor(): messagebox.showinfo('Bilgi', 'Önce durdurun.'); return
        if messagebox.askyesno('Durumu sıfırla', 'Zincirlerin kayıtlı ilerlemesi silinsin mi?\n(Kaydedilen sonuçlar silinmez.)'):
            for f in glob.glob(os.path.join(arama.DURUM, '*.json')): os.remove(f)
            durum_lbl.config(text='Zincir durumları silindi; sonraki başlatma başlangıç yerleşimlerinden başlar.')

    b_bas = ttk.Button(fb, text='▶ Başlat / Devam et', command=baslat); b_bas.pack(side='left', padx=2)
    b_dur = ttk.Button(fb, text='■ Durdur', command=durdur, state='disabled'); b_dur.pack(side='left', padx=2)
    ttk.Button(fb, text='Durumu sıfırla', command=sifirla).pack(side='left', padx=2)
    ttk.Button(fb, text='Klasörü aç', command=lambda: os.startfile(DIR)).pack(side='left', padx=2)

    # ---------------- zincirler ----------------
    fz = ttk.LabelFrame(root, text='Zincirler (puan düşük = iyi)'); fz.pack(fill='x', padx=8, pady=6)
    cols = ('z', 'tur', 'den', 'su', 'eniyi', 'durum')
    basl = ('zincir', 'tur', 'deneme', 'şu an', 'en iyi', 'en iyi durum')
    tree = ttk.Treeview(fz, columns=cols, show='headings', height=6)
    for c, b, w in zip(cols, basl, (60, 50, 110, 80, 80, 700)):
        tree.heading(c, text=b); tree.column(c, width=w, anchor='w' if c == 'durum' else 'center')
    tree.pack(fill='x', padx=4, pady=4)

    # ---------------- sonuçlar + önizleme ----------------
    pw = ttk.PanedWindow(root, orient='horizontal'); pw.pack(fill='both', expand=True, padx=8, pady=(0, 6))
    fs = ttk.LabelFrame(pw, text='Kaydedilen sonuçlar (tamamen çizilmiş kartlar)'); pw.add(fs, weight=1)
    scols = ('kopru', 'kotu', 'puan', 'kart', 'ad')
    sbasl = ('köprü', 'parça üstü', 'puan', 'kart', 'ad')
    st = ttk.Treeview(fs, columns=scols, show='headings')
    for c, b, w in zip(scols, sbasl, (55, 75, 65, 50, 260)):
        st.heading(c, text=b); st.column(c, width=w, anchor='center' if c != 'ad' else 'w')
    st.pack(fill='both', expand=True, padx=4, pady=4)
    fsb = ttk.Frame(fs); fsb.pack(fill='x')
    fp = ttk.LabelFrame(pw, text='Önizleme'); pw.add(fp, weight=3)
    canvas = tk.Canvas(fp, background='#fafafa', highlightthickness=0); canvas.pack(fill='both', expand=True)
    log = tk.Text(root, height=5, font=('Consolas', 9)); log.pack(fill='x', padx=8, pady=(0, 8))

    def yaz_log(s):
        log.insert('end', time.strftime('%H:%M:%S ') + s + '\n'); log.see('end')

    def sonuclari_yenile(sec=None):
        st.delete(*st.get_children())
        rows = []
        for t in glob.glob(os.path.join(SON, '*.txt')):
            ad = os.path.basename(t)[:-4]
            try:
                with open(t, encoding='utf-8') as f: d = json.load(f)
            except Exception:
                continue
            rows.append((d.get('puan', 0), d.get('kopru'), d.get('kotu'), d.get('ayarlar', {}).get('kart_eni', ''), ad, d.get('hata')))
        rows.sort(key=lambda x: x[0])
        for p, k, b, ke, ad, h in rows:
            st.insert('', 'end', iid=ad, values=(k, b, f'{p:.0f}', ke, ad + ('  ⚠HATA' if h else '')))
        if sec and st.exists(sec): st.selection_set(sec)

    def goster(*_):
        s = st.selection()
        if not s: return
        S['secili'] = s[0]; png = os.path.join(SON, s[0] + '.png')
        if not os.path.exists(png): return
        im = Image.open(png)
        W, H = max(200, canvas.winfo_width() - 4), max(150, canvas.winfo_height() - 4)
        im.thumbnail((W, H), Image.LANCZOS)
        S['img'] = ImageTk.PhotoImage(im); canvas.delete('all'); canvas.create_image(W // 2 + 2, H // 2 + 2, image=S['img'])

    def secili_dosya(uz):
        return os.path.join(SON, S['secili'] + uz) if S['secili'] else None

    def buyuk_ac():
        p = secili_dosya('.png')
        if p and os.path.exists(p): os.startfile(p)

    def baslangica_ekle():
        p = secili_dosya('.json')
        if not p: return
        with open(secili_dosya('.txt'), encoding='utf-8') as f: ke = json.load(f).get('ayarlar', {}).get('kart_eni', 185)
        hedef = os.path.join(DIR, 'baslangic', str(ke)); os.makedirs(hedef, exist_ok=True)
        shutil.copy(p, os.path.join(hedef, os.path.basename(p)))
        yaz_log(f'{os.path.basename(p)} başlangıç yerleşimlerine eklendi (yeni/sıfırlanmış zincirler kullanır).')

    def sil():
        if not S['secili']: return
        if messagebox.askyesno('Sil', S['secili'] + ' silinsin mi?'):
            for uz in ('.json', '.png', '.txt'):
                p = secili_dosya(uz)
                if p and os.path.exists(p): os.remove(p)
            S['secili'] = None; canvas.delete('all'); sonuclari_yenile()

    ttk.Button(fsb, text='Büyük aç', command=buyuk_ac).pack(side='left', padx=2, pady=2)
    ttk.Button(fsb, text='Başlangıçlara ekle', command=baslangica_ekle).pack(side='left', padx=2)
    ttk.Button(fsb, text='Sil', command=sil).pack(side='left', padx=2)
    ttk.Button(fsb, text='Yenile', command=sonuclari_yenile).pack(side='left', padx=2)
    st.bind('<<TreeviewSelect>>', goster)
    canvas.bind('<Configure>', lambda e: root.after(80, goster))

    # ---------------- kuyruk ----------------
    def yokla():
        try:
            while True:
                m = S['q'].get_nowait(); z = str(m.get('zincir'))
                if m['tip'] == 'ilerleme' and tree.exists(z):
                    tree.item(z, values=(z, m['tur'], f'{m["k"]}/{m["N"]}', f'{m["cur"]:.0f}', f'{m["best"]:.0f}', m['durum']))
                elif m['tip'] == 'bilgi':
                    yaz_log(f'zincir {z}: {m["metin"]}')
                    if tree.exists(z): tree.set(z, 'durum', m['metin'])
                elif m['tip'] == 'sonuc':
                    yaz_log(f'zincir {z}: yeni sonuç kaydedildi → {m["ad"]}')
                    sonuclari_yenile(sec=S['secili'])
                elif m['tip'] == 'hata':
                    yaz_log(f'zincir {z} HATA:\n{m["metin"]}')
                elif m['tip'] == 'bitti':
                    yaz_log(f'zincir {z} durdu ve kaydetti.')
        except Exception:
            pass
        if S['procs'] and not calisiyor():
            S['procs'] = []; b_bas.config(state='normal'); b_dur.config(state='disabled')
            durum_lbl.config(text='Durdu. Başlat ile kaldığı yerden devam eder.')
            if S['kapaniyor']: root.destroy(); return
        root.after(400, yokla)

    def kapat():
        if calisiyor():
            if not messagebox.askyesno('Çıkış', 'Zincirler kaydedilip durdurulsun ve program kapansın mı?'): return
            S['kapaniyor'] = True; durdur()
        else:
            root.destroy()

    root.protocol('WM_DELETE_WINDOW', kapat)
    sonuclari_yenile()
    yaz_log('Hazır. Ayarları kontrol edip "Başlat"a basın. Kapatırsanız ilerleme kaydedilir; tekrar açıp Başlat ile devam eder.')
    root.after(400, yokla)
    root.mainloop()


if __name__ == '__main__':
    mp.freeze_support()
    main()
