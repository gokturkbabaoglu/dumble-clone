"""PCB önizleme (yalnız kontrol için): padler, gövde (F.Fab), kenar, B.Cu yollar."""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from sexp import parse, find, first
import gen_pcb as GP, pad_check as PC
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
def render(pcbfile, png, title=''):
    b = parse(open(pcbfile, encoding='utf-8').read())
    fig, ax = plt.subplots(figsize=(18.5, 9.6 + 0.6), dpi=110)
    ax.set_xlim(GP.X0 - 3, GP.X0 + GP.W + 3); ax.set_ylim(GP.Y0 + GP.H + 3, GP.Y0 - 3); ax.set_aspect('equal'); ax.axis('off')
    ax.plot([GP.X0, GP.X0 + GP.W, GP.X0 + GP.W, GP.X0, GP.X0], [GP.Y0, GP.Y0, GP.Y0 + GP.H, GP.Y0 + GP.H, GP.Y0], 'k', lw=1)
    for s in find(b, 'segment'):
        a, e = first(s, 'start'), first(s, 'end')
        ax.plot([float(a[1]), float(e[1])], [float(a[2]), float(e[2])], color='#1f6fd1', lw=max(0.6, float(first(s, 'width')[1]) * 3.5), solid_capstyle='round', zorder=2)
    for f in find(b, 'footprint'):
        at = first(f, 'at'); fx, fy = float(at[1]), float(at[2]); fa = float(at[3]) if len(at) > 3 else 0
        ref = [p for p in find(f, 'property') if p[1] == 'Reference'][0][2]
        for g in find(f, 'fp_rect') + find(f, 'fp_line') + find(f, 'fp_circle'):
            if first(g, 'layer')[1] != 'F.Fab': continue
            if g[0] == 'fp_circle':
                c = first(g, 'center'); e = first(g, 'end'); r = math.hypot(float(c[1]) - float(e[1]), float(c[2]) - float(e[2]))
                dx, dy = GP.rot(float(c[1]), float(c[2]), fa); ax.add_patch(plt.Circle((fx + dx, fy + dy), r, fill=False, color='gray', lw=0.5)); continue
            s, e = first(g, 'start'), first(g, 'end')
            pts = [(float(s[1]), float(s[2])), (float(e[1]), float(e[2]))]
            if g[0] == 'fp_rect': pts = [pts[0], (pts[1][0], pts[0][1]), pts[1], (pts[0][0], pts[1][1]), pts[0]]
            w = [GP.rot(x, y, fa) for x, y in pts]
            ax.plot([fx + p[0] for p in w], [fy + p[1] for p in w], color='gray', lw=0.5)
        cx = cy = 0; pads = GP.pad_world(f)
        for p in pads:
            o = PC.outline(p, 36); ax.add_patch(Polygon(o, closed=True, fc='#c98a2b', ec='none', zorder=3))
            ax.add_patch(plt.Circle((p['x'], p['y']), p['drill'] / 2, color='white', zorder=4))
            cx += p['x']; cy += p['y']
        if pads: ax.text(cx / len(pads), cy / len(pads), ref, fontsize=6, ha='center', va='center', zorder=5, color='darkred', weight='bold')
    ax.set_title(title, fontsize=10)
    fig.savefig(png, bbox_inches='tight'); plt.close(fig)
if __name__ == '__main__':
    render(os.path.join(HERE, 'amfi_yeni.kicad_pcb'), sys.argv[2] if len(sys.argv) > 2 else '/tmp/pcb.png')
