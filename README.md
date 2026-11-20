# 12 V gitar amfisi — BF245B JFET + LM386 + TDA2003, ISF ton kontrolü

12 V ile çalışan, 4 Ω 6,5" full range hoparlör süren küçük bir pratik amfisi. Drive, Gain, ISF (US ↔ UK karakter), Volume kontrolleri, Dark/Normal/Bright anahtarı ve kesicili 3,5 mm kulaklık çıkışı var. Tek yüzlü, ev yapımı baskı devre; pot, jak ve LED kartın ön kenarına lehimli.

> Bu repo yalnızca bu 12 V JFET/op-amp amfisi içindir. Lambalı 5F1 amfi projesi ayrıdır.

## Durum (20 Kasım 2026)

- **Güncel kart: kart v5** — [`guncel/kicad/`](guncel/kicad/) (KiCad 10, proje `amfi_yeni.kicad_pro`). KiCad'de sıfırdan yeni tasarım: tellerle çizilmiş şema (ERC 0 hata / 0 uyarı), büyük padli ayak izi kütüphanesi (lazerle boya yakma + asit için), 185 × 96 mm tek yüz (yalnız alt bakır), ince yollar (0,4 mm, aralık 0,4 mm).
- **Açık işler:** 2 bağlantı henüz çizilmedi (U2.4–TOUT, R22–R31). Yollar KiCad'de elle kalınlaştırılıp düzenlenecek.
- Parçalar alındı. Kart henüz basılmadı, devre henüz denenmedi.
- Devre (netlist) Rev 5 + RV4 DRIVE; simülasyonları [`guncel/sim/`](guncel/sim/README.md).

## Klasörler

| Klasör | İçerik |
|---|---|
| [`guncel/kicad/`](guncel/kicad/) | **Güncel KiCad projesi (kart v5):** şema, kart, ayak izi kütüphanesi `amfi_yeni.pretty`, üretim/denetim betikleri |
| [`guncel/sim/`](guncel/sim/README.md) | Micro-Cap 12 simülasyonları: DC, AC, transient, THD, gürültü, empedans/kararlılık, C9/RV4, diğer amfilerle karşılaştırma |
| [`guncel/parca-gorselleri/`](guncel/parca-gorselleri/) | Jak, anahtar ve soğutucu ürün görselleri/ölçü çizimleri |
| [`eski/`](eski/README.md) | Önceki kartlar (v1, v2, v3 taslağı, v4 KiCad/Freerouting) ve araçları — kullanılmıyor, arşiv |

## Kontroller

| Kontrol | Parça | Ne yapar |
|---|---|---|
| Drive | RV4 B2.2K lineer + C9 22µ | JFET katının kazancı: ilk %70 temiz–sıcak, son %30 crunch–overdrive |
| Gain | B100K + R7 15k | LM386 katına giren sinyal; düşükte temiz, yüksekte crunch |
| SW1 | Mavi ON-OFF-ON | Yukarı Bright (470p) / orta Normal / aşağı Dark (3,3n) |
| ISF | B250K | Bir uç US (Fender tipi), öbür uç UK (Marshall tipi) |
| Volume | B500K | Güç katına giden seviye |
| Kulaklık | PJ-324M (kesicili) | Fiş takılınca hoparlör susar; L-pad (10 Ω / 330 Ω) |
| Güç | Kırmızı ON-ON, 6 bacak | Yukarı = açık |

- **Sinyal yolu:** gitar → Q1 BF245B → Gain + Dark/Bright → LM386 (≈38×) → ISF (iki sabit ton yığını arasında geçiş) → Volume → 47k/10k bölücü + ≈6 kHz alçak geçiren → TDA2003 (≈40 dB) → hoparlör / kulaklık
- **Besleme:** 12 V / 2 A adaptör → panel DC jak → TB1 → 1 A sigorta → güç anahtarı → 1N5822 → V12; RC filtrelerle LM386 (100 Ω) ve JFET (1k) beslemeleri ayrılır

## Kablolama

Kabloyla bağlanan parçalar: SW1 (Dark/Normal/Bright), güç anahtarı, panel DC jak ve hoparlör.

- **SW1** → P1 (B), P2 (orta), P3 (A). Bacaklar dikey takılır: üst = A (Dark), orta = ortak, alt = B (Bright). Kol yukarı = Bright.
- **Güç anahtarı** → P4 / P5: tek sütunun orta ve alt bacakları kullanılır (orta = sigortadan sonra, alt = 1N5822'ye). Kol yukarı = açık.
- **DC jak** → TB1, **hoparlör** → TB2 (kulaklık jakının kesici kontağından gelir). Hoparlör kabloları hoparlörde lehimlenir, kablolar burgulanır.

## Parça listesi (takılacak haliyle)

★ = tasarımdan farklı; çalışmayı bozmadığı için böyle bırakıldı (notlar aşağıda).

**Dirençler**

| Değer | Adet | Referanslar |
|---|---|---|
| 1 Ω | 1 | R27 |
| 2,2 Ω | 1 | R26 |
| 10 Ω | 2 | R9, R28 |
| 100 Ω | 1 | R1 |
| 220 Ω | 1 | R25 |
| 330 Ω | 1 | R29 |
| 1k | 1 | R2 |
| 1,2k | 1 | R8 |
| 2,2k | 2 | R3, R31 |
| 4,7k | 1 | R17 |
| 6,8k | 2 | R4, R16 |
| 10k | 4 | R12, R24, R30, R5b ★ |
| 15k | 1 | R7 |
| 22k | 2 | R22, R5a ★ |
| 33k | 1 | R18 |
| 47k | 1 | R23 |
| 91k | 1 | R19 |
| 100k | 3 | R10, R11, R13 |
| 120k | 2 | R15, R20 |
| 150k | 1 | R14 |
| 470k | 1 | R21 |
| 1M | 1 | R6 |

**Kondansatörler** (elektrolitiklerin hepsi yeni alındı, 25 V)

| Değer | Tür | Adet | Referanslar |
|---|---|---|---|
| 220p (221) | seramik | 1 | C15 |
| 33p | seramik | 1 | C26 |
| 470p | seramik | 2 | CB1, C18 |
| 3,3n | film | 2 | CD1, C21 |
| 22n | film | 2 | C19, C20 |
| 47n | film | 2 | C13, C17 |
| 100n | film | 6 | C2, C4, C6, C10, C16, C24 |
| 1µ | elektrolitik | 1 | C22 ★ |
| 4,7µ | elektrolitik | 1 | C14 |
| 10µ | elektrolitik | 2 | C11, C12 |
| 22µ | elektrolitik | 1 | C9 ★ (RV4 ile seri) |
| 100µ | elektrolitik | 2 | C5, C8 |
| 220µ | elektrolitik | 1 | C3 |
| 470µ | elektrolitik | 1 | C23 |
| 1000µ | elektrolitik | 1 | C7 |
| 2200µ | elektrolitik | 2 | C1, C25 |

**Diğer**

| Parça | Adet | Referans |
|---|---|---|
| BF245B | 1 | Q1 |
| LM386 + DIP-8 soket | 1 | U1 |
| TDA2003 + klips soğutucu | 1 | U2 (soğutucu kartın arka kenarından taşar) |
| 1N5822 | 1 | D1 |
| Sarı LED (+ R3 2,2k) | 1 | D2 |
| 10k trimer | 1 | TR1 (drain ≈7 V'a ayarlanır) |
| B100K / B250K / B500K pot, 16 mm (WH148 tipi) | 1/1/1 | RV1 / RV2 / RV3 |
| B2.2K pot (lineer) | 1 | RV4 ★ DRIVE (C9 ile seri) |
| 6,35 mm mono jak | 1 | J1 |
| PJ-324M | 1 | J2 |
| Vidalı klemens, 2'li | 2 | TB1, TB2 |
| Sigorta yuvası + 1 A sigorta | 1 | F1 ★ |
| Mavi ON-OFF-ON anahtar | 1 | SW1 |
| Kırmızı ON-ON 6 bacaklı anahtar | 1 | Güç |
| Panel DC jak, 3 uçlu | 1 | — |
| Bakır plaket 20 × 20 cm | 1 | — |
| M3 vida / mesafe | 5 | MH1–MH5 |
| Tel köprü (0,6 mm bakır tel) | 1 | JP1 — 5,08 mm (giriş susturma köprüsü) |
| 4 Ω 6,5" full range kâğıt hoparlör | 1 | Kablolar hoparlörün üzerinde lehimlenir, karta TB2 ile bağlanır |
| 12 V / 2 A adaptör | 1 | — |
| Kutu ve pot düğmeleri | — | 3D baskı |

**Düzenleme notları**

- **R5 33k → 22k + 10k seri ★**: ters U şeklinde R5 deliklerine. Tek 33k R18'e gider.
- **R20 + R30 = 120k + 10k, R22 + R31 = 22k + 2,2k**: kartta ayrı parçalar.
- **C22 ★ = 1 µF elektrolitik**: + ucu TDA2003 tarafına (TIN); kartta Ø5 mm / 2,0 mm elektrolitik yeri.
- **C9 + RV4 DRIVE ★**: C9 22 µF artık takılıyor ve RV4 ile seri bağlanıyor (bu seri kol TR1'e paralel): SRC → C9 (+ ucu SRC'de) → RV4 B2.2K (değişken direnç; uç + slider birleşik) → GND. RV4 yalnızca AC kazancı ayarlar, TR1 ile kurulan DC çalışma noktası (drain ≈ 7 V) değişmez. Simülasyon: JFET kazancı ×3.1 (tam sol, normal çalmada temiz) → ×10.8 (tam sağ, overdrive); düğmenin ilk %70'i temiz–sıcak, son %30'u crunch–overdrive. B2.2K pot alındı. Saat yönünde direnç azalacak şekilde bağlanır. Kartta ön kenarda, J1 ile Gain arasında.
- **Potlar B ★**: A pot alınmadı; Gain için R7 15k (slider–GND) takılır.
- **Sigorta ★ 1 A normal (hızlı)**: tasarımda yavaş atan öngörülmüştü. Açılışta atarsa 1–2 A yavaş atan sigortaya geç.
- **Elektrolitikler**: hepsi yeni, 25 V (en az 16 V gerekli; görünüm aynı olsun diye hepsi yenilendi).

**Montaj ve kart yapımı malzemeleri**

- TR1: 10k çok turlu trimer, 3296W tipi.
- Elektrolitikler 105 °C, aynı seri; C1, C7, C25 için mümkünse low ESR.
- TDA2003 için termal macun, M3 vida/somun; kartı kutuya sabitlemek için M3 aralayıcılar.
- Hoparlör kablosu 0,5–0,75 mm² ikili (≈50 cm); DC jak kablosu 0,5 mm² kırmızı/siyah (≈30 cm, burgulanacak); köprü teli izoleli tek damar (≈1 m); makaron; kablo bağı.
- Kart yapımı: perklorür ya da sodyum persülfat, parlak kâğıt (toner transfer), aseton/tiner, matkap uçları 0,8 / 1,0 / 1,2 / 1,5 mm ve montaj delikleri için 3,2 mm.

## Eski rapor ve bağlantılar

- Eski devir raporları (v2/v3 ve v4 dönemi) ve eski kartın teslim raporu: [`eski/`](eski/README.md).
