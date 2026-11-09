import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from params import *
U = 1.27
def mk(pins, body, pad, hole=None, shape='rect'):
    return dict(pins=pins, body=body, pad=pad, hole=hole or (0.9 if pad < 2.1 else (1.1 if pad < 2.5 else 1.3)), shape=shape)
FP = {}
FP['R'] = mk([(0,0),(10.16,0)], ('rect',6.5,2.6), 2.0, 0.9)
FP['CF'] = mk([(0,0),(5.08,0)], ('rect',7.2,3.5), 2.0, 0.9)
FP['CF1U'] = mk([(0,0),(5.08,0),(FILM_1U_ALT,0)], ('rect',10.0,4.5), 2.0, 0.9)
FP['CC'] = mk([(0,0),(5.08,0)], ('rect',5.0,3.0), 1.9, 0.8)   # seramik pF
for k,(d,p) in ELKO.items():
    pins=[(0,0),(p,0)]
    if k in ELKO_ALT: pins.append((ELKO_ALT[k],0))
    FP['E'+k] = mk(pins, ('circ',d), 2.0 if d<8 else 2.4, 0.9 if d<8 else 1.1)
FP['TO92'] = mk([(0,0),(2.54,0),(5.08,0)], ('to92',5.0,4.0), 1.7, 0.8)
FP['TRIM'] = mk([(0,0),(2.54,0),(5.08,0)], ('rect',9.8,4.9), 1.7, 0.8)
FP['DIP8'] = mk([(0,0),(2.54,0),(5.08,0),(7.62,0),(7.62,-7.62),(5.08,-7.62),(2.54,-7.62),(0,-7.62)], ('dip',10.2,6.6), 1.7, 0.8)
FP['DO201'] = mk([(0,0),(15.24,0)], ('rect',9.5,5.4), 2.4, 1.3)
FP['PW5'] = mk([(-3.4,0),(-1.7,3.7),(0,0),(1.7,3.7),(3.4,0)], ('pw',10.4,4.6), 1.9, 1.0)
FP['PAD'] = mk([(0,0)], None, 2.6, 1.1)
FP['KO1'] = mk([(0,0)], ('front',15.0,20.0), 0.01, 0.0)
FP['KO2'] = mk([(0,0)], ('front',17.0,22.0), 0.01, 0.0)
FP['MH'] = mk([(0,0)], ('circ',7.0), 5.6, 3.2)
FP['JMP'] = mk([(0,0),(5.08,0)], ('rect',4.0,1.2), 2.0, 0.9)     # tel köprü (JP1)
# front parts: pin offsets relative to axis point on front edge; local frame: +y = toward back (north) -> image -Y
def front(pins_depth_lat, body, pad, hole, shape):
    # (depth from front face, lateral) -> image offset (X=lateral... ) ; drawing lateral + (up in top view, front left) maps to image -X
    return mk([(-lat, -dep) for dep,lat in pins_depth_lat], body, pad, hole, shape)
FP['J635'] = front([(J635_PIN_FROM_FRONT[i], J635_LATERAL[i]) for i in range(3)], ('front',)+J635_BODY, J635_PAD, J635_HOLE, 'oval')
FP['PJ324'] = front([PJ324[i] for i in (1,2,3,4,5)], ('front',)+PJ324_BODY, PJ324_PAD, PJ324_HOLE, 'round')
FP['POT'] = mk([(-POT_PITCH,-POT_SETBACK),(0,-POT_SETBACK),(POT_PITCH,-POT_SETBACK)], ('front',)+POT_BODY, POT_PAD, POT_HOLE)
FP['LED'] = mk([(-LED_PITCH/2,-LED_SETBACK),(LED_PITCH/2,-LED_SETBACK)], ('front',LED_D+1,LED_SETBACK-1.5), 1.9, 0.9)
FP['FUSE'] = mk([(0,0),(FUSE_PITCH,0)], ('rectc',)+FUSE_BODY, FUSE_PAD, FUSE_HOLE)
FP['TB2'] = mk([(0,0),(TB_PITCH,0)], ('rectc',)+TB_BODY, TB_PAD, TB_HOLE)
# ------------------------------- NETLIST -------------------------------
C = {
 # power
 'TB1':('TB2','DC giriş',['DCIN','GND']),
 'F1':('FUSE','1A',['DCIN','FUSED']),
 'D1':('DO201','1N5822',['VIN','V12']),
 'C1':('E2200µ','2200µ',['V12','GND','GND']),
 'C2':('CF','100n',['V12','GND']),
 'R1':('R','100',['V12','V2']),
 'C3':('E220µ','220µ',['V2','GND']),
 'C8':('E100µ','100µ',['V2','GND']),
 'C4':('CF','100n',['V2','GND']),
 'R2':('R','1k',['V2','V3']),
 'C5':('E100µ','100µ',['V3','GND']),
 'R3':('R',R3_LED,['V12','LEDA']),
 'D2':('LED','LED',['LEDA','GND']),
 # input / jfet
 'J1':('J635','GİRİŞ',[{'GND':'GND','INDET':'INDET','IN':'IN'}[f] for f in J635_FUNC]),
 'JP1':('JMP','sus*',['INDET','GND']),
 'R5':('R','33k',['IN','GATE']),
 'R6':('R','1M',['GATE','GND']),
 'Q1':('TO92','BF245B',['DRAIN','SRC','GATE']),     # NXP pinout 1=D 2=S 3=G (kontrol et)
 'TR1':('TRIM','10k',['SRC','GND','GND']),
 'C9':('E22µ','22µ*',['SRC','GND']),
 'R4':('R','6.8k',['V3','DRAIN']),
 'C10':('CF','100n',['DRAIN','GAININ']),
 # gain + sw1
 'RV1':('POT','GAIN B100K',['GND','GAINW','GAININ']),
 'R7':('R','15k',['GAINW','GND']),
 'CB':('CC','470p',['GAININ','SWB']),
 'CD':('CF','3.3n',['SWD','GND']),
 'P_SWB':('PAD','SW1 B',['SWB']),'P_SWC':('PAD','SW1 orta',['GAINW']),'P_SWD':('PAD','SW1 A',['SWD']),
 # lm386
 'U1':('DIP8','LM386',['G1','GND','GAINW','GND','O386','V2','BYP','G8']),
 'R8':('R','1.2k',['G1','G1C']),
 'C11':('E10µ','10µ',['G1C','G8']),
 'C12':('E10µ','10µ',['BYP','GND']),
 'R9':('R','10',['O386','ZOB1']),
 'C13':('CF','47n',['ZOB1','GND']),
 'C14':('E4.7µ','4.7µ',['O386','X']),
 # US stack
 'R10':('R','100k',['X','GND']),
 'R11':('R','100k',['X','USN1']),
 'C15a':('CC','220p',['X','UST']),
 'C15b':('CC','33p',['X','UST']),
 'C16':('CF','100n',['USN1','USB']),
 'C17':('CF','47n',['USN1','USM']),
 'R13':('R','100k',['UST','USOUT']),
 'R14':('R','150k',['USOUT','USB']),
 'R15':('R','120k',['USB','USM']),
 'R16':('R','6.8k',['USM','GND']),
 # UK stack
 'R12':('R','10k',['X','Y']),
 'R17':('R','4.7k',['Y','GND']),
 'R18':('R','33k',['Y','UKN1']),
 'C18':('CC','470p',['Y','UKT']),
 'C19':('CF','22n',['UKN1','UKB']),
 'C20':('CF','22n',['UKN1','UKM']),
 'R19':('R','91k',['UKT','UKOUT']),
 'R20a':('R','120k',['UKOUT','UKBM']),
 'R20b':('R','10k',['UKBM','UKB']),
 'R21':('R','470k',['UKB','UKM']),
 'R22a':('R','22k',['UKM','UKM2']),
 'R22b':('R','2.2k',['UKM2','GND']),
 # ISF + volume pots
 'RV2':('POT','ISF B250K',['USOUT','ISFW','UKOUT']),
 'RV3':('POT','VOL B500K',['GND','VOLW','ISFW']),
 'R23':('R','47k',['VOLW','Z']),
 'R24':('R','10k',['Z','GND']),
 'C21':('CF','3.3n',['Z','GND']),
 'C22':('CF1U','1µ',['Z','TIN','TIN']),
 # TDA
 'U2':('PW5','TDA2003',['TIN','TNEG','GND','TOUT','V12']),
 'R25':('R','220',['TNEG','TOUT']),
 'R26':('R','2.2',['TNEG','TRC']),
 'C23':('E470µ','470µ',['TRC','GND']),
 'R27':('R','1',['TOUT','ZOB2']),
 'C24':('CF','100n',['ZOB2','GND']),
 'C6':('CF','100n',['V12','GND']),
 'C7':('E1000µ','1000µ',['V12','GND']),
 'C25':('E2200µ','2200µ',['TOUT','SPK','SPK']),
 # headphone / speaker
 'J2':('PJ324','KULAKLIK',['HPS','HPNC2','SPK','SPK','SPKT']),   # 1 sleeve,2 ring-NC,3 ring,4 tip,5 tip-NC
 'R28':('R','10',['SPK','HPS']),
 'R29':('R','330',['HPS','GND']),
 'TB2':('TB2','HOPARLÖR',['SPKT','GND']),
 # power switch pads (panel switch)
 'P_PW1':('PAD','GÜÇ orta',['FUSED']),'P_PW2':('PAD','GÜÇ uç',['VIN']),
 'KO_SW1':('KO1','SW1 gövdesi',['NC_KO1']),'KO_SW2':('KO2','güç anahtarı gövdesi',['NC_KO2']),
 'MH1':('MH','M3',['NC_MH1']),'MH2':('MH','M3',['NC_MH2']),'MH3':('MH','M3',['NC_MH3']),
}
POWER_NETS={'V12','VIN','DCIN','FUSED','TOUT','SPK','SPKT','TNEG','TRC','ZOB2'}
