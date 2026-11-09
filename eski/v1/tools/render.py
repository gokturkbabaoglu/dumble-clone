import sys, json, math
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon
from design import *
from place import W,H,pins_of,rot,court
def pin_mm(ref,pl,i):
    fp=C[ref][0]; x,y,r=pl[ref]
    if fp=='PW5':
        dx,dy=PW_TRUE[i]
        for _ in range(r//90): dx,dy=-dy,dx
        return (x*U+dx, y*U+dy)
    p=pins_of(ref,pl)[i]; return (p[0]*U,p[1]*U)
def draw_parts(ax,pl,mirror=False,labels=True,values=True,alpha=1):
    for ref,(fp,val,ns) in C.items():
        f=FP[fp]; x,y,r=pl[ref]
        ps=[pin_mm(ref,pl,i) for i in range(len(ns))]
        cx=sum(p[0] for p in ps)/len(ps); cy=sum(p[1] for p in ps)/len(ps)
        b=f['body']
        if b:
            if b[0]=='circ':
                ax.add_patch(Circle((cx,cy),b[1]/2,fill=False,lw=1.1,ec='#1a4d8f',alpha=alpha))
                # + mark near pin0
                p0=ps[0]; ax.text(p0[0]+(p0[0]-cx)*0.25-0.2,p0[1]+(p0[1]-cy)*0.25-1.9 if abs(p0[1]-cy)<0.1 else p0[1],'+',fontsize=7,color='#c0392b',ha='center',va='center',fontweight='bold')
                # stripe on negative side
                p1=ps[1]; ang=math.atan2(p1[1]-cy,p1[0]-cx)
            elif b[0]=='pw':
                w,h=b[1],b[2]
                ax.add_patch(Rectangle((x*U-w/2,y*U-h-0.8),w,h,fill=True,fc='#dfe6ee',ec='#1a4d8f',lw=1.1,alpha=alpha))
                ax.add_patch(Rectangle((x*U-w/2-2,y*U-h-0.8-14),w+4,14,fill=True,fc='#bfbfbf',ec='#555',lw=0.8,alpha=0.6*alpha,hatch='|||'))
                ax.text(x*U,y*U-h-8,'SOĞUTUCU\n(kart dışı)',fontsize=5.5,ha='center',va='center',color='#333')
            else:
                w,h=b[1],b[2]
                if r%180==90: w,h=h,w
                if b[0]=='to92':
                    ax.add_patch(Rectangle((cx-w/2,cy-h/2),w,h,fill=False,ec='#1a4d8f',lw=1.1,alpha=alpha))
                    # flat side marker
                    if r%180==0: ax.plot([cx-w/2,cx+w/2],[cy+h/2-0.6,cy+h/2-0.6],color='#1a4d8f',lw=0.6)
                elif b[0]=='dip':
                    ax.add_patch(Rectangle((cx-w/2,cy-h/2),w,h,fill=False,ec='#1a4d8f',lw=1.1,alpha=alpha))
                else:
                    ax.add_patch(Rectangle((cx-w/2,cy-h/2),w,h,fill=False,ec='#1a4d8f',lw=1.1,alpha=alpha))
        for i,p in enumerate(ps):
            pr=f['pad']/2
            ax.add_patch(Circle(p,pr,fc='#d9a441' if not mirror else '#d9a441',ec='#7a5a12',lw=0.5,alpha=alpha,zorder=5))
            ax.add_patch(Circle(p,0.45,fc='white',ec='none',zorder=6,alpha=alpha))
        if labels and fp!='PAD':
            txt=ref if not values else f'{ref}\n{val}'
            ax.text(cx,cy,txt,fontsize=4.6,ha='center',va='center',color='#0b2d5c',zorder=7,
                    rotation=(90 if (r%180==90 and fp in('R','CF','DO201','TRIM')) else 0),linespacing=0.95)
        if fp=='PAD':
            ax.text(ps[0][0],ps[0][1]+(-2.6 if y<H-6 else -2.6),val,fontsize=4.3,ha='center',va='bottom',rotation=90 if y>H-6 else 0,color='#5b2c00',zorder=7)
def board(ax,mirror=False):
    ax.add_patch(Rectangle((0,0),W*U,H*U,fill=True,fc='#f4efe2',ec='black',lw=1.5,zorder=0))
    for (px,py) in [(3,3),(W*U-3,H*U-3),(3,H*U-3),(W*U-3,3)]:
        ax.add_patch(Circle((px,py),1.6,fc='white',ec='black',lw=0.8,zorder=1))
    ax.set_xlim(-6,W*U+6); ax.set_ylim(H*U+8,-26)
    ax.set_aspect('equal'); ax.axis('off')
if __name__=='__main__':
    pl={k:tuple(v) for k,v in json.load(open(sys.argv[1])).items()}
    fig,ax=plt.subplots(figsize=(11,9)); board(ax); draw_parts(ax,pl)
    fig.savefig(sys.argv[2],dpi=110,bbox_inches='tight')
