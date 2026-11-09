import sys, os, json, math, random, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from geom import *
from route2 import Router
PX = 20
def wid(n): return 1.3 if n in POWER_NETS else 1.0
def cell_mm(c): return (c[0]*U, c[1]*U)
def build_geom(pl, r):
    items=[]; padpos={}
    for ref,(fp,v,ns) in C.items():
        if fp.startswith('KO'): continue
        if fp=='MH':
            items.append((ns[0],'hole',(pins_mm(ref,pl)[0],3.2))); continue
        pm=pins_mm(ref,pl); pc=pins_cell(ref,pl); d=FP[fp]['pad']
        for i,n in enumerate(ns):
            items.append((n,'pad',(pm[i],d,FP[fp]['hole']))); padpos[(ref,i)]=pm[i]
            if abs(pm[i][0]-pc[i][0]*U)>0.05 or abs(pm[i][1]-pc[i][1]*U)>0.05:
                items.append((n,'seg',(cell_mm(pc[i]),pm[i],min(wid(n),1.0))))
    for n,segs in r.paths.items():
        js=set((tuple(a),tuple(b)) for a,b in r.jumps.get(n,[]))
        for path in segs:
            for a,b in zip(path,path[1:]):
                if (a,b) in js or (b,a) in js:
                    items.append((n,'jumper',(cell_mm(a),cell_mm(b))))
                    items.append((n,'pad',(cell_mm(a),2.0,0.9))); items.append((n,'pad',(cell_mm(b),2.0,0.9)))
                else: items.append((n,'seg',(cell_mm(a),cell_mm(b),wid(n))))
    return items, padpos
def raster(items, sel=None, grow=0.0):
    im=Image.new('L',(int(BW*PX)+1,int(BH*PX)+1),0); d=ImageDraw.Draw(im)
    for n,k,data in items:
        if sel and not sel(n): continue
        if k=='pad':
            (x,y),dia,_=data; rr=(dia/2+grow)*PX
            d.ellipse([x*PX-rr,y*PX-rr,x*PX+rr,y*PX+rr],fill=255)
        elif k=='seg':
            a,b,w=data; ww=(w+2*grow)*PX
            d.line([a[0]*PX,a[1]*PX,b[0]*PX,b[1]*PX],fill=255,width=int(round(ww)))
            for p in (a,b):
                rr=ww/2; d.ellipse([p[0]*PX-rr,p[1]*PX-rr,p[0]*PX+rr,p[1]*PX+rr],fill=255)
    return np.array(im)>0
HOLES_M=[]
def mount_holes():
    return HOLES_M
def pour(items, grow=0.55):
    sig=raster(items,lambda n:n!='GND',grow=grow)
    board=np.ones_like(sig); m=int(1.0*PX)
    board[:m,:]=0; board[-m:,:]=0; board[:,:m]=0; board[:,-m:]=0
    hy,hx=np.ogrid[:board.shape[0],:board.shape[1]]
    for (px,py) in mount_holes(): board[(hx-px*PX)**2+(hy-py*PX)**2<(3.2*PX)**2]=0
    for n,k,d in items:
        if k=='hole':
            (px,py),dd=d; board[(hx-px*PX)**2+(hy-py*PX)**2<((dd/2+1.2)*PX)**2]=0
    g=board&~sig
    rr_=6; yy,xx=np.ogrid[-rr_:rr_+1,-rr_:rr_+1]; st=(xx*xx+yy*yy)<=rr_*rr_
    g=ndimage.binary_opening(g,structure=st)
    for n,k,data in items:
        if n=='GND' and k=='pad':
            (x,y),d,_=data; r1=(d/2+0.6)*PX
            x0,x1=int(max(0,(x*PX-r1-2))),int(min(g.shape[1],x*PX+r1+3)); y0,y1=int(max(0,y*PX-r1-2)),int(min(g.shape[0],y*PX+r1+3))
            sub_hx=hx[:,x0:x1]; sub_hy=hy[y0:y1,:]
            rr=(sub_hx-x*PX)**2+(sub_hy-y*PX)**2; ring=rr<=r1*r1
            gs=g[y0:y1,x0:x1]; gs[ring]=False
            sp=0.45*PX
            spoke=ring&((np.abs(sub_hx-x*PX)<=sp)|(np.abs(sub_hy-y*PX)<=sp))
            gs|=spoke&board[y0:y1,x0:x1]&~sig[y0:y1,x0:x1]
    g|=raster(items,lambda n:n=='GND')
    lab,nl=ndimage.label(g)
    gp=[data[0] for n,k,data in items if n=='GND' and k=='pad']
    keep=set(lab[int(y*PX),int(x*PX)] for x,y in gp); keep.discard(0)
    return np.isin(lab,list(keep))
def verify(items, padpos, g):
    cu=raster(items,lambda n:n!='GND')|g
    lab,nl=ndimage.label(cu); parent=list(range(nl+1))
    def f(a):
        while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
        return a
    for n,k,data in items:
        if k=='jumper':
            a,b=data; parent[f(lab[int(a[1]*PX),int(a[0]*PX)])]=f(lab[int(b[1]*PX),int(b[0]*PX)])
    netcomp={}; errs=[]
    for (ref,i),p in padpos.items():
        n=C[ref][2][i]; l=f(lab[int(p[1]*PX),int(p[0]*PX)])
        if l==0: errs.append(('nocopper',ref,i)); continue
        netcomp.setdefault(n,set()).add(l)
    for n,s in netcomp.items():
        if len(s)>1: errs.append(('open',n,len(s)))
    inv={}
    for n,s in netcomp.items():
        for l in s: inv.setdefault(l,set()).add(n)
    for l,s in inv.items():
        if len(s)>1: errs.append(('short',sorted(s)))
    return errs
def route_eval(pl, order):
    r=Router(pl)
    full=r.pincells['GND']; bbp,bbj=[],[]
    f=[n for n in order if not r.route_net(n)]
    if f: return None,f
    items,_=build_geom(pl,r); g=pour(items)
    lab,_=ndimage.label(g); reps={}; iso=[]
    for ref,(fp,v,ns) in C.items():
        pm=pins_mm(ref,pl); pc=pins_cell(ref,pl)
        for i,n in enumerate(ns):
            if n!='GND': continue
            l=lab[int(pm[i][1]*PX),int(pm[i][0]*PX)]
            if l==0: iso.append(pc[i])
            else: reps.setdefault(l,pc[i])
    r.pincells['GND']=list(reps.values())+iso
    ok=r.route_net('GND'); r.pincells['GND']=full
    r.paths['GND']=bbp+r.paths.get('GND',[]); r.jumps['GND']=bbj+r.jumps.get('GND',[])
    if not ok: return None,['GND']
    return r,[]
def bad_jumps(r):
    n=0
    for net,js in r.jumps.items():
        for a,b in js:
            xa,ya=a; xb,yb=b
            cells=[(x,y) for x in range(min(xa,xb),max(xa,xb)+1) for y in range(min(ya,yb),max(ya,yb)+1)]
            if any(r.body[c] for c in cells): n+=1
    return n
def orders(pl, k, seed=3):
    random.seed(seed)
    netlist=[n for n in nets if n!='GND' and len(nets[n])>1]
    def span(n):
        cs=[pins_cell(rf,pl)[i] for rf,i in nets[n]]
        return max(c[0] for c in cs)-min(c[0] for c in cs)+max(c[1] for c in cs)-min(c[1] for c in cs)
    out=[sorted(netlist,key=span), sorted(netlist,key=lambda n:-span(n))]
    for _ in range(max(0,k-2)): out.append(sorted(netlist,key=lambda n:span(n)*random.uniform(.5,1.5)))
    return out[:k]
if __name__=='__main__':
    pl={k:tuple(v) for k,v in json.load(open(sys.argv[1])).items()}
    best=None
    ords=[]
    for sd in range(int(sys.argv[2])): ords+=orders(pl,1,sd) if sd>0 else orders(pl,2,0)
    import itertools
    for t,o in enumerate(ords):
        r,f=route_eval(pl,o)
        if r is None: print(t,'fail',f); continue
        nj=sum(len(v) for v in r.jumps.values()); L=sum(len(p) for s in r.paths.values() for p in s)
        print(t,'jumps',nj,'L',L,flush=True)
        bj=bad_jumps(r)
        if best is None or nj*100+bj*150+L<best[0]: best=(nj*100+bj*150+L,r); print('  best so far',nj,bj)
    r=best[1]; items,padpos=build_geom(pl,r); g=pour(items)
    print('VERIFY',verify(items,padpos,g))
    pickle.dump({'pl':pl,'items':items,'padpos':padpos,'g':g},open('final_geom.pkl','wb'))
