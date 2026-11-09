# 12 V Gitar Amfisi — Proje Dosyası (Rev 5)

## Kararlar

- Besleme 12 V'u geçmeyecek; 12 V / 2 A adaptör.
- Kontroller: Volume, Gain, ISF + Dark/Normal/Bright anahtarı. Kulaklık çıkışı 3,5 mm, kesicili jak (PJ-324M).
- Aktif parçalar: tek JFET (BF245B), LM386 (gain/overdrive katı), TDA2003 (güç katı).
- Hoparlör: 4 Ω, 6,5" full range kağıt koni. Full range hoparlörün vızıltısını azaltmak için güç katı önünde ≈6 kHz alçak geçiren.
- Kart: tek yüzlü baskı devre (pertinaksta ISF bölümü çok fazla atlama gerektiriyordu). Pot/jak/anahtarlar ön panelde, kabloyla bağlanır.
- Kutu ve pot düğmeleri 3D baskı (PETG önerilir; TDA soğutucusu duvara değmemeli).

## Devre özeti

| Blok | Değerler |
|---|---|
| JFET katı | R5 33k gate stopper, R6 1M, R4 6,8k drain, TR1 10k çok turlu source trimpotu (drain ≈ 7 V'a ayarla), C9 22µ isteğe bağlı (daha fazla kazanç), C10 100n çıkış |
| Gain | B100K + R7 15k (orta uç–GND) ya da A100K (R7 takılmaz). SW1: Bright = 470p pot uç3–orta, Dark = 3,3n orta–GND |
| LM386 | R8 1,2k + C11 10µ (pin 1–8, kazanç ≈ 38), C12 10µ pin 7, Zobel R9 10 Ω + C13 47n, C14 4,7µ çıkış, R10 100k bleed |
| US yığını | R11 100k, C15 250p, C16 100n, C17 47n, R13 100k, R14 150k, R15 120k, R16 6,8k |
| UK yığını | R12 10k / R17 4,7k bölücü, R18 33k, C18 470p, C19 22n, C20 22n, R19 91k, R20 130k, R21 470k, R22 24k |
| ISF / Volume | ISF B250K (uç1 = US, uç3 = UK), Volume B500K (B pot) ya da A100K |
| Volume sonrası | R23 47k / R24 10k bölücü, C21 3,3n, C22 1µ film |
| TDA2003 | R25 220 Ω, R26 2,2 Ω + C23 470µ (kazanç ≈ 40 dB), Zobel R27 1 Ω + C24 100n, C6 100n + C7 1000µ besleme, C25 2200µ çıkış |
| Kulaklık | R28 10 Ω (şönt, ÇIKIŞ–sleeve), R29 330 Ω (sleeve–GND), hoparlör jakın NC kontağından |
| Besleme | F1 1 A yavaş, D1 1N5822, C1 2200µ + C2 100n, R1 100 Ω → V2 (C3 220µ, C8 100µ, C4 100n), R2 1k → V3 (C5 100µ), R3 2,2k LED |

Hesaplanan ISF davranışı: 1 kHz'de iki uç arasında ≈1–2 dB seviye farkı; US ucu 400 Hz'de ≈5 dB daha derin oyuk, 4 kHz'de ≈6 dB daha parlak.

## Parça listesi (alınacaklar)

**Yarı iletkenler:** TDA2003, 1N5822

**Potlar/anahtarlar:** B250K (ISF), 10k çok turlu trimpot, SPDT ON-OFF-ON mini toggle, SPST güç anahtarı. A pot bulunursa A100K ×2 (Gain + Volume); bulunmazsa eldeki B100K (+15k) ve B500K.

**Dirençler (¼ W):**

| Değer | Adet | 4 bant | 5 bant |
|---|---|---|---|
| 1 Ω | 1 | kahve-siyah-altın-altın | kahve-siyah-siyah-gümüş-kahve |
| 2,2 Ω | 1 | kırmızı-kırmızı-altın-altın | kırmızı-kırmızı-siyah-gümüş-kahve |
| 220 Ω | 1 | kırmızı-kırmızı-kahve-altın | kırmızı-kırmızı-siyah-siyah-kahve |
| 330 Ω | 1 | turuncu-turuncu-kahve-altın | turuncu-turuncu-siyah-siyah-kahve |
| 1,2k | 1 | kahve-kırmızı-kırmızı-altın | kahve-kırmızı-siyah-kahve-kahve |
| 4,7k | 1 | sarı-mor-kırmızı-altın | sarı-mor-siyah-kahve-kahve |
| 6,8k | 2 | mavi-gri-kırmızı-altın | mavi-gri-siyah-kahve-kahve |
| 24k | 1 | kırmızı-sarı-turuncu-altın | kırmızı-sarı-siyah-kırmızı-kahve |
| 47k | 1 | sarı-mor-turuncu-altın | sarı-mor-siyah-kırmızı-kahve |
| 91k | 1 | beyaz-kahve-turuncu-altın | beyaz-kahve-siyah-kırmızı-kahve |
| 100k | 3 | kahve-siyah-sarı-altın | kahve-siyah-siyah-turuncu-kahve |
| 120k | 1 | kahve-kırmızı-sarı-altın | kahve-kırmızı-siyah-turuncu-kahve |
| 130k | 1 | kahve-turuncu-sarı-altın | kahve-turuncu-siyah-turuncu-kahve |
| 150k | 1 | kahve-yeşil-sarı-altın | kahve-yeşil-siyah-turuncu-kahve |
| 470k | 1 | sarı-mor-sarı-altın | sarı-mor-siyah-turuncu-kahve |

**Film/seramik:** 250 pF (221 + 330 paralel ya da 271), 470 pF ×2 (471), 3,3 nF ×2 (332), 1 µF film (105)

**Elektrolitik (≥16 V):** 470 µF, 1000 µF, 2200 µF ×2, 22 µF (isteğe bağlı)

**Diğer:** sigorta yuvası + 1 A yavaş sigorta, TDA2003 soğutucusu + termal macun + vida, tek yüzlü bakır plaket (≥115 × 80 mm), aşındırma sıvısı, 0,8 / 1,0 / 1,2 mm matkap uçları, izoleli tek damarlı köprü teli, hoparlör kablosu.

**Eldekiler:** BF245B, LM386, sarı LED, B500K, B100K, 6,35 mm giriş jakı, PJ-324M, DC jak, 12 V adaptör, 8 bacaklı DIP soket; dirençler 10 Ω ×2, 100 Ω, 1k, 2,2k, 10k ×2, 15k, 33k ×2, 1M; kondansatörler 47n ×2 (473J100), 22n ×2 (223J100), 100n ×8 (104K63), 220µ/25 V, 4,7µ/16 V, 10µ ×2, 100µ/100 V ×2.

Eşdeğerler ve kabul aralıkları için yazdırılabilir listeye bak: [12V_Gitar_Amfisi_Alisveris_Listesi.pdf](12V_Gitar_Amfisi_Alisveris_Listesi.pdf).

## Kart notları

- 112 × 79 mm, 4 köşede 3,2 mm montaj deliği. TDA2003 soğutucusu kartın arka kenarından dışarı taşar; TDA'nın tabı GND'dir, izolasyon gerekmez.
- Tel köprüler (parça tarafı, izoleli tel): J1 TNEG 10 mm (R25 bacağının 1,3 mm yanından geçer), J2 TOUT 11 mm, J3 SPK 11 mm, J4 V12 10 mm.
- Varsayılan bacak aralıkları: dirençler 10,16 mm; film kondansatörler 5 mm; küçük elektrolitikler 2,5 mm; 220 µF 3,8 mm; 100/470/1000/2200 µF 5 mm; 1N5822 15,2 mm; TO-92 ve trimpot 2,54 mm. Delmeden önce kendi parçalarınla 1:1 çıktı üzerinde kontrol et.
- Delikler: küçük parçalar 0,8–0,9 mm; büyük elektrolitik, diyot, TDA ve kablo noktaları 1,0–1,2 mm.
- Kablo noktaları 5,08 mm aralıklı; istenirse klemens takılabilir.

## Kablolama ve topraklama

- Burgulu gruplar: giriş (uç + şase), Gain (3 tel), ISF (2 tel), Volume (2 tel), kulaklık (ÇIKIŞ + sleeve), hoparlör (NC → + ve −), güç anahtarı (giden + dönen), LED.
- DC jak gövdesi karta sadece "GND (DC jak)" noktasından bağlanır. Giriş jakının şasesi sadece "GİRİŞ şase" noktasına gider.
- Pot gövdeleri isteğe bağlı olarak tek bir telle VOL 1/GND'ye bağlanabilir. İç yüzeye bakır bant konursa tek telle "GND (DC jak)" noktasına bağlanır.
- Besleme ve hoparlör kablolarını giriş ve pot kablolarından en az 2–3 cm uzakta geçir.

## Montaj ve ilk çalıştırma

1. Kartı aşındırıp del; önce köprüleri, sonra alçak parçaları (dirençler), en son elektrolitikleri ve TDA2003'ü lehimle. LM386'yı sokete tak (ilk testte takma).
2. BF245B: diyot kademesinde gate, diğer iki bacağa karşı diyot gibi ölçülür; G ucunu karttaki G pedine getir.
3. LM386 takılı değilken güç ver: TDA çıkışında (C25 öncesi) ≈ 6 V, hoparlörde uğultu olmamalı, TDA ısınmamalı.
4. Gücü kes, LM386'yı tak: pin 5 ≈ 6 V.
5. TR1 ile JFET drain gerilimini ≈ 7 V'a ayarla.
6. İlk sesli testi volume kısıkken yap.
