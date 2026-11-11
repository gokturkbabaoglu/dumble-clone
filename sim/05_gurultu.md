# 5 — Gürültü analizi

**Çalıştırma yolu:** Micro-Cap → File → Open → `sim\05_NOISE\05a_gurultu.cir` → Analysis → AC… → Run.

**Ayarlar:**
- Frequency Range: Log, 20k,20 (20 Hz–20 kHz), 301 nokta.
- Noise Input = VGIT, Noise Output = SPK.
- Grafikler: INOISE·1e9 (nV/√Hz), ONOISE·1e6 (µV/√Hz) ve SQRT(SD(ONOISE·ONOISE))·1e6 (µV rms, 20 Hz'den itibaren integral).
- Kaynak empedansı RSRC = 3.45k (gitar). Tüm potlar ½, SW = 0, C9 yok.

**Dosyalar:** sayısal çıktı `.ANO` (her frekansta eleman bazında gürültü katkısı), `.csv`, `.jpg`, eleman katkıları `05a_katki.txt`.

## Sonuçlar
| | 100 Hz | 1 kHz | 10 kHz |
|---|---|---|---|
| Girişe indirgenmiş gürültü (INOISE) | 804 nV/√Hz | 522 nV/√Hz | 274 nV/√Hz |
| Çıkış gürültüsü (ONOISE) | 1.65 µV/√Hz | 1.53 µV/√Hz | 0.96 µV/√Hz |

- **Toplam çıkış gürültüsü (20 Hz–20 kHz, 4 Ω):** 155 µV rms.
- **Temiz tam güce göre SNR:** 1.3 W = 2.27 V rms için ≈ **83 dB**.
- **Volume ½'deki tipik çalışma seviyesine göre (≈0.35 W):** ≈ 72 dB.

## En gürültülü yer (20 Hz–20 kHz integral, katkı payı)
| Kaynak | Pay | Not |
|---|---|---|
| TDA2003'ün kendi gürültüsü | %39 | Volume potundan sonra, ×100 kazançla doğrudan çıkışa |
| R24 (10k, TDA giriş bölücüsü) | %37.5 | TDA girişinde, Volume'dan bağımsız |
| JFET Q1 | %13 | 100 Hz'de baskın (%78): modeldeki flicker (1/f) gürültü (KF = 7.9f, AF = 0.5) |
| LM386 | %5 | |
| Diğer dirençler (R7, Volume potu, R5…) | <%2'şer | |

**Yorum:**
- Duyulan "hışırtı" büyük ölçüde güç katından geliyor: TDA2003 ve girişindeki R23/R24 bölücüsü. Bu gürültü Volume ve Gain ayarından bağımsız, sabit bir taban oluşturuyor.
- Giriş katının (JFET) payı daha çok düşük frekansta, uğultu benzeri. Bu, modelin AF = 0.5 flicker parametresine bağlı olduğundan **yaklaşık** kabul edilmeli.
- Girişe indirgenmiş değer yüksek görünüyor (≈0.5 µV/√Hz @1 kHz). Sebebi: C9 yokken JFET katı yalnızca +3.4 dB kazanç veriyor, sonraki katlarda ise ton katı −18 dB kayıp yaratıyor. C9 takılırsa bu değer kabaca 7 kat düşer (yaklaşık; ayrıca simüle edilmedi).
