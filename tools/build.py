from render import schematic_svg, board_svg
from wiring import wiring_svg
from layout import wires

GC = {'J1': '#c2410c', 'S2': '#7c3aed', 'VOL': '#0369a1', 'GAIN': '#047857', 'PWR': '#b91c1c', 'SPK': '#a16207', 'HP': '#be185d'}
DEST = {
 1: 'J1 giriş jakı — uç (tip)', 2: 'J1 giriş jakı — gövde (sleeve)',
 3: 'S2 Bright/Dark — orta bacak', 4: 'S2 — yan bacaklardan biri (bu taraf = Dark)',
 5: 'VR3 Shape — 3. bacak (sağ)', 6: 'VR3 Shape — 1. bacak (sol)',
 7: 'VR2 Volume — 2. bacak (orta)', 8: 'VR2 Volume — 1. bacak (sol)',
 9: 'VR1 Gain — 2. bacak (orta)', 10: 'VR1 Gain — 3. bacak (sağ)',
 11: 'S1 Aç/Kapa — orta bacak', 12: 'J2 DC jak — eksi (−)',
 13: 'S3 Hoparlör — orta bacak (S3 uç → hoparlör +)', 14: 'Hoparlör eksi (−)',
 15: 'J3 kulaklık — L', 16: 'J3 kulaklık — R', 17: 'J3 kulaklık — gövde',
}
rows = ''
for i, (x, y, n, lab, g) in enumerate(wires, 1):
    rows += (f'<tr><td><span class="num" style="border-color:{GC[g]};color:{GC[g]}">{i}</span></td>'
             f'<td class="mono">{chr(64+y)}{x}</td><td>{DEST[i]}</td></tr>')

html = f'''<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LM386 Dumble amfi – şema ve pertinaks yerleşimi</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{--ink:#1f2933;--mut:#5b6672;--line:#e3e6ea;--bg:#fafaf7;--acc:#0369a1}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Inter,system-ui,sans-serif}}
main{{max-width:1240px;margin:0 auto;padding:22px 16px 60px}}
h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:18px;margin:34px 0 10px;padding-top:6px;border-top:1px solid var(--line)}}
h3{{font-size:15px;margin:18px 0 6px}}
.sub{{color:var(--mut);margin:0 0 14px}}
.fig{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px;overflow-x:auto}}
.fig svg{{display:block;width:100%;min-width:760px;height:auto}}
.grid2{{display:grid;grid-template-columns:1fr;gap:14px}}

table{{border-collapse:collapse;width:100%;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}}
th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{background:#f2f4f6;font-size:13px}} tr:last-child td{{border-bottom:none}}
.mono{{font-family:'JetBrains Mono',monospace;font-size:13px}}
.num{{display:inline-flex;width:24px;height:24px;border:2.5px solid;border-radius:50%;align-items:center;justify-content:center;font-weight:800;font-size:12px;background:#fff}}
.chg li{{margin:3px 0}} .tag{{display:inline-block;font-size:12px;font-weight:700;padding:1px 7px;border-radius:99px;background:#fff4d6;color:#8a5a00;border:1px solid #f0d58c}}
.note{{background:#fff;border-left:4px solid var(--acc);padding:10px 14px;border-radius:6px;margin:10px 0}}
.wrap{{overflow-x:auto}}
</style></head><body><main>
<h1>LM386 Dumble tarzı amfi — şema ve pertinaks yerleşimi</h1>
<p class="sub">Revizyon 4 · 4 Kasım 2026 · Proje raporundaki netlist'ten sadeleştirildi</p>

<h2>Bu revizyonda ne değişti</h2>
<ul class="chg">
<li><b>Revizyon 4:</b> Rd (2,2k), RM (2,2k) ve Rb (560 Ω) tek dirence indi; LM386 pin 7'ye C11 (10 µF) ve pin 6–4 arasına C12 (100 nF) eklendi; kabine sarı güç LED'i (2,2k ile) eklendi.</li>
<li><b>Anahtarlar:</b> S1 = açma/kapama, S2 = Bright/Dark, S3 = hoparlör aç/kapa.</li>
<li><b>Bright/Dark sadeleşti:</b> C8 artık source ile Y noktası arasında. Y, Rb (560 Ω) ve C9 üzerinden GND'ye gidiyor. S2 sadece Y'yi GND'ye kısa devre ediyor (2 kablo). Kapalı = Dark, açık = Bright. Seviye farkı ortalarda ≈ 6 dB, tizde ≈ 3–4 dB (önceden 12 dB).</li>
<li><b>Tone yerine Shape (ISF tarzı):</b> Köprülü-T orta frekans çentiği (CT1, CT2, RT 10k, RM 2,2k) ve onunla düz sinyal arasında geçiş yapan VR3. Sol uç: oyuk mid (US), sağ uç: düz, orta frekanslar önde (UK).</li>
<li><b>Gain potu B1k:</b> Kazanç 41–200 kat, dönüşe daha eşit yayılıyor.</li>
<li><b>VR4 trim kalktı:</b> Drain direnci sabit 2,2 kΩ.</li>
<li><b>D1 kart dışında:</b> J2 (+) ile S1 arasında, makaronlu.</li>
<li><b>Sinyal yolu soldan sağa:</b> Güç ve hoparlör toprağı sağ uçtan giriyor, hoparlör akımı preamp toprağından geçmiyor.</li>
</ul>

<h2>Şema</h2>
<div class="fig">{schematic_svg()}</div>

<h2>Kontroller</h2>
<div class="wrap"><table>
<tr><th>Kontrol</th><th>Parça</th><th>Ne yapar</th></tr>
<tr><td><b>Volume</b></td><td>VR2 B100k</td><td>LM386'ya giren sinyal miktarı. Hem sesi hem distorsiyon miktarını etkiler.</td></tr>
<tr><td><b>Gain</b></td><td>VR1 B1k</td><td>LM386'nın kazancı (41–200 kat). Açtıkça ses yükselir, distorsiyon artar, bas sıkılaşır.</td></tr>
<tr><td><b>Shape</b></td><td>VR3 B22k</td><td>Sol: orta frekanslar (~0,7–1 kHz) oyuk, bas ve tiz önde (US). Sağ: düz, orta frekanslar önde (UK). Arası yumuşak geçiş.</td></tr>
<tr><td><b>S1</b></td><td>Aç/Kapa</td><td>12 V beslemeyi keser.</td></tr>
<tr><td><b>S2</b></td><td>Bright/Dark</td><td>Dark: dolgun, tam kazanç. Bright: ortalar ≈ 6 dB kısık, tiz daha az kısık. Ses incelir ve parlaklaşır.</td></tr>
<tr><td><b>S3</b></td><td>Hoparlör</td><td>Hoparlörü keser, kulaklık çalışmaya devam eder.</td></tr>
</table></div>

<h2>Pertinaks yerleşimi</h2>
<p>Adalı (her deliği ayrı pedli) pertinaks için. Kullanılan alan <b>31 × 14 delik</b> (≈ 7,9 × 3,6 cm). 38 × 18'lik kartın sol üst köşesinden başla; sağda ve altta boş yer kalır. Sütunlar 1–24, satırlar A–N. Gri = GND, kırmızı = +12 V, turuncu = V_pre, bakır = sinyal; bunlar alt yüzde lehim köprüsü ya da çıplak tel ile yapılan yollar. Numaralı beyaz pedler kabine giden kablolar.</p>
<div class="grid2">
<div class="fig">{board_svg(False)}</div>
<div class="fig">{board_svg(True)}</div>
</div>
<div class="note">
<b>Dikkat edilecekler</b>
<ul>
<li>Dirençler dik (bir bacak bükülü), Rf ve Rg yatık. Dik dirençte gövde, çizimde daire olan deliğin üstünde durur.</li>
<li>U1'in çentiği sola bakar. 1. bacak sol altta (G21).</li>
<li>Q1'in düz yüzü yukarı (Rd'lere) bakar. Bu durumda soldan sağa G-S-D olur. Lehimlemeden önce multimetreyle bacakları doğrula. Farklıysa transistörü çevir.</li>
<li>Elektrolitiklerde + işaretine dikkat et (C1, C2, C6, C8, C11). C8'in + bacağı source tarafında (J7), C11'in + bacağı pin 7 tarafında (B22).</li>
<li>C11 ve C12'nin altında, 3. satır boyunca GND yolu ile 4. satırdaki çıkış yolu yan yana gidiyor; bu iki yol arasında lehim köprüsü olmadığını kontrol et.</li>
<li>Alt yüzde çalışırken ayna görüntüsünü (alttaki çizim) kullan.</li>
<li>Bitince süreklilik moduyla kontrol et: H5 (gate) – GND, G23 (pin 3) – GND ve +12 V – GND arasında kısa devre olmamalı.</li>
</ul></div>

<h2>Kart dışı bağlantı şeması</h2>
<p>Kabin içinden bakış. Potlar arkadan (lehim tarafından) çizildi: arkadan bakınca 3. bacak solda, 1. bacak sağda. Gain ve Volume saat yönünde açılır. Shape solda Fender (oyuk ortalar), sağda Marshall (ortalar önde).</p>
<div class="fig">{wiring_svg()}</div>
<h3>Burgulu kablo grupları</h3>
<div class="wrap"><table>
<tr><th>Grup</th><th>Pedler</th><th>Not</th></tr>
<tr><td>Giriş (J1)</td><td>1 + 2</td><td>En kısa yoldan götür. Hoparlör ve güç kablolarına paralel gitmesin, kesişirse dik açıyla kesişsin. Elinde varsa ekranlı kablo daha iyi.</td></tr>
<tr><td>S2 Bright/Dark</td><td>3 + 4</td><td></td></tr>
<tr><td>Shape (VR3)</td><td>5 + 6</td><td>5 → 3. bacak, 6 → 1. bacak</td></tr>
<tr><td>Volume (VR2)</td><td>7 + 8</td><td>7 → 2. bacak, 8 → 1. bacak</td></tr>
<tr><td>Gain (VR1)</td><td>9 + 10</td><td>9 → 2. bacak, 10 → 3. bacak. Pin 1–8 geri besleme ağına gidiyor, kısa tut.</td></tr>
<tr><td>Güç</td><td>11 + 12</td><td></td></tr>
<tr><td>Hoparlör</td><td>13 + 14</td><td></td></tr>
<tr><td>Kulaklık (J3)</td><td>15 + 16 + 17</td><td>Üçlü ör.</td></tr>
<tr><td>Burgusuz</td><td>—</td><td>VR3 2. bacak → VR2 3. bacak kısa tel; S3 → hoparlör (+); D1 anahtarın üstünde; pot gövdeleri arası çıplak tel.</td></tr>
</table></div>

<h2>Kablo bağlantıları</h2>
<p>Pot bacak numarası: pot önden bakılırken (mil sana doğru, bacaklar aşağıda) soldan sağa 1-2-3. Aynı gruba giden kabloları birbirine ör.</p>
<div class="wrap"><table>
<tr><th>#</th><th>Ped</th><th>Nereye</th></tr>
{rows}
</table></div>

<h3>Kabin üzerindeki ara bağlantılar (kart dışı)</h3>
<div class="wrap"><table>
<tr><th>Nerede</th><th>Bağlantı</th></tr>
<tr><td>Shape → Volume</td><td>VR3'ün 2. (orta) bacağı → VR2'nin 3. bacağına kısa tel.</td></tr>
<tr><td>S2</td><td>Sadece orta bacak ve bir yan bacak kullanılır. Anahtar o yana itildiğinde Dark olur.</td></tr>
<tr><td>Gain (VR1)</td><td>Sadece 2. ve 3. bacak kullanılır, 1. bacak boş. Saat yönü = daha fazla kazanç.</td></tr>
<tr><td>Güç</td><td>J2 (+) → D1 anot. D1 katot (çizgili uç) → S1 yan bacak. S1 orta bacak → ped 11. Makaron geçir. Adaptörün merkez ucunun + olduğunu ölçerek doğrula.</td></tr>
<tr><td>Hoparlör</td><td>S3 uç bacak → hoparlör (+). Hoparlör (−) → ped 14.</td></tr>
<tr><td>Güç LED'i</td><td>S1 orta bacak → RLED 2,2k → LED uzun bacak (anot). LED kısa bacak (katot) → J2 (−).</td></tr>
<tr><td>Pot gövdeleri</td><td>Hepsi birbirine ve VR2'nin 1. bacağına (GND).</td></tr>
</table></div>

<h2>İlk çalıştırma</h2>
<ol>
<li>U1 takılı değilken (soket kullanırsan) güç ver. Ölç: pin 6 ≈ 11,3 V, C6 (+) ≈ 9–10 V.</li>
<li>Q1 drain (H7) 4,5–8,5 V, source (H6) 1–2,3 V arasında olmalı.</li>
<li>Gücü kes, U1'i tak. İlk denemeyi volume kısık ve kulaklık kulakta değilken yap.</li>
<li>Hoparlör 0,5 W: volume ve gain birlikte sonuna kadar açıkken hoparlörü zorlayabilirsin.</li>
</ol>
</main></body></html>'''
open('index.html', 'w').write(html)
print(len(html))
