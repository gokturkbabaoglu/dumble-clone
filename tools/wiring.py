import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch
import numpy as np
R='#d62728'; Bk='#222222'; Bl='#1f77b4'; Y='#e6a700'; G='#2ca02c'; O='#ff7f0e'; V='#8e44ad'; W='#9aa0a6'
def _resample(pts):
    pts=np.array(pts,float); seg=np.sqrt(((pts[1:]-pts[:-1])**2).sum(1)); L=seg.sum()
    t=np.linspace(0,L,max(80,int(L*8))); cum=np.concatenate([[0],np.cumsum(seg)])
    P=np.array([np.interp(t,cum,pts[:,0]),np.interp(t,cum,pts[:,1])]).T
    return P,t,L
def line(ax,pts,c,lw=1.9,ls='-',z=3):
    pts=np.array(pts,float); ax.plot(pts[:,0],pts[:,1],color=c,lw=lw,ls=ls,solid_capstyle='round',zorder=z)
def bundle(ax,starts,ends,cols,via=None,pitch=4.0,amp=1.5,lw=1.9):
    """starts/ends: lists of points; cols: colors. wires converge, twist along path, then split."""
    s0=np.mean(np.array(starts,float),0); e0=np.mean(np.array(ends,float),0)
    path=[s0]+(via or [])+[e0]
    P,t,L=_resample(path)
    # entry/exit points of the twisted section
    a=P[min(len(P)-1,int(len(P)*0.12))]; b=P[max(0,int(len(P)*0.88))]
    Pt,tt,Lt=_resample([a]+[np.array(v) for v in (via or [])]+[b])
    d=np.gradient(Pt,axis=0); n=np.stack([-d[:,1],d[:,0]],1); n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-9
    k=len(cols)
    for i,c in enumerate(cols):
        off=amp*np.sin(2*np.pi*tt/pitch+2*np.pi*i/k)
        Q=Pt+n*off[:,None]
        ax.plot(Q[:,0],Q[:,1],color=c,lw=lw,zorder=3,solid_capstyle='round')
        line(ax,[starts[i],Q[0]],c,lw); line(ax,[Q[-1],ends[i]],c,lw)
def pad(ax,x,y,label,vert=True):
    ax.add_patch(Circle((x,y),1.9,fc='#d9a441',ec='#7a5a12',lw=0.8,zorder=5)); ax.add_patch(Circle((x,y),0.6,fc='white',zorder=6))
    if vert: ax.text(x,y+3,label,fontsize=6.4,rotation=90,ha='center',va='bottom',color='#5b2c00',zorder=6)
    else: ax.text(x+3,y,label,fontsize=6.4,ha='left',va='center',color='#5b2c00',zorder=6)
def lugbox(ax,x,y,label=None,num=None):
    ax.add_patch(Rectangle((x-1.2,y-5),2.4,5.6,fc='#e0c27a',ec='#7a5a12',lw=0.8,zorder=4))
    ax.add_patch(Circle((x,y-0.6),0.7,fc='white',zorder=5))
    if num: ax.text(x,y-6.3,num,fontsize=6.6,ha='center',va='top',fontweight='bold',zorder=5)
    if label: ax.text(x,y-6.3,label,fontsize=5.6,ha='center',va='top',zorder=5)
    return (x,y)
def potrear(ax,x,y,name,val,notes=None):
    ax.add_patch(Circle((x,y-8),11,fc='#c8ccd2',ec='#555',lw=1.2,zorder=2))
    ax.add_patch(Circle((x,y-8),4.2,fc='#9aa0a8',ec='#555',lw=0.8,zorder=2))
    L={}
    for i,dx in enumerate([-5,0,5]):
        L[i+1]=lugbox(ax,x+dx,y+5,num=str(i+1))
    ax.text(x,y-21,f'{name}\n{val}',fontsize=7.3,ha='center',va='top',fontweight='bold')
    if notes: ax.text(x,y-29,notes,fontsize=5.6,ha='center',va='top',color='#444')
    return L
def capsym(ax,p,q,label):
    m=((p[0]+q[0])/2,(p[1]+q[1])/2)
    line(ax,[p,q],'#555',1.3)
    ax.add_patch(Rectangle((m[0]-2.6,m[1]-1.4),5.2,2.8,fc='#f6e3a1',ec='#7a5a12',lw=0.8,zorder=4))
    ax.text(m[0],m[1]+2,label,fontsize=6,ha='center',va='bottom',zorder=5)
def base(title,sub,xlim=(0,428),ylim=(-40,172)):
    fig,ax=plt.subplots(figsize=(21,10.5))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect('equal'); ax.axis('off')
    ax.text(xlim[0]+2,ylim[1]-2,title,fontsize=14,fontweight='bold',va='top')
    ax.text(xlim[0]+2,ylim[1]-10,sub,fontsize=8,va='top',color='#333')
    return fig,ax
def legend(ax,x,y,items,title='Renkler / kurallar'):
    h=6+len(items)*5.2
    ax.add_patch(FancyBboxPatch((x,y-h),110,h,boxstyle='round,pad=1',fc='white',ec='#999',lw=0.8,zorder=6))
    ax.text(x+2,y-2,title,fontsize=7.3,fontweight='bold',va='top',zorder=7)
    for i,(c,t) in enumerate(items):
        yy=y-8.5-i*5.2
        if c: ax.plot([x+2,x+9],[yy,yy],color=c,lw=2.4,zorder=7,ls='--' if c==G else '-')
        ax.text(x+11,yy,t,fontsize=6.3,va='center',zorder=7)
# ============ IMAGE 4 ============
fig,ax=base('Ön Panel Kablolaması — sinyal, kulaklık ve hoparlör',
 'Görünüm: kutunun İÇİNDEN ön panelin ARKASINA bakış (pot bacakları yukarıda, karta doğru). Bu yüzden sıra önden bakışa göre TERS: GİRİŞ en sağda.\n'
 'Kart da aynı yönden çizildi: ön kenardaki kablo noktaları arkadan görüldüğü sırayla.')
BX0,BX1,BY=12,302,128
ax.add_patch(Rectangle((BX0,BY-6),BX1-BX0,30,fc='#f4efe2',ec='black',lw=1.4,zorder=1))
ax.text(BX1-2,BY+21.5,'KART — ön kenar (arkadan bakış)',fontsize=7,ha='right',va='top',color='#444')
def xd(xu): return 20+(88-xu)*3.2
PP={'P_IN':(4,'GİRİŞ uç'),'P_ING':(8,'GİRİŞ şase'),'P_GIN':(16,'GAIN 3'),'P_GW':(20,'GAIN 2'),'P_GG':(24,'GAIN 1/GND'),
    'P_US':(40,'ISF 1 (US)'),'P_UK':(44,'ISF 3 (UK)'),'P_VW':(56,'VOL 2'),'P_VG':(60,'VOL 1/GND'),
    'P_SPK':(68,'ÇIKIŞ→jak uç'),'P_HPS':(72,'jak sleeve'),'P_SPKG':(76,'hop. −')}
P={}
for k,(xu,lab) in PP.items():
    P[k]=(xd(xu),BY); pad(ax,*P[k],lab)
PY=22
ax.add_patch(Rectangle((BX0-4,PY-36),BX1-BX0+8,4,fc='#7f8c8d',ec='black',lw=1,zorder=1))
ax.text((BX0+BX1)/2,PY-37.5,'ÖN PANEL (iç yüzü) — önden bakan kişi bu parçaları soldan sağa  GİRİŞ · GAIN · SW1 · ISF · VOLUME · KULAKLIK  sırasıyla görür',fontsize=7.2,ha='center',va='top',color='#333')
# input jack
jx=284
ax.add_patch(Rectangle((jx-8,PY-26),16,26,fc='#cfd3d8',ec='#555',lw=1.2,zorder=2))
ax.text(jx,PY-14,'GİRİŞ\n6.35 mm',fontsize=6.6,ha='center',va='center',fontweight='bold')
jt=lugbox(ax,jx-4,PY+5,label='uç'); js=lugbox(ax,jx+4,PY+5,label='şase')
bundle(ax,[P['P_IN'],P['P_ING']],[jt,js],[R,Bk],via=[(286,95),(285,60)])
ax.text(296,80,'BURGULU ÇİFT\nkısa tut,\nhoparlör ve\nbesleme\nkablolarından\nuzak geçir',fontsize=6,ha='left',va='center',color=R)
# gain pot
gx=244; GL=potrear(ax,gx,PY,'GAIN','B100K (veya A100K)')
bundle(ax,[P['P_GIN'],P['P_GW'],P['P_GG']],[GL[3],GL[2],GL[1]],[Y,Bl,Bk],via=[(242,95),(244,62)])
# SW1
sx=210
ax.add_patch(Rectangle((sx-8,PY-16),16,16,fc='#cfd3d8',ec='#555',lw=1.2,zorder=2))
ax.text(sx,PY-8,'SW1\nON-OFF-ON',fontsize=6.2,ha='center',va='center',fontweight='bold')
sa=lugbox(ax,sx-5,PY+5,label='A'); sc=lugbox(ax,sx,PY+5,label='orta'); sb=lugbox(ax,sx+5,PY+5,label='B')
line(ax,[sc,(sc[0],PY+16),(GL[2][0],PY+16),GL[2]],Bl,1.6)
line(ax,[sb,(sb[0],PY+12),(GL[3][0]+4,PY+12),(GL[3][0]+4,PY+8),GL[3]],'#555',1.3)
ax.add_patch(Rectangle((sb[0]+6,PY+10.6),5.2,2.8,fc='#f6e3a1',ec='#7a5a12',lw=0.8,zorder=4)); ax.text(sb[0]+8.6,PY+13.8,'470p',fontsize=6,ha='center',va='bottom')
line(ax,[sa,(sa[0],PY+20),(GL[1][0]-3,PY+20),(GL[1][0]-3,PY+8),GL[1]],'#555',1.3)
ax.add_patch(Rectangle((sa[0]+8,PY+18.6),5.2,2.8,fc='#f6e3a1',ec='#7a5a12',lw=0.8,zorder=4)); ax.text(sa[0]+10.6,PY+21.8,'3.3n',fontsize=6,ha='center',va='bottom')
ax.text(sx,PY-19,'Kol A tarafına itilince orta–B bağlanır (BRIGHT),\nB tarafına itilince orta–A (DARK), ortada boş.\nYön ters gelirse 470p ile 3.3n\'yi yer değiştir.',fontsize=5.6,ha='center',va='top',color='#444')
# ISF pot
ix=168; IL=potrear(ax,ix,PY,'ISF','B250K','saat yönü → UK')
bundle(ax,[P['P_US'],P['P_UK']],[IL[1],IL[3]],[O,V],via=[(168,95),(168,62)])
# volume
vx=124; VL=potrear(ax,vx,PY,'VOLUME','B500K (veya A100K)','saat yönü → ses artar')
line(ax,[IL[2],(IL[2][0],PY+24),(VL[3][0],PY+24),VL[3]],G,1.9)
ax.text((IL[2][0]+VL[3][0])/2,PY+25,'ISF orta → VOL 3 (kısa tel)',fontsize=6,ha='center',va='bottom',color=G)
bundle(ax,[P['P_VW'],P['P_VG']],[VL[2],VL[1]],[Bl,Bk],via=[(118,95),(122,62)])
# pot body ground (optional)
for x0 in (vx,ix,gx):
    ax.add_patch(Circle((x0+7,PY-14),0.9,fc='#2ca02c',zorder=6))
line(ax,[(vx+7,PY-14),(ix+7,PY-14),(gx+7,PY-14)],G,1.4,ls='--',z=5)
line(ax,[VL[1],(VL[1][0]-4,PY+8),(VL[1][0]-4,PY-14),(vx+7,PY-14)],G,1.4,ls='--',z=5)
ax.text(ix,PY-27,'',fontsize=5)
# HP jack PJ-324M rear
hx=78
ax.add_patch(Rectangle((hx-13,PY-18),26,18,fc='#2f2f2f',ec='#111',lw=1.2,zorder=2))
ax.text(hx,PY-9,'KULAKLIK 3.5 mm\nPJ-324M',fontsize=6.2,ha='center',va='center',color='white',fontweight='bold')
HP={}
for name,dx in [('S',-10),('T',-5),('T-NC',0),('R',5),('R-NC',10)]:
    HP[name]=lugbox(ax,hx+dx,PY+5,label=name)
line(ax,[HP['T'],(HP['T'][0],PY+10),(HP['R'][0],PY+10),HP['R']],'#555',1.4)
ax.text(hx,PY+11,'T–R köprü',fontsize=5.6,ha='center',va='bottom')
bundle(ax,[P['P_SPK'],P['P_HPS']],[HP['T'],HP['S']],[R,Bk],via=[(76,95),(74,58)])
ax.text(hx,PY-21,'Bacak isimleri işlevseldir: multimetreyle bul\n(T-NC: fiş yokken T ile kısa, fiş takılınca açılır).\nR-NC boş kalır.',fontsize=5.6,ha='center',va='top',color='#444')
# speaker
spx,spy=30,62
ax.add_patch(Circle((spx,spy),13,fc='#ddd',ec='#555',lw=1.2,zorder=2)); ax.add_patch(Circle((spx,spy),5,fc='#bbb',ec='#555',zorder=2))
ax.text(spx,spy-16,'HOPARLÖR 4Ω 6.5"',fontsize=7,ha='center',va='top',fontweight='bold')
sp_p=(spx+6,spy+11); sp_m=(spx-6,spy+11)
ax.text(sp_p[0],sp_p[1]+1.5,'+',fontsize=9,color=R,ha='center',va='bottom',fontweight='bold'); ax.text(sp_m[0],sp_m[1]+1.5,'−',fontsize=9,ha='center',va='bottom',fontweight='bold')
for p in (sp_p,sp_m): ax.add_patch(Rectangle((p[0]-1.4,p[1]-1.4),2.8,2.8,fc='#e0c27a',ec='#7a5a12',zorder=4))
jn=(hx-17,PY+30)
line(ax,[P['P_SPKG'],(P['P_SPKG'][0],PY+60),jn],Bk)
line(ax,[HP['T-NC'],(HP['T-NC'][0],PY+14),(hx-13,PY+30)],R)
bundle(ax,[(hx-13,PY+30),jn],[sp_p,sp_m],[R,Bk],pitch=4.5)
ax.text(58,40,'hoparlör kablosu\nburgulu çift',fontsize=6,color='#444',ha='center')
legend(ax,312,150,[(R,'kırmızı: sinyal/çıkış (+)'),(Bk,'siyah: GND / şase'),(Y,'sarı: GAIN 3 (giriş ucu)'),(Bl,'mavi: pot orta ucu (wiper)'),(O,'turuncu / mor: ISF uçları'),
 (G,'yeşil kesik: pot gövdeleri → VOL 1 (isteğe bağlı)'),(None,'Burgu: yaklaşık 1 tur / 1.5–2 cm, sıkı.'),(None,'Pot kabloları birlikte, hoparlör ve besleme'),(None,'kablolarından en az 2–3 cm uzakta geçsin.')],title='Renkler ve kurallar')
fig.savefig('../images/4_panel_kablolama.png',dpi=160,bbox_inches='tight',facecolor='white')
print('ok4')
# ============ IMAGE 5: power, LED, grounding ============
fig,ax=base('Besleme, LED ve Topraklama Kablolaması',
 'Görünüm: kartın sağ kenarı (üstten bakış). DC jak arka panelde, güç anahtarı ve LED ön panelde.',xlim=(0,330),ylim=(-30,168))
# board right part (top view)
ax.add_patch(Rectangle((150,40),70,90,fc='#f4efe2',ec='black',lw=1.4,zorder=1))
ax.text(152,44,'KART (sağ kenar, üstten)',fontsize=7,va='bottom',color='#444')
pv=(214,122); pg=(214,113); la=(214,72); lk=(214,63)
for p,l in [(pv,'+12V (anahtar)'),(pg,'GND (DC jak)'),(la,'LED +'),(lk,'LED −')]:
    ax.add_patch(Circle(p,1.9,fc='#d9a441',ec='#7a5a12',lw=0.8,zorder=5)); ax.add_patch(Circle(p,0.6,fc='white',zorder=6))
    ax.text(p[0]-3,p[1],l,fontsize=6.6,ha='right',va='center',color='#5b2c00',zorder=6)
ax.text(185,95,'TDA2003 +\nsoğutucu\n(kartın arka kenarı)',fontsize=6.3,ha='center',color='#666')
# back panel with DC jack
ax.add_patch(Rectangle((300,60),5,85,fc='#7f8c8d',ec='black',lw=1)); ax.text(308,102,'ARKA PANEL',fontsize=7,rotation=90,va='center')
ax.add_patch(Rectangle((282,108),16,20,fc='#cfd3d8',ec='#555',lw=1.2,zorder=2)); ax.text(290,118,'DC JAK\n5.5/2.1',fontsize=6.3,ha='center',va='center',fontweight='bold')
dcp=(283,124); dcn=(283,113); dcs=(283,108.5)
for p,l in [(dcp,'orta pin (+)'),(dcn,'gövde (−)')]:
    ax.add_patch(Rectangle((p[0]-4,p[1]-1.2),5,2.4,fc='#e0c27a',ec='#7a5a12',zorder=4)); ax.text(p[0]-1.5,p[1]+2,l,fontsize=5.6,ha='center',va='bottom')
# fuse holder
ax.add_patch(Rectangle((246,128),18,6,fc='#eee',ec='#555',lw=1.1,zorder=2)); ax.text(255,136,'SİGORTA 1A yavaş (T)',fontsize=6.3,ha='center',va='bottom')
# front panel: power switch + LED
ax.add_patch(Rectangle((60,-12),5,150,fc='#7f8c8d',ec='black',lw=1)); ax.text(57,60,'ÖN PANEL',fontsize=7,rotation=90,va='center',ha='right')
ax.add_patch(Rectangle((68,98),14,18,fc='#cfd3d8',ec='#555',lw=1.2,zorder=2)); ax.text(75,107,'GÜÇ\nanahtarı\nSW2',fontsize=6.2,ha='center',va='center',fontweight='bold')
sw1=(83,112); sw2=(83,102)
for p in (sw1,sw2): ax.add_patch(Rectangle((p[0],p[1]-1.2),4.5,2.4,fc='#e0c27a',ec='#7a5a12',zorder=4))
sw1=(87,112); sw2=(87,102)
# LED
ax.add_patch(Circle((74,66),4,fc='#ffe066',ec='#a68a00',lw=1.2,zorder=2)); ax.text(74,59,'LED (sarı)',fontsize=6.3,ha='center',va='top',fontweight='bold')
lA=(86,69); lK=(86,63)
line(ax,[(77,68),lA],'#888',1.4); line(ax,[(77,64),lK],'#888',1.4)
ax.text(87,72,'uzun bacak (+)',fontsize=5.6,va='bottom'); ax.text(87,60,'kısa bacak / düz kenar (−)',fontsize=5.6,va='top')
# wires
line(ax,[dcp,(272,124),(272,131),(264,131)],R)
line(ax,[(246,131),(238,131)],R)
bundle(ax,[(238,131),pv],[sw1,sw2],[R,O],via=[(200,136),(130,118)],pitch=5)
ax.text(165,134,'güç anahtarına giden ve dönen iki tel birlikte burgulu',fontsize=6.2,ha='center',va='bottom',color='#444')
ax.text(150,112,'kırmızı: sigortadan anahtara\nturuncu: anahtardan karta (+12V)',fontsize=5.8,ha='center',va='top',color='#444')
line(ax,[dcn,pg],Bk)
ax.text(250,110.5,'GND: DC jak gövdesi → kart\n(tek tel, kısa, tek nokta)',fontsize=6.2,ha='center',va='top')
bundle(ax,[lA,lK],[la,lk],[R,Bk],via=[(130,66),(190,68)],pitch=5)
ax.text(150,58,'LED çifti burgulu (kritik değil)',fontsize=6,ha='center',va='top',color='#444')
# notes box
notes=['TOPRAKLAMA KURALLARI',
'1. DC jakın gövdesi (−) karta SADECE "GND (DC jak)" noktasından bağlanır.',
'2. Giriş jakının şasesi sadece "GİRİŞ şase" noktasına gider; başka bir yere bağlama.',
'3. Jak gövdelerini ve pot gövdelerini birbirine ya da ayrıca toprağa bağlama.',
'   (İstisna: pot gövdeleri tek bir telle VOL 1/GND\'ye bağlanabilir, bkz. ön panel görseli.)',
'4. İç yüzeye bakır bant/folyo koyarsan, tek bir telle "GND (DC jak)" noktasına bağla.',
'5. Besleme ve hoparlör kablolarını giriş ve pot kablolarından en az 2–3 cm uzakta geçir;',
'   kesişmeleri gerekiyorsa dik açıyla kesiştir.',
'6. Adaptör fişinin orta ucu + olmalı (etiketinde ⊖–◉–⊕ işareti). Ters bağlansa D1 korur.']
ax.add_patch(FancyBboxPatch((70,-26),240,44,boxstyle='round,pad=1',fc='white',ec='#999',lw=0.8))
for i,t in enumerate(notes):
    ax.text(73,15-i*4.6,t,fontsize=6.9 if i else 7.6,fontweight='bold' if i==0 else 'normal',va='top')
fig.savefig('../images/5_besleme_kablolama.png',dpi=160,bbox_inches='tight',facecolor='white')
print('ok5')
