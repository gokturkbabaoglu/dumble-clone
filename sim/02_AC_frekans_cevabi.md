# 2 — AC analizi (frekans cevabı)

Micro-Cap 12.2.0.5, EasyEDA LM386EE + TDA2003_DS modelleri. Yük 4 Ω (HP=0). Tüm çalıştırmalar dB, giriş VGIT AC 1 V = 0 dB referansı.
Aksi belirtilmedikçe: GAIN=0.5, VOL=0.5, ISF=0.5, SW=0 (Normal), C9V=1p (C9 yok), C15V=253p, R5V=33k.

**Çalıştırma yolu:** Micro-Cap → File → Open → `sim\02_AC\<dosya>.cir` → Analysis → AC… → Run. Ayarlar dosyanın içinde kayıtlı (Frequency Range `20k,10` Log, 301 nokta, Stepping sekmesi her dosyada hazır). Sayısal sonuç aynı klasördeki `.ANO`, işlenmiş hali `.csv`, ekran görüntüsü `.jpg`/`.png`.

## 2a — SW1 (Dark / Normal / Bright) — `02a_SW1`
Stepping: SW −1 → 1, adım 1.

| SW1 | Tepe (SPK) | −3 dB bandı |
|---|---|---|
| Dark (CD 3.3n) | 13.1 dB @ 2.8 kHz | 1.1–6.4 kHz |
| Normal | 14.2 dB @ 3.6 kHz | 1.4–9.6 kHz |
| Bright (CB 470p) | 15.7 dB @ 6.2 kHz | — (üst uç açık) |

Gain pot ucunda (GAINW) Bright, ~3 kHz'den itibaren yükselen bir raf (20 kHz'de +8 dB) veriyor. Dark ise ~6 kHz'de −3 dB.

## 2b — Kat kazançları (stepping yok) — `02b_kat_kazanclari`

| Düğüm | 100 Hz | 1 kHz | 5 kHz | Kata ait kazanç @1 kHz |
|---|---|---|---|---|
| DRAIN (JFET çıkışı) | 3.4 | 3.4 | 3.4 | **+3.4 dB** (C9 yok, kaynak dirençleri bypass edilmemiş) |
| GAINW (Gain pot ucu) | −12.9 | −12.7 | −12.7 | −16.0 dB (pot + 15k yükü) |
| O386 (LM386 çıkışı) | 18.9 | 19.2 | 19.2 | **+31.9 dB** (≈39×) |
| ISFW (ton katı çıkışı) | 3.4 | 1.4 | 8.3 | **−17.8 dB** (1 kHz'de orta frekans çukuru) |
| TIN (TDA girişi, Volume ½) | −28.4 | −30.5 | −26.1 | −31.9 dB (Volume pot + R25…) |
| SPK (4 Ω) | 6.2 | 9.4 | 13.9 | **+39.9 dB** (TDA2003, ≈99×) |

Toplam: 1 kHz'de +9.4 dB (×2.9), tepe 14.2 dB @ 3.6 kHz, −3 dB bandı 1.36–9.6 kHz. Alt uç düşük kalıyor: 100 Hz, 1 kHz'e göre −3 dB, 10 Hz'de −30 dB.

## 2c — ISF US → UK — `02c_ISF`
Stepping: ISF 0 → 1, adım 0.25 (0 = US/Fender ucu, 1 = UK/Marshall ucu). Ton katı transferi = dB(ISFW) − dB(O386).

| ISF | Çukur frekansı | Çukur derinliği | 5 kHz transfer | SPK tepe | SPK @1 kHz |
|---|---|---|---|---|---|
| 0 (US) | 394 Hz | −22.1 dB | −8.0 dB | 16.9 dB @ 4.2 kHz | 10.4 |
| 0.25 | 404 Hz | −21.9 | −9.6 | 15.4 @ 3.9 kHz | 9.7 |
| 0.5 | 414 Hz | −21.5 | −10.8 | 14.2 @ 3.6 kHz | 9.4 |
| 0.75 | 425 Hz | −20.8 | −11.8 | 13.4 @ 3.3 kHz | 9.4 |
| 1 (UK) | 425 Hz | −19.8 | −12.4 | 13.1 @ 3.1 kHz | 9.9 |

Yorum: ISF'nin ana etkisi tizde. US'den UK'ye geçince 5 kHz'de ~4.4 dB tiz kaybı var ve tepe 4.2 kHz'den 3.1 kHz'e iniyor. Orta çukur yalnızca ~2.3 dB sığlaşıyor; konumu da ~400 Hz civarında neredeyse sabit kalıyor. Bas tarafı (100 Hz) ±0.6 dB içinde.

## 2d — Gain — `02d_GAIN`
Stepping: GAIN 0.1 / 0.55 / 1.

| GAIN | O386 @1 kHz | SPK @1 kHz | SPK tepe |
|---|---|---|---|
| 0.1 | 10.5 dB | 0.7 dB | 5.6 dB |
| 0.55 | 20.0 | 10.2 | 15.0 |
| 1 | 31.7 | 21.9 | 26.8 |

Gain potu yaklaşık 21 dB'lik bir aralık süpürüyor. GAIN=1'de LM386 kat alt köşesi 93 Hz'e çıkıyor (diğer konumlarda 20–29 Hz).

## 2e — Volume — `02e_VOLUME`
Stepping: VOL 0.1 / 0.4 / 0.7 / 1. SPK @1 kHz: 1.5 / 8.0 / 12.1 / 17.7 dB (16 dB aralık). Eğri şekli değişmiyor.

## 2f — Tasarım ve gerçek yapım farkları — `02f_C15_R5_asbuilt`
ISF = 0, iç içe stepping: C15V 253p / 330p × R5V 32k / 33k.

- **C15 330p (gerçek yapım):** çukur 394 Hz → 347 Hz'e iniyor. 1 kHz'de ton katı +1.7 dB daha az kayıp veriyor, SPK'de +1.7 dB (10.4 → 12.2 dB). Tepe 4.2 kHz → 3.7 kHz. Yani biraz daha "dolgun orta", fark duyulabilir sınırda.
- **R5 32k ↔ 33k:** etkisi ≤0.01 dB. İhmal edilebilir.

## 2g — C9 (JFET kaynak bypass) — `02g_C9`
C9V 1p (yok) / 22u.

| | DRAIN @1 kHz | SPK @1 kHz | SPK tepe |
|---|---|---|---|
| C9 yok | 3.4 dB | 9.4 dB | 14.2 dB |
| C9 = 22 µF | 20.7 dB | 26.7 dB | 31.6 dB |

C9 takılınca JFET katı kazancı +17.3 dB artıyor (≈×7.3). Bas kesimi 13 Hz, sorun yok. Not: bu kazanç artışı sonraki katların kırpılma noktasını büyük ölçüde değiştirir. Bu yüzden Analiz 3'te her iki durum da ayrı ele alınacak.

## Özet
- Amfi doğal olarak orta-tiz vurgulu (tepe 3–4 kHz). ~400 Hz civarında derin (≈ −22 dB) bir "Fender tipi" orta çukuru var.
- Bas tarafı zayıf: 100 Hz'de 1 kHz'e göre −3 dB, 10 Hz'de −30 dB.
- En büyük kazanç seçeneği C9. Ardından sırayla Gain potu (21 dB), Volume (16 dB) ve SW1 (Bright tizde ~+2 dB tepe) geliyor.
