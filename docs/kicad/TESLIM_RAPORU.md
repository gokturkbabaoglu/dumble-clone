# Teslim raporu — KiCad kartı (12 V gitar amfisi)

Tarih: 15 Kasım 2026 · Proje: `kicad/amfi/amfi.kicad_pro` (KiCad 10)

## Ne teslim edildi

Amfinin baskı devresi KiCad 10'da sıfırdan yeniden tasarlandı. Devre değişmedi: BF245B JFET → LM386 → ISF ton (US/UK) → Volume → TDA2003 → 4 Ω hoparlör / 3,5 mm kulaklık, 12 V besleme.

| Konu | Sonuç |
|---|---|
| Kart boyutu | **185 × 96 mm** (v3: 185 × 114,3 mm) |
| Yapım | Tek yüz, yalnız alt bakır, via yok, toner transfer |
| GND | Alt katın tamamında dolgu; padler dolguya doğrudan bağlı |
| Tel köprü | **2 adet**: K1 (D2 yanı) ve K2 (C3 yanı), ikisi de 5,08 mm, düz, parça üstünden geçmiyor, ikisi de GND |
| Bağlantı | KiCad'de bağlanmamış uç yok |
| Kurallar | Bakır–bakır ≥ 0,5 mm; yol 1,0 mm (sinyal), 1,3 mm (besleme/çıkış), dar geçişlerde en az 0,5 mm |
| Vida delikleri | 5 × M3: arka kenarda 3, ön tarafta 2 (MH4, MH5 — yeni) |
| Ön panel sırası | v3 ile aynı: J1, RV4, RV1, SW1, RV2, RV3, J2, LED, güç anahtarı |

### Parazit ölçütleri

| Ölçüt | Değer |
|---|---|
| Giriş yolu (J1 → R5 → Q1 gate) | 33 mm |
| Girişe en yakın güç/çıkış yolu | 110 mm |
| Hoparlör akım döngüsü alanı | 374 mm² |
| TDA2003 giriş (TIN) yolu | 55 mm |

Giriş katı solda, güç katı sağ arkada, besleme sağ kenarda.

### Nasıl seçildi

Freerouting ile 185 mm genişlikte, 114 mm'den 84 mm'ye kadar yaklaşık 150 yerleşim yönlendirildi. 96 mm, tamamen yönlendirilen ve en az tel köprü isteyen en küçük karttı (yerleşim `K4@96#11`).

## Dosyalar

| Dosya | Ne için |
|---|---|
| `kicad/amfi/` | KiCad projesi (şema, kart, kütüphane, kurallar) |
| `docs/kicad/toner_alt_bakir_1e1_A4.pdf` | Toner transfer: alt bakır, A4, 1:1 (kalın yollu sürüm) |
| `docs/kicad/parca_yerlesimi_A4.pdf` | Parça yerleşimi (parça yüzünden bakış), A4 |
| `docs/kicad/lazer/` | Lazer için aynalı PNG/SVG, DXF |
| `kicad/*.py` | Üretim, yerleşim, toplu yönlendirme, analiz, köprü ve PDF betikleri |

Aynı proje ve PDF'ler bilgisayarda `Masaüstü\Yeni klasör (3)\kicad_amfi\` (PDF'ler `cikti\` içinde) klasöründe de var. PDF'ler KiCad'in kendi çizim işleviyle (`kicad/cikti.py`) üretildi.

### Parça adı değişiklikleri

C15a → C15, C15b → C26, R20a → R20, R20b → R30, R22a → R22, R22b → R31. KiCad'de ayrıca CB → CB1, CD → CD1, P_SWB/P_SWC/P_SWD → P1/P2/P3, P_PW1/P_PW2 → P4/P5. Yeni parçalar: MH4, MH5 (vida), K1, K2 (tel köprü). README ve `tools/` içindeki eski adlar da düzeltildi.

## Yapım adımları

1. **Baskı:** Toner PDF'ini %100 ölçekle bas ("sayfaya sığdır" kapalı). Kart genişliği cetvelle 185 mm çıkmalı. PDF A3 sayfadır, kart sol üst köşededir; A4 yazıcıda kart kesilebilir, gerekirse A4'e ortalanmış PDF üretilmeli.
2. **Yön:** Toner PDF'i aynalanmadan basılır, kağıt yüzüstü bakıra konur. Parça yerleşimi PDF'i yalnız bakıp yerleştirmek içindir.
3. **Kesim:** Ön kenarda bakır kenara 0,5 mm yaklaşıyor. Kartı biraz geniş kes, ön kenarı çizgiye kadar yavaşça eğele.
4. **Delme:**

   | Çap | Kaç delik |
   |---|---|
   | 0,7–0,9 mm | 134 |
   | 1,0–1,3 mm | 36 |
   | 1,6 mm | 5 |
   | 2,3 mm | 3 |
   | 3,2 mm | 5 (M3 vida) |

5. **Lehim öncesi kontrol:** GND ile +12 V arasında kısa devre olmamalı; ince yollarda kopukluk var mı bak.
6. **Tel köprüler:** K1 ve K2'yi parça yüzünden tak. Takılmazsa iki küçük GND bölgesi ana GND'ye bağlanmaz.
7. **Lehim ve ilk çalıştırma.**

## Açık kalanlar

- Kart henüz basılmadı, devre denenmedi.
- A4 sayfaya ortalanmış PDF istenirse üretilecek.
- v2/v3 bölümleri README'de arşiv olarak duruyor.

## Güncelleme — 18 Kasım: kalın yollar

Yerleşim ve kart boyu (185 × 96 mm) aynı. Yollar 0,5 mm aralık korunarak sığdığı kadar kalınlaştırıldı (uzunluğun ~%60'ı ≥ 1,5 mm, ~%40'ı sıkışık bölgelerde 1,0–1,5 mm). Padler büyütüldü. KiCad DRC (konsol): bağlanmamış öğe yok; GND dolgusunda 0,47 mm'lik iki dar boğaz uyarısı. Kullanıcı kendi DRC'sinde bir GND dolgu parçasının ana dolguya bağlanmadığını bildirdi — açık iş.

Aynı kartı 1,5–2 mm yollarla Freerouting'le yeniden yönlendirme denendi (~400 yerleşim, 96–150 mm derinlik): hiçbiri tam yönlendirilemedi; bu yoldan vazgeçildi.
