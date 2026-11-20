# 8 — C9'a seri potun düğme hissi: 2.2k ve 5k lineer pot

**Çalıştırma yolu:** `sim\08_POT\08a_pot_kazanc.cir` → Analysis → AC → Run, `08b_pot_THD.cir` → Analysis → Transient → Run ("Operating Point Only" kapalı).

**Model:**
- C9 = 22 µF ile seri RBP = {POTR·(1−ROT)}. ROT, düğme dönüşü: 0 = tam sol (en az kazanç), 1 = tam sağ (en çok kazanç).
- Stepping: POTR 2.2k / 5k × ROT 0…1 (adım 0.1).
- Diğer ayarlar: GAIN = VOL = ISF = 0.5, SW = 0, 4 Ω. THD için giriş 150 mV tepe, 1 kHz (normal bir gitar vuruşu).

## 2.2k lineer pot
| Düğme dönüşü | Pot direnci | JFET kazancı | Hoparlör @1 kHz | THD @150 mV (H2 / H3) |
|---|---|---|---|---|
| %0 | 2200 Ω | ×3.1 | 15.9 dB | 0.6 % (H2 0.6 / H3 0.0) |
| %10 | 1980 Ω | ×3.3 | 16.3 dB | 0.6 % (H2 0.6 / H3 0.0) |
| %20 | 1760 Ω | ×3.4 | 16.7 dB | 0.7 % (H2 0.7 / H3 0.0) |
| %30 | 1540 Ω | ×3.7 | 17.3 dB | 0.8 % (H2 0.8 / H3 0.0) |
| %40 | 1320 Ω | ×3.9 | 17.9 dB | 0.9 % (H2 0.9 / H3 0.0) |
| %50 | 1100 Ω | ×4.3 | 18.6 dB | 1.1 % (H2 1.1 / H3 0.0) |
| %60 | 880 Ω | ×4.7 | 19.5 dB | 1.4 % (H2 1.4 / H3 0.1) |
| %70 | 660 Ω | ×5.4 | 20.6 dB | 1.8 % (H2 1.8 / H3 0.1) |
| %80 | 440 Ω | ×6.3 | 22.0 dB | 15.6 % (H2 5.8 / H3 13.3) |
| %90 | 220 Ω | ×7.8 | 23.9 dB | 31.3 % (H2 8.8 / H3 29.5) |
| %100 | 0 Ω | ×10.8 | 26.7 dB | 45.0 % (H2 10.0 / H3 41.8) |

## 5k lineer pot
| Düğme dönüşü | Pot direnci | JFET kazancı | Hoparlör @1 kHz | THD @150 mV (H2 / H3) |
|---|---|---|---|---|
| %0 | 5000 Ω | ×2.3 | 13.1 dB | 0.3 % (H2 0.3 / H3 0.0) |
| %10 | 4500 Ω | ×2.4 | 13.4 dB | 0.3 % (H2 0.3 / H3 0.0) |
| %20 | 4000 Ω | ×2.5 | 13.8 dB | 0.4 % (H2 0.4 / H3 0.0) |
| %30 | 3500 Ω | ×2.6 | 14.2 dB | 0.4 % (H2 0.4 / H3 0.0) |
| %40 | 3000 Ω | ×2.7 | 14.8 dB | 0.4 % (H2 0.4 / H3 0.0) |
| %50 | 2500 Ω | ×3.0 | 15.4 dB | 0.5 % (H2 0.5 / H3 0.0) |
| %60 | 2000 Ω | ×3.3 | 16.2 dB | 0.6 % (H2 0.6 / H3 0.0) |
| %70 | 1500 Ω | ×3.7 | 17.4 dB | 0.8 % (H2 0.8 / H3 0.0) |
| %80 | 1000 Ω | ×4.5 | 19.0 dB | 1.2 % (H2 1.2 / H3 0.1) |
| %90 | 500 Ω | ×6.0 | 21.6 dB | 10.7 % (H2 4.4 / H3 8.3) |
| %100 | 0 Ω | ×10.8 | 26.7 dB | 45.0 % (H2 10.0 / H3 41.8) |

## Yorum
- **2.2k:** düğmenin ilk %70'i temiz–sıcak bölgede kademeli ilerliyor (THD 0.6 → 1.8 %, tamamı H2; ses ≈+5 dB yükseliyor). Son %30'da crunch ve overdrive geliyor: %80'de 16 %, %100'de 45 %. Ayar aralığının yaklaşık üçte biri distorsiyona ayrılmış durumda; kullanılabilir bir his.
- **5k:** en sol konum biraz daha temiz (×2.3, THD 0.3 %), ama düğmenin ilk %60'ında neredeyse hiçbir şey değişmiyor (≈3 dB). Bütün crunch ve overdrive son ≈%15'e sıkışıyor (%80'de 1.2 %, %90'da 11 %, %100'de 45 %). Düğme "uzun süre boş, sonra birden" hissettirir. Lineer 5k, 2.2k'dan daha kötü bir his veriyor.
- **İki potta da tam sağ aynı noktaya varıyor:** C9 tam bypass, ×10.8. Fark yalnızca aralığın nasıl dağıldığında.
- **Öneri (uygulanmadı):** elindeki 2.2k lineer pot yeterli ve daha iyi bir his veriyor. 5k kullanmak istersen, bağlantı yönüne göre logaritmik (A) ya da ters logaritmik (C) bir pot daha düzgün dağılım verir; amaç, direncin sağ uçta hızlı düşmesi (yaklaşık).
