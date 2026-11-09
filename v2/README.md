# Kart v2 — 12 V gitar amfisi (son durum)

Revizyon 5 devresinin yeni kartı. Elde olan parçalara göre çizildi. Tek yüzlü, 165,1 × 114,3 mm, GND dolgulu, 1,27 mm ızgara. Potlar, jaklar, LED ve anahtarlar ön kenarda dizili.

**Durum:** Kart çizildi ve doğrulandı: kopuk ya da kısa devre yok, en dar aralık 0,5 mm, 7 tel köprü (K1–K7). Parçalar alındı (A potlar hariç). Kart henüz basılmadı. **Aşındırmadan önce:** devir raporundaki "Sorulacaklar" listesindeki ölçüler alınmalı ve 1:1 baskı üzerinde parçalar denenmeli.

**Devir raporu (güncel parça listesi, muadiller, sorulacak ölçüler):** https://claude.ai/artifact/CqNFPdVpvteivkdLXzBCgm

| Dosya | İçerik |
|---|---|
| `images/1_devre_semasi.png` | Devre şeması |
| `images/2_pcb_on_yuz.png` | Parça yüzü |
| `images/3_pcb_arka_yuz.png` | Bakır yüzü |
| `images/4_kablolama.png` | Panel kablolaması, anahtarların arka görünüşü, bükümlü teller |
| `docs/6_toner_transfer_1e1.pdf` | Toner transfer için 1:1 baskı |
| `tools/` | Tasarım araçları (aşağıda) |
| `../parca-gorselleri/` | Parçaların ürün görselleri ve çizimleri |

## Ön kenar yerleşimi (sol kenardan, mm)

J1 giriş 12 · RV1 Gain 36 · SW1 57 · RV2 ISF 79 · RV3 Volume 103 · J2 kulaklık 125 · D2 LED 140 · SW2 güç 155

## Tel köprüler

K1 GAINW · K2 V12 · K3–K7 GND. **K7 LM386 soketinin altından geçer, soketten önce lehimlenmeli.**

## Takılırken tasarımdan farklı olanlar (★)

- **R5 33k → 22k + 10k seri**, ters U şeklinde R5 deliklerine. Tek 33k R18'e gider.
- **R20 = 120k + 10k, R22 = 22k + 2,2k**: kart bu çiftlere göre çizildi.
- **C15a ★ = 330p (331), C15b ★ boş.** Tasarım 220p + 33p idi. US yığınında tiz biraz artar. 220p bulunursa geri dönülür.
- **C22 ★ = 1 µF elektrolitik**: + ucu TDA2003 tarafına (TIN). Kartta 5 mm ve 7,5 mm iki delik var.
- **Potlar B**: Gain için R7 15k (slider–GND) takılır.
- **Sigorta 1 A normal**: açılışta atarsa 1,6–2 A gecikmeli.

## Araçlar

Python 3 + numpy, scipy, Pillow, matplotlib. Komutlar `tools/` içinde çalıştırılır; çıktılar `out/` klasörüne yazılır.

- `params.py`: parça ölçüleri ve ön kenar konumları. **Ölçü değişince yalnızca burası düzeltilir.**
- `design2.py`: netlist ve ayak izleri.
- `place2.py`, `rsa2.py`: yerleşim (benzetimli tavlama).
- `route2.py`: yol çizici (Lee/Dijkstra, tel köprülü).
- `final2.py c121.json <tohum sayısı>`: son yönlendirme, GND dolgusu, doğrulama → `final_geom.pkl`.
- `draw_pcb2.py final_geom.pkl [çıktı klasörü]`: kart görselleri ve toner PDF'i.
- `schem2.py`, `wiring2.py`: şema ve kablolama çizimleri.
- `c121.json`: son yerleşim. `final_geom.pkl`: son geometri.
