# KiCad PCB düzenleyicinin Python konsolunda çalışır (Araçlar > Komut Dosyası Konsolu):
#   exec(open(r"<klasör>\toplu.py", encoding="utf-8").read())
# Aynı klasördeki toplu_liste.json içindeki kartları sırayla: DSN'e aktarır, Freerouting'i (penceresiz, paralel)
# çalıştırır, SES'i içe alır, GND dolgusunu yeniden ekleyip doldurur, <ad>_r.kicad_pcb olarak kaydeder.
# Sonuçlar toplu_sonuc.json dosyasına yazılır.
import os, json, subprocess, time, shutil, tempfile, traceback
import pcbnew

KLASOR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else r"C:\Users\ASUS\Desktop\Yeni klasör (3)\kicad_amfi"
JAR = os.path.expanduser(r"~\Documents\KiCad\10.0\3rdparty\plugins\app_freerouting_kicad-plugin\jar\freerouting-2.5.0.jar")
_zip = os.path.join(KLASOR, 'paket.zip')
if os.path.exists(_zip):            # kart dosyaları tek paket halinde gelir; aç ve sil
    import zipfile
    with zipfile.ZipFile(_zip) as zf: zf.extractall(KLASOR)
    os.remove(_zip)
cfg = json.load(open(os.path.join(KLASOR, 'toplu_liste.json'), encoding='utf-8'))
KARTLAR = cfg['kartlar']
PARALEL = cfg.get('paralel', 3)
EK = cfg.get('ek_arguman', [])
TMP = tempfile.mkdtemp(prefix='amfi_fr_')        # yol boşluk içermesin
sonuc = {}
log = open(os.path.join(KLASOR, 'toplu_log.txt'), 'w', encoding='utf-8')
def yaz(*a):
    log.write(' '.join(str(x) for x in a) + '\n'); log.flush()

def hazirla(ad):
    b = pcbnew.LoadBoard(os.path.join(KLASOR, ad + '.kicad_pcb'))
    # dolgu bölgelerini (kuralsız, netli) çıkar: yönlendirme sırasında engel olmasınlar
    zonlar = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()]
    for z in zonlar: b.Remove(z)
    dsn = os.path.join(TMP, ad + '.dsn')
    pcbnew.ExportSpecctraDSN(b, dsn)
    return b, zonlar, dsn

isler = []
for ad in KARTLAR:
    try:
        b, z, dsn = hazirla(ad)
        ses = os.path.join(TMP, ad + '.ses')
        cmd = ['java', '-jar', JAR, '-de', dsn, '-do', ses, '--gui.enabled=false', '--api_server.enabled=false',
               '--mcp_server.enabled=false'] + EK
        isler.append(dict(ad=ad, b=b, z=z, ses=ses, cmd=cmd, p=None, t0=None))
    except Exception:
        yaz(ad, 'HAZIRLIK HATASI', traceback.format_exc())

bekleyen = list(isler); calisan = []
while bekleyen or calisan:
    while bekleyen and len(calisan) < PARALEL:
        j = bekleyen.pop(0)
        j['p'] = subprocess.Popen(j['cmd'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        j['t0'] = time.time(); calisan.append(j); yaz(j['ad'], 'başladı')
    for j in list(calisan):
        if j['p'].poll() is not None or time.time() - j['t0'] > cfg.get('zaman_asimi', 900):
            if j['p'].poll() is None: j['p'].kill()
            calisan.remove(j)
            ad = j['ad']; b = j['b']
            try:
                if os.path.exists(j['ses']):
                    pcbnew.ImportSpecctraSES(b, j['ses'])
                for z in j['z']:
                    b.Add(z)
                pcbnew.ZONE_FILLER(b).Fill(b.Zones())
                b.BuildConnectivity()
                kopuk = b.GetConnectivity().GetUnconnectedCount(False)
                out = os.path.join(KLASOR, ad + '_r.kicad_pcb')
                pcbnew.SaveBoard(out, b)
                sonuc[ad] = dict(kopuk=kopuk, sure=round(time.time() - j['t0']), ses=os.path.exists(j['ses']))
                yaz(ad, 'bitti', sonuc[ad])
            except Exception:
                sonuc[ad] = dict(hata=traceback.format_exc()); yaz(ad, 'HATA', sonuc[ad]['hata'])
            json.dump(sonuc, open(os.path.join(KLASOR, 'toplu_sonuc.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    time.sleep(1)
yaz('TAMAM')
log.close()
print('toplu yönlendirme bitti:', sonuc)
