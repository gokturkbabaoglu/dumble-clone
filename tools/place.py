import random, math, json, sys
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from design import *
W,H=88,62   # board in u (111.8 x 78.7 mm)
def rot(p,r):
    x,y=p
    for _ in range(r//90): x,y=-y,x
    return x,y
def pins_of(ref,pl):
    fp=FP[C[ref][0]]; x,y,r=pl[ref]
    return [(x+rot(p,r)[0], y+rot(p,r)[1]) for p in fp['pins']]
def court(ref,pl):
    fp=FP[C[ref][0]]; x,y,r=pl[ref]
    ps=pins_of(ref,pl)
    xs=[p[0] for p in ps]; ys=[p[1] for p in ps]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    b=fp['body']; padr=fp['pad']/2/U
    x0,x1,y0,y1=min(xs)-padr,max(xs)+padr,min(ys)-padr,max(ys)+padr
    if b:
        if b[0]=='circ': w=h=b[1]/U
        else: w,h=b[1]/U,b[2]/U
        if b[0] in('circ',): pass
        elif r%180==90: w,h=h,w
        if b[0]=='pw': w,h=(w,h) if r%180==0 else (h,w)
        bx0,bx1,by0,by1=cx-w/2,cx+w/2,cy-h/2,cy+h/2
        if b[0]=='pw':  # body sits on tab side (y<0 at rot0) from odd row
            by0,by1=y-h-0.5,y-0.5
            if r!=0: pass
        x0,x1,y0,y1=min(x0,bx0),max(x1,bx1),min(y0,by0),max(y1,by1)
    m=0.35
    return (x0-m,x1+m,y0-m,y1+m)
FIXED={
 'P_IN':(4,58,0),'P_ING':(8,58,0),'P_GIN':(16,58,0),'P_GW':(20,58,0),'P_GG':(24,58,0),
 'P_US':(40,58,0),'P_UK':(44,58,0),'P_VW':(56,58,0),'P_VG':(60,58,0),
 'P_SPK':(68,58,0),'P_HPS':(72,58,0),'P_SPKG':(76,58,0),
 'P_VIN':(85,6,0),'P_PG':(85,10,0),'P_LEDA':(85,40,0),'P_LEDK':(85,44,0),
 'U2':(66,6,0),
}
REG={}  # x0,x1,y0,y1
def reg(refs,box):
    for r in refs: REG[r]=box
reg(['R5','R6','Q1','TR1','C9','R4','C10','R2','C5'],(1,24,2,55))
reg(['U1','R7','R8','C11','C12','R9','C13','C14','R1','C3','C8','C4'],(12,36,2,55))
reg(['R10','R11','C15','C16','C17','R13','R14','R15','R16'],(28,56,2,32))
reg(['R12','R17','R18','C18','C19','C20','R19','R20','R21','R22'],(28,56,28,55))
reg(['R23','R24','C21','C22','R25','R26','C23','R27','C24','C6','C7','C25','R28','R29'],(48,84,2,55))
reg(['D1','C1','C2','R3'],(64,87,1,55))
nets={}
for ref,(fp,v,ns) in C.items():
    for i,n in enumerate(ns): nets.setdefault(n,[]).append((ref,i))
def hpwl(pl,net):
    xs=[];ys=[]
    for ref,i in nets[net]:
        p=pins_of(ref,pl)[i]; xs.append(p[0]); ys.append(p[1])
    return (max(xs)-min(xs))+(max(ys)-min(ys))
NW={n:(0.15 if n=='GND' else (1.5 if n in('V12','TOUT','SPK','TNEG') else 1.0)) for n in nets}
def ov(a,b):
    return max(0,min(a[1],b[1])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[2],b[2]))
def regpen(ref,cb):
    pen=0
    x0,x1,y0,y1=cb
    bx=REG.get(ref,(0.5,W-0.5,0.5,H-0.5))
    pen+=max(0,bx[0]-x0)+max(0,x1-bx[1])+max(0,bx[2]-y0)+max(0,y1-bx[3])
    pen+=max(0,0.5-x0)*5+max(0,x1-(W-0.5))*5+max(0,0.5-y0)*5+max(0,y1-(H-0.5))*5
    return pen
PAIRS=[(('C7',0),('U2',4),3),(('C6',0),('U2',4),4),(('C1',0),('D1',1),3),(('C2',0),('D1',1),2),
 (('C4',0),('U1',5),4),(('C8',0),('U1',5),2),(('C23',0),('R26',1),2),(('C12',0),('U1',6),2),(('C13',1),('U1',3),1),
 (('C24',1),('U2',2),1),(('C6',1),('U2',2),2),(('R27',0),('U2',3),2),(('R25',0),('U2',1),2),(('R26',0),('U2',1),2),(('C22',1),('U2',0),2)]
def pairc(pl):
    t=0
    for (a,i),(b,j),w in PAIRS:
        p=pins_of(a,pl)[i]; q=pins_of(b,pl)[j]; t+=w*(abs(p[0]-q[0])+abs(p[1]-q[1]))
    return t
def cost(pl):
    c=sum(NW[n]*hpwl(pl,n) for n in nets)+pairc(pl)
    refs=list(pl); cbs={r:court(r,pl) for r in refs}
    o=0
    for i in range(len(refs)):
        for j in range(i+1,len(refs)):
            o+=ov(cbs[refs[i]],cbs[refs[j]])
    rp=sum(regpen(r,cbs[r]) for r in refs if r not in FIXED)
    return c+40*o+60*rp, o, rp
def run(seed,iters):
    random.seed(seed)
    pl=dict(FIXED)
    for r in C:
        if r in pl: continue
        bx=REG.get(r,(2,W-2,2,H-2))
        pl[r]=(random.randint(int(bx[0])+2,int(bx[1])-6),random.randint(int(bx[2])+2,int(bx[3])-2),random.choice([0,90]))
    cur,_,_=cost(pl); best=(cur,dict(pl))
    movable=[r for r in C if r not in FIXED]
    T=30.0
    for k in range(iters):
        T=30*(0.02/30)**(k/iters)
        r=random.choice(movable); old=pl[r]
        m=random.random()
        if m<0.7:
            d=max(1,int(6*T/30)+1)
            pl[r]=(old[0]+random.randint(-d,d),old[1]+random.randint(-d,d),old[2])
        elif m<0.85:
            pl[r]=(old[0],old[1],random.choice([0,90,180,270]))
        else:
            r2=random.choice(movable); old2=pl[r2]
            pl[r],pl[r2]=(old2[0],old2[1],old[2]),(old[0],old[1],old2[2])
        new,_,_=cost(pl)
        if new<cur or random.random()<math.exp((cur-new)/T):
            cur=new
            if new<best[0]: best=(new,dict(pl))
        else:
            if m>=0.85: pl[r2]=old2
            pl[r]=old
    return best
if __name__=='__main__':
    seed=int(sys.argv[1]); it=int(sys.argv[2])
    b=run(seed,it)
    c,o,rp=cost(b[1])
    print(seed,round(c,1),'overlap',round(o,2),'reg',round(rp,2))
    json.dump({k:list(v) for k,v in b[1].items()},open(f'pl_{seed}.json','w'))
