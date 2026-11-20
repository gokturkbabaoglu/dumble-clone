# 9 — Diğer amfilerle karşılaştırma

## 9a — Ton katları aynı grafikte (Micro-Cap) — `sim\09_KARSILASTIRMA\09a_ton_katlari.ckt`
**Çalıştırma yolu:** File → Open → dosya türü "SPICE (*.CKT)" → `09a_ton_katlari.ckt` → Analysis → AC → Run. Ayarlar ve grafikler dosyadaki `.AC` ve `.PRINT` satırlarından otomatik gelir; grafik sütunundaki P hücreleri 1 yapıldı.

**Model:**
- **Referans ton katları:** her birinin kendi kaynak empedansı ve 1 MΩ yükü var. Değerler aşağıdaki kaynaklardan.
  - Fender 5F6-A Bassman: 56k, 250p, 20n, 20n, Treble 250k, Bass 1M, Mid 25k. Kaynak 1.3k (katot izleyici).
  - Fender AB763 blackface: 100k, 250p, 100n, 47n, Treble 250k, Bass 250k, Mid sabit 6.8k. Kaynak 38k (anot çıkışı; yaklaşık).
  - Marshall JMP50 1987: 33k, 500p, 22n, 22n, Treble 220k, Bass 1M, Mid 25k. Kaynak 615 Ω.
- **Bizim ISF ağı:** `amfi_tasarim.cir`'den bire bir aktarıldı (C15 = 253p). LM386 çıkışından sürülüyor; Volume ½ ve TDA girişi (150k, datasheet tipik değeri) yük olarak dahil. ISF = 0 (US) ve ISF = 1 (UK).
- **Referans potlar:** %50 doğrusal konumda. Gerçek potlar logaritmik olduğu için düğme "5" konumu tam karşılık gelmez (yaklaşık).
- **Doğrulama:** aynı netlist Python ile ayrıca çözüldü; Micro-Cap'le ±0.1 dB içinde uyumlu. Bizim US eğrisi Analiz 2c'deki tam devre sonucuyla da aynı (1 kHz'de −16.8 dB).

| Ton katı | 100 Hz | 1 kHz | 5 kHz | Orta çukur | Çukur derinliği¹ | Tiz eğimi² |
|---|---|---|---|---|---|---|
| Fender 5F6-A | −4.3 | −12.9 | −6.1 | 710 Hz, −13.6 dB | −8.4 dB | −1.8 dB |
| Fender AB763 | −14.7 | −18.2 | −10.2 | 399 Hz, −24.7 dB | −12.2 dB | +4.4 dB |
| Marshall 1987 | −2.9 | −8.6 | −4.7 | 632 Hz, −9.5 dB | −5.8 dB | −1.8 dB |
| **Bizim US (ISF = 0)** | −14.6 | −16.8 | −8.0 | 390 Hz, −22.1 dB | −10.8 dB | +6.7 dB |
| **Bizim UK (ISF = 1)** | −15.2 | −17.3 | −12.3 | 428 Hz, −19.8 dB | −6.0 dB | +2.9 dB |

¹ Çukur seviyesi − (100 Hz + 5 kHz ortalaması). ² 5 kHz − 100 Hz.

**Yorum:**
- **US konumu ≈ Fender blackface (AB763).** Çukur frekansı (390 / 399 Hz), derinliği (−10.8 / −12.2 dB) ve tize doğru yükselen eğim neredeyse aynı. Bizimki biraz daha parlak (+2.3 dB tiz). Bu, "Fender" hedefinin tutturulduğunu gösteriyor.
- **UK konumu yarı yarıya Marshall.**
  - Çukur derinliği Marshall'a çok yakın (−6.0 / −5.8 dB).
  - Ama çukur 428 Hz'de; Marshall'da 632 Hz.
  - Bizimki hâlâ tize eğimli (+2.9 dB); Marshall düz (−1.8 dB).
  - Marshall'ın "orta frekansı öne çıkan" karakteri için çukurun ≈600 Hz'e çıkması gerekirdi. *(Öneri; uygulanmadı:)* UK kolundaki C19 ve C20 değerlerini küçültmek çukuru yukarı taşır; değerler simülasyonla seçilmeli (yaklaşık).
- **Kayıp:** bizim katın 1 kHz kaybı (≈ −17 dB) AB763 ile aynı sınıfta. Bassman'dan ≈4 dB, Marshall'dan ≈8 dB daha fazla. LM386'nın ≈32 dB kazancı bunu rahatça karşılıyor.
- **ISF'nin US ↔ UK geçişi** gerçek bir Fender ↔ Marshall farkından daha dar. Esas olarak tiz değişiyor, orta çukurun yeri pek değişmiyor (Analiz 2c ile tutarlı).

## 9b — Kazanç yapısı ve güç karşılaştırması
Bizim değerler simülasyondan, diğerleri kaynaklardan. Sayısal karşılaştırmalar yaklaşık.

| | Bizim amfi | Fender 5F1 Champ | Dumble ODS | Smokey | Little Gem | Ruby |
|---|---|---|---|---|---|---|
| Kazanç katları | JFET (×3.1–×10.8, DRIVE) → LM386 (×39) → ton katı → TDA2003 (×100) | 12AX7, iki triyot kat → 6V6 | Temiz: kat → ton katı → kat; OD'de +2 triyot (toplam 4 kat, kaskad) | Yalnız LM386 (×200 sabit) | LM386, gain 26–200 (pot) | JFET tampon (×1) → LM386 |
| Ton kontrolü | ISF (US↔UK sabit ağlar) + Dark/Bright | Yok (tek Volume) | 3 bant FMV; Rock/Jazz, Bright, Deep anahtarları | Yok | Yok | Yok |
| Kırpılma | LM386 (C9/DRIVE ile erken); tam güçte TDA ile birlikte | Ön kat + 6V6 (güç katı kırpması) | OD katlarında kaskad kırpma | LM386 | LM386 | LM386 |
| Güç | ≈1.3 W temiz, ≈2.4 W max, 4 Ω (sim) | ≈5 W | 50–100 W sınıfı (yaklaşık) | ≈0.5 W (9 V) | ≈0.5 W | ≈0.5–1 W |
| Giriş empedansı | 1.03 MΩ | ≈1 MΩ | ≈1 MΩ | düşük (≈50k, yaklaşık) | düşük | yüksek (1.5 MΩ, JFET) |

**Benzerlikler ve farklar:**
- **5F1 Champ ile:** 5F1'de ilk triyotun katodu bypass edilmemiş, bu yüzden kazancı düşük. Bu, bizim C9'suz/DRIVE solda olan durumumuzun tam karşılığı. Champ'te hiç ton kontrolü yok; bizde var.
- **Dumble ODS ile:** ODS'de temiz kanal, ton katından sonra kaskad bağlanan iki ek triyotla overdrive'a geçer. Bizde DRIVE potu tek bir katın kazancını büyütüyor: "temiz kanalın kazancını artırmak"a benzer, ayrı bir OD kanalı değil. ODS'de ton katı kırpılmadan önce; bizde ise LM386 kırptıktan sonra ton katı geliyor. Bu, bozulmuş sesi şekillendiren Marshall/HRM tarzı bir yerleşim. ODS'nin FET girişi bizim JFET katımıza benziyor.
- **LM386 amfileriyle:** Smokey, Little Gem ve Ruby'de LM386 hem ön kat hem güç katı. Bizde LM386 yalnızca kazanç katı; gücü ayrı bir TDA2003 veriyor. Bu ≈3–5 kat daha fazla güç ve ayrı bir ton katı demek. Bizim JFET katı da Ruby'deki gibi yalnızca tampon değil, kazançlı.

## 9c — Güçlü ve zayıf yönler (simülasyona göre)
| Güçlü yönler | Zayıf yönler |
|---|---|
| Yüksek giriş empedansı (1 MΩ): manyetiği yüklemiyor | TDA katının bas kesimi 151 Hz (C23/R26): bas zayıf |
| US konumu Fender blackface ton eğrisine çok yakın | UK konumu tam Marshall değil: çukur 428 Hz (Marshall ≈630 Hz) |
| DRIVE potu: temizden overdrive'a tek düğmeyle geniş aralık, DC noktasını bozmadan | 3–4 kHz tepe + geniş bantlı hoparlör → sert ve cızırtılı tiz riski (yaklaşık) |
| Temiz bölgede bozulma çoğunlukla 2. harmonik (sıcak) | Tam güçte LM386 ve TDA aynı anda sert kırpıyor (3. harmonik) |
| SNR ≈80–83 dB; ön katlarda çok iyi besleme filtrelemesi | Hışırtının çoğu güç katından (TDA + R24); TDA hattı besleme dalgalanmasına açık (−31 dB @100 Hz) |
| TDA kararlı (tepe yok, 100 kHz bant), çıkış empedansı çok düşük | Maksimum güç sim'de ≈2.4 W (gerçekte ölçülmeli); kulaklık seviyesi düşük (≈0.16 mW) |
| LM386 amfilerinden ≈3–5 kat güç; ayrı ton katı | ISF US↔UK farkı dar; esas olarak tizi değiştiriyor |

## Kaynaklar
- Fender 5F6-A ton katı değerleri ve Marshall JMP50 1987 değişiklikleri: [AMP Books – Bassman tone stack](https://ampbooks.com/mobile/classic-circuits/bassman-tonestack/), [AMP Books – JMP50 1987](https://ampbooks.com/mobile/classic-circuits/JMP50-1987)
- 5F6-A treble/bass yapısı: [Silicon Chip – Fender Bassman (Nisan 2024)](https://www.siliconchip.com.au/Issue/SC/2024/April/Fender+Bassman+Guitar+Amp)
- 5F6-A kaynak empedansı (1.3k): [Rob Robinette – How the TMB Tone Stack Works](https://robrobinette.com/How_The_TMB_Tone_Stack_Works.htm)
- AB763 ton kondansatörleri: [Premier Guitar – Ask Amp Man](https://www.premierguitar.com/gear/reviews/ask-amp-man-can-my-fender-amp-sound-more-like-a-marshall), 100k slope: [Ampgarage forumu](https://ampgarage.com:443/forum/viewtopic.php?p=459781)
- 5F1 Champ: [Wikipedia – Fender Champ](https://wikipedia.com/wiki/Fender_Vibro_Champ), [Fender Champ şemaları (bypass'sız ilk kat)](https://vero-p2p.blogspot.com/2024/07/fender-champs-schematics-layouts.html)
- Dumble ODS: [Guitar Player – '77 ODS](https://www.guitarplayer.com/gear/examining-a-77-dumble-overdrive-special-1x12), [Premier Guitar – ODS Reverb](https://www.premierguitar.com/gear/amps/dumble-overdrive-special-reverb), [Wikipedia – Dumble Amplifiers](https://www.wikipedia.org/wiki/Howard_Dumble)
- LM386 amfileri: [ElectroSmash – Smokey](https://electrosmash.com/smokey-amp-analysis), [ElectroSmash – Little Gem](https://electrosmash.com/little-gem-analysis), [ElectroSmash – Ruby](https://electrosmash.com/ruby-amp-analysis), [runoffgroove – Ruby](https://runoffgroove.com/ruby.html), [Rob Robinette – How the Ruby Amp Works](https://robrobinette.com/How_the_Ruby_Amp_Works.htm)
