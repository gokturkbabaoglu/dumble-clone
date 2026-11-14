# KiCad PCB düzenleyici Python konsolunda: açık kartın toner ve parça yerleşimi PDF'lerini üretir.
import os, pcbnew
b = pcbnew.GetBoard()
klasor = os.path.join(os.path.dirname(b.GetFileName()), 'cikti')
os.makedirs(klasor, exist_ok=True)
pc = pcbnew.PLOT_CONTROLLER(b)
po = pc.GetPlotOptions()
po.SetOutputDirectory(klasor)
po.SetPlotFrameRef(False)
po.SetAutoScale(False)
po.SetScale(1)
po.SetMirror(False)          # B.Cu üstten bakışla basılır; plakete yüzüstü konunca doğru yöne döner
po.SetBlackAndWhite(True)
po.SetUseAuxOrigin(False)
try:
    po.SetDrillMarksType(pcbnew.DRILL_MARKS_SMALL_DRILL_SHAPE)   # delik merkez işaretleri
except Exception:
    po.SetDrillMarksType(1)
kenar_eklendi = False
for fn in ('SetPlotOnAllLayersSequence', 'SetPlotOnAllLayersSelection'):
    if kenar_eklendi or not hasattr(po, fn): continue
    try:
        if fn.endswith('Sequence'):
            sq = pcbnew.LSEQ(); sq.push_back(pcbnew.Edge_Cuts); getattr(po, fn)(sq)
        else:
            ls = pcbnew.LSET(); ls.AddLayer(pcbnew.Edge_Cuts); getattr(po, fn)(ls)
        kenar_eklendi = True
    except Exception as e:
        print(fn, 'olmadı:', e)
print('kenar her sayfada:', kenar_eklendi, [a for a in dir(po) if 'AllLayers' in a])
for katman, ad, acik in ((pcbnew.B_Cu, 'toner_alt_bakir_1e1', 'B.Cu 1:1'), (pcbnew.F_SilkS, 'parca_yerlesimi', 'F.SilkS')):
    pc.SetLayer(katman)
    pc.OpenPlotfile(ad, pcbnew.PLOT_FORMAT_PDF, acik)
    pc.PlotLayer()
pc.ClosePlot()
print('PDF hazır:', klasor)
