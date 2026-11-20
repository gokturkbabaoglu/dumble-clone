import numpy as np,re,sys
def val(s,env):
    s=s.strip()
    if s.startswith('{'): 
        e=s[1:-1].replace('Meg','e6').replace('k','e3')
        return eval(e,{},env)
    m={'f':1e-15,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3,'k':1e3,'meg':1e6}
    mm=re.match(r'([\d.eE+-]+)(meg|[fpnumk])?',s,re.I)
    return float(mm.group(1))*m.get((mm.group(2) or '').lower(),1)
def parse(path):
    L=[l.strip() for l in open(path) if l.strip() and not l.startswith('*')][1:]
    env={'T':0.5,'B':0.5,'M':0.5}
    subs={};top=[];cur=None
    for l in L:
        if l.upper().startswith('.SUBCKT'):
            p=l.split(); cur=(p[1],p[2:4],[]); continue
        if l.upper().startswith('.ENDS'): subs[cur[0]]=cur; cur=None; continue
        if l.startswith('.'): continue
        (cur[2] if cur else top).append(l)
    els=[]
    for l in top:
        p=l.split()
        if p[0].upper().startswith('X'):
            name=p[3]; pv=float(re.search(r'ISFP=([\d.]+)',l).group(1))
            sn,ports,body=subs[name]; mp={ports[0]:p[1],ports[1]:p[2],'0':'0'}
            for b in body:
                q=b.split(); n=[mp.get(x,p[0]+'.'+x) for x in q[1:3]]
                els.append((q[0][0].upper(),n[0],n[1],val(q[3],{'ISFP':pv})))
        elif p[0][0].upper()=='V': els.append(('V',p[1],p[2],1.0))
        else: els.append((p[0][0].upper(),p[1],p[2],val(p[3],env)))
    return els
def solve(els,f):
    nodes=sorted({n for e in els for n in e[1:3] if n!='0'}); idx={n:i for i,n in enumerate(nodes)}
    vs=[e for e in els if e[0]=='V']; N=len(nodes); A=np.zeros((N+len(vs),)*2,complex); b=np.zeros(N+len(vs),complex)
    w=2j*np.pi*f
    for t,a,c,v in els:
        if t=='V': continue
        y=1/v if t=='R' else w*v
        for p,q,s in ((a,a,1),(c,c,1),(a,c,-1),(c,a,-1)):
            if p!='0' and q!='0': A[idx[p],idx[q]]+=s*y
    for k,(t,a,c,v) in enumerate(vs):
        if a!='0': A[idx[a],N+k]+=1; A[N+k,idx[a]]+=1
        b[N+k]=v
    x=np.linalg.solve(A,b); return {n:x[idx[n]] for n in nodes}
if __name__=='__main__':
    els=parse(sys.argv[1]); outs=['OF5','OBF','OMA','ISFUS','ISFUK']
    for f in (100,400,1000,3000,5000):
        r=solve(els,f); print(f,[round(20*np.log10(abs(r[o])),1) for o in outs])
