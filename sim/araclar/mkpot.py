import re,mk6
s=open('/tmp/c9base.txt',encoding='latin1').read()
s=s.replace('V={IF(MODE<0.5,1p,22u)}','V=22u',1)
s=s.replace('V={IF(MODE<1.5,1m,IF(MODE<2.5,1k,2.2k))}','V={POTR*(1-ROT)+1m}',1)
s=s.replace('Text=.DEFINE MODE 0\r\n','').replace('Text=.DEFINE MODE 0\n','Text=.DEFINE POTR 2.2k\nText=.DEFINE ROT 0.5\n',1)
s=re.sub(r'Text=\* MODE:[^\n]*','Text=* RBP = C9 seri pot (lineer); ROT 0=tam sola (en az kazanc), 1=tam saga (en cok kazanç)',s)
assert 'POTR' in s and 'V=22u' in s
mk6.RAW=s
O='/mnt/user-data/outputs/sim/08_POT/'
st=[('POTR','2.2k','5k','2.8k'),('ROT','0','1','0.1')]
mk6.build(O+'08a_pot_kazanc.cir','AC',[(1,'dB(v(DRAIN))'),(2,'dB(v(SPK))')],steps=st)
mk6.build(O+'08b_pot_THD.cir','Transient',[(1,'v(SPK)'),(2,'v(O386)')],steps=st,defs={'VIN':'0.15'})
