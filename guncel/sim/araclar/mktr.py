import re
raw=open('/tmp/cur.txt',encoding='latin1').read()
C=['#0000FF','#FF0000','#008000','#FF00FF','#808000','#008080']
def wf(plt,i,y,col):
    return f"""[WaveForm]
Analysis=Transient
Plt={plt}
AliasID={i}
XExp=T
YExp={y}
XRng=0.02,0.015
YRng=12,-12
Options=OUTPUT,LINEARX,LINEARY
Range Grid X=0.001
Range Grid Y=4.8
Enable=Enable
Line Color={col}
Text Color={col}
Rainbow=False
VFmtX=3
VFmtY=3
ScaleFactorX="None"
ScaleFactorY="None"
ScaleUnitsX="Auto"
ScaleUnitsY="Auto"
SFmtX=2
SFmtY=2
NOFmtX=3E
NOFmtY=3E
"""
def make(out,waves,steps):
    s=raw
    blocks=re.split(r'\n(?=\[)',s); keep=[];first=None
    for b in blocks:
        h=b.split('\n',1)[0].strip()
        if h in('[WaveForm]','[Stepping]') and '\nAnalysis=Transient\n' in b+'\n':
            if first is None: first=len(keep)
            continue
        keep.append(b)
    new=''.join(wf(p,i+1,y,C[i%6])+'\n' for i,(p,y) in enumerate(waves))
    for i,(n,f,t,v) in enumerate(steps):
        new+=f"[Stepping]\nAnalysis=Transient\nIndex={i+1}\nStatus=On\nParameter Type=Symbolic\nName={n}\nFrom={f}\nTo={t}\nValue={v}\n\n"
    keep.insert(first,new.rstrip('\n')+'\n'); s='\n'.join(keep)
    s,n=re.subn(r'(\[Limits\]\nAnalysis=Transient\n)TMax=[^\n]*\nTStart=[^\n]*\nTStep=[^\n]*\nNPts=\d+',r'\g<1>TMax=20m\nTStart=15m\nTStep=2u\nNPts=1001',s); assert n==1
    open(out,'w',encoding='latin1',newline='\r\n').write(s)
make('/mnt/user-data/outputs/sim/03_TR/03a_transient.cir',
 [(1,'v(SPK)'),(2,'v(O386)'),(2,'v(TIN)'),(3,'v(DRAIN)'),(3,'v(GATE)')],
 [('VIN','0.1','1','0.9'),('C9V','1p','22u','22u')])
import re as _r
def mk2(out,defs,waves,steps):
    global raw
    old=raw
    for k,v in defs.items():
        raw,n=_r.subn(rf'Text=\.DEFINE {k} .*',f'Text=.DEFINE {k} {v}',raw); assert n==1
    make(out,waves,steps); raw=old
mk2('/mnt/user-data/outputs/sim/03_TR/03b_tam_guc_THD.cir',{'VOL':1},
 [(1,'v(SPK)'),(2,'v(O386)'),(2,'v(TIN)')],[('VIN','0.02','1.02','0.2')])
