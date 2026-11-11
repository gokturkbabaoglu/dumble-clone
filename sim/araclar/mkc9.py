import re,mk6
s=mk6.RAW
# C9 value
s,n=re.subn(r'(\nV=C9\n(?:.*\n){0,4}?ON=[^\n]*CAPACITANCE\nV=)[^\n]*',r'\g<1>{IF(MODE<0.5,1p,22u)}',s); assert n==1
# move ground right after C9 comp
s,n=re.subn(r'(\[Comp\]\nName=Ground\nPx=)344,432(\nRot=7\n)',r'\g<1>344,480\2',s); assert n==1
res="""[Comp]
Name=Resistor
Px=344,480
Rot=3

[Attr]
ON=10,-14,PART
V=RBP
Style=8192

[Attr]
ON=10,-28,RESISTANCE
V={IF(MODE<1.5,1m,IF(MODE<2.5,1k,2.2k))}
Style=8192

[Attr]
ON=0,0,PACKAGE
V

"""
k=s.index('[Comp]\nName=Ground\nPx=344,480')
s=s[:k]+res+s[k:]
s=s.replace('Text=.DEFINE HP 0','Text=.DEFINE HP 0\nText=.DEFINE MODE 0\nText=* MODE: 0=C9 yok, 1=C9 22u, 2=22u+1k, 3=22u+2.2k',1)
# component count fields may exist; leave
mk6.RAW=s
O='/mnt/user-data/outputs/sim/07_C9/'
st=[('MODE','0','3','1')]
mk6.build(O+'07a_C9_AC.cir','AC',[(1,'dB(v(SPK))'),(2,'dB(v(DRAIN))'),(2,'dB(v(O386))')],steps=st)
mk6.build(O+'07b_C9_THD.cir','Transient',[(1,'v(SPK)'),(2,'v(O386)'),(3,'v(DRAIN)')],steps=[('MODE','0','3','1'),('VIN','0.03','0.33','0.15')])
open('/tmp/c9base.txt','w',encoding='latin1').write(s)
mk6.build(O+'07c_C9_gurultu.cir','AC',[(1,'INOISE*1e9'),(2,'SQRT(SD(ONOISE*ONOISE))*1e6')],steps=st,frange='20k,20')
p=O+'07c_C9_gurultu.cir'; t=open(p,'rb').read().replace(b'NInput=NONE\r\nNOutput=2',b'NInput=VGIT\r\nNOutput=SPK'); assert b'NInput=VGIT' in t; open(p,'wb').write(t)
