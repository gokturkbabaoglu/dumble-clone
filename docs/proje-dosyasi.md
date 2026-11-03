# LM386 Dumble tarzı gitar amfisi — devam dosyası (revizyon 3)

Hazırlanma: 4 Kasım 2026. Bu dosya projenin tam durumunu içerir; yeni bir sohbette bu dosyayı ekleyip kaldığın yerden devam edebilirsin.

**Yeni sohbet için kısa talimat (Claude'a):** Bu dosya bir LM386 gitar amfisi projesinin güncel ve onaylanmış tasarımıdır. Tasarım kararları kullanıcıyla birlikte verildi; değiştirmeden önce sor. Kullanıcı Türkçe yazıyor, elektronik mühendisliği son sınıf öğrencisi. Sıradaki iş: kartın lehimlenmesi, ilk ölçümlerin kontrolü ve kabin tasarımı.

**Bağlantılar**
- Şema, pertinaks yerleşimi (üst ve ayna alt görünüm) ve kart dışı bağlantı çizimi: https://claude.ai/artifact/4vbBJ9Gwj1bcYF8xBSRxXn
- Proje raporu (Claude Docs): https://claude.ai/artifact/Lovh5gBZ2zxJ7Dnp8eKDwZ

---

## 1. Proje ve kısıtlar

- YouTube'da görülen LM386 tabanlı, Dumble tarzı (temizden kremsi overdrive'a) küçük gitar amfisi.
- Elde olan parçalarla, olabildiğince az ek parça alarak yapılıyor.
- Besleme 12 V 2 A adaptör. Tek 8 Ω 0,5 W hoparlör (ikinci hoparlör yok) ve 3,5 mm kulaklık çıkışı.
- Devre 18×38 delikli, **her deliği ayrı pedli (adalı)** pertinaksta. Pot, anahtar ve jaklar küçük bir kabinde (3D baskı planlanıyor).
- Kullanıcı karmaşıklığı az, sinyal yolu temiz bir tasarım istiyor. Kabin küçük olduğu için 3 bantlı tone stack (bas/mid/tiz) istemedi.

## 2. Revizyon geçmişi ve kararlar

| Rev | Değişiklik | Neden |
|---|---|---|
| 1 | BF245B JFET preamp + LM386, Fat/Bright ve ayrı bright anahtarı, VR4 bias trimi, tek Tone potu | İlk rapor |
| 2 | Anahtarlar S1 güç, S2 Bright/Dark, S3 hoparlör olarak düzeltildi. VR4 kaldırıldı (Rd = 2 kΩ sabit). D1 kart dışına alındı. Sinyal yolu soldan sağa | Önceki oturumda anahtar görevleri yanlış anlaşılmıştı; sadeleştirme |
| 3 | Bright/Dark kısmi bypass'a geçti (fark 12 dB → ≈6 dB). Tone yerine ISF tarzı Shape. Gain potu B10k → B1k. Kart 18×38'e yeniden yerleşti. Kart dışı bağlantı şeması eklendi | Normal amfi davranışı, kullanıcı tercihi |

Gain potu: B10k'da kazanç dönüşün ilk %85–90'ında 22→30 kat arasında kalıyordu (ölü his). B1k ile: tam kısık 41, yarı 58, 3/4 83, tam açık 200 kat. İdeali C (ters log) tip ama bulunması zor.

## 3. Devre özeti

**Sinyal yolu:** gitar → J1 → Q1 BF245B (ortak source, Rd 2k, Bright/Dark source bypass'ı) → C7 → Shape (köprülü-T çentik + VR3 geçiş) → VR2 Volume → LM386 pin 3 (VR1 Gain pin 1–8 arasında) → C2 → S3 → hoparlör ve R2/R3 → kulaklık.

**Bright/Dark:** Rs = 1k source'tan GND'ye. C8 (10 µF) source'tan Y noktasına. Y → GND: Rb1 ‖ Rb2 (1k‖1k = 500 Ω) ‖ C9 (100 nF). S2, Y'yi GND'ye kısa devre eder: kapalı = Dark (tam bypass), açık = Bright.

**Shape (ISF tarzı):** A (C7 çıkışı) –CT1 (47n)– M –CT2 (47n)– B; RT 10k A–B arasında; M → RM1 + RM2 (1k+1k) → GND. VR3 B22k: bacak 3 = A (düz), bacak 1 = B (çentikli), orta bacak → VR2 bacak 3. Saat yönü (sağ) = Marshall, sol = Fender. Blackstar ISF'in birebir devresi değil, aynı fikrin basit uyarlaması.

**Güç katı:** LM386, pin 1–8 arası C3‖C4 (200 nF) + VR1 B1k (bacak 2 ve 3). Zobel R1 10 Ω + C5 47 nF. Çıkış C2 220 µF. Besleme dekuplajı C1 220 µF. Preamp beslemesi Rf 1k + C6 100 µF (V_pre).

**Güç girişi:** J2 + → D1 1N4007 anot; D1 katot → S1 yan bacak; S1 orta → kart +12 V (ped 11). J2 − → ped 12.

## 4. Kontroller

| Kontrol | Parça | Yön (önden) | Ne yapar |
|---|---|---|---|
| Volume | VR2 B100k | Saat yönü = açılır | LM386'ya giren sinyal; ses ve distorsiyon birlikte artar |
| Gain | VR1 B1k | Saat yönü = açılır | LM386 kazancı 41–200 kat; distorsiyon artar, bas sıkılaşır |
| Shape | VR3 B22k | Sol = Fender, sağ = Marshall | Sol: ortalar oyuk, bas ve tiz önde. Sağ: düz, ortalar önde |
| S1 | Sürgülü anahtar | — | 12 V beslemeyi keser |
| S2 | Sürgülü anahtar | Kapalı = Dark | Dark: dolgun, tam kazanç. Bright: ortalar ≈6 dB kısık, daha parlak |
| S3 | Sürgülü anahtar | — | Hoparlörü keser, kulaklık çalışmaya devam eder |

Not: Distorsiyon son katta (LM386) oluştuğu için ayrı master volume yok; Volume ve Gain ikisi de sesi ve drive'ı etkiler. 0,5 W hoparlörde ikisini birlikte sonuna kadar açma.

## 5. Parça listesi (tamamı elde, 3 Kasım'da kontrol edildi)

**Dirençler**

| Değer | Adet | 4 bant (%5) | 5 bant (%1) | Kod |
|---|---|---|---|---|
| 1 kΩ | 10 | kahve-siyah-kırmızı-altın | kahve-siyah-siyah-kahve-kahve | Rf, Rd1, Rd2, Rs, Rb1, Rb2, RM1, RM2, R2, R3 |
| 10 kΩ | 1 | kahve-siyah-turuncu-altın | kahve-siyah-siyah-kırmızı-kahve | RT |
| 1 MΩ | 1 | kahve-siyah-yeşil-altın | kahve-siyah-siyah-sarı-kahve | Rg |
| 10 Ω | 1 | kahve-siyah-siyah-altın | kahve-siyah-siyah-altın-kahve | R1 |

**Kondansatörler**

| Değer | Adet | Üzerinde yazan | Tip | Kod |
|---|---|---|---|---|
| 220 µF | 2 | 220µF 25V | Elektrolitik | C1, C2 |
| 100 µF | 1 | 100µF 100V | Elektrolitik | C6 |
| 10 µF | 1 | 10µF 25V | Elektrolitik | C8 |
| 100 nF | 3 | 104J100 (biri 104K63) | Film | C3, C4, C7 |
| 47 nF | 3 | 473J100 | Film | C5, CT1, CT2 |
| 100 nF | 1 | 104 | Seramik/MLCC | C9 |

**Diğer:** U1 LM386 (DIP-8, isteğe bağlı soket) · Q1 BF245B (TO-92) · D1 1N4007 · VR1 B1k, VR2 B100k, VR3 B22k · S1–S3 3 bacaklı sürgülü anahtar · J1 6,35 mm jak · J2 DC soket + 12 V 2 A adaptör · J3 3,5 mm stereo jak · SP1 8 Ω 0,5 W · 18×38 adalı pertinaks · 3 pot düğmesi.

**Kullanılmayan yedekler:** B20k, B10k, B5k, B500k potlar; 4n7; 2× 223J100; BF247A, 2N3819, 2N3904, BC547.

## 6. Netlist

LM386 pinleri: 1 ve 8 gain, 2 −in, 3 +in, 4 GND, 5 çıkış, 6 Vs, 7 boş. Pot bacakları önden bakışta (mil sana doğru, bacaklar aşağıda) soldan sağa 1-2-3; saat yönü sileceği 3'e götürür.

| Düğüm | Bağlı uçlar |
|---|---|
| GND | J1 gövde, Rg, Rs, Rb1, Rb2, C9, RM2, C6 −, U1 pin 2 ve 4, C1 −, C5, VR2 bacak 1, S2 yan bacak, J2 −, SP1 −, J3 gövde, pot gövdeleri |
| Besleme | J2 + → D1 anot; D1 katot → S1 yan; S1 orta → +12V |
| +12V | U1 pin 6, C1 +, Rf |
| VPRE | Rf diğer ucu, C6 +, Rd1 |
| RDM | Rd1 – Rd2 |
| DRAIN | Rd2, Q1 D, C7 |
| GATE | J1 uç, Q1 G, Rg |
| SRC | Q1 S, Rs, C8 + |
| Y | C8 −, Rb1, Rb2, C9, S2 orta bacak |
| A | C7 diğer ucu, CT1, RT, VR3 bacak 3 |
| M | CT1–CT2 ortak uç, RM1 |
| MM | RM1 – RM2 (RM2 → GND) |
| B | CT2 diğer ucu, RT diğer ucu, VR3 bacak 1 |
| Volume üst | VR3 bacak 2 – VR2 bacak 3 (kabinde kısa tel) |
| IN3 | VR2 bacak 2, U1 pin 3 |
| G1 / GA / G8 | U1 pin 1 → C3‖C4 → VR1 bacak 3; VR1 bacak 2 → U1 pin 8; VR1 bacak 1 boş |
| OUT | U1 pin 5, C2 +, R1 |
| ZOB | R1 – C5 (C5 → GND) |
| SPK | C2 −, S3 orta (S3 yan → SP1 +), R2, R3 |
| HPL / HPR | R2 → J3 L, R3 → J3 R |

## 7. Hesaplar ve hedef değerler

- BF245B: Idss 6–15 mA. Rs 1k ile Id ≈ 1–2,3 mA. Rd 2k ile drain 4,5–8,5 V (bütün tolerans aralığında doyumda kalıyor).
- V_pre ≈ 9–10 V, U1 pin 6 ≈ 11,3 V (D1 düşümü sonrası).
- Q1 kazancı (gm ≈ 3,1 mS varsayımı): Dark ≈ +16 dB, Bright ortalarda ≈ +10 dB, tizde ≈ +12 dB.
- LM386 kazancı: Av = 30k / (150 + 1,35k ‖ R_VR1); 41–200 kat. Gain ağının bas kesimi ≈ 590 Hz.
- Shape (Rsrc 2k, yük 50k varsayımı, düz yola göre dB):

| VR3 konumu | 82 Hz | 300 Hz | 700 Hz | 1 kHz | 2,5 kHz | 6 kHz |
|---|---|---|---|---|---|---|
| Sol (Fender) | −6,0 | −8,1 | −12,5 | −13,1 | −8,3 | −6,3 |
| Orta | −6,2 | −7,3 | −8,4 | −8,5 | −7,6 | −6,9 |
| Sağ (Marshall) | −5,2 | −4,9 | −4,3 | −4,3 | −5,0 | −5,6 |

## 8. Pertinaks yerleşimi

- Görünüm: **parça yüzü, üstten**. Sütunlar 1–31 (soldan sağa), satırlar A–N (yukarıdan aşağı). Kullanılan alan 31×14 delik; 18×38'lik kartın sol üst köşesinden başla.
- Dik diren = iki komşu delik (gövde ilk deliğin üstünde). Rf, Rg, RT yatık. U1'in çentiği sola bakar, pin 1 = G21. Q1'in düz yüzü yukarı, soldan sağa G-S-D.
- Alt yüz yolları lehim köprüsü ya da çıplak telle. Alt yüzde çalışırken soldan sağa sıralama ters döner (ayna görüntüsü).
- Raylar: A satırı +12V (A12–A29) ve VPRE (A2–A8); N satırı GND (N1–N31); 1. sütun ve 31. sütun GND hatları.

**Parça yerleşimi**

| Kod | Değer | Bacaklar (delik → düğüm) | Montaj |
|---|---|---|---|
| Rf | 1k | A8→VPRE, A12→+12V | yatık |
| C6 | 100µ | B3(+)→VPRE, D3(−)→GND | elektrolitik |
| Rd1 | 1k | B7→VPRE, C7→RDM | dik |
| Rd2 | 1k | D7→RDM, E7→DRAIN | dik |
| Q1 | BF245B | H5(G)→GATE, H6(S)→SRC, H7(D)→DRAIN | TO-92 |
| Rg | 1M | H4→GATE, L4→GND | yatık |
| Rs | 1k | J6→SRC, K6→GND | dik |
| C8 | 10µ | J7(+)→SRC, J8(−)→Y | elektrolitik |
| Rb1 | 1k | K9→Y, L9→GND | dik |
| C9 | 104 | K11→Y, L11→GND | seramik |
| Rb2 | 1k | K12→Y, L12→GND | dik |
| C7 | 100n | F8→DRAIN, F10→A | film |
| CT1 | 47n | F12→A, F14→M | film |
| CT2 | 47n | F15→M, F17→B | film |
| RT | 10k | D12→A, D17→B | yatık |
| RM1 | 1k | H14→M, I14→MM | dik |
| RM2 | 1k | J14→MM, K14→GND | dik |
| U1 | LM386 | G21(1)→G1, G22(2)→GND, G23(3)→IN3, G24(4)→GND, D24(5)→OUT, D23(6)→+12V, D22(7)→NC7, D21(8)→G8 | DIP-8 |
| C3 | 100n | H21→G1, J21→GA | film |
| C4 | 100n | H19→G1, J19→GA | film |
| R1 | 10R | E26→ZOB, D26→OUT | dik |
| C5 | 47n | F26→ZOB, H26→GND | film |
| C2 | 220µ | E29(+)→OUT, G29(−)→SPK | elektrolitik |
| C1 | 220µ | B29(+)→+12V, B31(−)→GND | elektrolitik |
| R2 | 1k | J27→SPK, K27→HPL | dik |
| R3 | 1k | J29→SPK, K29→HPR | dik |

**Alt yüz yolları** (köşe noktaları; aradaki tüm delikler aynı yola dahil)

| Düğüm | Alt yüz yolu |
|---|---|
| GND | N1 → N31 |
| GND | D1 → N1 |
| GND | B31 → N31 |
| +12V | A12 → A29 |
| +12V | A29 → B29 |
| VPRE | A2 → A8 |
| VPRE | A3 → B3 |
| VPRE | A7 → B7 |
| GND | D3 → D1 |
| RDM | C7 → D7 |
| DRAIN | E7 → H7 |
| DRAIN | F7 → F8 |
| GATE | H3 → H5 |
| GND | L4 → L1 |
| SRC | H6 → J6 |
| SRC | J6 → J7 |
| GND | K6 → N6 |
| Y | J8 → J12 |
| Y | J9 → K9 |
| Y | J11 → K11 |
| Y | J12 → K12 |
| GND | L9 → N9 |
| GND | L11 → N11 |
| GND | L12 → N12 |
| GND | L10 → N10 |
| A | F10 → F12 |
| A | E11 → F11 |
| A | D12 → F12 |
| M | F14 → F15 |
| M | F14 → H14 |
| B | D17 → F17 |
| B | F17 → F18 |
| MM | I14 → J14 |
| GND | K14 → N14 |
| +12V | A23 → D23 |
| GND | G22 → N22 |
| GND | G24 → N24 |
| IN3 | G23 → H23 |
| GND | J22 → J23 |
| G1 | G21 → H21 |
| G1 | H19 → H21 |
| GA | J19 → J21 |
| GA | J20 → K20 |
| G8 | D21 → D20 |
| OUT | D24 → D29 → E29 |
| ZOB | E26 → F26 |
| GND | H26 → H24 |
| SPK | G29 → J29 |
| SPK | H29 → H28 |
| SPK | I29 → I27 → J27 |
| HPL | K27 → L27 |
| HPR | K29 → L29 |

**Kablo pedleri** (karttan kabine)

| # | Delik | Düğüm | Grup | Nereye |
|---|---|---|---|---|
| 1 | H3 | GATE | Giriş | J1 uç |
| 2 | I1 | GND | Giriş | J1 gövde |
| 3 | J10 | Y | S2 | S2 orta bacak |
| 4 | L10 | GND | S2 | S2 yan bacak (Dark tarafı) |
| 5 | E11 | A | Shape/Volume | VR3 bacak 3 |
| 6 | F18 | B | Shape/Volume | VR3 bacak 1 |
| 7 | H23 | IN3 | Shape/Volume | VR2 bacak 2 |
| 8 | J23 | GND | Shape/Volume | VR2 bacak 1 |
| 9 | D20 | G8 | Gain | VR1 bacak 2 |
| 10 | K20 | GA | Gain | VR1 bacak 3 |
| 11 | A28 | +12V | Güç | S1 orta bacak |
| 12 | E31 | GND | Güç | J2 − |
| 13 | H28 | SPK | Hoparlör | S3 orta bacak |
| 14 | I31 | GND | Hoparlör | SP1 − |
| 15 | L27 | HPL | Kulaklık | J3 L (uç) |
| 16 | L29 | HPR | Kulaklık | J3 R (halka) |
| 17 | L31 | GND | Kulaklık | J3 gövde |

## 9. Kart dışı bağlantılar

**Burgulu gruplar:** Giriş 1+2 · S2 3+4 · Shape 5+6 · Volume 7+8 · Gain 9+10 · Güç 11+12 · Hoparlör 13+14 · Kulaklık 15+16+17 (üçlü).

**Burgusuz:** VR3 bacak 2 → VR2 bacak 3 kısa tel · J2 + → D1 → S1 yan bacak (makaronlu, çizgi S1 tarafında) · S3 yan bacak → SP1 + · pot gövdeleri çıplak telle birbirine ve VR2 bacak 1'e.

**Kurallar**
- Giriş kablosu en kısa yoldan; hoparlör ve güç kablolarına paralel gitmesin, kesişirse dik açıyla.
- Gain kabloları kısa (LM386 geri besleme ağı).
- Pot arkasından bakınca bacak 3 solda, 1 sağda.
- Bazı sürgülü anahtarlarda orta bacak sürgünün tersindeki yan bacağa bağlanır. S2'de hangi konumda orta–yan birleşiyor ölç; o konum Dark.
- Jak gövdelerini metal panelle birbirine bağlama.

## 10. Montaj ve ilk çalıştırma

1. Adaptörün boştaki voltajını ve merkez ucun + olduğunu ölç. BF245B bacaklarını diyot moduyla doğrula.
2. Alt yüz yolları (önce GND ve +12V), sonra dirençler ve soket, film/seramik kondansatörler, Q1, elektrolitikler (C8 + bacağı J7'de), en son kablolar.
3. Süreklilik: H5 (gate)–GND, G23 (pin 3)–GND, +12V–GND kısa devre olmamalı. Y (J10)–GND ≈ 500 Ω normal.
4. U1 takılı değilken güç: pin 6 ≈ 11,3 V, C6 + ≈ 9–10 V, Q1 drain (H7) 4,5–8,5 V, source (H6) 1–2,3 V.
5. Gücü kes, U1'i tak. İlk test volume kısık, kulaklık kulakta değilken.

## 11. Açık konular

- [ ] Adaptör polaritesi ve BF245B bacak sırası ölçümü
- [ ] S2'nin Dark konumunu ölçerek belirleme
- [ ] Kartı lehimleme, süreklilik ve ilk çalıştırma ölçümleri (sonuçları paylaş)
- [ ] Kabin tasarımı (3D baskı): 3 pot, 3 anahtar, 3 jak, hoparlör
- [ ] İleride: 1–3 W hoparlör

---

## Ek: Yerleşim kaynak kodu (layout.py)

Bu Python dosyası kart yerleşiminin tek kaynağıdır: parça bacakları, alt yüz yolları ve kablo pedleri. Çalıştırınca çakışma ve bağlantı kontrolü yapar (`python3 layout.py`). Değişiklik gerekirse buradan başlanabilir.

```python
"""Perfboard (dot-pad pertinaks) layout for LM386 Dumble-style amp.
Component-side view. Copper-side solder trails drawn as lines.
Run: python3 layout.py  -> checks + writes layout.svg
"""
import math, sys
from collections import defaultdict

W, H = 31, 14  # columns x rows

# ---------- components ----------
# pads: (x, y, net, pinlabel)
# body: ('circle', cx, cy, r_pitch) | ('rect', cx, cy, w, h)   (pitch units, 1 pitch = 2.54 mm)
P = 2.54
comps = []
def comp(ref, val, pads, body, kind):
    comps.append(dict(ref=ref, val=val, pads=pads, body=body, kind=kind))

def r_stand(ref, val, a, b, na, nb, body_on='a'):
    bx, by = a if body_on == 'a' else b
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('circle', bx, by, 1.2 / P), 'r_stand')

def r_flat(ref, val, a, b, na, nb):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    horiz = a[1] == b[1]
    w, h = (6.3 / P, 2.4 / P) if horiz else (2.4 / P, 6.3 / P)
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('rect', cx, cy, w, h), 'r_flat')

def ecap(ref, val, plus, minus, np_, nm, dia_mm):
    cx, cy = (plus[0] + minus[0]) / 2, (plus[1] + minus[1]) / 2
    comp(ref, val, [(plus[0], plus[1], np_, '+'), (minus[0], minus[1], nm, '−')], ('circle', cx, cy, dia_mm / 2 / P), 'ecap')

def film(ref, val, a, b, na, nb, thick_mm=3.5):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    horiz = a[1] == b[1]
    L = 7.2 / P; t = thick_mm / P
    w, h = (L, t) if horiz else (t, L)
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('rect', cx, cy, w, h), 'film')

def ceram(ref, val, a, b, na, nb):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    horiz = a[1] == b[1]
    w, h = (5 / P, 2.5 / P) if horiz else (2.5 / P, 5 / P)
    comp(ref, val, [(a[0], a[1], na, ''), (b[0], b[1], nb, '')], ('rect', cx, cy, w, h), 'ceram')

# ---------- placement ----------
SH = 7  # power-amp section shift (columns)
# Preamp supply
r_flat('Rf', '1k', (8, 1), (12, 1), 'VPRE', '+12V')
ecap('C6', '100µ', (3, 2), (3, 4), 'VPRE', 'GND', 10)
r_stand('Rd1', '1k', (7, 2), (7, 3), 'VPRE', 'RDM')
r_stand('Rd2', '1k', (7, 4), (7, 5), 'RDM', 'DRAIN')
comp('Q1', 'BF245B', [(5, 8, 'GATE', 'G'), (6, 8, 'SRC', 'S'), (7, 8, 'DRAIN', 'D')], ('rect', 6, 8.15, 4.8 / P, 3.8 / P), 'to92')
r_flat('Rg', '1M', (4, 8), (4, 12), 'GATE', 'GND')
r_stand('Rs', '1k', (6, 10), (6, 11), 'SRC', 'GND')
# Bright/Dark: C8 source->Y ; Y->GND via Rb1||Rb2||C9 ; S2 shorts Y to GND (Dark)
ecap('C8', '10µ', (7, 10), (8, 10), 'SRC', 'Y', 5)
r_stand('Rb1', '1k', (9, 11), (9, 12), 'Y', 'GND')
ceram('C9', '104', (11, 11), (11, 12), 'Y', 'GND')
r_stand('Rb2', '1k', (12, 11), (12, 12), 'Y', 'GND')
film('C7', '100n', (8, 6), (10, 6), 'DRAIN', 'A')
# Shape (bridged-T): A -CT1- M -CT2- B ; RT A-B ; RM1+RM2 M->GND
film('CT1', '47n', (12, 6), (14, 6), 'A', 'M', 3.0)
film('CT2', '47n', (15, 6), (17, 6), 'M', 'B', 3.0)
r_flat('RT', '10k', (12, 4), (17, 4), 'A', 'B')
r_stand('RM1', '1k', (14, 8), (14, 9), 'M', 'MM')
r_stand('RM2', '1k', (14, 10), (14, 11), 'MM', 'GND')
# LM386, notch left. top row (y=4): 8 7 6 5 ; bottom row (y=7): 1 2 3 4
ux, uyt, uyb = 14 + SH, 4, 7
comp('U1', 'LM386', [
    (ux, uyb, 'G1', '1'), (ux + 1, uyb, 'GND', '2'), (ux + 2, uyb, 'IN3', '3'), (ux + 3, uyb, 'GND', '4'),
    (ux + 3, uyt, 'OUT', '5'), (ux + 2, uyt, '+12V', '6'), (ux + 1, uyt, 'NC7', '7'), (ux, uyt, 'G8', '8')],
    ('rect', ux + 1.5, (uyt + uyb) / 2, 9.8 / P, 6.4 / P), 'dip8')
film('C3', '100n', (14+SH, 8), (14+SH, 10), 'G1', 'GA')
film('C4', '100n', (12+SH, 8), (12+SH, 10), 'G1', 'GA')
r_stand('R1', '10R', (19+SH, 5), (19+SH, 4), 'ZOB', 'OUT', body_on='a')
film('C5', '47n', (19+SH, 6), (19+SH, 8), 'ZOB', 'GND', 3.0)
ecap('C2', '220µ', (22+SH, 5), (22+SH, 7), 'OUT', 'SPK', 8)
ecap('C1', '220µ', (22+SH, 2), (24+SH, 2), '+12V', 'GND', 8)
r_stand('R2', '1k', (20+SH, 10), (20+SH, 11), 'SPK', 'HPL')
r_stand('R3', '1k', (22+SH, 10), (22+SH, 11), 'SPK', 'HPR')

wires = [
    (3, 8, 'GATE', 'GİRİŞ uç', 'J1'), (1, 9, 'GND', 'GİRİŞ gövde', 'J1'),
    (10, 10, 'Y', 'S2', 'S2'), (10, 12, 'GND', 'S2 GND', 'S2'),
    (11, 5, 'A', 'SHAPE 3', 'VOL'), (18, 6, 'B', 'SHAPE 1', 'VOL'),
    (16+SH, 8, 'IN3', 'VOL 2', 'VOL'), (16+SH, 10, 'GND', 'VOL 1', 'VOL'),
    (13+SH, 4, 'G8', 'GAIN 2', 'GAIN'), (13+SH, 11, 'GA', 'GAIN 3', 'GAIN'),
    (21+SH, 1, '+12V', '+12V (S1)', 'PWR'), (24+SH, 5, 'GND', 'GND (DC jak)', 'PWR'),
    (21+SH, 8, 'SPK', 'S3 orta', 'SPK'), (24+SH, 9, 'GND', 'HOP −', 'SPK'),
    (20+SH, 12, 'HPL', 'KUL L', 'HP'), (22+SH, 12, 'HPR', 'KUL R', 'HP'), (24+SH, 12, 'GND', 'KUL gövde', 'HP'),
]

def hline(y, x0, x1): return [(x, y) for x in range(min(x0, x1), max(x0, x1) + 1)]
def vline(x, y0, y1): return [(x, y) for y in range(min(y0, y1), max(y0, y1) + 1)]
def sh(pts): return [(x + SH, y) for x, y in pts]
traces = [
    ('GND', hline(14, 1, 24+SH)), ('GND', vline(1, 4, 14)), ('GND', vline(24+SH, 2, 14)),
    ('+12V', hline(1, 12, 22+SH)), ('+12V', vline(22+SH, 1, 2)),
    ('VPRE', hline(1, 2, 8)), ('VPRE', vline(3, 1, 2)), ('VPRE', vline(7, 1, 2)),
    ('GND', [(3, 4), (2, 4), (1, 4)]),
    ('RDM', vline(7, 3, 4)),
    ('DRAIN', vline(7, 5, 8)), ('DRAIN', [(7, 6), (8, 6)]),
    ('GATE', hline(8, 3, 5)),
    ('GND', [(4, 12), (3, 12), (2, 12), (1, 12)]),
    ('SRC', vline(6, 8, 10)), ('SRC', [(6, 10), (7, 10)]),
    ('GND', vline(6, 11, 14)),
    ('Y', hline(10, 8, 12)), ('Y', vline(9, 10, 11)), ('Y', vline(11, 10, 11)), ('Y', vline(12, 10, 11)),
    ('GND', vline(9, 12, 14)), ('GND', vline(11, 12, 14)), ('GND', vline(12, 12, 14)), ('GND', vline(10, 12, 14)),
    ('A', hline(6, 10, 12)), ('A', vline(11, 5, 6)), ('A', vline(12, 4, 6)),
    ('M', [(14, 6), (15, 6)]), ('M', vline(14, 6, 8)),
    ('B', vline(17, 4, 6)), ('B', [(17, 6), (18, 6)]),
    ('MM', vline(14, 9, 10)), ('GND', vline(14, 11, 14)),
    ('+12V', sh(vline(16, 1, 4))),
    ('GND', sh(vline(15, 7, 14))), ('GND', sh(vline(17, 7, 14))),
    ('IN3', sh(vline(16, 7, 8))), ('GND', sh([(15, 10), (16, 10)])),
    ('G1', sh(vline(14, 7, 8))), ('G1', sh(hline(8, 12, 14))), ('GA', sh(hline(10, 12, 14))), ('GA', sh(vline(13, 10, 11))),
    ('G8', sh([(14, 4), (13, 4)])),
    ('OUT', sh([(17, 4), (18, 4), (19, 4), (20, 4), (21, 4), (22, 4), (22, 5)])),
    ('ZOB', sh(vline(19, 5, 6))), ('GND', sh([(19, 8), (18, 8), (17, 8)])),
    ('SPK', sh(vline(22, 7, 10))), ('SPK', sh([(22, 8), (21, 8)])), ('SPK', sh([(22, 9), (21, 9), (20, 9), (20, 10)])),
    ('HPL', sh(vline(20, 11, 12))), ('HPR', sh(vline(22, 11, 12))),
]

# ---------- checks ----------
def check():
    errs = []
    used = {}
    pad_net = {}
    for c in comps:
        for (x, y, n, _) in c['pads']:
            if not (1 <= x <= W and 1 <= y <= H): errs.append(f'{c["ref"]} pad off board {x,y}')
            if (x, y) in used: errs.append(f'hole {x,y} used by {used[(x,y)]} and {c["ref"]}')
            used[(x, y)] = c['ref']
            if n != 'NC7': pad_net[(x, y)] = n
    for (x, y, n, lab, g) in wires:
        if (x, y) in used: errs.append(f'wire {lab} hole {x,y} already used by {used[(x,y)]}')
        used[(x, y)] = 'wire:' + lab
        pad_net[(x, y)] = n
    # union find over traces
    parent = {}
    def f(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def u(a, b): parent[f(a)] = f(b)
    trace_net = {}
    for net, pts in traces:
        for i, p in enumerate(pts):
            if not (1 <= p[0] <= W and 1 <= p[1] <= H): errs.append(f'trace off board {p}')
            if p in trace_net and trace_net[p] != net: errs.append(f'trace conflict at {p}: {trace_net[p]} vs {net}')
            trace_net[p] = net
            if p in pad_net and pad_net[p] != net: errs.append(f'trace {net} hits pad of net {pad_net[p]} at {p}')
            if i:
                q = pts[i - 1]
                if abs(p[0] - q[0]) + abs(p[1] - q[1]) != 1: errs.append(f'non-adjacent trace step {q}->{p}')
                u(p, q)
            else:
                f(p)
    # under-body trace pads are fine; but trace through a hole that is under a component body and has a lead? handled above
    groups = defaultdict(set)
    for p, n in pad_net.items():
        groups[n].add(f(p))
    for n, g in groups.items():
        if len(g) > 1: errs.append(f'net {n} split into {len(g)} islands')
    # each trace island single net
    isl = defaultdict(set)
    for p, n in list(pad_net.items()) + list(trace_net.items()):
        isl[f(p)].add(n)
    for k, s in isl.items():
        if len(s) > 1: errs.append(f'island mixes nets {s}')
    # body overlap (approx)
    def bbox(b):
        if b[0] == 'circle': return ('c', b[1], b[2], b[3])
        return ('r', b[1], b[2], b[3], b[4])
    def overlap(a, b):
        if a[0] == 'c' and b[0] == 'c':
            return math.hypot(a[1] - b[1], a[2] - b[2]) - (a[3] + b[3])
        def rr(z):
            if z[0] == 'c': return (z[1] - z[3], z[2] - z[3], z[1] + z[3], z[2] + z[3])
            return (z[1] - z[3] / 2, z[2] - z[4] / 2, z[1] + z[3] / 2, z[2] + z[4] / 2)
        A, B = rr(a), rr(b)
        dx = max(B[0] - A[2], A[0] - B[2]); dy = max(B[1] - A[3], A[1] - B[3])
        if dx < 0 and dy < 0: return max(dx, dy)
        return max(dx, dy)
    warns = []
    for i in range(len(comps)):
        for j in range(i + 1, len(comps)):
            o = overlap(bbox(comps[i]['body']), bbox(comps[j]['body']))
            if o < -0.12: warns.append(f'body overlap {comps[i]["ref"]}-{comps[j]["ref"]}: {o:.2f} pitch')
    # wire pad covered by a body?
    for (x, y, n, lab, g) in wires:
        for c in comps:
            b = c['body']
            if b[0] == 'circle' and c['kind'] == 'ecap' and math.hypot(x - b[1], y - b[2]) < b[3] - 0.1:
                warns.append(f'wire pad {lab} under body of {c["ref"]}')
    # adjacency of different-net used pads (info)
    adj = []
    for (x, y), n in pad_net.items():
        for dx, dy in ((1, 0), (0, 1)):
            q = (x + dx, y + dy)
            m = pad_net.get(q) or trace_net.get(q)
            if m and m != n and not (q in trace_net and trace_net[q] == n):
                adj.append(f'{(x,y)}{n} ~ {q}{m}')
    return errs, warns, adj, trace_net, pad_net

if __name__ == '__main__':
    e, w, a, _, _ = check()
    print('ERRORS:', *e, sep='\n  ') if e else print('no errors')
    print('WARN:', *w, sep='\n  ') if w else print('no body warnings')
    print('adjacent diff-net pads:', len(a))
    for s in a: print('  ', s)

```
