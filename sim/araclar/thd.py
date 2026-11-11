import csv,sys,numpy as np
from collections import OrderedDict
d=OrderedDict()
for r in csv.reader(open(sys.argv[1])): d.setdefault(r[0],[]).append([float(x) for x in r[1:]])
names=sys.argv[2].split(',')
for lab,rows in d.items():
    a=np.array(rows); _,i=np.unique(a[:,0],return_index=True); a=a[i]
    t=np.linspace(0.015,0.020,1000,endpoint=False)
    out=[]
    for ci,n in enumerate(names,1):
        y=np.interp(t,a[:,0],a[:,ci]); Y=np.abs(np.fft.rfft(y))/len(y)*2; h=[Y[5*k] for k in range(1,11)]
        thd=np.sqrt(sum(x*x for x in h[1:]))/h[0]*100
        out.append(f"{n}: {h[0]:.3f}Vpk THD {thd:5.1f}% H2 {h[1]/h[0]*100:5.1f}% H3 {h[2]/h[0]*100:5.1f}%")
    print(f"{lab:22s} | "+" | ".join(out))
