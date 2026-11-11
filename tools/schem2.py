import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Arc, FancyBboxPatch
import numpy as np
fig,ax=plt.subplots(figsize=(22,11.5))
ax.set_xlim(-5,352); ax.set_ylim(2,160); ax.set_aspect('equal'); ax.axis('off')
LW=1.1; K='black'; FS=6.6
def wire(*pts,**kw):
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    ax.plot(xs,ys,color=kw.get('c',K),lw=kw.get('lw',LW),ls=kw.get('ls','-'),solid_capstyle='round',zorder=2)
def dot(x,y): ax.add_patch(Circle((x,y),0.75,color=K,zorder=4))
def txt(x,y,s,fs=FS,**kw): ax.text(x,y,s,fontsize=fs,zorder=5,**kw)
def gnd(x,y):
    wire((x,y),(x,y-2.5))
    for i,w in enumerate([3,2,1]): wire((x-w,y-2.5-i*0.9),(x+w,y-2.5-i*0.9))
def res(a,b,ref,val,side=1,opt=False):
    (x1,y1),(x2,y2)=a,b
    L=np.hypot(x2-x1,y2-y1); ux,uy=(x2-x1)/L,(y2-y1)/L; px,py=-uy,ux
    bl=min(7,L-2); s=(L-bl)/2
    p1=(x1+ux*s,y1+uy*s); p2=(x2-ux*s,y2-uy*s)
    wire(a,p1); wire(p2,b)
    corners=[(p1[0]+px*1.3,p1[1]+py*1.3),(p2[0]+px*1.3,p2[1]+py*1.3),(p2[0]-px*1.3,p2[1]-py*1.3),(p1[0]-px*1.3,p1[1]-py*1.3)]
    ax.add_patch(Polygon(corners,closed=True,fill=True,fc='white',ec=K,lw=LW,ls='--' if opt else '-',zorder=3))
    mx,my=(x1+x2)/2,(y1+y2)/2
    if abs(ux)>0.5: txt(mx,my+side*2.4,f'{ref} {val}',ha='center',va='bottom' if side>0 else 'top')
    else: txt(mx+side*2.2,my,f'{ref}\n{val}',ha='left' if side>0 else 'right',va='center',linespacing=0.95)
def cap(a,b,ref,val,polar=False,side=1,opt=False):
    (x1,y1),(x2,y2)=a,b
    L=np.hypot(x2-x1,y2-y1); ux,uy=(x2-x1)/L,(y2-y1)/L; px,py=-uy,ux
    mx,my=(x1+x2)/2,(y1+y2)/2; g=0.8
    q1=(mx-ux*g,my-uy*g); q2=(mx+ux*g,my+uy*g)
    ls='--' if opt else '-'
    wire(a,q1,ls=ls); wire(q2,b,ls=ls)
    w=2.6
    wire((q1[0]+px*w,q1[1]+py*w),(q1[0]-px*w,q1[1]-py*w),lw=1.6)
    if polar:
        ax.add_patch(Polygon([(q2[0]+px*w,q2[1]+py*w),(q2[0]-px*w,q2[1]-py*w),(q2[0]-px*w+ux*0.9,q2[1]-py*w+uy*0.9),(q2[0]+px*w+ux*0.9,q2[1]+py*w+uy*0.9)],closed=True,fc=K,ec=K,zorder=3))
        txt(q1[0]-ux*1.8+px*2.4,q1[1]-uy*1.8+py*2.4,'+',fs=7,ha='center',va='center',fontweight='bold')
    else:
        wire((q2[0]+px*w,q2[1]+py*w),(q2[0]-px*w,q2[1]-py*w),lw=1.6)
    if abs(ux)>0.5: txt(mx,my+side*3.3,f'{ref} {val}',ha='center',va='bottom' if side>0 else 'top')
    else: txt(mx+side*3.3,my,f'{ref}\n{val}',ha='left' if side>0 else 'right',va='center',linespacing=0.95)
def pot(top,bot,wx,ref,val,lug_top='3',lug_bot='1'):
    res(top,bot,'','')
    x,yt=top; yb=bot[1]; my=(yt+yb)/2
    ax.annotate('',xy=(x+1.4,my),xytext=(wx,my),arrowprops=dict(arrowstyle='-|>',lw=LW,color=K))
    if ref=='VOLUME': txt(x+2.2,my+9,f'{ref}\n{val}',ha='left',va='center',fontweight='bold')
    else: txt(x-2,my,f'{ref}\n{val}',ha='right',va='center',fontweight='bold')
    txt(x+0.8,yt-0.5,lug_top,fs=5.5,va='top',color='#555'); txt(x+0.8,yb+0.5,lug_bot,fs=5.5,va='bottom',color='#555')
    txt(wx-1.2,my+0.6,'2',fs=5.5,color='#555',ha='right',va='bottom')
    return (wx,my)
def tag(x,y,s,ha='center',va='bottom'):
    ax.text(x,y,s,fontsize=5.4,ha=ha,va=va,color='#8a4b00',zorder=6,bbox=dict(boxstyle='round,pad=0.15',fc='#fff3df',ec='#d9a441',lw=0.5))
def panel(x0,y0,x1,y1,label='ön panel'):
    ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,ec='#2b7bb9',lw=0.9,ls=(0,(4,2)),zorder=1))
    txt(x0+0.8,y1-0.8,label,fs=5.6,color='#2b7bb9',va='top',style='italic')
def vlabel(x,y,s,up=True):
    wire((x,y),(x,y+(2 if up else -2)))
    txt(x,y+(2.5 if up else -2.5),s,fs=6.2,ha='center',va='bottom' if up else 'top',fontweight='bold',color='#a01818')
# ===== INPUT + JFET =====
panel(-3,80,13,100,'kartta (ön kenar)')
# jack
ax.add_patch(Rectangle((0,88),4,6,fill=False,ec=K,lw=LW)); txt(2,87.5,'GİRİŞ 6.35',fs=5.2,ha='left',va='top')
wire((4,92),(14,92)); wire((4,89),(8,89),(8,86)); gnd(8,86)
wire((4,90.5),(5.5,90.5),(5.5,83),(3,83),ls='--'); txt(-1.5,83.6,'JP1*',fs=4.8,color='#555'); gnd(3,83)
txt(4.4,90.9,'kesici',fs=3.8,color='#555')
res((14,92),(28,92),'R5','33k')
dot(30,92); wire((28,92),(34,92))
res((30,92),(30,76),'R6','1M',side=-1); gnd(30,76)
# JFET symbol at gate (34,92)
wire((34,92),(38,92)); wire((38,88),(38,96),lw=2)
wire((38,95),(42,95),(42,100)); wire((38,89),(42,89),(42,84))
ax.annotate('',xy=(38.1,92),xytext=(36,92),arrowprops=dict(arrowstyle='-|>',lw=0.9,color=K))
ax.add_patch(Circle((39.5,92),5.2,fill=False,ec=K,lw=0.8))
txt(16,108,'Q1 BF245B',fontweight='bold'); txt(16,105.5,'G/S/D bacak sırası üreticiye\ngöre değişir: ölçerek doğrula',fs=5,va='top')
# drain
dot(42,100); res((42,100),(42,116),'R4','6.8k'); vlabel(42,116,'V3')
cap((42,100),(58,100),'C10','100n')
# source
dot(42,84); res((42,84),(42,70),'TR1','10k trim',side=-1); gnd(42,70)
wire((42,84),(50,84)); cap((50,84),(50,76),'C9','22µ',polar=True)
res((50,76),(50,62),'','')
ax.annotate('',xy=(51.4,69),xytext=(56,69),arrowprops=dict(arrowstyle='-|>',lw=LW,color=K))
wire((56,69),(56,62),(50,62)); dot(50,62); gnd(50,62)
txt(57,72,'RV4 DRIVE\nB2.2K',fs=FS,ha='left',va='center',fontweight='bold')
txt(57,66.5,'saat yönü → kazanç ↑\n(kart yerleşimi\nhenüz güncellenmedi)',fs=4.8,color='#555',ha='left',va='top')
txt(24,66,'Ayar: TR1 ile\nV(drain) ≈ 7 V',fs=5.6,color='#1a4d8f',ha='center')
# ===== GAIN pot + D/B =====
panel(60,82,93,114,'RV1 kartta · SW1 panelde')
wire((58,100),(64,100),(64,106),(68,106))
gw=pot((68,106),(68,86),74,'GAIN','B100K')
wire((68,86),(68,84)); gnd(68,84)
# switch: common to wiper
dot(74,96); wire((74,96),(77,96))
ax.add_patch(Circle((77,96),0.6,fill=False,ec=K)); ax.add_patch(Circle((82,100),0.6,fill=False,ec=K)); ax.add_patch(Circle((82,92),0.6,fill=False,ec=K))
wire((77.5,96.3),(81.4,99.2)); txt(77,110.6,'SW1 ON-OFF-ON',fs=5.2,ha='left',va='top'); txt(81,101.5,'B',fs=5.5,color='#555',ha='right'); txt(81,90.5,'D',fs=5.5,color='#555',ha='right',va='top')
cap((82.6,100),(90,100),'','',); txt(86.3,103.2,'470p',fs=5.6,ha='center')
wire((90,100),(90,108),(68,108),(68,106))
cap((82.6,92),(90,92),'','',); txt(86.3,88.6,'3.3n',fs=5.6,ha='center',va='top')
wire((90,92),(90,87)); gnd(90,87)
txt(76,79,'CB 470p ve CD 3.3n kartta;\nSW1 panelde, 3 kısa burgulu tel\n(SW1 A / orta / B pedleri)',fs=4.8,color='#555',ha='center',va='top')
wire((74,96),(74,90),(102,90))
# ===== LM386 =====
dot(95.5,90); res((95.5,90),(95.5,72),'R7','15k*',side=-1,opt=True); gnd(95.5,72)
txt(96,68.5,'* B pot ile (takılır)',fs=5,color='#555')
ax.add_patch(Polygon([(102,82),(102,98),(118,90)],closed=True,fill=True,fc='white',ec=K,lw=LW,zorder=3))
txt(104.5,90,'+',fs=8,va='center'); txt(104.5,85,'−',fs=8,va='center'); txt(108,93.5,'U1\nLM386',fs=5.8,ha='left',fontweight='bold')
txt(101,90.6,'3',fs=5,ha='right',color='#555'); txt(101,85.6,'2',fs=5,ha='right',color='#555')
wire((102,85),(100.5,85),(100.5,83)); gnd(100.5,83)
# supply
wire((110,94),(110,98)); vlabel(110,98,'V2'); txt(110.6,95,'6',fs=5,color='#555')
wire((110,86),(110,80)); gnd(110,80); txt(110.6,82.5,'4',fs=5,color='#555')
# gain pins 1-8
wire((106,96),(106,104)); wire((114,92),(114,104)); txt(105.3,97,'1',fs=5,color='#555',ha='right'); txt(114.6,93,'8',fs=5,color='#555')
res((106,104),(106,118),'R8','1.2k',side=-1); wire((106,118),(114,118)); cap((114,118),(114,104),'C11','10µ',polar=True,side=1)
# bypass pin7
wire((112,86.5),(116,82),(118,82)); txt(115,85.5,'7',fs=5,color='#555')
cap((118,82),(118,72),'','',polar=True); gnd(118,72); txt(118,67.5,'C12 10µ',ha='center',va='top')
# output
wire((118,90),(126,90)); txt(118.5,91,'5',fs=5,color='#555')
dot(124,90); res((124,90),(124,76),'R9','10',side=1); cap((124,76),(124,66),'C13','47n',side=1); gnd(124,66)
cap((126,90),(136,90),'C14','4.7µ',polar=True)
# ===== TONE STACKS =====
dot(138,90); wire((136,90),(146,90))
res((138,90),(138,76),'R10','100k',side=-1); gnd(138,76)
dot(146,90)
# US
wire((146,90),(146,140)); dot(146,140)
cap((146,140),(176,140),'C15a','220p')
wire((150,140),(150,136)); cap((150,136),(172,136),'C15b','33p',side=-1); wire((172,136),(172,140)); dot(150,140); dot(172,140)
dot(146,116); res((146,116),(160,116),'R11','100k',side=1)
wire((146,116),(146,116))
wire((162,108),(162,124)); wire((160,116),(162,116)); dot(162,116)
cap((162,124),(176,124),'C16','100n'); cap((162,108),(176,108),'C17','47n',side=-1)
res((176,140),(176,132),'R13','100k'); dot(176,132)
res((176,132),(176,124),'R14','150k'); dot(176,124)
res((176,124),(176,108),'R15','120k'); dot(176,108)
res((176,108),(176,96),'R16','6.8k'); gnd(176,96)
wire((176,132),(194,132))
txt(160,148,'US yığını (Fender tipi)',fs=7,fontweight='bold',ha='center',color='#1a4d8f')
# UK
res((146,90),(146,76),'R12','10k'); dot(146,76)
res((146,76),(158,76),'R17','4.7k',side=-1); wire((158,76),(160,76),(160,74)); gnd(160,74)
wire((146,76),(146,38)); dot(146,62)
cap((146,62),(176,62),'C18','470p')
dot(146,38); res((146,38),(160,38),'R18','33k',side=1)
wire((162,30),(162,46)); wire((160,38),(162,38)); dot(162,38)
cap((162,46),(176,46),'C19','22n'); cap((162,30),(176,30),'C20','22n',side=-1)
res((176,62),(176,54),'R19','91k'); dot(176,54)
res((176,54),(176,46),'R20a+b','120k+10k'); dot(176,46)
res((176,46),(176,30),'R21','470k'); dot(176,30)
res((176,30),(176,18),'R22a+b','22k+2.2k'); gnd(176,18)
wire((176,54),(194,54))
txt(160,9,'UK yığını (Marshall tipi)',fs=7,fontweight='bold',ha='center',color='#1a4d8f')
# ===== ISF + VOLUME (panel) =====
panel(192,40,232,146,'kartta (ön kenar)')
wire((194,132),(200,132),(200,104)); wire((194,54),(200,54),(200,84))
iw=pot((200,104),(200,84),206,'ISF','B250K',lug_top='1',lug_bot='3')
txt(201,130,'US ↑',fs=5.5,color='#555'); txt(201,57,'UK ↓',fs=5.5,color='#555')
wire((206,94),(210,94),(210,110),(218,110),(218,106))
vw=pot((218,106),(218,86),224,'VOLUME','B500K')
wire((218,86),(218,84)); gnd(218,84)
txt(212,70,'B pot düzeni:\nGain B100K + R7 15k\nVolume B500K\n(log eğriye yakın)',fs=5,color='#555',ha='center')
wire((224,96),(236,96))
# ===== VOLUME DIVIDER + TDA =====
res((236,96),(250,96),'R23','47k'); dot(252,96); wire((250,96),(258,96))
res((252,96),(252,82),'R24','10k',side=-1); gnd(252,82)
dot(256,96); cap((256,96),(256,84),'C21','3.3n'); gnd(256,84)
cap((258,96),(270,96),'C22','1µ film')
wire((270,96),(274,96))
ax.add_patch(Polygon([(274,84),(274,104),(294,94)],closed=True,fill=True,fc='white',ec=K,lw=LW,zorder=3))
txt(276.5,96,'+',fs=8,va='center'); txt(276.5,89,'−',fs=8,va='center'); txt(280,99,'U2\nTDA2003',fs=5.8,fontweight='bold')
txt(273,96.6,'1',fs=5,ha='right',color='#555'); txt(273,89.6,'2',fs=5,ha='right',color='#555')
wire((270,89),(274,89)); wire((270,89),(270,80)); dot(270,80)
res((270,80),(300,80),'R25','220',side=-1)
res((270,80),(270,66),'R26','2.2',side=-1); cap((270,66),(270,54),'C23','470µ',polar=True,side=-1); gnd(270,54)
wire((284,99),(284,112)); vlabel(284,112,'V12'); txt(284.6,101,'5',fs=5,color='#555')
wire((284,89),(284,84)); gnd(284,84); txt(284.6,86.5,'3',fs=5,color='#555')
wire((284,112),(299,112)); dot(291,112)
cap((291,112),(291,103),'C6','100n',side=-1); gnd(291,103)
cap((299,112),(299,103),'C7','1000µ',polar=True,side=1); gnd(299,103)
txt(292,117,'(TDA pin5 yanına)',fs=5,color='#555')
wire((294,94),(304,94)); txt(294.5,95,'4',fs=5,color='#555'); dot(300,94); wire((300,80),(300,94))
dot(304,94); res((304,94),(304,80),'R27','1',side=1); cap((304,80),(304,70),'C24','100n'); gnd(304,70)
cap((304,94),(316,94),'C25','2200µ',polar=True)
dot(318,94); wire((316,94),(326,94))
res((318,94),(318,80),'R28','10',side=-1); dot(318,80)
res((318,80),(318,66),'R29','330',side=-1); gnd(318,66)
wire((318,80),(326,80))

# ===== HP jack + speaker (panel) =====
panel(327,76,350,112,'kartta (ön kenar)')
ax.add_patch(Rectangle((331,76),9,22,fill=False,ec=K,lw=LW)); txt(335.5,99,'KULAKLIK\n3.5 mm\nPJ-324M',fs=5.3,ha='center',va='bottom')
wire((326,94),(331,94)); txt(332,94,'T+R (4,3)',fs=4.6,va='center')
wire((326,80),(331,80)); txt(332,80,'S (1)',fs=4.6,va='center')
txt(332,87,'NC (5)',fs=4.6,va='center'); wire((331,87),(329,87),(329,72),(337,72)); 
txt(341,86,'fiş takılınca\nNC açılır,\nhoparlör susar',fs=4.6,va='center')
# speaker
ax.add_patch(Rectangle((337,66),3,8,fill=False,ec=K,lw=LW)); ax.add_patch(Polygon([(340,66),(345,62),(345,78),(340,74)],closed=True,fill=False,ec=K,lw=LW))
txt(346,70,'4Ω\n6.5"',fs=5.2,va='center'); txt(335,73,'+',fs=6)
wire((337,68),(334,68),(334,62)); gnd(334,62); tag(329,70,'TB2',ha='center',va='center'); txt(338,58,'hoparlör kabloyla',fs=4.6,color='#555')
# ===== POWER =====
txt(2,52,'BESLEME',fs=8,fontweight='bold',color='#1a4d8f')
panel(-3,26,8,48,'arka panel')
ax.add_patch(Rectangle((0,32),5,8,fill=False,ec=K,lw=LW)); txt(2.5,41,'DC jak\n12 V',fs=5.3,ha='center',va='bottom')
wire((5,38),(14,38)); tag(10.5,38.6,'TB1')
ax.add_patch(Rectangle((14,36.8),7,2.4,fill=False,ec=K,lw=LW)); wire((15,38),(20,38),lw=0.6); txt(17.5,40.4,'F1 1A',fs=5.3,ha='center')
wire((21,38),(24,38),(24,46),(27.4,46)); panel(25,42,40,52,'ön panel')
ax.add_patch(Circle((28,46),0.6,fill=False,ec=K)); ax.add_patch(Circle((34,46),0.6,fill=False,ec=K)); wire((28.4,46.4),(33.4,48.5)); txt(36,49.6,'SW2 güç',fs=5.0,ha='left')
wire((34.6,46),(42,46),(42,38),(44,38)); txt(31,43.5,'GÜÇ orta / uç',fs=4.5,color='#8a4b00',ha='center')
wire((5,34),(10,34),(10,28)); gnd(10,28); tag(10,28,'TB1',ha='left',va='top')
# diode
wire((44,38),(48,38)); ax.add_patch(Polygon([(48,35.5),(48,40.5),(52,38)],closed=True,fc='white',ec=K,lw=LW)); wire((52,35.5),(52,40.5),lw=1.6); txt(50,42,'D1 1N5822',fs=5.6,ha='center')
wire((52,38),(66,38)); dot(58,38); dot(62,38)
cap((58,38),(58,26),'C1','2200µ',polar=True,side=-1); gnd(58,26)
cap((62,38),(62,26),'C2','100n'); gnd(62,26)
vlabel(66,38,'V12')
res((66,38),(80,38),'R1','100'); dot(82,38); wire((80,38),(98,38))
cap((82,38),(82,26),'C3','220µ',polar=True,side=-1); gnd(82,26)
dot(90,38); cap((90,38),(90,26),'C8','100µ',polar=True,side=1); gnd(90,26)
dot(98,38); cap((98,38),(98,26),'C4','100n',side=1); gnd(98,26)
wire((98,38),(104,38)); vlabel(104,38,'V2')
res((104,38),(118,38),'R2','1k'); dot(120,38); wire((118,38),(126,38))
cap((120,38),(120,26),'C5','100µ',polar=True,side=1); gnd(120,26)
vlabel(126,38,'V3')
# LED
wire((66,38),(66,14),(70,14)); res((70,14),(84,14),'R3','2.2k'); wire((84,14),(90,14))
panel(91,6,112,22,'kartta (ön kenar)')
ax.add_patch(Polygon([(96,12),(96,16),(100,14)],closed=True,fc='#ffe066',ec=K,lw=LW)); wire((100,12),(100,16),lw=1.6)
wire((90,14),(96,14)); wire((100,14),(106,14),(106,11)); gnd(106,11); txt(98,17.5,'LED (sarı)',fs=5.3,ha='center')

# title & notes
txt(-2,157,'12V Gitar Amfisi — Devre Şeması (kart v2)',fs=13,fontweight='bold')
txt(-2,152.5,'BF245B tampon/ilk kat → LM386 gain katı → ISF (US↔UK) ton yığınları → Volume → TDA2003 güç katı → 4Ω hoparlör / kulaklık',fs=7.5,color='#333')
txt(200,157,'Mavi çerçeve: "kartta" = karta lehimli ön panel parçası, "panelde" = panele vidalı, kabloyla bağlı.  Turuncu = vidalı klemens (TB1, TB2).',fs=6.4,color='#8a4b00')
txt(200,153,'Toprak sembolü = kartın GND dolgusu.  Kesikli: R7 (B pot ile takılır), JP1 (giriş susturma, ölçüp doğrulayınca).',fs=6.4,color='#333')
import os; os.makedirs('out',exist_ok=True)
fig.savefig('out/1_devre_semasi.png',dpi=170,bbox_inches='tight',facecolor='white')
