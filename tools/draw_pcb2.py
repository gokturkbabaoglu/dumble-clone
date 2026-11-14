import sys, os, pickle, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, Polygon, FancyBboxPatch
from geom import *
from final2 import raster, PX, mount_holes
OUT=sys.argv[2] if len(sys.argv)>2 else 'out'
os.makedirs(OUT,exist_ok=True)
EC='#163e7a'; LBL='#0b2d5c'
def draw_parts(ax,pl,detail=True,X=lambda x:x,txtcol=LBL):
    for ref,(fp,val,ns) in C.items():
        f=FP[fp]; x,y,r=pl[ref]; ps=pins_mm(ref,pl); b=f['body']
        cx=sum(p[0] for p in ps)/len(ps); cy=sum(p[1] for p in ps)/len(ps)
        if fp.startswith('KO') and not detail: continue
        if fp=='MH' and not detail: continue
        if fp.startswith('KO'):
            w,dd=b[1],b[2]; ax_,ay_=x*U,y*U
            ax.add_patch(Rectangle((ax_-w/2,ay_-dd),w,dd,fill=False,ec='#c0392b',lw=0.9,ls=(0,(3,2)),zorder=8))
            ax.text(ax_,ay_-dd/2,val+'\n(panelde, üstte)',fontsize=4.2,ha='center',va='center',color='#c0392b',zorder=9); continue
        if fp=='MH':
            ax.add_patch(Circle(ps[0],1.6,fc='white',ec='black',lw=0.8,zorder=8)); ax.text(ps[0][0],ps[0][1]+4,'M3',fontsize=4,ha='center',zorder=9,color='#555'); continue
        if fp=='PAD':
            ax.text(X(ps[0][0]),ps[0][1]-2.4,val,fontsize=4.6,ha='center',va='bottom',color='#8a4b00' if detail else '#fff3c4',zorder=9,fontweight='bold')
            continue
        if not detail:
            ax.text(X(cx),cy,ref,fontsize=4.0,ha='center',va='center',color='#e8f0ff',alpha=0.85,zorder=9); continue
        if b[0]=='circ':
            p0,p1=ps[0],ps[1]; ccx=(p0[0]+p1[0])/2; ccy=(p0[1]+p1[1])/2
            if len(ps)==3: ccx=(p0[0]+ps[2][0])/2
            ax.add_patch(Circle((ccx,ccy),b[1]/2,fc='#e8eef7',ec=EC,lw=1.0,zorder=3,alpha=0.93))
            a=math.degrees(math.atan2(p1[1]-ccy,p1[0]-ccx))
            ax.add_patch(Wedge((ccx,ccy),b[1]/2,a-35,a+35,width=b[1]*0.13,fc='#5b6b80',ec='none',zorder=3.5))
            ux,uy=p0[0]-ccx,p0[1]-ccy; L=math.hypot(ux,uy) or 1
            ax.text(p0[0]+ux/L*2.2,p0[1]+uy/L*2.2,'+',fontsize=7,color='#c0392b',ha='center',va='center',fontweight='bold',zorder=9)
            ax.text(ccx,ccy+(b[1]/2*0.45 if b[1]>7 else 0),f'{ref}\n{val}',fontsize=4.3,ha='center',va='center',color=LBL,zorder=9,fontweight='bold',linespacing=0.9)
            if len(ps)==3: ax.text(ps[2][0],ps[2][1]+1.8,'5/7.5',fontsize=3.6,ha='center',color='#555',zorder=9)
            continue
        if b[0]=='front':
            w,d=b[1],b[2]; ax_,ay_=x*U,y*U
            ax.add_patch(Rectangle((ax_-w/2,ay_-d),w,d,fc='#dfe6ee',ec=EC,lw=1.1,zorder=3))
            if fp=='J635':
                ax.add_patch(Rectangle((ax_-5.1,ay_),10.2,9,fc='#bbb',ec='#555',lw=0.8,zorder=2))
            elif fp=='PJ324':
                ax.add_patch(Rectangle((ax_-3,ay_),6,3.5,fc='#bbb',ec='#555',lw=0.8,zorder=2))
            elif fp=='POT':
                ax.add_patch(Rectangle((ax_-3.5,ay_),7,7,fc='#bbb',ec='#555',lw=0.8,zorder=2))
                ax.add_patch(Rectangle((ax_-3,ay_+7),6,8,fc='#ddd',ec='#555',lw=0.8,zorder=2))
                for i,p in enumerate(ps): ax.text(p[0],p[1]-2.3,str(i+1),fontsize=4.5,ha='center',color='#c0392b',zorder=9,fontweight='bold')
            elif fp=='LED':
                ax.add_patch(Circle((ax_,ay_+1.5),LED_D/2,fc='#ffe066',ec='#a68a00',lw=0.8,zorder=2))
                ax.text(ps[0][0],ps[0][1]-2.2,'+',fontsize=6,color='#c0392b',ha='center',fontweight='bold',zorder=9)
            if fp in ('J635','PJ324'):
                names={'J635':['1 şase','2 kesici','3 uç'],'PJ324':['1','2','3','4','5']}[fp]
                for i,p in enumerate(ps): ax.text(p[0]+(2.3 if fp=='J635' else 1.6),p[1],names[i],fontsize=4.0,color='#c0392b',va='center',zorder=9,fontweight='bold')
            ax.text(ax_,ay_-d+2.2 if fp!='POT' else ay_-d+2.0,f'{ref}\n{val}',fontsize=4.6,ha='center',va='top',color=LBL,zorder=9,fontweight='bold',linespacing=0.9)
            continue
        if b[0]=='pw':
            w,h=b[1],b[2]; ax_,ay_=x*U,y*U; hw,hd=HS_KEEPOUT
            ax.add_patch(Rectangle((ax_-hw/2,ay_-0.8-hd),hw,hd,fc='#4a4a4a',ec='#222',lw=0.8,zorder=2,alpha=0.35,hatch='|||'))
            ax.add_patch(Rectangle((ax_-w/2,ay_-h-0.8),w,h,fc='#d0d8e2',ec=EC,lw=1.0,zorder=3))
            ax.text(ax_,ay_-0.8-hd+2,'klipsli soğutucu',fontsize=4.2,ha='center',va='top',zorder=4)
            for i,p in enumerate(ps): ax.text(p[0],p[1]+(2.3 if i%2 else -2.0),str(i+1),fontsize=4.0,ha='center',va='center',color=EC,zorder=9)
            ax.text(ax_,ay_-h/2-0.8,f'{ref} {val}',fontsize=4.4,ha='center',va='center',color=LBL,zorder=9,fontweight='bold')
            continue
        w,h=b[1],b[2]
        if r%180==90 and b[0] not in ('rectc',): w,h=h,w
        if b[0]=='rectc' and r%180==90: w,h=h,w
        ls='--' if val.endswith('*') else '-'
        fc={'FUSE':'#f3e6c0','TB2':'#7fb3d5'}.get(fp,'#e8eef7')
        ax.add_patch(Rectangle((cx-w/2,cy-h/2),w,h,fc=fc,ec=EC,lw=1.0,zorder=3,ls=ls))
        if fp=='TO92':
            for i,l in enumerate(['G','S','D']):   # Fairchild BF245B
                p=ps[i]; ax.text(p[0]+(0 if r%180==0 else -2.3),p[1]+(-2.3 if r%180==0 else 0),l,fontsize=5,ha='center',va='center',color='#c0392b',fontweight='bold',zorder=9)
        if fp=='DIP8':
            ax.add_patch(Circle(ps[0],1.4,fill=False,ec='#c0392b',lw=1,zorder=9))
        if fp=='DO201':
            vx=ps[1][0]-ps[0][0]; vy=ps[1][1]-ps[0][1]; L=math.hypot(vx,vy); bx,by=cx+vx/L*3.2,cy+vy/L*3.2
            if abs(vx)>abs(vy): ax.add_patch(Rectangle((bx-0.6,by-h/2),1.2,h,fc='#555',zorder=4))
            else: ax.add_patch(Rectangle((bx-w/2,by-0.6),w,1.2,fc='#555',zorder=4))
        if fp=='TB2':
            ax.text(cx,cy-h/2-1.0,'kablo girişi ↑',fontsize=3.8,ha='center',va='bottom',color='#555',zorder=9)
        rot=90 if (r%180==90 and fp in ('R','CF','CC','DO201','TRIM','CF1U','JMP')) else 0
        ax.text(cx,cy,f'{ref}\n{val}',fontsize=4.3,ha='center',va='center',rotation=rot,color=LBL,zorder=9,linespacing=0.9,fontweight='bold')
def frame(ax):
    ax.set_xlim(-8,BW+8); ax.set_ylim(BH+22,-26); ax.set_aspect('equal'); ax.axis('off')
if __name__=='__main__':
    D=pickle.load(open(sys.argv[1],'rb'))
    pl=D['pl']; items=D.get('items'); g=D.get('g')
    jumpers=[(n,d) for n,k,d in (items or []) if k=='jumper']
    # köprüler soldan sağa, arkadan öne numaralanır (K1, K2, …)
    jumpers.sort(key=lambda t:(round(min(t[1][0][0],t[1][1][0])/10),min(t[1][0][1],t[1][1][1])))
    def jlen(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
    cu=(raster(items,lambda n:n!='GND')|g) if items else None
    def holes(ax,X=lambda x:x,col='white'):
        for n,k,d in items:
            if k=='pad': ax.add_patch(Circle((X(d[0][0]),d[0][1]),d[2]/2,fc=col,ec='none',zorder=6))
        for n,k,dd in items:
            if k=='hole': ax.add_patch(Circle((X(dd[0][0]),dd[0][1]),1.6,fc='white',ec='black',lw=0.8,zorder=7))
    # FRONT
    fig,ax=plt.subplots(figsize=(16,11.5))
    ax.add_patch(Rectangle((0,0),BW,BH,fc='#f2ecd9',ec='black',lw=1.5,zorder=0))
    if cu is not None:
        img=np.zeros(cu.shape+(4,)); img[cu]=[0.85,0.55,0.25,1]
        ax.imshow(img,extent=(0,BW,BH,0),alpha=0.22,zorder=1,interpolation='antialiased')
    draw_parts(ax,pl)
    if items:
        for n,k,d in items:
            if k=='pad': ax.add_patch(Circle(d[0],d[1]/2,fc='#d9a441',ec='#7a5a12',lw=0.4,zorder=5))
        holes(ax)
        for i,(n,(a,b)) in enumerate(jumpers):
            # köprü = ayrı parça: gövde (izoleli tel) + iki delik + etiket
            hor=abs(a[1]-b[1])<0.01; L=jlen(a,b)
            x0,x1=sorted([a[0],b[0]]); y0,y1=sorted([a[1],b[1]])
            if hor: ax.add_patch(FancyBboxPatch((x0+1.2,a[1]-0.9),L-2.4,1.8,boxstyle='round,pad=0,rounding_size=0.9',fc='#f6d4cf',ec='#c0392b',lw=1.0,zorder=9))
            else: ax.add_patch(FancyBboxPatch((a[0]-0.9,y0+1.2),1.8,L-2.4,boxstyle='round,pad=0,rounding_size=0.9',fc='#f6d4cf',ec='#c0392b',lw=1.0,zorder=9))
            ax.plot([a[0],b[0]],[a[1],b[1]],color='#c0392b',lw=1.4,zorder=10,solid_capstyle='round')
            lab=f'K{i+1}\n{n} {L:.1f}'
            if hor: ax.text((x0+x1)/2,a[1]-1.4,lab,fontsize=5.0,color='#8e1f12',fontweight='bold',ha='center',va='bottom',zorder=11,linespacing=0.9,bbox=dict(boxstyle='round,pad=0.1',fc='white',ec='none',alpha=0.85))
            else: ax.text(a[0]+1.4,(y0+y1)/2,lab,fontsize=5.0,color='#8e1f12',fontweight='bold',ha='left',va='center',zorder=11,linespacing=0.9,bbox=dict(boxstyle='round,pad=0.1',fc='white',ec='none',alpha=0.85))
        # köprü listesi (malzeme listesi için)
        with open(f'{OUT}/kopru_listesi.csv','w',encoding='utf-8') as f:
            f.write('köprü;net;delik arası (mm);yön;önerilen tel boyu (mm)\n')
            for i,(n,(a,b)) in enumerate(jumpers):
                L=jlen(a,b); f.write(f'K{i+1};{n};{L:.1f};{"yatay" if abs(a[1]-b[1])<0.01 else "dikey"};{L+8:.0f}\n')
    frame(ax)
    ax.text(0,-24,'Baskı Devre v3 — ÖN YÜZ (parça tarafı, üstten bakış)',fontsize=13,fontweight='bold',va='top')
    jl='  '.join(f'K{i+1}: {n} {jlen(a,b):.1f} mm' for i,(n,(a,b)) in enumerate(jumpers))
    ax.text(0,-18.5,f'Kart {BW:.1f} × {BH:.1f} mm, tek yüz. Pot, jak ve LED kartın ön kenarına lehimlenir; gri çıkıntılar ön panelden geçen kısımlar. Tel köprüler (ayrı parça, {len(jumpers)} adet, izoleli tek damar, entegre/büyük parça üstünden geçmez): {jl}',fontsize=7,va='top')
    ax.text(0,-15,'SW1 ve güç anahtarı panele vidalanır, turuncu etiketli pedlere kısa burgulu kabloyla bağlanır. Kesikli çerçeve: JP1 (giriş susturma köprüsü, isteğe bağlı). Kenarlardaki geniş bakır şerit GND hattıdır.',fontsize=7,va='top')
    ax.text(BW/2,BH+19,'▼ ÖN PANEL ▼',fontsize=8,ha='center',color='#2b7bb9')
    fig.savefig(f'{OUT}/2_pcb_on_yuz.png',dpi=240,bbox_inches='tight',facecolor='white')
    if not items: sys.exit()
    # BACK
    X=lambda x:BW-x
    fig,ax=plt.subplots(figsize=(16,11.5))
    ax.add_patch(Rectangle((0,0),BW,BH,fc='#1f5a36',ec='black',lw=1.5,zorder=0))
    img=np.zeros(cu.shape+(4,)); img[cu]=[0.84,0.56,0.27,1]; img=img[:,::-1]
    ax.imshow(img,extent=(0,BW,BH,0),zorder=1,interpolation='antialiased')
    holes(ax,X,'#111')
    draw_parts(ax,{k:v for k,v in pl.items()},detail=False,X=X)
    for i,(n,(a,b)) in enumerate(jumpers):
        for p in (a,b): ax.text(X(p[0]),p[1]+2.2,f'K{i+1}',fontsize=5.3,color='#ffdede',ha='center',fontweight='bold',zorder=11)
    frame(ax)
    ax.text(0,-24,'Baskı Devre v3 — ARKA YÜZ (bakır tarafı, alttan bakış)',fontsize=13,fontweight='bold',va='top')
    ax.text(0,-18.5,'Yollar 1.0 mm (sinyal) / 1.3 mm (besleme, çıkış). Boş alanlar GND dolgusu. Delikler: 0.7–1.0 mm elkolar (çapa göre), 0.8–0.9 mm küçük parçalar, 1.3 mm pot, 1.3 mm klemens/sigorta/diyot,',fontsize=7,va='top')
    ax.text(0,-15,'1.6 mm PJ-324M, 2.3 mm (ya da iki küçük delik birleştirilerek yarık) 6.35 jak. Toner transferi için ayrı 1:1 PDF\'i kullan.',fontsize=7,va='top')
    ax.text(BW/2,BH+19,'▼ ÖN PANEL ▼',fontsize=8,ha='center',color='#2b7bb9')
    fig.savefig(f'{OUT}/3_pcb_arka_yuz.png',dpi=240,bbox_inches='tight',facecolor='white')
    # TONER PDF
    fig=plt.figure(figsize=(210/25.4,297/25.4)); ox,oy=(210-BW)/2,40
    ax=fig.add_axes([ox/210,1-(oy+BH)/297,BW/210,BH/297])
    im=np.ones(cu.shape+(3,)); im[cu]=0
    ax.imshow(im,extent=(0,BW,BH,0),interpolation='none')   # tam çözünürlük (≈508 dpi), yeniden örnekleme yok
    for n,k,d in items:
        if k=='pad': ax.add_patch(Circle(d[0],0.35,fc='white',ec='none'))
        if k=='hole': ax.add_patch(Circle(d[0],1.6,fc='white',ec='black',lw=0.3))
    ax.add_patch(Rectangle((0,0),BW,BH,fill=False,ec='black',lw=0.4))
    ax.set_xlim(0,BW); ax.set_ylim(BH,0); ax.axis('off')
    fig.text(0.5,1-15/297,'12V Gitar Amfisi v3 — BAKIR KATMANI, TONER TRANSFERİ İÇİN (1:1)',ha='center',fontsize=11,fontweight='bold')
    fig.text(0.5,1-22/297,'Yazdırırken ölçeklendirme KAPALI (%100 / Gerçek boyut). 50 mm cetvelini kumpasla kontrol et.',ha='center',fontsize=8)
    fig.text(0.5,1-27/297,'Bu görüntü zaten doğru yönde: kâğıt yüzü bakıra gelecek şekilde konunca bakırda alttan bakış oluşur.',ha='center',fontsize=7)
    ax2=fig.add_axes([ox/210,1-(oy+BH+20)/297,50/210,6/297]); ax2.set_xlim(0,50); ax2.set_ylim(0,6); ax2.axis('off')
    ax2.plot([0,50],[3,3],color='k',lw=1)
    for i in range(0,51,10): ax2.plot([i,i],[1.5,4.5],color='k',lw=0.8); ax2.text(i,5,str(i),fontsize=5,ha='center')
    fig.text(0.5,1-(oy+BH+32)/297,'Kart ölçüsü: %.1f × %.1f mm.  Delmeden önce: jakları, potları ve büyük elkoları bu çıktının ön yüz görseliyle karşılaştır.'%(BW,BH),ha='center',fontsize=7)
    fig.savefig(f'{OUT}/6_toner_transfer_1e1.pdf',dpi=600)
    print('drawn',len(jumpers))
