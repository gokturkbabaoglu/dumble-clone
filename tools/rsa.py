import sys, json, random, math
sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from design import *
import place
from place import pins_of, court, ov, regpen, FIXED, nets as NETS
from route import Router
from final import build_geom, pour
def evaluate(pl, orders):
    best=None
    for order in orders:
        r=Router(pl); fail=0
        for n in order:
            if not r.route_net(n): fail+=1
        nj=sum(len(v) for v in r.jumps.values())
        items,_=build_geom(pl,r); g,comps=pour(items)
        L=sum(len(p) for segs in r.paths.values() for p in segs)
        sc=fail*100+nj*10+(len(comps)-1)*10+L*0.02
        if best is None or sc<best[0]: best=(sc,nj,len(comps),order)
    return best
def legal(pl,ref):
    cb=court(ref,pl)
    if regpen(ref,cb)>0: return False
    for o in pl:
        if o!=ref and ov(cb,court(o,pl))>0: return False
    return True
if __name__=='__main__':
    seed=int(sys.argv[2]); random.seed(seed)
    pl={k:tuple(v) for k,v in json.load(open(sys.argv[1])).items()}
    netlist=[n for n in NETS if n!='GND']
    def span(n):
        cs=[pins_of(rf,pl)[i] for rf,i in NETS[n]]
        return max(c[0] for c in cs)-min(c[0] for c in cs)+max(c[1] for c in cs)-min(c[1] for c in cs)
    orders=[sorted(netlist,key=span), sorted(netlist,key=lambda n:-span(n))]
    cur=evaluate(pl,orders); best=(cur,dict(pl)); print('start',cur[:3],flush=True)
    movable=[r for r in C if r not in FIXED]
    T=8.0; N=int(sys.argv[3])
    for k in range(N):
        T=8*(0.3/8)**(k/N)
        r=random.choice(movable); old=pl[r]; m=random.random(); r2=None
        if m<0.6: pl[r]=(old[0]+random.randint(-3,3),old[1]+random.randint(-3,3),old[2])
        elif m<0.8: pl[r]=(old[0],old[1],random.choice([0,90,180,270]))
        else:
            r2=random.choice(movable); old2=pl[r2]
            pl[r],pl[r2]=(old2[0],old2[1],old[2]),(old[0],old[1],old2[2])
        if not legal(pl,r) or (r2 and not legal(pl,r2)):
            pl[r]=old
            if r2: pl[r2]=old2
            continue
        # refresh orders with new spans occasionally
        if k%25==0:
            orders=[sorted(netlist,key=span), sorted(netlist,key=lambda n:-span(n)), sorted(netlist,key=lambda n:span(n)*random.uniform(.5,1.5))]
        new=evaluate(pl,orders)
        if new[0]<cur[0] or random.random()<math.exp((cur[0]-new[0])/T):
            cur=new
            if new[0]<best[0][0]:
                best=(new,dict(pl)); print(k,'best',new[:3],flush=True)
                json.dump({kk:list(v) for kk,v in pl.items()},open(f'rsa_{seed}.json','w'))
        else:
            pl[r]=old
            if r2: pl[r2]=old2
    print('END',best[0][:3])
