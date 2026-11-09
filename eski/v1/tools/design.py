# Netlist, footprints. Units: u = 1.27 mm grid
U=1.27
# footprint: list of pin offsets (dx,dy) in u at rot 0, plus body (w,h) mm and shape
FP={
 'R':   dict(pins=[(0,0),(8,0)], body=('rect',6.5,2.6), pad=2.0),
 'R4':  dict(pins=[(0,0),(4,0)], body=('rect',3.2,2.0), pad=1.8),   # unused
 'CF':  dict(pins=[(0,0),(4,0)], body=('rect',7.2,3.5), pad=2.0),   # film/ceramic 5mm
 'E2':  dict(pins=[(0,0),(2,0)], body=('circ',5.5), pad=1.8),      # small elko 2.5mm
 'E8':  dict(pins=[(0,0),(3,0)], body=('circ',8.0), pad=2.0),      # 220u/25V
 'E10': dict(pins=[(0,0),(4,0)], body=('circ',10.5), pad=2.2),     # 100u/100V,470u
 'E13': dict(pins=[(0,0),(4,0)], body=('circ',13.0), pad=2.3),     # 1000u
 'E16': dict(pins=[(0,0),(4,0)], body=('circ',16.0), pad=2.4),     # 2200u
 'TO92':dict(pins=[(0,0),(2,0),(4,0)], body=('to92',5.0,4.0), pad=1.7),
 'TRIM':dict(pins=[(0,0),(2,0),(4,0)], body=('rect',9.8,4.9), pad=1.7),
 'DIP8':dict(pins=[(0,0),(2,0),(4,0),(6,0),(6,-6),(4,-6),(2,-6),(0,-6)], body=('dip',10.2,6.6), pad=1.7),
 'DO201':dict(pins=[(0,0),(12,0)], body=('rect',9.5,5.4), pad=2.4),
 'PW5': dict(pins=[(-3,0),(-1,3),(0,0),(1,3),(3,0)], body=('pw',10.4,4.6), pad=1.9),
 'PAD': dict(pins=[(0,0)], body=None, pad=2.4),
}
# true mm offsets for pentawatt pins (relative to pin3), rot0, y down
PW_TRUE=[(-3.4,0),(-1.7,3.7),(0,0),(1.7,3.7),(3.4,0)]
# components: ref: (fp, value, [nets per pin])
C={
 # power
 'D1':('DO201','1N5822',['VIN','V12']),          # anode, cathode
 'C1':('E16','2200µ',['V12','GND']),
 'C2':('CF','100n',['V12','GND']),
 'R1':('R','100',['V12','V2']),
 'C3':('E8','220µ',['V2','GND']),
 'C8':('E10','100µ',['V2','GND']),
 'C4':('CF','100n',['V2','GND']),
 'R2':('R','1k',['V2','V3']),
 'C5':('E10','100µ',['V3','GND']),
 'R3':('R','2.2k',['V12','LEDA']),
 # jfet
 'R5':('R','33k',['IN','GATE']),
 'R6':('R','1M',['GATE','GND']),
 'Q1':('TO92','BF245B',['GATE','SRC','DRAIN']),   # G S D
 'TR1':('TRIM','10k',['SRC','GND','GND']),
 'C9':('E2','22µ*',['SRC','GND']),
 'R4':('R','6.8k',['V3','DRAIN']),
 'C10':('CF','100n',['DRAIN','GAININ']),
 # lm386
 'U1':('DIP8','LM386',['G1','GND','GAINW','GND','O386','V2','BYP','G8']),
 'R7':('R','15k*',['GAINW','GND']),
 'R8':('R','1.2k',['G1','G1C']),
 'C11':('E2','10µ',['G1C','G8']),
 'C12':('E2','10µ',['BYP','GND']),
 'R9':('R','10',['O386','ZOB1']),
 'C13':('CF','47n',['ZOB1','GND']),
 'C14':('E2','4.7µ',['O386','X']),
 # tone stacks
 'R10':('R','100k',['X','GND']),
 'R11':('R','100k',['X','USN1']),
 'C15':('CF','250p',['X','UST']),
 'C16':('CF','100n',['USN1','USB']),
 'C17':('CF','47n',['USN1','USM']),
 'R13':('R','100k',['UST','USOUT']),
 'R14':('R','150k',['USOUT','USB']),
 'R15':('R','120k',['USB','USM']),
 'R16':('R','6.8k',['USM','GND']),
 'R12':('R','10k',['X','Y']),
 'R17':('R','4.7k',['Y','GND']),
 'R18':('R','33k',['Y','UKN1']),
 'C18':('CF','470p',['Y','UKT']),
 'C19':('CF','22n',['UKN1','UKB']),
 'C20':('CF','22n',['UKN1','UKM']),
 'R19':('R','91k',['UKT','UKOUT']),
 'R20':('R','130k',['UKOUT','UKB']),
 'R21':('R','470k',['UKB','UKM']),
 'R22':('R','24k',['UKM','GND']),
 # volume divider / tda
 'R23':('R','47k',['VOLW','Z']),
 'R24':('R','10k',['Z','GND']),
 'C21':('CF','3.3n',['Z','GND']),
 'C22':('CF','1µ',['Z','TIN']),
 'U2':('PW5','TDA2003',['TIN','TNEG','GND','TOUT','V12']),
 'R25':('R','220',['TNEG','TOUT']),
 'R26':('R','2.2',['TNEG','TRC']),
 'C23':('E10','470µ',['TRC','GND']),
 'R27':('R','1',['TOUT','ZOB2']),
 'C24':('CF','100n',['ZOB2','GND']),
 'C6':('CF','100n',['V12','GND']),
 'C7':('E13','1000µ',['V12','GND']),
 'C25':('E16','2200µ',['TOUT','SPK']),
 'R28':('R','10',['SPK','HPS']),
 'R29':('R','330',['HPS','GND']),
 'C21b':None,
}
del C['C21b']
# edge pads (wire points)
PADS={
 'P_IN':'IN','P_ING':'GND','P_GIN':'GAININ','P_GW':'GAINW','P_GG':'GND',
 'P_US':'USOUT','P_UK':'UKOUT','P_VW':'VOLW','P_VG':'GND',
 'P_SPK':'SPK','P_HPS':'HPS','P_SPKG':'GND',
 'P_LEDA':'LEDA','P_LEDK':'GND','P_VIN':'VIN','P_PG':'GND'}
PADLABEL={'P_IN':'GİRİŞ uç','P_ING':'GİRİŞ şase','P_GIN':'GAIN 3','P_GW':'GAIN 2','P_GG':'GAIN 1/GND',
 'P_US':'ISF 1 (US)','P_UK':'ISF 3 (UK)','P_VW':'VOL 2','P_VG':'VOL 1/GND',
 'P_SPK':'ÇIKIŞ→jak uç','P_HPS':'jak sleeve','P_SPKG':'hop. −',
 'P_LEDA':'LED +','P_LEDK':'LED −','P_VIN':'+12V (anahtar)','P_PG':'GND (DC jak)'}
for p,n in PADS.items(): C[p]=('PAD',PADLABEL[p],[n])
