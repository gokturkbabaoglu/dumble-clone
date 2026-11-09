# ======================= PARAMETRELER (ölçüler netleşince buradan değiştir) =======================
# Tüm ölçüler mm. Görüntü koordinatı: X sağa, Y aşağı (ön kenar = Y büyük).
BW, BH = 165.1, 114.3            # kart boyutu
# --- 6.35 mm giriş jakı (mono, kesicili) ---
J635_PIN_FROM_FRONT = (7.5, 15.0, 22.5)   # gövde ön yüzünden pin 1,2,3'e
J635_LATERAL = (-1.25, 1.25, 1.25)        # eksenden yanal kayma (pin 1,2,3); ters çıkarsa işaretleri değiştir
J635_FUNC = ('GND', 'INDET', 'IN')        # pin1 şase, pin2 kesici(detect), pin3 uç
J635_BODY = (14.0, 25.0)                  # en x derinlik
J635_HOLE = 2.3; J635_PAD = 3.6           # yassı bacak 2.5x1 mm -> 2.3 mm delik ya da yarık
# --- PJ-324M 3.5 mm kulaklık jakı (üstten bakış çiziminden) ---
# (ön yüzden derinlik, yanal +=çizimde yukarı) ; pin: 1 sleeve, 2 ring-NC, 3 ring, 4 tip, 5 tip-NC
PJ324 = {1:(1.7,0.0), 2:(9.6,5.2), 3:(8.6,2.6), 4:(13.0,-4.6), 5:(5.9,-4.1)}
PJ324_BODY = (11.5, 14.2); PJ324_HOLE = 1.6; PJ324_PAD = 2.2
# --- 16 mm pot (WH148) ---
POT_PITCH = 5.0                 # bacak aralığı (1 mm bacak + 4 mm boşluk)
POT_SETBACK = 5.0               # gövde ön yüzünden bacak sırasına (ölçülmedi, tahmini)
POT_BODY = (17.0, 9.5); POT_HOLE = 1.3; POT_PAD = 2.6
# --- LED (90 derece bükülü bacak) ---
LED_D = 5.0; LED_PITCH = 2.54; LED_SETBACK = 5.0
# --- Sigorta yuvası ---
FUSE_BODY = (23.0, 9.0); FUSE_PITCH = 10.0; FUSE_HOLE = 1.3; FUSE_PAD = 2.8
# --- Vidalı klemens ---
TB_PITCH = 5.08; TB_BODY = (10.2, 7.6); TB_HOLE = 1.3; TB_PAD = 2.8
# --- Elektrolitikler (25 V tahmini ölçüler: çap, bacak aralığı) ---
ELKO = {'4.7µ':(5.0,2.54),'10µ':(5.0,2.54),'22µ':(5.0,2.54),'100µ':(6.3,2.54),'220µ':(8.0,3.81),
        '470µ':(10.0,5.08),'1000µ':(12.5,5.08),'2200µ':(16.0,5.08)}
ELKO_ALT = {'2200µ':7.62}      # ikinci delik seçeneği (7.5 mm aralık)
FILM_1U_ALT = 7.62              # 1 µF film için ikinci delik (5 mm + 7.5 mm)
# --- TDA2003 + klipsli soğutucu ---
HS_KEEPOUT = (22.0, 16.0)       # soğutucunun kart üstündeki izdüşümü (en x derinlik), tab tarafında
# --- Panel (ön) yerleşimi: ekseni X (mm) ---
FRONT_X = {'J1':12.0, 'RV1':36.0, 'SW1':57.0, 'RV2':79.0, 'RV3':103.0, 'J2':125.0, 'D2':140.0, 'SW2':155.0}
R3_LED = '2.2k'                 # LED rengine göre (sarı/yeşil 2.2k ~4.5 mA)
