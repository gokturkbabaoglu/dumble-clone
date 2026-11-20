import re,os
RAW=open('/tmp/cur.txt',encoding='latin1').read()
C=['#0000FF','#FF0000','#008000','#FF00FF','#808000','#008080']
def wf(an,plt,i,x,y,xr,col):
    opt='OUTPUT,LINEARY' if an=='AC' else 'OUTPUT,LINEARX,LINEARY'
    return f"""[WaveForm]
Analysis={an}
Plt={plt}
AliasID={i}
XExp={x}
YExp={y}
XRng={xr}
YRng=1,-1
Options={opt}
Range Grid X=1
Range Grid Y=0.4
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
def build(out,an,waves,steps=(),defs={},vals={},frange='20k,10',tr=None,noise=False):
    s=RAW
    for k,v in defs.items():
        if re.search(rf'Text=\.DEFINE {k} ',s): s=re.sub(rf'Text=\.DEFINE {k} .*',f'Text=.DEFINE {k} {v}',s)
        else: s=s.replace('Text=.DEFINE HP 0',f'Text=.DEFINE HP 0\nText=.DEFINE {k} {v}',1)
    for part,v in vals.items():
        s,n=re.subn(rf'(\nV={re.escape(part)}\n(?:.*\n){{0,8}}?.*?(?:VALUE|RESISTANCE|CAPACITANCE)\nV=)[^\n]*',lambda m:m.group(1)+v,s,count=1); assert n==1,part
    blocks=re.split(r'\n(?=\[)',s); keep=[];first=None
    for b in blocks:
        h=b.split('\n',1)[0].strip()
        if h in('[WaveForm]','[Stepping]') and f'\nAnalysis={an}\n' in b+'\n':
            if first is None: first=len(keep)
            continue
        keep.append(b)
    x='F' if an=='AC' else 'T'
    xr=frange.replace('k','000').replace('Meg','000000') if an=='AC' else '0.02,0.015'
    new=''.join(wf(an,p,i+1,x,y,xr,C[i%6])+'\n' for i,(p,y) in enumerate(waves))
    for i,(n,f,t,v) in enumerate(steps):
        new+=f"[Stepping]\nAnalysis={an}\nIndex={i+1}\nStatus=On\nParameter Type=Symbolic\nName={n}\nFrom={f}\nTo={t}\nValue={v}\n\n"
    keep.insert(first,new.rstrip('\n')+'\n'); s='\n'.join(keep)
    if an=='AC':
        s,n=re.subn(r'(\[Limits\]\nAnalysis=AC\nFRange=)[^\n]*',rf'\g<1>{frange}',s); assert n==1
    else:
        s,n=re.subn(r'(\[Limits\]\nAnalysis=Transient\n)TMax=[^\n]*\nTStart=[^\n]*\nTStep=[^\n]*\nNPts=\d+',r'\g<1>TMax=20m\nTStart=15m\nTStep=2u\nNPts=1001',s); assert n==1
    os.makedirs(os.path.dirname(out),exist_ok=True)
    open(out,'w',encoding='latin1',newline='\r\n').write(s)
if __name__=='__main__':
    O='/mnt/user-data/outputs/sim/'
    build(O+'06_IMP/06a_empedans.cir','AC',[(1,'MAG(V(IN))/MAG(I(R5))'),(2,'MAG(V(SPK))')],
          steps=[('RL','4','4Meg','3999996')],defs={'RL':'4'},vals={'RSPK':'{IF(HP>0.5,1G,RL)}'})
    build(O+'06_IMP/06b_kulaklik.cir','Transient',[(1,'v(SPK)-v(HPS)'),(2,'v(O386)')],
          steps=[('VOL','0.25','1','0.25'),('VIN','0.2','1','0.8')],defs={'HP':'1'})
    build(O+'06_IMP/06c_besleme_ripple.cir','AC',[(1,'dB(v(SPK))'),(2,'dB(v(V12))'),(2,'dB(v(V2))'),(2,'dB(v(V3))'),(2,'dB(v(O386))')],
          vals={'V1':'DC 12 AC 1','VGIT':'DC 0 AC 0 0 Sin 0 {VIN} 1k'})
    build(O+'06_IMP/06d_TDA_kararlilik.cir','AC',[(1,'dB(v(SPK)/v(TIN))'),(2,'ph(v(SPK)/v(TIN))')],frange='10Meg,10')
    build(O+'04_THD/04a_THD_gain_C9.cir','Transient',[(1,'v(SPK)'),(2,'v(O386)'),(3,'v(DRAIN)')],
          steps=[('GAIN','0.1','1','0.45'),('C9V','1p','22u','22u')])
