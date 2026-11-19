# KiCad PCB düzenleyici Python konsolunda: kalın yol kartlarını doldur, kontrol et, kaydet, PDF üret.
#   exec(open(r"...\kalin_yol\son.py", encoding="utf-8").read())
# son_liste.json: {"kartlar": ["amfi_X", ...], "pdf": "amfi_X"}  (girdi: <ad>.kicad_pcb, çıktı: <ad>_d.kicad_pcb)
import os, json, traceback, importlib, pcbnew
pcbnew = importlib.reload(pcbnew)   # konsolda SWIG türleri bozulabiliyor
KLASOR = os.environ.get('AMFI_KLASOR', r"C:\Users\ASUS\Desktop\amfi son\kicad_amfi\kalin_eski")
cfg = json.load(open(os.path.join(KLASOR, 'son_liste.json'), encoding='utf-8'))
sonuc = {}
for ad in cfg['kartlar']:
    try:
        b = pcbnew.LoadBoard(os.path.join(KLASOR, ad + '.kicad_pcb'))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        b.BuildConnectivity()
        kopuk = b.GetConnectivity().GetUnconnectedCount(False)
        out = os.path.join(KLASOR, ad + '_d.kicad_pcb')
        pcbnew.SaveBoard(out, b)
        rpt = os.path.join(KLASOR, ad + '_drc.rpt')
        try:
            pcbnew.WriteDRCReport(b, rpt, pcbnew.EDA_UNITS_MM, True)
        except Exception as e:
            rpt = 'DRC olmadı: %s' % e
        sonuc[ad] = dict(kopuk=kopuk, drc=rpt)
    except Exception:
        sonuc[ad] = dict(hata=traceback.format_exc())
json.dump(sonuc, open(os.path.join(KLASOR, 'son_sonuc.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
if cfg.get('pdf'):
    b = pcbnew.LoadBoard(os.path.join(KLASOR, cfg['pdf'] + '_d.kicad_pcb'))
    klasor = os.path.join(KLASOR, 'cikti'); os.makedirs(klasor, exist_ok=True)
    pc = pcbnew.PLOT_CONTROLLER(b); po = pc.GetPlotOptions()
    po.SetOutputDirectory(klasor); po.SetPlotFrameRef(False); po.SetAutoScale(False); po.SetScale(1)
    po.SetMirror(False); po.SetBlackAndWhite(True); po.SetUseAuxOrigin(False)
    try: po.SetDrillMarksType(pcbnew.DRILL_MARKS_SMALL_DRILL_SHAPE)
    except Exception: po.SetDrillMarksType(1)
    for fn in ('SetPlotOnAllLayersSequence', 'SetPlotOnAllLayersSelection'):
        if not hasattr(po, fn): continue
        try:
            if fn.endswith('Sequence'):
                sq = pcbnew.LSEQ(); sq.push_back(pcbnew.Edge_Cuts); getattr(po, fn)(sq)
            else:
                ls = pcbnew.LSET(); ls.AddLayer(pcbnew.Edge_Cuts); getattr(po, fn)(ls)
            break
        except Exception as e: print(fn, e)
    for katman, ad, acik in ((pcbnew.B_Cu, 'toner_alt_bakir_1e1_A4', 'B.Cu 1:1'), (pcbnew.F_SilkS, 'parca_yerlesimi_A4', 'F.SilkS')):
        pc.SetLayer(katman); pc.OpenPlotfile(ad, pcbnew.PLOT_FORMAT_PDF, acik); pc.PlotLayer()
    pc.ClosePlot()
print('son bitti:', sonuc)
