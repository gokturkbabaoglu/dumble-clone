import sys, os, json, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from place2 import *
from final2 import route_eval, orders, bad_jumps
def evaluate(pl, ords):
    best=None
    for o in ords:
        r,f=route_eval(pl,o)
        if r is None: sc=((300+80*len(f)) if set(f)=={'GND'} else (1000+100*len(f)),99,0)
        else:
            nj=sum(len(v) for v in r.jumps.values()); L=sum(len(p) for s in r.paths.values() for p in s)
            bj=bad_jumps(r); sc=(nj*60+bj*100+L*0.02,nj,bj)
        if best is None or sc[0]<best[0]: best=sc
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
    ords=orders(pl,1,0)
    cur=evaluate(pl,ords); best=(cur,dict(pl)); print('start',cur,flush=True)
    json.dump({kk:list(v) for kk,v in pl.items()},open(f'rsa_{seed}.json','w'))
    movable=[r for r in C if r not in FIXED]; N=int(sys.argv[3])
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
        ords=orders(pl,1,0)
        new=evaluate(pl,ords)
        if new[0]<cur[0] or random.random()<math.exp((cur[0]-new[0])/T):
            cur=new
            if new[0]<best[0][0]:
                best=(new,dict(pl)); print(k,'best',new,flush=True)
                json.dump({kk:list(v) for kk,v in pl.items()},open(f'rsa_{seed}.json','w'))
        else:
            pl[r]=old
            if r2: pl[r2]=old2
    print('END',best[0])
