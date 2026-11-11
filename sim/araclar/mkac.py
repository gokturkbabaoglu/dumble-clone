import re,sys
SRC='/tmp/cur.txt'
raw=open(SRC,encoding='latin1').read()
COLORS=['#0000FF','#FF0000','#008000','#FF00FF','#808000','#008080','#800000']
def wf(plt,i,y,yr,col):
    hi,lo=yr
    return f"""[WaveForm]
Analysis=AC
Plt={plt}
AliasID={i}
XExp=F
YExp={y}
XRng=20000,10
YRng={hi},{lo}
Options=OUTPUT,LINEARY
Range Grid X=3998
Range Grid Y={(hi-lo)/5:g}
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
def make(out,defines,waves,step=None,step2=None,npts=301):
    s=raw
    for k,v in defines.items():
        s,n=re.subn(rf'Text=\.DEFINE {k} .*',f'Text=.DEFINE {k} {v}',s); assert n==1,k
    # remove AC waveform blocks and AC stepping
    blocks=re.split(r'\n(?=\[)',s)
    keep=[];first=None
    for b in blocks:
        h=b.split('\n',1)[0].strip()
        if h in('[WaveForm]','[Stepping]') and '\nAnalysis=AC\n' in b+'\n':
            if first is None: first=len(keep)
            continue
        keep.append(b)
    new=''
    for i,(plt,y,yr) in enumerate(waves):
        new+=wf(plt,i+1,y,yr,COLORS[i%len(COLORS)])+'\n'
    for idx,st in enumerate([x for x in (step,step2) if x]):
        name,fr,to,val=st
        new+=f"[Stepping]\nAnalysis=AC\nIndex={idx+1}\nStatus=On\nParameter Type=Symbolic\nName={name}\nFrom={fr}\nTo={to}\nValue={val}\n\n"
    keep.insert(first,new.rstrip('\n')+'\n')
    s='\n'.join(keep)
    s=re.sub(r'(\[Limits\]\nAnalysis=AC\nFRange=)[^\n]*\nNPts=\d+',rf'\g<1>20k,10\nNPts={npts}',s)
    open(out,'w',encoding='latin1',newline='\r\n').write(s)
D='/mnt/user-data/outputs/sim/02_AC/'
stages=[(1,'dB(v(SPK))',(30,-30)),(2,'dB(v(DRAIN))',(30,-30)),(2,'dB(v(GAINW))',(30,-30)),(2,'dB(v(O386))',(30,-30)),(2,'dB(v(ISFW))',(30,-30)),(2,'dB(v(TIN))',(30,-30))]
make(D+'02b_kat_kazanclari.cir',{},stages)
make(D+'02c_ISF.cir',{'SW':0},[(1,'dB(v(SPK))',(30,-30)),(2,'dB(v(ISFW))-dB(v(O386))',(0,-30))],step=('ISF',0,1,0.25))
make(D+'02d_GAIN.cir',{},[(1,'dB(v(SPK))',(40,-20)),(2,'dB(v(O386))',(40,-20))],step=('GAIN',0.1,1,0.45))
make(D+'02e_VOLUME.cir',{},[(1,'dB(v(SPK))',(40,-40))],step=('VOL',0.1,1,0.3))
make(D+'02f_C15_R5_asbuilt.cir',{'ISF':0},[(1,'dB(v(SPK))',(30,-30)),(2,'dB(v(ISFW))-dB(v(O386))',(0,-30))],step=('C15V','253p','330p','77p'),step2=('R5V','32k','33k','1k'))
make(D+'02g_C9.cir',{},[(1,'dB(v(SPK))',(30,-30)),(2,'dB(v(DRAIN))',(30,-10))],step=('C9V','1p','22u','22u'))
def mknoise(out):
    global raw
    old=raw
    raw=re.sub(r'NInput=NONE\nNOutput=2','NInput=VGIT\nNOutput=SPK',raw)
    make(out,{},[(1,'INOISE*1e9',(100,0)),(2,'ONOISE*1e6',(100,0)),(3,'SQRT(SD(ONOISE*ONOISE))*1e6',(1000,0))])
    raw=old
import os; os.makedirs('/mnt/user-data/outputs/sim/05_NOISE',exist_ok=True)
mknoise('/mnt/user-data/outputs/sim/05_NOISE/05a_gurultu.cir')
