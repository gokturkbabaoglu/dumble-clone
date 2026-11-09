import heapq, json, random, sys, math
import numpy as np
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from geom import *
NETS=nets
def pins_of(ref,pl): return pins_cell(ref,pl)
DIRS=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
DCOST=[1,1.414,1,1.414,1,1.414,1,1.414]
JCOST=45
def build(pl):
    netnames=sorted(NETS)
    nid={n:i for i,n in enumerate(netnames)}
    pincells={}
    for ref,(fp,v,ns) in C.items():
        if fp.startswith('KO'): continue
        for i,p in enumerate(pins_of(ref,pl)):
            pincells.setdefault(ns[i],[]).append((int(p[0]),int(p[1])))
    return netnames,nid,pincells
class Router:
    def __init__(s,pl):
        s.pl=pl
        s.netnames,s.nid,s.pincells=build(pl)
        N=len(s.netnames)
        s.near=np.zeros((N,W+1,H+1),np.int16)
        s.tot=np.zeros((W+1,H+1),np.int16)
        s.owner=-np.ones((W+1,H+1),np.int16)
        s.paths={}; s.jumps={}; s.tcells={}
        for n,cells in s.pincells.items():
            for c in cells: s.add(s.nid[n],c)
        # jump restrictions: no endpoints near any pin, no jump over component bodies
        s.nojump=np.zeros((W+1,H+1),bool)
        for n,cells in s.pincells.items():
            for (x,y) in cells: s.nojump[max(0,x-1):x+2,max(0,y-1):y+2]=True
        s.body=np.zeros((W+1,H+1),bool)
        s.pinmask=np.zeros((W+1,H+1),bool)
        s.jpath=np.zeros((W+1,H+1),bool)
        N=len(s.netnames)
        s.pn=np.zeros((N,W+1,H+1),np.int16); s.pnt=np.zeros((W+1,H+1),np.int16)
        for n,cells in s.pincells.items():
            k=s.nid[n]
            for (x,y) in cells:
                s.pn[k,max(0,x-1):x+2,max(0,y-1):y+2]+=1; s.pnt[max(0,x-1):x+2,max(0,y-1):y+2]+=1
        for n,cells in s.pincells.items():
            for (x,y) in cells: s.pinmask[x,y]=True
        s.big=np.zeros((W+1,H+1),bool)
        for ref,(fp,v,ns) in C.items():
            if fp=='PAD': continue
            bb=FP[fp]['body']
            if bb is None: continue
            if bb[0]=='circ':
                ps=pins_mm(ref,pl); q=ps[1] if len(ps)>1 else ps[0]; cx=(ps[0][0]+q[0])/2/U; cy=(ps[0][1]+q[1])/2/U
                rr=bb[1]/2/U+0.6
                for x in range(int(cx-rr)-1,int(cx+rr)+2):
                    for y in range(int(cy-rr)-1,int(cy+rr)+2):
                        if 0<=x<=W and 0<=y<=H and (x-cx)**2+(y-cy)**2<=rr*rr: s.body[x,y]=True; s.big[x,y]=True
            else:
                isbig=fp in ('J635','PJ324','POT','LED','PW5','DIP8','FUSE','TB2','DO201','MH') or fp.startswith('KO')
                x0,x1,y0,y1=body_box_mm(ref,pl)
                for x in range(int(x0/U),int(x1/U)+2):
                    for y in range(int(y0/U),int(y1/U)+2):
                        if 0<=x<=W and 0<=y<=H:
                            s.body[x,y]=True
                            if isbig: s.big[x,y]=True
        # big pads: extra clearance ring
        for ref,(fp,v,ns) in C.items():
            if FP[fp]['pad']>=3.0:
                for i,c in enumerate(pins_of(ref,pl)):
                    k=s.nid[ns[i]]; x,y=c
                    x0,x1,y0,y1=max(0,x-2),min(W,x+2),max(0,y-2),min(H,y+2)
                    s.near[k,x0:x1+1,y0:y1+1]+=1; s.tot[x0:x1+1,y0:y1+1]+=1
    def add(s,k,c,sign=1):
        x,y=c
        x0,x1,y0,y1=max(0,x-1),min(W,x+1),max(0,y-1),min(H,y+1)
        s.near[k,x0:x1+1,y0:y1+1]+=sign; s.tot[x0:x1+1,y0:y1+1]+=sign
        if sign>0: s.owner[x,y]=k
        elif s.near[k,x,y]==0 or True:
            pass
    def ripup(s,n):
        k=s.nid[n]
        for c in s.tcells.get(n,[]):
            s.add(k,c,-1); s.owner[c]=-1
        s.tcells[n]=[]; s.paths[n]=[]; s.jumps[n]=[]
    def free(s,k,c):
        x,y=c
        if x<1 or y<1 or x>W-1 or y>H-1: return False
        return s.tot[x,y]-s.near[k,x,y]==0
    def route_net(s,n):
        k=s.nid[n]; pins=list(dict.fromkeys(s.pincells[n]))
        if len(pins)<2: return True
        tree=set([pins[0]]); rem=pins[1:]
        segs=[]; jumps=[]; ok=True
        while rem:
            res=s.dijkstra(k,tree,set(rem))
            if res is None: ok=False; break
            path,js,end=res
            segs.append(path); jumps+=js
            for (a,b) in js:
                xa,ya=a; xb,yb=b
                for x in range(min(xa,xb)-1,max(xa,xb)+2):
                    for y in range(min(ya,yb)-1,max(ya,yb)+2):
                        if 0<=x<=W and 0<=y<=H: s.jpath[x,y]=True
                s.pinmask[a]=True; s.pinmask[b]=True
            for c in path:
                if c not in tree:
                    tree.add(c)
            for c in path: 
                if s.owner[c]!=k:
                    s.add(k,c); s.tcells.setdefault(n,[]).append(c)
            rem.remove(end)
        s.paths[n]=segs; s.jumps[n]=jumps
        return ok
    def dijkstra(s,k,src,targets):
        free=s.free
        dist={}; prev={}
        pq=[]
        for c in src:
            st=(c,8); dist[st]=0; heapq.heappush(pq,(0,c,8))
        # heuristic: min chebyshev-ish to targets
        tl=list(targets)
        def h(c): return min(max(abs(c[0]-t[0]),abs(c[1]-t[1]))+0.414*min(abs(c[0]-t[0]),abs(c[1]-t[1])) for t in tl)
        pq=[(h(c),0,c,8) for c in src]; heapq.heapify(pq)
        while pq:
            f,g,c,d=heapq.heappop(pq)
            if dist.get((c,d),1e18)<g: continue
            if c in targets and (c,d) not in [(x,8) for x in src]:
                # reconstruct
                path=[c]; js=[]; st=(c,d)
                while st in prev:
                    pst,jump=prev[st]
                    if jump: js.append((pst[0],st[0]))
                    path.append(pst[0]); st=pst
                path.reverse()
                return path,js,c
            for nd,(dx,dy) in enumerate(DIRS):
                if d!=8:
                    turn=min((nd-d)%8,(d-nd)%8)
                    if turn>2: continue
                    tc=[0,0.25,0.8][turn]
                else: tc=0
                nc=(c[0]+dx,c[1]+dy)
                if not free(k,nc): continue
                if dx and dy:  # diagonal corner cutting check
                    if not (free(k,(c[0]+dx,c[1])) or free(k,(c[0],c[1]+dy))): continue
                ng=g+DCOST[nd]+tc
                st=(nc,nd)
                if ng<dist.get(st,1e18):
                    dist[st]=ng; prev[st]=((c,d),False); heapq.heappush(pq,(ng+h(nc),ng,nc,nd))
            # jumps (orthogonal)
            gnd=(s.netnames[k]=='GND')
            if s.pinmask[c] or (s.pnt[c]-s.pn[k][c])>0 or (s.body[c] and not gnd) or s.jpath[c]: continue
            for nd in (0,2,4,6):
                dx,dy=DIRS[nd]
                if d!=8 and d!=nd: continue
                for L in range(1,11):
                    nc=(c[0]+dx*L,c[1]+dy*L)
                    if not (0<=nc[0]<=W and 0<=nc[1]<=H): break
                    if (s.big[nc] and not gnd) or s.pinmask[nc] or s.jpath[nc]: break
                    if L<3 or (s.body[nc] and not gnd) or (s.pnt[nc]-s.pn[k][nc])>0 or not free(k,nc): continue
                    ng=g+JCOST+L
                    st=(nc,nd)
                    if ng<dist.get(st,1e18):
                        dist[st]=ng; prev[st]=((c,d),True); heapq.heappush(pq,(ng+h(nc),ng,nc,nd))
        return None
def route_all(pl,order):
    r=Router(pl); fails=[]
    for n in order:
        if n=='GND': continue
        if not r.route_net(n): fails.append(n)
    nj=sum(len(v) for v in r.jumps.values())
    L=sum(len(p) for segs in r.paths.values() for p in segs)
    return r,fails,nj,L
if __name__=='__main__':
    pl={k:tuple(v) for k,v in json.load(open(sys.argv[1])).items()}
    import itertools
    netlist=[n for n in NETS if n!='GND']
    def span(n):
        cs=[pins_of(r,pl)[i] for r,i in NETS[n]]
        return max(c[0] for c in cs)-min(c[0] for c in cs)+max(c[1] for c in cs)-min(c[1] for c in cs)
    best=None
    for t in range(int(sys.argv[2])):
        if t==0: order=sorted(netlist,key=span)
        elif t==1: order=sorted(netlist,key=lambda n:-span(n))
        else:
            order=sorted(netlist,key=lambda n:span(n)*random.uniform(0.3,1.7))
        r,f,nj,L=route_all(pl,order)
        sc=(len(f)*1000+nj*50+L)
        print(t,'fail',f,'jumps',nj,'len',L,flush=True)
        if best is None or sc<best[0]: best=(sc,order,f,nj)
    json.dump({'order':best[1]},open(sys.argv[1].replace('.json','_order.json'),'w'))
    print('best',best[2],best[3])
