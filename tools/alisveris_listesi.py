from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
D='/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('S',D+'DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('SB',D+'DejaVuSans-Bold.ttf'))
from reportlab.lib.fonts import addMapping
addMapping('S',0,0,'S');addMapping('S',1,0,'SB')
FS=9.5
N=ParagraphStyle('n',fontName='S',fontSize=FS,leading=FS*1.25)
C=ParagraphStyle('c',parent=N,fontSize=8.5,leading=10.2)
H1=ParagraphStyle('h1',fontName='SB',fontSize=15,leading=18,spaceAfter=2)
H2=ParagraphStyle('h2',fontName='SB',fontSize=11.5,leading=14,spaceBefore=6,spaceAfter=3,textColor=colors.HexColor('#1f3a5f'),keepWithNext=1)
H3=ParagraphStyle('h3',fontName='SB',fontSize=9.8,leading=12,spaceBefore=4,spaceAfter=2,keepWithNext=1)
s=[]
P=lambda t,st=N: s.append(Paragraph(t,st))
def tbl(rows,widths,head=True):
    data=[[Paragraph(str(c),ParagraphStyle('x',parent=C,fontName='SB' if (head and i==0) else 'S')) for c in r] for i,r in enumerate(rows)]
    t=Table(data,colWidths=[w*mm for w in widths],repeatRows=1 if head else 0)
    st=[('GRID',(0,0),(-1,-1),0.4,colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),1.5),('BOTTOMPADDING',(0,0),(-1,-1),1.5),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)]
    if head: st.append(('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6ecf3')))
    t.setStyle(TableStyle(st)); s.append(t)
def checks(items,done=False):
    box='☑' if done else '☐'
    rows=[]; it=list(items)
    half=(len(it)+1)//2
    for i in range(half):
        a=it[i]; b=it[i+half] if i+half<len(it) else ''
        rows.append([f'{box} {a}', f'{box} {b}' if b else ''])
    t=Table([[Paragraph(x,N) for x in r] for r in rows],colWidths=[90*mm,90*mm])
    t.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),0.5),('BOTTOMPADDING',(0,0),(-1,-1),0.5),('LEFTPADDING',(0,0),(-1,-1),0)]))
    s.append(t)

P('12V Gitar Amfisi – Alışveriş Listesi',H1)
P('9 Kasım 2026 · Gain/Volume potu için iki durum: <b>A pot</b> (logaritmik bulunursa) ve <b>B pot</b> (bulunamazsa eldeki B100K + B500K kullanılır).')
P('Alınacak parçalar',H2)
P('Yarı iletkenler',H3); checks(['TDA2003 ×1','1N5822 ×1'])
P('Potlar, anahtarlar, trimpot',H3)
checks(['A100K ×2 (A pot durumu: Gain + Volume; B pot durumunda ek pot gerekmez)','B250K ×1 (ISF)','10k çok turlu trimpot ×1 (JFET bias)','SPDT ON-OFF-ON mini toggle ×1 (Dark/Normal/Bright)','SPST güç anahtarı ×1'])
P('Dirençler (¼ W)',H3)
R=[['✓','Değer','Adet','Görevi','4 bant','5 bant'],
['☐','1 Ω','1','TDA Zobel','kahve-siyah-altın-altın','kahve-siyah-siyah-gümüş-kahve'],
['☐','2.2 Ω','1','TDA kazancı','kırmızı-kırmızı-altın-altın','kırmızı-kırmızı-siyah-gümüş-kahve'],
['☐','220 Ω','1','TDA geri besleme','kırmızı-kırmızı-kahve-altın','kırmızı-kırmızı-siyah-siyah-kahve'],
['☐','330 Ω','1','Kulaklık seri','turuncu-turuncu-kahve-altın','turuncu-turuncu-siyah-siyah-kahve'],
['☐','1.2k','1','LM386 kazancı','kahve-kırmızı-kırmızı-altın','kahve-kırmızı-siyah-kahve-kahve'],
['☐','4.7k','1','UK bölücü (alt)','sarı-mor-kırmızı-altın','sarı-mor-siyah-kahve-kahve'],
['☐','6.8k','2','JFET drain, US mid','mavi-gri-kırmızı-altın','mavi-gri-siyah-kahve-kahve'],
['☐','24k','1','UK mid','kırmızı-sarı-turuncu-altın','kırmızı-sarı-siyah-kırmızı-kahve'],
['☐','47k','1','Volume bölücü (seri)','sarı-mor-turuncu-altın','sarı-mor-siyah-kırmızı-kahve'],
['☐','91k','1','UK treble (üst)','beyaz-kahve-turuncu-altın','beyaz-kahve-siyah-kırmızı-kahve'],
['☐','100k','3','Bleed, US slope, US treble (üst)','kahve-siyah-sarı-altın','kahve-siyah-siyah-turuncu-kahve'],
['☐','120k','1','US bass','kahve-kırmızı-sarı-altın','kahve-kırmızı-siyah-turuncu-kahve'],
['☐','130k','1','UK treble (alt)','kahve-turuncu-sarı-altın','kahve-turuncu-siyah-turuncu-kahve'],
['☐','150k','1','US treble (alt)','kahve-yeşil-sarı-altın','kahve-yeşil-siyah-turuncu-kahve'],
['☐','470k','1','UK bass','sarı-mor-sarı-altın','sarı-mor-siyah-turuncu-kahve']]
tbl(R,[7,13,11,37,49,63])
P('Eldeki 15k yalnızca B pot durumunda kullanılır.',C)
P('Film / seramik kondansatörler',H3)
tbl([['✓','Değer','Adet','Üzerindeki kod'],['☐','250 pF','1','221 + 330 paralel, ya da 271'],['☐','470 pF','2','471 (dikkat: "470" = 47 pF)'],['☐','3.3 nF','2','332 / 3n3'],['☐','1 µF film','1','105 / 1µ']],[7,22,12,139])
P('Elektrolitik kondansatörler (≥16 V, tercihen 25 V)',H3)
checks(['470 µF ×1','1000 µF ×1','2200 µF ×2','22 µF ×1 (isteğe bağlı, JFET kazancı için)'])
P('Besleme ve diğer',H3)
checks(['Sigorta yuvası + 1 A yavaş atan sigorta','TDA2003 soğutucusu, termal macun, vida ve somun','Perfboard, bağlantı kabloları','Hoparlör kablosu'])

P('Elimde olanlar',H2)
P('Yarı iletkenler',H3); checks(['BF245B','LM386','Sarı LED'],True)
P('Potlar',H3); checks(['B500K (B pot durumu: Volume)','B100K (B pot durumu: Gain)'],True)
P('Jaklar ve besleme',H3); checks(['6.35 mm jak (giriş)','3.5 mm jak PJ-324M (kulaklık)','DC jakı','12 V adaptör'],True)
P('Dirençler',H3); checks(['10 Ω ×2','100 Ω','1k','2.2k','10k ×2','15k (B pot durumu)','33k ×2','1M'],True)
P('Kondansatörler',H3); checks(['47 nF ×2 (473J100)','22 nF ×2 (223J100)','100 nF ×8 (104K63)','220 µF / 25 V','4.7 µF / 16 V','10 µF ×2 (25 V ve 50 V)','100 µF / 100 V ×2'],True)
P('Mekanik',H3); checks(['8 bacaklı DIP soket','Kutu ve pot düğmeleri (3D baskı)'],True)

P('Bulunamazsa: eşdeğerler ve kabul aralıkları',H2)
P('Aralık içindeki herhangi bir değer devrede çalışır; ISF tonu en fazla bir iki dB değişir. Tam değer yoksa iki direnç seri (toplanır) ya da paralel bağlanarak da tamamlanabilir.')
P('Yarı iletkenler ve kontroller',H3)
tbl([['Parça','Yerine kullanılabilecek'],['TDA2003','TDA2002 (aynı bacak dizilimi, biraz daha düşük güç)'],['1N5822','1N5820, 1N5821, SB340, SR340; olmazsa 1N4007 (≈0.9 V kayıp)'],['A100K (Gain)','A50K – A250K'],['A100K (Volume)','A50K – A500K'],['B250K (ISF)','B220K – B500K'],['10k çok turlu trimpot','10k – 20k; tek turlu da olur (ayarı daha hassas)'],['SPDT ON-OFF-ON','SPDT ON-ON (Normal konumu olmaz, Dark/Bright kalır)'],['SPST güç anahtarı','Herhangi bir SPDT / DPDT anahtar, rocker anahtar']],[45,135])
P('Dirençler',H3)
rr=[('1 Ω','1 – 2.2 Ω'),('2.2 Ω','1.8 – 3.3 Ω'),('220 Ω','180 – 270 Ω'),('330 Ω','220 – 470 Ω (küçük = kulaklık daha yüksek)'),('1.2k','1k – 1.5k'),('4.7k','3.9k – 5.6k'),('6.8k (JFET drain)','5.6k – 10k'),('6.8k (US mid)','5.6k – 8.2k'),('24k','22k – 27k'),('47k','39k – 56k'),('91k','82k – 100k'),('100k (bleed)','47k – 1M'),('100k (US slope, treble üst)','82k – 120k'),('120k','100k – 150k'),('130k','120k – 150k'),('150k','130k – 180k'),('470k','390k – 680k')]
h=(len(rr)+1)//2
rows=[['Gereken','Kabul aralığı','Gereken','Kabul aralığı']]
for i in range(h):
    a=rr[i]; b=rr[i+h] if i+h<len(rr) else ('','')
    rows.append([a[0],a[1],b[0],b[1]])
tbl(rows,[38,52,38,52])
P('Kondansatörler',H3)
tbl([['Gereken','Kabul aralığı'],['250 pF','220 – 330 pF'],['470 pF','390 – 560 pF'],['3.3 nF','2.7 – 4.7 nF (büyük = daha koyu)'],['1 µF film','0.47 – 2.2 µF film; olmazsa 1 – 4.7 µF elektrolitik (+ ucu TDA tarafına)'],['470 µF (TDA kazanç ayağı)','470 – 2200 µF; daha küçüğü olmasın (bas azalır)'],['1000 µF (TDA besleme)','470 – 2200 µF'],['2200 µF (TDA çıkışı)','1000 – 3300 µF'],['2200 µF (giriş filtresi)','1000 – 4700 µF'],['22 µF (isteğe bağlı)','10 – 47 µF']],[55,125])
P('Elektrolitiklerde gerilim en az 16 V olmalı; daha yüksek gerilim her zaman olur, sadece boyut büyür.',C)
P('Diğer',H3)
tbl([['Gereken','Yerine kullanılabilecek'],['1 A yavaş sigorta','1 – 2 A yavaş sigorta ya da 1.1 A polyfuse'],['TDA2003 soğutucusu','TO-220 için kanatlı herhangi bir soğutucu (en az ~25 mm yükseklik)']],[45,135])
def pn(c,d):
    c.setFont('S',7);c.drawRightString(A4[0]-15*mm,8*mm,f'{d.page}')
SimpleDocTemplate('../docs/12V_Gitar_Amfisi_Alisveris_Listesi.pdf',pagesize=A4,leftMargin=15*mm,rightMargin=15*mm,topMargin=12*mm,bottomMargin=13*mm,title='12V Gitar Amfisi – Alışveriş Listesi').build(s,onFirstPage=pn,onLaterPages=pn)
