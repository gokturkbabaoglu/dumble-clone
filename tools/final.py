import sys, json, math, random
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from design import *
from place import W,H,pins_of
from route import Router, route_all
from render import pin_mm
PX=20  # px per mm
BW,BH=W*U,H*U
POWER={'V12','VIN','TOUT','SPK','TNEG','TRC','ZOB2'}
def wid(n): return 1.3 if n in POWER else 1.0
def cell_mm(c): return (c[0]*U,c[1]*U)
def build_geom(pl,r):
    """returns list of copper items: (net, kind, data)"""
    items=[]
    # pads
    padpos={}
    for ref,(fp,v,ns) in C.items():
        for i,n in enumerate(ns):
            p=pin_mm(ref,pl,i); d=FP[fp]['pad']
            items.append((n,'pad',(p,d))); padpos[(ref,i)]=p
    # traces: path segments; jumps break path
    for n,segs in r.paths.items():
        js=set(tuple(map(tuple,j)) for j in r.jumps.get(n,[]))
        for path in segs:
            pts=[]
            for a,b in zip(path,path[1:]):
                if (a,b) in js or (b,a) in js:
                    items.append((n,'jumper',(cell_mm(a),cell_mm(b))))
                    items.append((n,'pad',(cell_mm(a),2.0))); items.append((n,'pad',(cell_mm(b),2.0)))
                else:
                    items.append((n,'seg',(cell_mm(a),cell_mm(b),wid(n))))
    # pentawatt: connect true pad to grid cell
    for i,n in enumerate(C['U2'][2]):
        g=pins_of('U2',pl)[i]; t=pin_mm('U2',pl,i)
        items.append((n,'seg',(cell_mm(g),t,1.0)))
    return items,padpos
def raster(items,netsel=None,grow=0.0):
    im=Image.new('L',(int(BW*PX)+1,int(BH*PX)+1),0); d=ImageDraw.Draw(im)
    for n,k,data in items:
        if netsel and not netsel(n): continue
        if k=='pad':
            (x,y),dia=data; rr=(dia/2+grow)*PX
            d.ellipse([x*PX-rr,y*PX-rr,x*PX+rr,y*PX+rr],fill=255)
        elif k=='seg':
            a,b,w=data; ww=(w+2*grow)*PX
            d.line([a[0]*PX,a[1]*PX,b[0]*PX,b[1]*PX],fill=255,width=int(round(ww)))
            for p in (a,b):
                rr=ww/2; d.ellipse([p[0]*PX-rr,p[1]*PX-rr,p[0]*PX+rr,p[1]*PX+rr],fill=255)
    return np.array(im)>0
def pour(items):
    sig=raster(items,lambda n:n!='GND',grow=0.7)
    board=np.ones_like(sig)
    m=int(1.0*PX); board[:m,:]=0; board[-m:,:]=0; board[:,:m]=0; board[:,-m:]=0
    hy,hx=np.ogrid[:board.shape[0],:board.shape[1]]
    for (px,py) in [(3,3),(BW-3,BH-3),(3,BH-3),(BW-3,3)]:
        board[(hx-px*PX)**2+(hy-py*PX)**2<(3.0*PX)**2]=0
    g=board & ~sig
    g|=raster(items,lambda n:n=='GND')
    lab,nl=ndimage.label(g)
    gtr=raster(items,lambda n:n=='GND'); g|=gtr
    gp=[data[0] for n,k,data in items if n=='GND' and k=='pad']
    keep=set(lab[int(y*PX),int(x*PX)] for x,y in gp)
    g=np.isin(lab,list(keep)) & (lab>0)
    comps={}
    for x,y in gp: comps.setdefault(lab[int(y*PX),int(x*PX)],[]).append((x,y))
    return g,comps
def verify(items,padpos,pl,gnd):
    cu=raster(items,lambda n:n!='GND')|gnd
    lab,nl=ndimage.label(cu)
    # union via jumpers
    parent=list(range(nl+1))
    def f(a):
        while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
        return a
    for n,k,data in items:
        if k=='jumper':
            a,b=data; la=lab[int(a[1]*PX),int(a[0]*PX)]; lb=lab[int(b[1]*PX),int(b[0]*PX)]
            parent[f(la)]=f(lb)
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
def njumps(r): return sum(len(v) for v in r.jumps.values())
def improve(r,order,iters):
    nets=[n for n in order]
    for it in range(iters):
        withj=[n for n in nets if r.jumps.get(n)]
        if not withj: break
        n=random.choice(withj)
        # also rip a few random other nets near
        others=random.sample(nets,k=random.randint(0,3))
        group=[n]+[o for o in others if o!=n]
        before=njumps(r)
        saved={g:(list(r.tcells.get(g,[])),list(r.paths.get(g,[])),list(r.jumps.get(g,[]))) for g in group}
        for g in group: r.ripup(g)
        random.shuffle(group)
        ok=all(r.route_net(g) for g in group)
        after=njumps(r)
        if not ok or after>before:
            for g in group: r.ripup(g)
            k=0
            for g in group:
                tc,pp,jj=saved[g]; kk=r.nid[g]
                for c in tc: r.add(kk,c); 
                r.tcells[g]=tc; r.paths[g]=pp; r.jumps[g]=jj
if __name__=='__main__':
    plf=sys.argv[1]; ntr=int(sys.argv[2])
    pl={k:tuple(v) for k,v in json.load(open(plf)).items()}
    from place import nets as NETS
    netlist=[n for n in NETS if n!='GND']
    def span(n):
        cs=[pins_of(rf,pl)[i] for rf,i in NETS[n]]
        return max(c[0] for c in cs)-min(c[0] for c in cs)+max(c[1] for c in cs)-min(c[1] for c in cs)
    best=None
    random.seed(5)
    for t in range(ntr):
        order=sorted(netlist,key=lambda n:span(n)*(1 if t==0 else random.uniform(0.3,1.7)))
        gpos=random.choice(['first','last','mid'])
        if gpos=='first': order=['GND']+order
        elif gpos=='last': order=order+['GND']
        else: order.insert(len(order)//2,'GND')
        r=Router(pl); f=[]
        for n in order:
            if not r.route_net(n): f.append(n)
        if f: continue
        improve(r,order,250)
        nj=sum(len(v) for v in r.jumps.values()); L=sum(len(p) for segs in r.paths.values() for p in segs)
        items,padpos=build_geom(pl,r)
        g,comps=pour(items)
        sc=nj*50+len(comps)*60+L*0.1
        if best is None or sc<best[0]:
            best=(sc,order,nj,len(comps),L); print(t,gpos,'jumps',nj,'gndcomps',len(comps),'L',L,flush=True)
    json.dump({'order':best[1]},open(plf.replace('.json','_best.json'),'w'))
    print('BEST',best[2:])
