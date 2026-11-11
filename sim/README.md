# Micro-Cap simülasyonları

Amfinin (Rev 5 + RV4 DRIVE) Micro-Cap 12.2 ile yapılan analizleri. Her klasörde çalıştırma dosyası (`.cir`/`.ckt`, ayarlar dosyanın içinde), Micro-Cap'in sayısal çıktısı (`.ANO`/`.TNO`), işlenmiş tablo (`.csv`) ve ekran görüntüsü (`.jpg`/`.png`) var. Her analizin raporu ilgili `.md` dosyasında: menü yolu, ayarlar, sonuçlar, yorum.

| # | Rapor | Konu |
|---|---|---|
| 1 | [01_DC_calisma_noktasi.md](01_DC_calisma_noktasi.md) | DC çalışma noktaları, akım/güç |
| 2 | [02_AC_frekans_cevabi.md](02_AC_frekans_cevabi.md) | Kat kazançları, SW1, ISF, Gain, Volume, C15/R5 (yapım farkları), C9 |
| 3 | [03_TR_transient.md](03_TR_transient.md) | Kırpılma, headroom, 4 Ω'a güç, tam güç ve THD |
| 4 | [04_THD_distorsiyon.md](04_THD_distorsiyon.md) | THD, çift/tek harmonik; Gain × C9 |
| 5 | [05_gurultu.md](05_gurultu.md) | Girişe indirgenmiş gürültü, eleman katkıları |
| 6 | [06_empedans_kulaklik_besleme_kararlilik.md](06_empedans_kulaklik_besleme_kararlilik.md) | Giriş/çıkış empedansı, kulaklık seviyesi, besleme dalgalanması, TDA2003 kararlılığı |
| 7 | [07_C9_karsilastirma.md](07_C9_karsilastirma.md) | C9 yok / 22 µF / 22 µF + 1k / 22 µF + 2.2k |
| 8 | [08_pot_dugme_hissi.md](08_pot_dugme_hissi.md) | RV4 DRIVE: 2.2k ve 5k lineer pot düğme hissi |
| 9 | [09_karsilastirma.md](09_karsilastirma.md) | Fender 5F6-A / AB763 / Marshall ton katları (aynı grafikte), 5F1, Dumble ODS, LM386 amfileri; güçlü/zayıf yönler |

## Özet bulgular
- Giriş empedansı 1.03 MΩ; çıkış empedansı < 0.06 Ω; temiz güç ≈1.3 W, en fazla ≈2.4 W (4 Ω; modele göre, ölçülmeli).
- İlk kırpan kat LM386. C9 / RV4 DRIVE temiz ↔ overdrive geçişini belirliyor (JFET ×1.5 … ×10.8).
- ISF US konumu Fender blackface (AB763) eğrisine çok yakın; UK konumu Marshall'dan daha düşük frekanslı bir çukura sahip (428 Hz / 632 Hz).
- TDA katı 151 Hz altını kısıyor (C23 470 µ / R26 2.2 Ω): bas zayıflığının ana sebebi. *(Öneri: C23 1000–2200 µF, uygulanmadı.)*
- SNR ≈ 80–83 dB; gürültünün çoğu TDA2003 ve R24'ten.

## Model ve araçlar
- `model/amfi_tasarim.cir`: tam şema (Micro-Cap). `.DEFINE` satırları: GAIN, ISF, VOL, SW, DRIVE (RV4), C9V, C15V, R5V, HP, RSRC.
- `model/amp_models_v4.lib`: BF245B (datasheet), LM386EE (EasyEDA), TDA2003_DS (Jim Thompson modeli + ST datasheet düzeltmeleri).
- `.cir` dosyalarındaki `.LIB` satırı kütüphaneyi mutlak yolla arar (`C:\Users\ASUS\Desktop\Yeni klasör (3)\amp_models_v4.lib`). Başka bir bilgisayarda bu satırı düzeltin.
- `araclar/`: varyant `.cir` dosyalarını üreten ve `.ANO`/`.TNO` çıktılarından tablo, THD ve gürültü katkısı çıkaran Python betikleri. Betikler o oturumun dosya yollarıyla yazıldı; yeniden kullanmadan önce yollar düzenlenmeli.
- `07_C9/07c_C9_gurultu.ANO` (18 MB) boyutu nedeniyle eklenmedi; sonuçları `07c_C9_gurultu.csv` içinde.
