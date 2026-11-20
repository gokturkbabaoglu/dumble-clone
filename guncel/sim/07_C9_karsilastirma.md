# 7 — C9 karşılaştırması: yok / 22 µF / 22 µF + 1k / 22 µF + 2.2k

**Değişiklik (yalnızca simülasyon dosyalarında):**
- C9'un toprak ucuna seri bir direnç (RBP) eklendi.
- Tek bir MODE parametresi dört durumu seçiyor. Değerler: C9 = {IF(MODE<0.5,1p,22u)}, RBP = {IF(MODE<1.5,1m,IF(MODE<2.5,1k,2.2k))}.
- Diğer bütün bağlantıların aynı kaldığı ağ karşılaştırmasıyla doğrulandı. Asıl şema (`amfi_tasarim.cir`) değiştirilmedi.

**Çalıştırma yolu:** `sim\07_C9\` içindeki dosyalar.
- `07a_C9_AC.cir` → Analysis → AC → Run. 10 Hz–20 kHz, stepping MODE 0→3.
- `07b_C9_THD.cir` → Analysis → Transient → Run ("Operating Point Only" kapalı). 1 kHz; VIN 30 / 180 / 330 mV tepe × MODE.
- `07c_C9_gurultu.cir` → Analysis → AC → Run. Noise Input VGIT, Output SPK, 20 Hz–20 kHz.

Diğer ayarlar: GAIN = VOL = ISF = 0.5, SW = 0, 4 Ω. Her dosyanın `.ANO`/`.TNO`, `.csv` ve `.jpg` çıktıları aynı klasörde.

## Kazanç (1 kHz)
| Durum | JFET katı | LM386 çıkışı | Hoparlör | C9 yok'a göre fark |
|---|---|---|---|---|
| C9 yok | +3.4 dB (×1.5) | 19.2 dB | 9.4 dB | — |
| 22 µF + 2.2k | +9.9 dB (×3.1) | 25.7 dB | 15.9 dB | +6.5 dB |
| 22 µF + 1k | +13.0 dB (×4.5) | 28.8 dB | 19.0 dB | +9.6 dB |
| 22 µF (tam) | +20.7 dB (×10.8) | 36.5 dB | 26.7 dB | +17.3 dB |

Frekans cevabının şekli dört durumda da aynı (tepe 3.6 kHz, −3 dB bandı 1.36–9.6 kHz). C9 yalnızca seviyeyi değiştiriyor, tonu değiştirmiyor. Alt köşe 13–18 Hz; bas kaybı yok.

## Bozulma (hoparlör THD; parantez içinde baskın harmonik)
| Durum | 30 mV | 180 mV | 330 mV | Kırpılma başlangıcı (yaklaşık) |
|---|---|---|---|---|
| C9 yok | 0.0 % | 0.1 % | 0.3 % (H2) | ≈ 0.5 V tepe |
| 22 µF + 2.2k | 0.1 % | 0.7 % (H2) | 22 % (H3) | ≈ 250 mV |
| 22 µF + 1k | 0.2 % | 1.5 % (H2) | 41 % (H3) | ≈ 170 mV |
| 22 µF (tam) | 1.4 % (H2) | 51 % (H3) | 63 % (H3) | ≈ 70 mV |

Kırpılma başlangıcı, LM386 çıkışının ≈4.7 V tepe salınım sınırından hesaplandı.

- **JFET katının kendi bozulması** (330 mV'ta): yok 0.2 %, 2.2k 0.9 %, 1k 1.8 %, tam bypass 11.4 %. Hepsinde neredeyse tamamı H2.
- **Tam bypass'ta JFET de kırpılmaya yaklaşıyor:** drain 3.4 V tepe salınıyor.

## Gürültü (20 Hz–20 kHz, 4 Ω)
| Durum | Girişe indirgenmiş @1 kHz | Toplam çıkış gürültüsü | SNR (1.3 W'a göre) |
|---|---|---|---|
| C9 yok | 522 nV/√Hz | 155 µV | ≈ 83 dB |
| 22 µF + 2.2k | 317 nV/√Hz | 189 µV | ≈ 82 dB |
| 22 µF + 1k | 274 nV/√Hz | 227 µV | ≈ 80 dB |
| 22 µF (tam) | 235 nV/√Hz | 449 µV | ≈ 74 dB |

## Değerlendirme
- **C9 yok:** en temiz ve en sessiz. Normal çalmada hiç kırpmıyor; overdrive için Gain'i sonuna kadar açmak veya güçlü manyetik gerekiyor. ISF ve Dark/Bright en net bu durumda duyulur.
- **22 µF + 2.2k:** temiz bölgeyi büyük ölçüde koruyor; normal çalmada <1 %, tamamı H2, yani sıcak. Sert vuruşta crunch'a geçiyor. Gürültü artışı ihmal edilebilir (+1.7 dB). Temiz ağırlıklı ama "canlı" bir amfi için dengeli seçenek.
- **22 µF + 1k:** orta yol. Hafif vuruşta temiz, normal–sert vuruşta crunch. Gürültü +3.3 dB.
- **22 µF (tam):** neredeyse her zaman distorsiyonda; 180 mV'ta bile %51 ve H3 baskın, fuzz'a yakın. Gürültü 3 kat (+9.3 dB). Temiz ses pratikte yok.
- **Öneri (uygulanmadı):** temiz/crunch hedefi için 22 µF + 2.2k veya 1k. 2.2k daha temiz ve daha sessiz, 1k daha fazla crunch veriyor.
