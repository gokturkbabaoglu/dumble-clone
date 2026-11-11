import re,sys,csv,math
def parse(fn):
    t=open(fn,encoding='latin1').read()
    parts=re.split(r'\nTemperature=27 ?(.*)\n',t)
    runs=[]
    for i in range(1,len(parts),2):
        label=parts[i].strip(); body=parts[i+1]
        m=re.search(r'\n\s+F\s+(.*)\n',body)
        if not m: continue
        cols=m.group(1).split()
        rows=[]
        for l in body[m.end():].split('\n'):
            v=l.split()
            if len(v)!=len(cols)+1: 
                if rows: break
                continue
            try: rows.append([float(x) for x in v])
            except: 
                if rows: break
        runs.append((label,cols,rows))
    return runs
def at(rows,f,ci):
    best=min(rows,key=lambda r:abs(math.log(r[0]/f))); return best[ci+1]
def f3db(rows,ci):
    ref=max(r[ci+1] for r in rows); pk=max(rows,key=lambda r:r[ci+1])[0]
    lo=[r[0] for r in rows if r[0]<pk and r[ci+1]<ref-3]; hi=[r[0] for r in rows if r[0]>pk and r[ci+1]<ref-3]
    return ref,pk,(max(lo) if lo else None),(min(hi) if hi else None)
if __name__=='__main__':
    runs=parse(sys.argv[1]); out=sys.argv[2]
    with open(out,'w',newline='') as fh:
        w=csv.writer(fh)
        for label,cols,rows in runs:
            for r in rows: w.writerow([label]+r)
    for label,cols,rows in runs:
        for ci,c in enumerate(cols):
            ref,pk,lo,hi=f3db(rows,ci)
            print(f"{label:12s} {c:22s} 100Hz={at(rows,100,ci):7.2f} 1k={at(rows,1000,ci):7.2f} 5k={at(rows,5000,ci):7.2f} pk={ref:6.2f}@{pk:7.0f} -3dB: {lo and round(lo)} .. {hi and round(hi)}")
