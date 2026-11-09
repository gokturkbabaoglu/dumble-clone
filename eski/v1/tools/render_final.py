import sys, json, math, random
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
from scipy import ndimage
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Wedge, Polygon, FancyBboxPatch
from design import *
from place import W,H,pins_of,nets as NETS
from route import Router
import final
from final import build_geom, raster, verify, PX, BW, BH
from render import pin_mm
def pour_thermal(items,grow=0.55):
    sig=raster(items,lambda n:n!='GND',grow=grow)
    board=np.ones_like(sig)
    m=int(1.0*PX); board[:m,:]=0; board[-m:,:]=0; board[:,:m]=0; board[:,-m:]=0
    hy,hx=np.ogrid[:board.shape[0],:board.shape[1]]
    for (px,py) in [(3,3),(BW-3,BH-3),(3,BH-3),(BW-3,3)]:
        board[(hx-px*PX)**2+(hy-py*PX)**2<(3.0*PX)**2]=0
    g=board & ~sig
    rr_=6; yy,xx=np.ogrid[-rr_:rr_+1,-rr_:rr_+1]; st=(xx*xx+yy*yy)<=rr_*rr_
    g=ndimage.binary_opening(g,structure=st)
    # thermal reliefs on GND pads: clear ring, add 4 spokes
    for n,k,data in items:
        if n=='GND' and k=='pad':
            (x,y),d=data; r0=d/2*PX; r1=(d/2+0.6)*PX
            rr=(hx-x*PX)**2+(hy-y*PX)**2
            ring=(rr<=r1*r1)
            g[ring]=False
            sp=0.45*PX
            spoke=ring & ((np.abs(hx-x*PX)<=sp)|(np.abs(hy-y*PX)<=sp))
            g|=spoke & board & ~sig
    g|=raster(items,lambda n:n=='GND')
    lab,nl=ndimage.label(g)
    gp=[data[0] for n,k,data in items if n=='GND' and k=='pad']
    keep=set(lab[int(y*PX),int(x*PX)] for x,y in gp)
    keep.discard(0)
    g=np.isin(lab,list(keep))
    return g
def best_route(pl,trials,seed=3):
    random.seed(seed)
    netlist=[n for n in NETS if n!='GND']
    def span(n):
        cs=[pins_of(rf,pl)[i] for rf,i in NETS[n]]
        return max(c[0] for c in cs)-min(c[0] for c in cs)+max(c[1] for c in cs)-min(c[1] for c in cs)
    best=None
    for t in range(trials):
        if t==0: order=sorted(netlist,key=span)
        elif t==1: order=sorted(netlist,key=lambda n:-span(n))
        else: order=sorted(netlist,key=lambda n:span(n)*random.uniform(.5,1.5))
        r=Router(pl); f=[n for n in order if not r.route_net(n)]
        if f: continue
        sj=sum(len(v) for v in r.jumps.values())
        items,_=build_geom(pl,r); g=pour_thermal(items)
        lab,_=ndimage.label(g)
        reps={}; iso=[]
        for ref,(fp,v,ns) in C.items():
            for i,n in enumerate(ns):
                if n!='GND': continue
                p=pin_mm(ref,pl,i); l=lab[int(p[1]*PX),int(p[0]*PX)]
                cell=tuple(int(q) for q in pins_of(ref,pl)[i])
                if l==0: iso.append(cell)
                else: reps.setdefault(l,cell)
        full=r.pincells['GND']
        r.pincells['GND']=list(reps.values())+iso
        r.route_net('GND')
        r.pincells['GND']=full
        tj=sum(len(v) for v in r.jumps.values())
        L=sum(len(p) for segs in r.paths.values() for p in segs)
        sc=tj*100+L
        if best is None or sc<best[0]: best=(sc,r,tj,sj); print('trial',t,'jumps',tj,'(signal',sj,')',flush=True)
    return best[1]
if __name__=='__main__':
    pl={k:tuple(v) for k,v in json.load(open(sys.argv[1])).items()}
    r=best_route(pl,int(sys.argv[2]))
    items,padpos=build_geom(pl,r)
    # drop GND traces that are fully inside pour? keep (they are GND copper anyway)
    g=pour_thermal(items)
    errs=verify(items,padpos,pl,g)
    print('VERIFY errors:',errs)
    import pickle
    pickle.dump({'pl':pl,'items':items,'padpos':padpos,'g':g,'jumps':{n:v for n,v in r.jumps.items() if v}},open('final_geom.pkl','wb'))
