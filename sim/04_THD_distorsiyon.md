# 4 — Distorsiyon / Fourier (THD, çift–tek harmonik dengesi)

**Çalıştırma yolu:** Micro-Cap → File → Open → `sim\04_THD\04a_THD_gain_C9.cir` → Analysis → Transient… → Run ("Operating Point Only" kapalı olmalı).

**Ayarlar:**
- 20 ms koşu, son 5 ms (5 periyot) kaydedildi, adım 2 µs.
- Giriş 1 kHz, 100 mV tepe. VOL = 0.5.
- Stepping: GAIN 0.1 / 0.55 / 1 × C9V 1p (yok) / 22u.
- Harmonikler `.csv`'den FFT ile hesaplandı (özet: `04a_THD_ozet.txt`).
- Giriş seviyesine göre THD eğrisi (Volume = 1) için Analiz 3'teki 3b bölümüne bakınız (`03b_tam_guc_THD`).

| GAIN | C9 | SPK THD | H2 | H3 | LM386 çıkışı THD | JFET (drain) THD |
|---|---|---|---|---|---|---|
| 0.1 | yok | 0.1 % | 0.1 % | 0.0 % | 0.1 % | 0.1 % |
| 0.1 | 22 µF | 4.8 % | 4.8 % | 0.1 % | 3.2 % | 3.2 % (H2) |
| 0.55 | yok | 0.1 % | 0.1 % | 0.0 % | 0.1 % | 0.1 % |
| 0.55 | 22 µF | 31.9 % | 9.3 % | 30.0 % | 18.8 % | 3.2 % |
| 1 | yok | 0.1 % | 0.1 % | 0.0 % | 0.1 % | 0.1 % |
| 1 | 22 µF | 65.9 % | 5.5 % | 55.0 % | 39.2 % | 4.2 % |

## Yorum
- **C9 takılı değilken:** 100 mV girişte Gain ne olursa olsun amfi temiz (THD 0.1 %). Kalan bozulmanın tamamı 2. harmonik.
- **C9 takılıyken:** JFET katı tek başına ≈3 % 2. harmonik üretiyor. Bu, ses karakterine sıcaklık katan, "tüp benzeri" çift harmonik bozulma.
  - GAIN düşükken (0.1) çıkış bu çift harmonik karakterde kalıyor: THD ≈5 %, tamamı H2.
  - GAIN ½ ve üstünde LM386 simetrik kırpmaya giriyor. Bu durumda 3. harmonik baskın hale geliyor (H3 ≫ H2) ve ses daha sert, fuzz'a yakın bir karaktere dönüyor.
- **Giriş seviyesine göre THD (3b'den, Volume 1, C9 yok):** ≈0.4 V tepe girişe kadar <0.5 % (H2 baskın). 0.6 V'ta 12.5 %, 1 V'ta 40 % (H3 baskın).
