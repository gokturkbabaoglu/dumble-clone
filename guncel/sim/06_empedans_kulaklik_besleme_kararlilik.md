# 6 — Empedans, kulaklık seviyesi, besleme dalgalanması, TDA2003 kararlılığı

Bütün dosyalar `sim\06_IMP\` içinde. AC olanlar Analysis → AC…, transient olanlar Analysis → Transient… ile açılır, sonra Run.

## 6a — Giriş ve çıkış empedansı — `06a_empedans` (AC, 10 Hz–20 kHz)
- **Ayarlar:**
  - Hoparlör direnci bir parametreye bağlandı: RSPK = {IF(HP>0.5,1G,RL)}.
  - Stepping: RL 4 Ω / 4 MΩ (yüklü ve yüksüz).
  - Grafikler: MAG(V(IN))/MAG(I(R5)) ve MAG(V(SPK)).
- **Giriş empedansı:** 1.03 MΩ (20 Hz–5 kHz düz), 10 kHz'de 1.028 MΩ. Gitar manyetiği için uygun (≥1 MΩ, Fender/Marshall girişleriyle aynı sınıf).
- **Çıkış empedansı (hoparlör ucu):** Zout = RL·(V_yüksüz/V_yüklü − 1) formülüyle hesaplandı.
  - 1–10 kHz'de < 0.01 Ω. Bu, Micro-Cap çıktısının 3 haneli çözünürlüğünün sınırında.
  - 100 Hz'de ≈0.06 Ω (C25 2200 µF'ın etkisi).
  - Damping faktörü 4 Ω'da > 60: hoparlörü çok sıkı kontrol ediyor. Lambalı amfilerden farklı olarak hoparlör rezonansı vurgulanmaz.

## 6b — Kulaklık seviyesi — `06b_kulaklik` (Transient)
- **Ayarlar:** HP = 1 (hoparlör ayrık, 32 Ω kulaklık). Stepping: VOL 0.25 / 0.5 / 0.75 / 1 × VIN 0.2 / 1 V.
- **Ölçüm:** kulaklık gerilimi = v(SPK) − v(HPS). Devrede kulaklık, R28 = 10 Ω paralel ve R29 = 330 Ω seri üzerinden besleniyor (≈ −33 dB bölücü).

| VOL | VIN 0.2 V | VIN 1 V |
|---|---|---|
| 0.25 | 6 mV rms (0.001 mW) | 20 mV rms (0.013 mW) |
| 0.5 | 9 mV rms | 30 mV rms (0.03 mW) |
| 0.75 | 14 mV rms | 45 mV rms (0.06 mW) |
| 1 | 24 mV rms (0.018 mW) | 72 mV rms (**0.16 mW**) |

- **En yüksek seviye:** 32 Ω'a ≈0.16 mW. Tipik 100 dB/mW kulaklıkta ≈92 dB SPL (yaklaşık).
- **Güvenlik:** kulak içi ve kulak üstü kulaklık için güvenli. Kulaklık kendi seviyesinde, hassasiyeti düşük (ör. 90 dB/mW) modellerde biraz kısık kalabilir (yaklaşık).

## 6c — Besleme dalgalanması (PSRR) — `06c_besleme_ripple` (AC)
- **Ayarlar:** V1 = "DC 12 AC 1" (beslemeye 1 V AC), gitar girişi AC 0. Grafikler dB.

| Düğüm | 100 Hz | 1 kHz |
|---|---|---|
| V12 (D1 sonrası, TDA beslemesi) | −4.0 dB | −21.8 dB |
| V2 (RC filtre 1) | −30.1 | −67.9 |
| V3 (RC filtre 2, JFET/LM386) | −66.1 | −123.9 |
| O386 | −50.6 | −108 |
| **SPK** | **−31.1** | −52.6 |

- **Yorum:** ön katlar RC filtrelerle çok iyi korunuyor. Hoparlöre gelen dalgalanmanın çoğu TDA2003'ün kendi besleme hattından geliyor.
  - Adaptörde 100 Hz'de 100 mV dalgalanma olursa hoparlörde ≈2.8 mV olur. Bu sessiz bir ortamda zor duyulur (yaklaşık).
  - Kötü (filtresiz) bir adaptörde vızıltı TDA üzerinden gelir.

## 6d — TDA2003 kararlılığı — `06d_TDA_kararlilik` (AC, 10 Hz–10 MHz)
- **Ayarlar:** grafikler dB(v(SPK)/v(TIN)) ve ph(v(SPK)/v(TIN)).
- **Sonuç:**
  - Orta bant kazancı 40.0 dB (×100 = 1 + 220/2.2).
  - Üst −3 dB noktası 100 kHz. Tepe yok (kazanç 2.3 kHz'deki 39.98 dB'den monoton düşüyor). 1 MHz'de 19.5 dB, faz −92°.
  - Zobel (R27 1 Ω + C24 100 nF) devrede. Simülasyonda salınım veya peaking belirtisi yok.
- **Bulgu:** TDA katının alt −3 dB noktası **151 Hz**. Sebebi, geri besleme hattındaki C23 470 µF ile R26 2.2 Ω'un oluşturduğu köşe: 1/(2π·2.2·470µ) ≈ 154 Hz.
  - Gitarın en kalın teli (E, 82 Hz) bu katta ≈ −4.5 dB kayba uğruyor. Analiz 2'deki zayıf bas büyük ölçüde buradan geliyor.
  - *(Öneri; uygulanmadı:)* C23'ü 1000–2200 µF yapmak köşeyi ≈70–33 Hz'e indirir (yaklaşık).
- **Not:** bu analiz kapalı çevrimdir; gerçek baskı devre yerleşimindeki parazitler simülasyonda yok. Kararlılık için kısa toprak dönüşü ve Zobel'in TDA'ya yakın konması önemli.
