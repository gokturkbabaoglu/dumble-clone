"""Bakır aralığı kontrolü: farklı netlere ait bakırlar arasındaki en küçük mesafe (mm).
Kullanım: python3 drc.py final_geom.pkl
"""
import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import ndimage
from final2 import raster, PX

d = pickle.load(open(sys.argv[1], 'rb'))
items, g = d['items'], d['g']
netlist = sorted(set(n for n, k, _ in items if k in ('pad', 'seg')))
cop = {n: (g if n == 'GND' else raster(items, lambda m, n=n: m == n)) for n in netlist}
allc = np.zeros_like(g)
for n in netlist: allc |= cop[n]
worst = []
for n in netlist:
    others = allc & ~cop[n]
    if n == 'GND': others = allc & ~g
    dist = ndimage.distance_transform_edt(~cop[n]) / PX
    v = dist[others]
    if v.size:
        i = np.argmin(v); ys, xs = np.nonzero(others)
        worst.append((v[i], n, xs[i] / PX, ys[i] / PX))
worst.sort()
print('en küçük aralık: %.2f mm' % worst[0][0])
for w in worst[:8]: print('  %.2f mm  %-8s  (x=%.1f, y=%.1f)' % w)
