import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch
from geom import *
R='#d62728'; Bk='#222222'; Bl='#1f77b4'; Y='#e6a700'; G='#2ca02c'; O='#ff7f0e'
def _res(pts):
    pts=np.array(pts,float); seg=np.sqrt(((pts[1:]-pts[:-1])**2).sum(1)); L=seg.sum()
    t=np.linspace(0,L,max(80,int(L*8))); cum=np.concatenate([[0],np.cumsum(seg)])
    return np.array([np.interp(t,cum,pts[:,0]),np.interp(t,cum,pts[:,1])]).T,t
def line(ax,pts,c,lw=1.9,ls='-'):
    pts=np.array(pts,float); ax.plot(pts[:,0],pts[:,1],color=c,lw=lw,ls=ls,solid_capstyle='round',zorder=5)
def bundle(ax,starts,ends,cols,via=None,pitch=3.5,amp=1.0,lw=1.8):
    s0=np.mean(np.array(starts,float),0); e0=np.mean(np.array(ends,float),0)
    P,t=_res([s0]+(via or [])+[e0]); a=P[int(len(P)*0.15)]; b=P[int(len(P)*0.85)]
    Pt,tt=_res([a]+[np.array(v) for v in (via or [])]+[b])
    d=np.gradient(Pt,axis=0); n=np.stack([-d[:,1],d[:,0]],1); n/=np.linalg.norm(n,axis=1,keepdims=True)+1e-9
    for i,c in enumerate(cols):
        Q=Pt+n*(amp*np.sin(2*np.pi*tt/pitch+2*np.pi*i/len(cols)))[:,None]
        ax.plot(Q[:,0],Q[:,1],color=c,lw=lw,zorder=5); line(ax,[starts[i],Q[0]],c,lw); line(ax,[Q[-1],ends[i]],c,lw)
pl={k:tuple(v) for k,v in json.load(open(sys.argv[1])).items()}
OUT=sys.argv[2]
fig,ax=plt.subplots(figsize=(17,12.5))
ax.set_xlim(-10,BW+45); ax.set_ylim(BH+72,-40); ax.set_aspect('equal'); ax.axis('off')
ax.text(-8,-36,'Kablolama (kart v2) — sadece 4 bağlantı: SW1, güç anahtarı, DC jak, hoparlör',fontsize=14,fontweight='bold',va='top')
ax.text(-8,-29,'Üstten bakış (kartın parça yüzü). Pot, jak ve LED karta lehimli; burada sadece kabloyla bağlanan parçalar gösterildi.',fontsize=8.5,va='top')
ax.add_patch(Rectangle((0,0),BW,BH,fc='#f4efe2',ec='black',lw=1.4,zorder=1))
for ref in ['J1','RV1','RV2','RV3','J2','D2','U2','TB1','TB2','F1','D1','C1','C25','C7','MH1','MH2','MH3']:
    if ref not in pl: continue
    x0,x1,y0,y1=body_box_mm(ref,pl)
    ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc='#e3e8ef',ec='#8899aa',lw=0.7,zorder=2))
    ax.text((x0+x1)/2,(y0+y1)/2,ref,fontsize=6,ha='center',va='center',color='#556',zorder=3)
def padpt(ref,i=0): return pins_mm(ref,pl)[i]
def pad(ref,i,label,dy=-3):
    p=padpt(ref,i); ax.add_patch(Circle(p,1.4,fc='#d9a441',ec='#7a5a12',zorder=6)); ax.add_patch(Circle(p,0.45,fc='white',zorder=7))
    ax.text(p[0],p[1]+dy,label,fontsize=6,ha='center',va='bottom' if dy<0 else 'top',color='#5b2c00',zorder=7,fontweight='bold')
    return p
# front panel line
FP_Y=BH+3
ax.add_patch(Rectangle((-6,FP_Y),BW+12,3,fc='#7f8c8d',ec='black',lw=1,zorder=1))
ax.text(BW/2,BH+42.5,'ÖN PANEL (önden bakan kişi soldan sağa: GİRİŞ · GAIN · SW1 · ISF · VOLUME · KULAKLIK · LED · GÜÇ)',fontsize=7.5,ha='center',color='#333')
# ---- switches mounted rotated 90 deg (lugs in a vertical column -> lever moves up/down) ----
# top view: lug column is vertical, so from above only one lug is seen; lugs drawn slightly fanned for clarity
sx=FRONT_X['SW1']; by0=BH-15
ax.add_patch(Rectangle((sx-4,by0),8,15,fc='#5b8fd9',ec='#234',lw=1.1,zorder=3,alpha=0.85)); ax.text(sx,by0+7.5,'SW1',fontsize=5.5,ha='center',va='center',color='white',fontweight='bold',zorder=4,rotation=90)
lug={}
for name,dx in [('üst',-2.2),('orta',0),('alt',2.2)]:
    lug[name]=(sx+dx,by0-2.5); ax.add_patch(Rectangle((sx+dx-0.6,by0-4),1.2,4,fc='#e0c27a',ec='#7a5a12',zorder=4))
pa=pad('P_SWD',0,'SW1 A',dy=-2.5); pc=pad('P_SWC',0,'SW1 orta',dy=-5.5); pb=pad('P_SWB',0,'SW1 B',dy=-2.5)
bundle(ax,[pa,pc,pb],[lug['üst'],lug['orta'],lug['alt']],[Bk,Bl,Y],pitch=2.2,amp=0.6)
ax.text(sx+11,by0-14,'SW1: üst bacak → SW1 A (siyah)\norta bacak → SW1 orta (mavi)\nalt bacak → SW1 B (sarı)',fontsize=5.6,color='#333',zorder=8)
px=FRONT_X['SW2']; py0=BH-17
ax.add_patch(Rectangle((px-5,py0),10,17,fc='#d64545',ec='#511',lw=1.1,zorder=3,alpha=0.85)); ax.text(px,py0+8.5,'GÜÇ',fontsize=5.5,ha='center',va='center',color='white',fontweight='bold',zorder=4,rotation=90)
plug={}
for name,dx in [('üst',-2.2),('orta',0),('alt',2.2)]:
    plug[name]=(px+dx,py0-2.5); ax.add_patch(Rectangle((px+dx-0.6,py0-4),1.2,4,fc='#e0c27a',ec='#7a5a12',zorder=4))
p1=pad('P_PW1',0,'GÜÇ orta',dy=-5.5); p2=pad('P_PW2',0,'GÜÇ uç',dy=-2.5)
bundle(ax,[p1,p2],[plug['orta'],plug['alt']],[R,O],pitch=2.2,amp=0.6)
ax.text(px-46,py0-12,'Güç: bir sütunun orta bacağı → GÜÇ orta (kırmızı),\naynı sütunun alt bacağı → GÜÇ uç (turuncu).\nDiğer bacaklar boş.',fontsize=5.6,color='#333',zorder=8)
# ---- rear-view insets (looking at the back of the front panel from inside the box) ----
def inset(x0,title,kind):
    y0=BH+7
    ax.add_patch(FancyBboxPatch((x0,y0),34,30,boxstyle='round,pad=0.6',fc='white',ec='#999',lw=0.8,zorder=6))
    ax.text(x0+17,y0+1,title,fontsize=6.2,ha='center',va='top',fontweight='bold',zorder=7)
    ax.add_patch(Rectangle((x0+2,y0+27.5),30,1.5,fc='#999',ec='none',zorder=7)); ax.text(x0+17,y0+29.6,'kart yüzeyi (aşağıda)',fontsize=4.6,ha='center',va='top',color='#555',zorder=7)
    cx=x0+17
    if kind=='sw1':
        ax.add_patch(Rectangle((cx-4,y0+6),8,13,fc='#5b8fd9',ec='#234',zorder=7))
        for i,(lab,col) in enumerate([('A (üst)',Bk),('orta',Bl),('B (alt)',Y)]):
            yy=y0+8.5+i*4; ax.add_patch(Rectangle((cx-1.6,yy-0.9),3.2,1.8,fc='#e0c27a',ec='#7a5a12',zorder=8))
            ax.plot([cx+1.6,cx+9],[yy,yy],color=col,lw=1.6,zorder=8); ax.text(cx+9.5,yy,lab,fontsize=5,va='center',zorder=8)
        ax.text(x0+1.5,y0+21.5,'Kol YUKARI = Bright\nORTA = Normal\nAŞAĞI = Dark',fontsize=5,va='top',zorder=8)
    else:
        ax.add_patch(Rectangle((cx-6,y0+5),12,15,fc='#d64545',ec='#511',zorder=7))
        for c,dx in enumerate([-3,3]):
            for i in range(3):
                yy=y0+8+i*4.5; ax.add_patch(Rectangle((cx+dx-1.4,yy-0.9),2.8,1.8,fc='#e0c27a',ec='#7a5a12',zorder=8))
        ax.plot([cx+4.4,cx+11],[y0+12.5,y0+12.5],color=R,lw=1.6,zorder=8); ax.text(cx+11.5,y0+12.5,'orta',fontsize=5,va='center',zorder=8)
        ax.plot([cx+4.4,cx+11],[y0+17,y0+17],color=O,lw=1.6,zorder=8); ax.text(cx+11.5,y0+17,'alt',fontsize=5,va='center',zorder=8)
        ax.text(x0+1.5,y0+21.5,'Kol YUKARI = AÇIK\nAŞAĞI = KAPALI',fontsize=5,va='top',zorder=8)
inset(FRONT_X['SW1']-17,'SW1 arkadan (bacaklar dikey)','sw1')
inset(FRONT_X['SW2']-30,'Güç anahtarı arkadan','pw')
# rear: DC jack and speaker
RP_Y=-6
ax.add_patch(Rectangle((-6,RP_Y-3),BW+12,3,fc='#7f8c8d',ec='black',lw=1,zorder=1)); ax.text(20,RP_Y-4,'ARKA PANEL',fontsize=7.5,va='bottom',color='#333')
t1a=pad('TB1',0,'+',dy=3.5); t1b=pad('TB1',1,'−',dy=3.5)
dcx=BW+22; ax.add_patch(Circle((dcx,8),6,fc='#333',ec='#111',zorder=3)); ax.text(dcx,8,'DC\njak',fontsize=6,color='white',ha='center',va='center',zorder=4,fontweight='bold')
dcp=(dcx-3,15); dcn=(dcx+3,15); ax.text(dcp[0],17.5,'orta pin\n(+)',fontsize=5.3,ha='center',va='top'); ax.text(dcn[0],17.5,'gövde\n(−)',fontsize=5.3,ha='center',va='top')
for p in (dcp,dcn): ax.add_patch(Rectangle((p[0]-0.8,p[1]-1.5),1.6,3,fc='#e0c27a',ec='#7a5a12',zorder=4))
bundle(ax,[t1a,t1b],[dcp,dcn],[R,Bk],via=[(BW+6,-1)],pitch=3.5)
ax.text(dcx-6,26,'DC jak: kesici kulağı\nboş kalır (fiş takılıyken\ngövdeyle bip veren = −)',fontsize=5.5,color='#333')
t2a=pad('TB2',0,'+',dy=3.5); t2b=pad('TB2',1,'−',dy=3.5)
spx,spy=BW+24,48; ax.add_patch(Circle((spx,spy),9,fc='#ddd',ec='#555',zorder=3)); ax.text(spx,spy,'HOPARLÖR\n4Ω',fontsize=6,ha='center',va='center',zorder=4,fontweight='bold')
sp=(spx-5,spy-8); sm=(spx+5,spy-8); ax.text(sp[0]-1,sp[1]-1,'+',fontsize=7,color=R,ha='right'); ax.text(sm[0]+1,sm[1]-1,'−',fontsize=7)
bundle(ax,[t2a,t2b],[sp,sm],[R,Bk],via=[((t2a[0]+t2b[0])/2,-4),(BW+12,-4),(BW+16,30)],pitch=4)
ax.text(spx-12,spy+14,'hoparlörde lehim, kartta klemens; kablo burgulu',fontsize=5.6,color='#333')
# legend / rules
rules=['KURALLAR',
'• Tüm kablolar çift/üçlü burgulu (yaklaşık 1 tur / 1.5 cm).',
'• Hoparlör ve DC kabloları kartın SAĞ ARKA köşesinde kalır; girişin olduğu sol tarafa uzatma.',
'• SW1 kabloları 3–5 cm; potların üstünden değil, kart kenarına yakın geçir.',
'• DC jak gövdesi karta sadece TB1 (−) üzerinden bağlanır; jak/pot gövdelerini ayrıca toprağa bağlama.',
'• İç yüzeye bakır bant konursa tek telle TB1 (−)\'ye bağla.',
'• Anahtarlar panele bacakları DİKEY (üst-orta-alt) olacak şekilde takılır; böylece kol yukarı-aşağı çalışır.',
'• Anahtar gövdesinin alt kenarı kartın en az 3 mm üstünde kalmalı (gövde merkezi kart yüzeyinden ≈ 10 mm yukarıda).']
ax.add_patch(FancyBboxPatch((-6,BH+46),BW+12,23,boxstyle='round,pad=0.8',fc='white',ec='#999',lw=0.8,zorder=1))
for i,t in enumerate(rules): ax.text(-4,BH+48+i*2.6,t,fontsize=7 if i else 7.6,fontweight='bold' if i==0 else 'normal',va='top')
fig.savefig(f'{OUT}/4_kablolama.png',dpi=170,bbox_inches='tight',facecolor='white')
print('ok')
