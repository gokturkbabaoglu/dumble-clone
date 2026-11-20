# Analiz 1 — DC çalışma noktası

Micro-Cap 12.2.0.5 · dosya: `amfi_tasarim.cir` · modeller: `amp_models_v4.lib`
Ayarlar: GAIN = ISF = VOL = 0.5, SW = 0 (Normal), C9 yok, RSRC (TR1) = 3.45k, HP = 0 (4 Ω hoparlör)

## Nasıl tekrarlanır

1. **Analysis → Dynamic DC** → açılan pencerede OK. Düğüm gerilimleri şemanın üzerine yazılır.
2. Akım ve güç tablosu için: **Analysis → Transient** → "Operating Point Only" işaretli → **Run** → **F5** (Numeric Output).
   Tablo `amfi_tasarim.TNO` dosyasına da yazılır.

## Sonuçlar

| Büyüklük | Değer | Not |
|---|---|---|
| V12 (1N5822 sonrası) | 11.78 V | Diyot düşümü 0.22 V, 41.5 mA'de |
| V2 (LM386 beslemesi) | 11.26 V | R1 100 Ω üzerinden 5.23 mA |
| V3 (JFET beslemesi) | 10.70 V | R2 1k üzerinden 0.56 mA |
| JFET drain / source / gate | 6.89 / 1.93 / ≈0 V | Id = 0.56 mA, Vgs = −1.93 V, Vds = 4.96 V |
| LM386 çıkışı (O386) | 5.66 V | = 0.503 · V2 (V2/2'ye oturuyor) |
| LM386 boşta akımı | ≈ 4.7 mA | Datasheet: tipik 4 mA, en fazla 8 mA |
| TDA2003 girişi (TIN, pin 1) | 1.30 V | İç bias (150 k) |
| TDA2003 çıkışı (TOUT) | 5.64 V | = 0.479 · V12 (datasheet: 6.9/14.4 = 0.479) |
| TDA2003 boşta akımı | ≈ 36.0 mA | Datasheet: 44 mA @14.4 V → 12 V'ta ≈ 36 mA |
| TDA2003 boşta kaybı | ≈ 0.42 W | 11.78 V × 36.0 mA |
| Toplam besleme akımı | 41.2 mA | 12 V × 41.2 mA = 0.49 W |
| Hoparlör DC'si (SPK) | ≈ 1 mV | C25 2200 µ DC'yi kesiyor |

Not (2026-11-11): Şema okunaklı olsun diye yeniden yerleştirildi (bağlantılar aynı, programla doğrulandı); değerler yeni dosyadan alındı.

Ekran görüntüleri: `00_sema_genel.png`, `01_dc_besleme_jfet_lm386.png`, `01_dc_isf_ve_guc_kati.png`.

## Model notları

- **BF245B**: Micro-Cap'in `jfet.lib` dosyasındaki kayıt kullanılmadı, çünkü değerleri Idss ≈ 2.7 A veriyor. Yerine datasheet aralığından kurulan model kullanıldı: Idss = 10 mA, Vp = −2.5 V (yaklaşık). Gerçek kartta TR1 drain ≈ 7 V olacak şekilde ayarlanacağı için çalışma noktası bu seçime pek duyarlı değil.
- **LM386**: EasyEDA LM386EE modeli kullanıldı. Dilatush "No-Frills" modeli ≈ 27 mA boşta akım çekiyor (gerçekçi değil); DC'de V2'yi 9.3 V'a düşürüyor.
- **TDA2003**: Jim Thompson (2014) modeli. Orijinal dosya analog-innovations.com/TDA2003.zip'ten (web.archive.org kaydı) alınıp doğrulandı. Bu model çıkışı içteki 20k geri beslemeyle Vs/2'ye oturtuyor; datasheet devresindeki dış 220 Ω bu ayarı bozduğu için çıkış 0.7 V'ta kalıyordu. Bias, satürasyon, boşta akım, SVR ve gürültü ST datasheet değerleriyle düzeltilerek `TDA2003_DS` adıyla kullanıldı (yaklaşık).
- Takılacak hal (C15 = 330p, R5 = 32k) DC noktasını değiştirmiyor; farkları AC adımında gösterilecek.
