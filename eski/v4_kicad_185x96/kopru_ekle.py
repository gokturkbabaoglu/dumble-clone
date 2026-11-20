"""Bulunan köprüleri (K1..) yönlendirilmiş karta ayak izi olarak ekler. Kullanım: kopru_ekle.py girdi.kicad_pcb cikti.kicad_pcb"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kopru, gen_kicad as G

def fp_text(ref, a, b):
    L = round(math.dist(a, b), 2)
    dx, dy = b[0] - a[0], b[1] - a[1]
    r = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[(int(round(dx / L)), int(round(dy / L)))]
    name = 'Jumper_P%s' % ('%g' % L)
    u = lambda *k: G.uid('kopru', ref, *k)
    s = '\t(footprint "amfi:%s" (layer "F.Cu") (uuid "%s") (at %s %s %d)\n' % (name, u('fp'), a[0], a[1], r)
    s += '\t\t(property "Reference" "%s" (at %s -1.6 %d) (layer "F.SilkS") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))\n' % (ref, L / 2, r, u('ref'))
    s += '\t\t(property "Value" "tel köprü %s mm" (at %s 1.6 %d) (layer "F.Fab") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))\n' % ('%g' % L, L / 2, r, u('val'))
    s += '\t\t(property "Footprint" "amfi:%s" (at 0 0 %d) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))\n' % (name, r, u('fpp'))
    s += '\t\t(path "/%s") (sheetname "/") (sheetfile "amfi.kicad_sch")\n' % G.uid('sym', ref)
    s += "\t\t(attr through_hole)\n\t\t(jumper_pad_groups (\"1\" \"2\"))\n"
    s += '\t\t(fp_line (start 0 0) (end %s 0) (stroke (width 0.5) (type solid)) (layer "F.SilkS") (uuid "%s"))\n' % (L, u('l'))
    s += '\t\t(fp_rect (start -1.25 -1.25) (end %s 1.25) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "%s"))\n' % (L + 1.25, u('c'))
    for i, x in ((1, 0), (2, L)):
        s += '\t\t(pad "%d" thru_hole circle (at %s 0 %d) (size 2 2) (drill 0.9) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (net "GND") (zone_connect 2) (uuid "%s"))\n' % (i, x, r, u('p', i))
    s += '\t)\n'
    return s, L

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    res = kopru.bul(src)
    txt = open(src, encoding='utf-8').read()
    add = ''; liste = []
    for i, (pad, gap, best) in enumerate(res, 1):
        ref = 'K%d' % i
        f, L = fp_text(ref, best[2], best[3]); add += f
        liste.append((ref, pad, L, best[2], best[3]))
    k = txt.rstrip().rfind(')')
    open(dst, 'w', encoding='utf-8').write(txt[:k] + add + ')\n')
    for l in liste: print(l)
