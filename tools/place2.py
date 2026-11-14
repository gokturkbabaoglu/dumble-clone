import random, math, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom import *
from route2 import RING
EM=RING+1.6 if RING>0 else 0.8   # kenar payı (hücre)
FY = H  # front edge (u)
XS = int(round(EXTRA_W/U))  # sağa kayma (hücre)
def fx(ref): return FRONT_X[ref]/U
FIXED = {
 'J1':(fx('J1'),FY,0), 'RV4':(fx('RV4'),FY,0), 'RV1':(fx('RV1'),FY,0), 'RV2':(fx('RV2'),FY,0), 'RV3':(fx('RV3'),FY,0),
 'J2':(fx('J2'),FY,0), 'D2':(fx('D2'),FY,0),
 # SW1 wire pads (panel switch sits in front of them)
 'P_SWD':(fx('SW1')-4,FY-19,0), 'P_SWC':(fx('SW1'),FY-19,0), 'P_SWB':(fx('SW1')+4,FY-19,0),
 'P_PW1':(fx('SW2')-2,FY-20,0), 'P_PW2':(fx('SW2')+2,FY-20,0),
 'KO_SW1':(fx('SW1'),FY,0), 'KO_SW2':(fx('SW2'),FY,0),
 # rear right: power entry, TDA
 'TB1':(126+XS,4,180), 'TB2':(106+XS,4,0),
 'U2':(90+XS,13,0),
 'MH1':(4,4,0),'MH2':(60+XS,4,0),'MH3':(126+XS,46,0),
}
# positions in u must be ints for grid
FIXED = {k:(int(round(v[0])),int(round(v[1])),v[2]) for k,v in FIXED.items()}
REG = {}
def reg(refs, box):
    for r in refs: REG[r] = box
if XS>0:
  reg(['R5','R6','Q1','TR1','C9','R4','C10','R2','C5','JP1'], (1,33+XS//2,7,H-1))
  reg(['R7','CB','CD','U1','R8','C11','C12','R9','C13','C14','C3','C8','C4','R1'], (15+XS,57+XS,7,H-1))
  reg(['R10','R11','C15a','C15b','C16','C17','R13','R14','R15','R16'], (39+XS,76+XS,8,52))
  reg(['R12','R17','R18','C18','C19','C20','R19','R20a','R20b','R21','R22a','R22b'], (39+XS,78+XS,34,H-1))
  reg(['R23','R24','C21','C22','R25','R26','C23','R27','C24','C6','C7','C25','R28','R29'], (65+XS,113+XS,2,H-1))
  reg(['F1','D1','C1','C2','R3'], (104+XS,W-1,2,H-1))
else:  # 165 mm: ön kenar sıkıştırılmış
  reg(['R5','R6','Q1','TR1','C9','R4','C10','R2','C5','JP1'], (1,40,7,H-1))
  reg(['R7','CB','CD','U1','R8','C11','C12','R9','C13','C14','C3','C8','C4','R1'], (22,64,7,H-1))
  reg(['R10','R11','C15a','C15b','C16','C17','R13','R14','R15','R16'], (45,82,8,52))
  reg(['R12','R17','R18','C18','C19','C20','R19','R20a','R20b','R21','R22a','R22b'], (45,84,34,H-1))
  reg(['R23','R24','C21','C22','R25','R26','C23','R27','C24','C6','C7','C25','R28','R29'], (70,113,2,H-1))
  reg(['F1','D1','C1','C2','R3'], (104,W-1,2,H-1))
SENS={'IN','GATE','SRC','DRV','DRAIN','GAININ','GAINW','SWB','SWD'}
NW = {n:(0.15 if n=='GND' else (1.5 if n in POWER_NETS else (2.5 if n in SENS else 1.0))) for n in nets}
PAIRS=[(('R1',1),('U1',5),2),(('C7',0),('U2',4),3),(('C6',0),('U2',4),4),(('C1',0),('D1',1),3),(('C2',0),('D1',1),2),
 (('C4',0),('U1',5),4),(('C8',0),('U1',5),2),(('C23',0),('R26',1),2),(('C12',0),('U1',6),2),
 (('C24',1),('U2',2),1),(('C6',1),('U2',2),2),(('R27',0),('U2',3),2),(('R25',0),('U2',1),2),(('R26',0),('U2',1),2),
 (('C22',0),('U2',0),2),(('R5',0),('J1',2),2),(('CB',1),('P_SWB',0),3),(('CD',0),('P_SWD',0),3),
 (('C15a',0),('C15b',0),2),(('C15a',1),('C15b',1),2),(('F1',0),('TB1',0),3),
 (('R5',1),('Q1',0),3),(('R6',0),('Q1',0),2),(('C9',0),('Q1',1),2),(('C9',1),('RV4',2),2),(('TR1',0),('Q1',1),2),(('R4',1),('Q1',2),2)]
def hpwl(pl, net):
    xs=[];ys=[]
    for ref,i in nets[net]:
        p=pins_cell(ref,pl)[i]; xs.append(p[0]); ys.append(p[1])
    return (max(xs)-min(xs))+(max(ys)-min(ys))
def ov(a,b): return max(0,min(a[1],b[1])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[2],b[2]))
def regpen(ref,cb):
    x0,x1,y0,y1=cb; bx=REG.get(ref,(0.5,W-0.5,0.5,H-0.5)); pen=0
    pen+=max(0,bx[0]-x0)+max(0,x1-bx[1])+max(0,bx[2]-y0)+max(0,y1-bx[3])
    pen+=5*(max(0,EM-x0)+max(0,x1-(W-EM))+max(0,EM-y0)+max(0,y1-(H+0.01)))
    return pen
def pairc(pl):
    t=0
    for (a,i),(b,j),w in PAIRS:
        p=pins_cell(a,pl)[i]; q=pins_cell(b,pl)[j]; t+=w*(abs(p[0]-q[0])+abs(p[1]-q[1]))
    return t
def cost(pl):
    c=sum(NW[n]*hpwl(pl,n) for n in nets if len(nets[n])>1)+pairc(pl)
    refs=list(pl); cbs={r:court(r,pl) for r in refs}; o=0
    for i in range(len(refs)):
        for j in range(i+1,len(refs)): o+=ov(cbs[refs[i]],cbs[refs[j]])
    rp=sum(regpen(r,cbs[r]) for r in refs if r not in FIXED)
    return c+40*o+60*rp, o, rp
def run(seed,iters,init=None,T0=30):
    random.seed(seed); pl=dict(FIXED)
    if init:
        for k,v in init.items():
            if k not in FIXED: pl[k]=tuple(v)
    for r in C:
        if r in pl: continue
        bx=REG.get(r,(2,W-2,2,H-2))
        pl[r]=(random.randint(int(bx[0])+2,int(bx[1])-6),random.randint(int(bx[2])+2,int(bx[3])-3),random.choice([0,90]))
    cur,_,_=cost(pl); best=(cur,dict(pl)); movable=[r for r in C if r not in FIXED]
    for k in range(iters):
        T=T0*(0.02/T0)**(k/iters)
        r=random.choice(movable); old=pl[r]; m=random.random(); r2=None
        if m<0.7:
            d=max(1,int(6*T/30)+1); pl[r]=(old[0]+random.randint(-d,d),old[1]+random.randint(-d,d),old[2])
        elif m<0.85: pl[r]=(old[0],old[1],random.choice([0,90,180,270]))
        else:
            r2=random.choice(movable); old2=pl[r2]
            pl[r],pl[r2]=(old2[0],old2[1],old[2]),(old[0],old[1],old2[2])
        new,_,_=cost(pl)
        if new<cur or random.random()<math.exp((cur-new)/T):
            cur=new
            if new<best[0]: best=(new,dict(pl))
        else:
            pl[r]=old
            if r2: pl[r2]=old2
    return best
if __name__=='__main__':
    seed=int(sys.argv[1]); it=int(sys.argv[2])
    init=json.load(open(sys.argv[3])) if len(sys.argv)>3 else None
    b=run(seed,it,init,float(sys.argv[4]) if len(sys.argv)>4 else 30); c,o,rp=cost(b[1])
    print(seed,round(c,1),'overlap',round(o,2),'reg',round(rp,2))
    json.dump({k:list(v) for k,v in b[1].items()},open(f'pl_{seed}.json','w'))
