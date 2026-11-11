import re,sys
def load(fn):
    raw=open(fn,encoding='latin1').read()
    pins={}
    for blk in re.findall(r'\[compdef\]\n(.*?)(?=\n\[)',raw,re.S):
        nm=re.search(r'Name=(.*)',blk).group(1).strip()
        pins[nm]=[(m.group(1),int(m.group(3))*8,int(m.group(4))*8) for m in re.finditer(r'Pin="([^"]+)",(a,)?(-?\d+),(-?\d+)',blk)]
    T={0:lambda x,y:(x,y),1:lambda x,y:(-y,x),2:lambda x,y:(-x,-y),3:lambda x,y:(y,-x),4:lambda x,y:(x,-y),5:lambda x,y:(y,-x),6:lambda x,y:(-x,y),7:lambda x,y:(-y,-x)}
    blocks=re.split(r'\n(?=\[)',raw); pinpts=[]; wires=[]; texts=[]; cur=None; gi=0
    for b in blocks:
        h=b.split('\n',1)[0].strip()
        if h=='[Comp]':
            nm=re.search(r'Name=(.*)',b).group(1).strip(); px=tuple(map(int,re.search(r'Px=(.*)',b).group(1).split(',')))
            r=int(re.search(r'Rot=(\d)',b).group(1)) if 'Rot=' in b else 0
            cur={'nm':nm,'px':px,'r':r,'part':None}; pinpts.append(cur)
        elif h=='[Attr]' and cur is not None:
            m=re.search(r',PART\nV=(.*)',b)
            if m: cur['part']=m.group(1).strip()
        elif h=='[Wire]': wires.append(tuple(map(int,re.search(r'Pxs=(.*)',b).group(1).split(',')))); cur=None
        elif h=='[Grid Text]':
            texts.append((re.search(r'Text="(.*)"',b).group(1),tuple(map(int,re.search(r'Px=(.*)',b).group(1).split(','))))); cur=None
        else: cur=None if h!='[Attr]' else cur
    par={}
    def f(a):
        par.setdefault(a,a)
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    def u(a,b): par[f(a)]=f(b)
    pts=set()
    for w in wires: pts.add((w[0],w[1])); pts.add((w[2],w[3])); u(('P',w[0],w[1]),('P',w[2],w[3]))
    def onseg(p,w):
        (x,y),(a,b,c,d)=p,w
        return (a==c==x and min(b,d)<=y<=max(b,d)) or (b==d==y and min(a,c)<=x<=max(a,c))
    pinkeys=[]
    for c in pinpts:
        for pn,x,y in pins[c['nm']]:
            dx,dy=T[c['r']](x,y); p=(c['px'][0]+dx,c['px'][1]+dy)
            key=(c['part'] or 'GND',pn) if c['nm']!='Ground' else ('GNDSYM',p)
            pinkeys.append((key,p)); u(('K',key),('P',)+p)
            if c['nm']=='Ground': u(('P',)+p,('NET','0'))
    allp=list(pts)+[p for _,p in pinkeys]+[t[1] for t in texts]
    pass
    for t,p in texts:
        if p in pts or p in [pp for _,pp in pinkeys]:
            u(('P',)+p,('NET',t))
    groups={}
    for key,p in pinkeys:
        if key[0]=='GNDSYM': continue
        groups.setdefault(f(('K',key)),[]).append(key)
    return sorted(sorted(map(str,g)) for g in groups.values())
a=load(sys.argv[1]); b=load(sys.argv[2])
sa=set(map(tuple,a)); sb=set(map(tuple,b))
print('nets old',len(a),'new',len(b))
for g in sa-sb: print('OLD only',g)
for g in sb-sa: print('NEW only',g)
