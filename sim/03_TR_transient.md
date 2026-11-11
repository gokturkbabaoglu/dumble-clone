# 3 — Transient analizi (kırpılma, headroom, güç)

**Çalıştırma yolu:** Micro-Cap → File → Open → `sim\03_TR\03a_transient.cir` → Analysis → Transient… → Run. "Operating Point Only" işaretli olmamalı.

**Ayarlar:**
- Max Run Time 20m, tstart 15m (son 5 ms, 5 periyot), Max Time Step 2u, 1001 nokta.
- Giriş: 1 kHz sinüs, tepe değeri VIN.
- İç içe stepping: VIN 0.1 / 1 V × C9V 1p (C9 yok) / 22u.
- GAIN = VOL = ISF = 0.5, SW = 0, yük 4 Ω.

**Dosyalar:** sayısal çıktı `03a_transient.TNO`, tablo `.csv`, ekran görüntüsü `.jpg`.

| Durum | DRAIN (JFET) | O386 (LM386) | TIN (TDA girişi) | SPK (4 Ω) | Güç (4 Ω) |
|---|---|---|---|---|---|
| 100 mV, C9 yok | 0.29 Vpp, temiz | 1.8 Vpp, temiz | 6 mVpp | 0.59 Vpp | 11 mW |
| 100 mV, C9 22 µF | 2.2 Vpp, temiz | 0.53…9.65 V → **kırpıyor** | 40 mVpp | 4.1 Vpp | 0.38 W |
| 1 V, C9 yok | 3.0 Vpp, hafif asimetrik | 0.53…9.45 V → **kırpıyor** | 47 mVpp | 4.9 Vpp | 0.44 W |
| 1 V, C9 22 µF | 2.3…10.25 V → sınırda | 0.54…10.6 V → sert kırpma | 72 mVpp | 7.7 Vpp | 0.79 W |

## Yorum
- **İlk kırpan kat LM386.** Çıkışı yaklaşık 0.5 V ile 9.6–10.6 V arasında sıkışıyor.
  - C9 yokken LM386 çıkışı girişin ≈9 katı. Kırpılma ≈0.5 V tepe girişte başlıyor (yaklaşık). 100 mV'a göre **≈14 dB headroom** var. Normal bir gitar sinyali (100–300 mV) temiz kalıyor, sert çalınca crunch'a giriyor.
  - C9 takılıyken 100 mV bile LM386'yı kırpıyor. Kırpılma ≈70 mV tepe civarında başlıyor (yaklaşık). Yani C9, amfiyi "overdrive" karakterine çeviriyor.
- **JFET:** ancak 1 V + C9 durumunda kırpılmaya yaklaşıyor (drain 2.3–10.25 V).
- **TDA2003:** Volume ½'de hiçbir durumda kırpmıyor. Gücü belirleyen Volume ayarı ve öndeki LM386 kırpılması.
- **Hoparlördeki dalga:** sivri görünüyor. Sebebi, LM386'nın kare dalgasının ton katında tizce vurgulanması.
- **Güç:** Volume ½'de kırpılmış sinyalle 4 Ω'a ≈0.4–0.8 W gidiyor. TDA2003'ün 12 V'taki tam gücü (Volume 1) Analiz 4'te THD ölçümüyle birlikte bulunacak.

## 3b — Tam güç ve THD (Volume = 1) — `03b_tam_guc_THD`
Menü ve ayarlar 3a ile aynı; farklar: VOL = 1, C9 yok, GAIN = 0.5, stepping VIN 0.02 → 1.02 (adım 0.2). THD, son 5 periyodun FFT'sinden hesaplandı (Python ile, `.csv`'den).

| VIN tepe | SPK tepe | Güç (temel, 4 Ω) | THD SPK | H2 | H3 | THD O386 |
|---|---|---|---|---|---|---|
| 0.02 V | 0.15 V | 3 mW | 0.0 % | 0.02 % | 0.00 % | 0.1 % |
| 0.22 V | 1.68 V | 0.35 W | 0.2 % | 0.19 % | 0.01 % | 0.1 % |
| 0.42 V | 3.2 V | 1.29 W | 0.4 % | 0.37 % | 0.02 % | 0.2 % |
| 0.62 V | 4.4 V | 2.41 W | 12.5 % | 3.6 % | 10.4 % | 6.9 % |
| 0.82 V | 4.2 V | 2.21 W | 32 % | 7.1 % | 30.5 % | 18.9 % |
| 1.02 V | 4.1 V | 2.11 W | 40 % | 6.6 % | 37 % | 24.5 % |

**Yorum:**
- **Temiz güç:** ≈1.3 W'a kadar THD < 0.5 %. Bu bölgede bozulma neredeyse tamamen 2. harmonik (çift/tek oranı 18–38). Asimetrik, "tüp benzeri" yumuşak bir karakter.
- **Kırpılma:** ≈0.5–0.6 V tepe girişte başlıyor. Burada LM386 (0.53…10.2 V) ile TDA2003 (≈ −4.6…+5.0 V) neredeyse aynı anda kırpıyor ve tek harmonikler baskın hale geliyor (H3 ≫ H2). Sert, transistör tipi kırpma.
- **Maksimum güç:** 4 Ω'a ≈2.4 W (%10 THD civarı). ST datasheet'i 14.4 V'ta 6 W veriyor; 12 V'ta beklenen değer yaklaşık 4 W (yaklaşık). Simülasyondaki daha düşük değer, TDA2003_DS modelinin çıkış salınımını tutucu modellemesinden kaynaklanıyor olabilir. Gerçek devrede ölçüp doğrulamak gerekir.
