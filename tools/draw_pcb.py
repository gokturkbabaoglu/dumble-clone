import sys, pickle, math
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, Polygon
from design import *
from place import W,H,pins_of
from final import raster, PX, BW, BH
from render import pin_mm
D=pickle.load(open('final_geom.pkl','rb'))
pl,items,g=D['pl'],D['items'],D['g']
cu=raster(items,lambda n:n!='GND')|g
holes=[]
for n,k,data in items:
    if k=='pad': holes.append(data)
jumpers=[data for n,k,data in items if k=='jumper']
jnets=[n for n,k,data in items if k=='jumper']
def copper_img(mirror=False,col=(0.80,0.50,0.20),bg=(0.13,0.36,0.22)):
    img=np.zeros(cu.shape+(4,))
    img[cu]=list(col)+[1]
    if mirror: img=img[:,::-1]
    return img
def parts(ax,mirror=False,detail=True):
    X=(lambda x:BW-x) if mirror else (lambda x:x)
    for ref,(fp,val,ns) in C.items():
        f=FP[fp]; x,y,r=pl[ref]
        ps=[pin_mm(ref,pl,i) for i in range(len(ns))]
        cx=sum(p[0] for p in ps)/len(ps); cy=sum(p[1] for p in ps)/len(ps)
        b=f['body']
        if fp=='PAD':
            if not mirror:
                lbl=val
                ax.text(X(ps[0][0]),ps[0][1]-2.2,lbl,fontsize=4.6,rotation=90 if ps[0][1]>BH-8 else 0,ha='center' if ps[0][1]>BH-8 else ('right' if True else 'left'),va='bottom' if ps[0][1]>BH-8 else 'center',color='#5b2c00',zorder=8)
            else:
                ax.text(X(ps[0][0]),ps[0][1]-2.2,val,fontsize=4.6,rotation=90 if ps[0][1]>BH-8 else 0,ha='center' if ps[0][1]>BH-8 else 'left',va='bottom' if ps[0][1]>BH-8 else 'center',color='#fff3c4',zorder=8)
            continue
        if not detail:
            ax.text(X(cx),cy,ref,fontsize=4.2,ha='center',va='center',color='#e8f0ff',alpha=0.85,zorder=8)
            continue
        ec='#163e7a'
        if b[0]=='circ':
            ax.add_patch(Circle((X(cx),cy),b[1]/2,fc='#e8eef7',ec=ec,lw=1.0,zorder=3,alpha=0.92))
            p1=ps[1]; ang=math.degrees(math.atan2(-(p1[1]-cy),X(p1[0])-X(cx)))
            # negative stripe band (matplotlib y inverted -> use data coords)
            vx=X(p1[0])-X(cx); vy=p1[1]-cy; a=math.degrees(math.atan2(vy,vx))
            ax.add_patch(Wedge((X(cx),cy),b[1]/2,a-35,a+35,width=b[1]*0.12,fc='#5b6b80',ec='none',zorder=3.5))
            p0=ps[0]; ux=X(p0[0])-X(cx); uy=p0[1]-cy; L=math.hypot(ux,uy) or 1
            ax.text(X(p0[0])+ux/L*2.3,p0[1]+uy/L*2.3,'+',fontsize=7,color='#c0392b',ha='center',va='center',fontweight='bold',zorder=9)
        elif b[0]=='pw':
            w,h=b[1],b[2]
            ax.add_patch(Rectangle((X(x*U)-w/2,y*U-h-0.8),w,h,fc='#d0d8e2',ec=ec,lw=1.0,zorder=3))
            ax.add_patch(Rectangle((X(x*U)-w/2-3,y*U-h-0.8-15),w+6,15,fc='#c4c4c4',ec='#555',lw=0.8,zorder=2,hatch='|||'))
            ax.text(X(x*U),y*U-h-8,'SOĞUTUCU\n(kart dışına taşar)',fontsize=4.6,ha='center',va='center',zorder=4)
            for i,p in enumerate(ps): ax.text(X(p[0]),p[1]+(2.3 if i%2 else -2.1),str(i+1),fontsize=4.2,ha='center',va='center',color='#163e7a',zorder=9)
        else:
            w,h=b[1],b[2]
            if r%180==90: w,h=h,w
            if fp=='TO92':
                ax.add_patch(Rectangle((X(cx)-w/2,cy-h/2),w,h,fc='#e8eef7',ec=ec,lw=1.0,zorder=3))
                for i,lbl in enumerate(['G','S','D']):
                    p=ps[i]; dxo=0; dyo=0
                    if r%180==0: dyo=-2.4
                    else: dxo=-2.4
                    ax.text(X(p[0])+dxo,p[1]+dyo,lbl,fontsize=5,ha='center',va='center',color='#c0392b',fontweight='bold',zorder=9)
            else:
                ax.add_patch(Rectangle((X(cx)-w/2,cy-h/2),w,h,fc='#e8eef7',ec=ec,lw=1.0,zorder=3,ls='--' if val.endswith('*') else '-'))
            if fp=='DIP8':
                p=ps[0]; ax.add_patch(Circle((X(p[0]),p[1]),1.4,fill=False,ec='#c0392b',lw=1,zorder=9))
                ax.text(X(cx),cy+1.5,'pin1 ○',fontsize=4,ha='center',color='#c0392b',zorder=9)
            if fp=='DO201':
                p=ps[1]; vx=p[0]-ps[0][0]; vy=p[1]-ps[0][1]; L=math.hypot(vx,vy)
                bx,by=cx+vx/L*3.2,cy+vy/L*3.2
                if abs(vx)>abs(vy): ax.add_patch(Rectangle((X(bx)-0.6,by-h/2),1.2,h,fc='#555',zorder=4))
                else: ax.add_patch(Rectangle((X(bx)-w/2,by-0.6),w,1.2,fc='#555',zorder=4))
            if fp=='TRIM':
                ax.text(X(ps[1][0]),ps[1][1]+(2.6 if r%180==0 else 0),'ayar',fontsize=4,ha='center',color='#555',zorder=9)
        rot=90 if (r%180==90 and fp in ('R','CF','DO201','TRIM')) else 0
        ax.text(X(cx),cy,f'{ref}\n{val}',fontsize=4.4,ha='center',va='center',rotation=rot,color='#0b2d5c',zorder=9,linespacing=0.9,fontweight='bold')
def holes_draw(ax,mirror=False,fc='#d9a441',hc='white'):
    X=(lambda x:BW-x) if mirror else (lambda x:x)
    for (p,d) in holes:
        ax.add_patch(Circle((X(p[0]),p[1]),0.45,fc=hc,ec='none',zorder=6))
def frame(ax,mirror=False):
    ax.set_xlim(-8,BW+8); ax.set_ylim(BH+12,-30); ax.set_aspect('equal'); ax.axis('off')
    X=(lambda x:BW-x) if mirror else (lambda x:x)
    for (px,py) in [(3,3),(BW-3,BH-3),(3,BH-3),(BW-3,3)]:
        ax.add_patch(Circle((X(px),py),1.6,fc='white',ec='black',lw=0.8,zorder=7))
# ---------- FRONT ----------
fig,ax=plt.subplots(figsize=(14,11))
ax.add_patch(Rectangle((0,0),BW,BH,fc='#f2ecd9',ec='black',lw=1.5,zorder=0))
ax.imshow(copper_img(col=(0.85,0.55,0.25)),extent=(0,BW,BH,0),alpha=0.22,zorder=1,interpolation='antialiased')
parts(ax)
for n,k,data in items:
    if k=='pad':
        (x,y),d=data; ax.add_patch(Circle((x,y),d/2,fc='#d9a441',ec='#7a5a12',lw=0.4,zorder=5))
holes_draw(ax)
for i,(a,b) in enumerate(jumpers):
    ax.plot([a[0],b[0]],[a[1],b[1]],color='#c0392b',lw=2.6,zorder=10,solid_capstyle='round')
    if abs(a[1]-b[1])<0.01:
        xl=min(a[0],b[0]); ax.text(xl-1.8,a[1],f'J{i+1}',fontsize=6.5,color='#c0392b',fontweight='bold',ha='right',va='center',zorder=11,bbox=dict(boxstyle='round,pad=0.1',fc='white',ec='none',alpha=0.85))
    else:
        yt=min(a[1],b[1]); ax.text(a[0],yt-1.8,f'J{i+1}',fontsize=6.5,color='#c0392b',fontweight='bold',ha='center',va='bottom',zorder=11,bbox=dict(boxstyle='round,pad=0.1',fc='white',ec='none',alpha=0.85))
frame(ax)
ax.text(0,-26,'Baskı Devre — ÖN YÜZ (parça tarafı, üstten bakış)',fontsize=13,fontweight='bold',va='top')
jl='  '.join(f'J{i+1}: {jnets[i]}, {math.hypot(a[0]-b[0],a[1]-b[1]):.0f} mm' for i,(a,b) in enumerate(jumpers))
ax.text(0,-20,f'Kart: {BW:.0f} × {BH:.0f} mm, tek yüz bakır. Kırmızı çizgiler = parça tarafına lehimlenen tel köprüler ({len(jumpers)} adet): {jl}',fontsize=7.2,va='top')
ax.text(0,-16.5,'Köprüler için İZOLELİ tek damarlı tel kullan (J1, R25 bacağının 1.3 mm yanından geçer). Ön kenar (alt) = ön panel tarafı, sağ kenar = besleme ve LED.\nKesikli çerçeveli parçalar (C9 22µ*, R7 15k*) duruma göre takılır. Soluk turuncu = alttaki bakır yollar. Q1 G/S/D sırasını takmadan önce ölçerek doğrula.',fontsize=7.2,va='top')
ax.text(BW/2,BH+9,'▼ ÖN PANEL TARAFI ▼',fontsize=8,ha='center',color='#2b7bb9')
fig.savefig('../images/2_pcb_on_yuz.png',dpi=260,bbox_inches='tight',facecolor='white')
# ---------- BACK ----------
fig,ax=plt.subplots(figsize=(14,11))
ax.add_patch(Rectangle((0,0),BW,BH,fc='#1f5a36',ec='black',lw=1.5,zorder=0))
ax.imshow(copper_img(mirror=True,col=(0.84,0.56,0.27)),extent=(0,BW,BH,0),zorder=1,interpolation='antialiased')
holes_draw(ax,mirror=True,hc='#111')
parts(ax,mirror=True,detail=False)
for i,(a,b) in enumerate(jumpers):
    for p in (a,b): ax.text(BW-p[0],p[1]+2.2,f'J{i+1}',fontsize=5.5,color='#ffdede',ha='center',fontweight='bold',zorder=11)
frame(ax,mirror=True)
ax.text(0,-26,'Baskı Devre — ARKA YÜZ (bakır tarafı, alttan bakış = ön yüzün aynası)',fontsize=13,fontweight='bold',va='top')
ax.text(0,-20,'Yollar: sinyal 1.0 mm, besleme/çıkış 1.3 mm, yol–yol aralığı en az ≈0.7 mm, dolgu aralığı 0.55 mm. Geri kalan alan GND dolgusu (termal bağlantılı pedler).',fontsize=7.2,va='top')
ax.text(0,-16.5,'Toner transferi için bu görüntüyü değil, ayrıca verilen 1:1 PDF\'i kullan. Delik: küçük parçalar 0.8–0.9 mm, büyük elko/diyot/TDA/kablo noktaları 1.0–1.2 mm.',fontsize=7.2,va='top')
ax.text(BW/2,BH+9,'▼ ÖN PANEL TARAFI ▼',fontsize=8,ha='center',color='#2b7bb9')
fig.savefig('../images/3_pcb_arka_yuz.png',dpi=260,bbox_inches='tight',facecolor='white')
# ---------- TONER 1:1 PDF ----------
from matplotlib.backends.backend_pdf import PdfPages
fig=plt.figure(figsize=(210/25.4,297/25.4))
ox,oy=(210-BW)/2,40
ax=fig.add_axes([ox/210,1-(oy+BH)/297,BW/210,BH/297])
img=np.ones(cu.shape+(3,)); img[cu]=0
ax.imshow(img,extent=(0,BW,BH,0),interpolation='antialiased')
for (p,d) in holes: ax.add_patch(Circle(p,0.35,fc='white',ec='none'))
ax.add_patch(Rectangle((0,0),BW,BH,fill=False,ec='black',lw=0.4))
ax.set_xlim(0,BW); ax.set_ylim(BH,0); ax.axis('off')
fig.text(0.5,1-15/297,'12V Gitar Amfisi — BAKIR KATMANI, TONER TRANSFERİ İÇİN (1:1)',ha='center',fontsize=11,fontweight='bold')
fig.text(0.5,1-22/297,'Yazdırırken ölçeklendirme KAPALI (%100 / Gerçek boyut). Aşağıdaki 50 mm cetvelini kumpasla kontrol et.',ha='center',fontsize=8)
fig.text(0.5,1-27/297,'Bu görüntü zaten doğru yönde: kâğıdı yüzü bakıra gelecek şekilde koyunca bakırda alttan bakış (arka yüz görseli) oluşur.',ha='center',fontsize=7)
ax2=fig.add_axes([ox/210,1-(oy+BH+20)/297,50/210,6/297]); ax2.set_xlim(0,50); ax2.set_ylim(0,6); ax2.axis('off')
ax2.plot([0,50],[3,3],color='k',lw=1)
for i in range(0,51,10): ax2.plot([i,i],[1.5,4.5],color='k',lw=0.8); ax2.text(i,5,str(i),fontsize=5,ha='center')
ax2.text(52,3,'mm',fontsize=6,va='center')
# mirrored check text on copper
fig.text(0.5,1-(oy+BH+32)/297,'Kart ölçüsü: %.1f × %.1f mm'%(BW,BH),ha='center',fontsize=8)
fig.savefig('../docs/6_toner_transfer_1e1.pdf')
print('done', len(jumpers))
