import re,sys,collections
t=open(sys.argv[1],encoding='latin1').read().replace('\r','')
blocks=re.split(r'\*\*\*   NOISE ANALYSIS  FREQUENCY =\s*([\d.eE+-]+\s*[KMG]?) HZ',t)
def fv(s):
    s=s.strip(); m={'K':1e3,'M':1e6,'G':1e9}
    return float(s[:-1])*m[s[-1]] if s[-1] in m else float(s)
def num(s):
    m={'f':1e-15,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3,'K':1e3}
    return float(s[:-1])*m[s[-1]] if s[-1] in m else float(s)
data=[]
for i in range(1,len(blocks),2):
    f=fv(blocks[i]); b=blocks[i+1].split('TOTAL OUTPUT NOISE')[0]
    c=collections.Counter(); names=None
    for l in b.split('\n'):
        if l.startswith('Instance:'): names=l.split()[1:]
        elif l.startswith('TOTAL') and names:
            for n,v in zip(names,l.split()[1:]):
                g='LM386 (U1)' if n.startswith('U1.') else 'TDA2003 (U2)' if n.startswith('U2.') else 'JFET Q1' if n=='Q1' else n
                c[g]+=num(v)
            names=None
    data.append((f,c))
tot=collections.Counter()
for (f1,c1),(f2,c2) in zip(data,data[1:]):
    for k in set(c1)|set(c2): tot[k]+=(c1[k]+c2[k])/2*(f2-f1)
S=sum(tot.values())
print('integrated 20-20k total out uV rms',(S**.5)*1e6)
for k,v in tot.most_common(10): print(f'{k:15s} {v/S*100:6.1f}%  {v**.5*1e6:8.1f} uV')
for fsel in (100,1000):
    f,c=min(data,key=lambda d:abs(d[0]-fsel)); s=sum(c.values())
    print('@',f,[(k,round(v/s*100,1)) for k,v in c.most_common(4)])
