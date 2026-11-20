import re,sys,math,csv
t=open(sys.argv[1],encoding='latin1').read().replace('\r','')
parts=re.split(r'\nTemperature=27 (.*)\n',t)
w=csv.writer(open(sys.argv[2],'w',newline=''))
for i in range(1,len(parts),2):
    lab=parts[i]; body=parts[i+1]
    m=re.search(r'\n\s+T\s+(.*)\n',body); cols=m.group(1).split(); rows=[]
    for l in body[m.end():].split('\n'):
        v=l.split()
        if len(v)!=len(cols)+1:
            if rows: break
            continue
        try: rows.append([float(x) for x in v])
        except:
            if rows: break
    for r in rows: w.writerow([lab]+r)
    print('==',lab,len(rows),'pts')
    for ci,c in enumerate(cols):
        y=[r[ci+1] for r in rows]; mean=sum(y)/len(y); rms=math.sqrt(sum((a-mean)**2 for a in y)/len(y))
        extra=f"  P(4R)={rms**2/4*1000:.1f} mW" if c=='v(SPK)' else ''
        print(f"  {c:9s} min={min(y):7.3f} max={max(y):7.3f} pp={max(y)-min(y):7.3f} rms_ac={rms:6.3f}{extra}")
