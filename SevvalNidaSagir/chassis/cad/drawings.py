import os
"""RAPTOR şase ölçü belgesi: CAD modelinden gizli çizgi hesaplı teknik görünüşler + ölçüler (A4 yatay PDF)."""
import math
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle
import matplotlib.image as mpimg

import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import raptor_chassis as rc
from bom import BOM, BOM_COLUMNS, DIRENC_MOTOR, ROBOTISTAN_BTS

INK = "#111418"
HID = "#7d858c"
DIM = "#1f4e8c"
ACC = "#c4561d"
DATE = "18.11.2026"
PAGES_TOTAL = 9

def _heights():
    a = rc.assembly("B")
    d = {ch.name: ch.obj.val().BoundingBox() for ch in a.children}
    return d["direk_ucu"].zmax, (d["kamera"].zmin + d["kamera"].zmax) / 2

TOP_Z, CAM_Z = _heights()
WIDTH = 2 * (rc.WHEEL_X + rc.WHEEL_W / 2)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7})


def num(v, nd=1):
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".") if nd else f"{v:.0f}"
    return s.replace(".", ",")


# ---------------- HLR projeksiyon ----------------
def project(shape, N, X):
    if isinstance(shape, cq.Workplane):
        shape = shape.val()
    algo = HLRBRep_Algo()
    algo.Add(shape.wrapped)
    algo.Projector(HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*N), gp_Dir(*X))))
    algo.Update()
    algo.Hide()
    h = HLRBRep_HLRToShape(algo)

    def collect(comps):
        out = []
        for c in comps:
            if c is None or c.IsNull():
                continue
            BRepLib.BuildCurves3d_s(c, 1e-6)
            for e in cq.Shape.cast(c).Edges():
                n = 2 if e.geomType() == "LINE" else max(10, min(120, int(e.Length() / 0.6)))
                pts = [e.positionAt(t) for t in np.linspace(0, 1, n)]
                out.append(np.array([(p.x, p.y) for p in pts]))
        return out

    vis = collect([h.VCompound(), h.Rg1LineVCompound(), h.OutLineVCompound()])
    hid = collect([h.HCompound(), h.OutLineHCompound()])
    return vis, hid


def bounds(polys):
    a = np.vstack(polys)
    return a[:, 0].min(), a[:, 0].max(), a[:, 1].min(), a[:, 1].max()


VIEWS = {
    "ust": ((0, 0, 1), (1, 0, 0)),      # üstten: x sağ, y ileri
    "on": ((0, 1, 0), (-1, 0, 0)),      # önden: aracın sağı resmin solunda
    "sag": ((1, 0, 0), (0, 1, 0)),      # sağdan: ön sağda
    "arka": ((0, -1, 0), (1, 0, 0)),    # arkadan: x sağ
}


# ---------------- Sayfa ----------------
class Sheet:
    def __init__(self, pdf, title, part, scale, sheet_no, sub=True):
        self.pdf = pdf
        self.fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4))
        self.fig.patch.set_facecolor("white")
        bg = self.fig.add_axes([0, 0, 1, 1])
        bg.set_xlim(0, 297)
        bg.set_ylim(0, 210)
        bg.axis("off")
        self.bg = bg
        bg.add_patch(Rectangle((8, 8), 281, 194, fill=False, lw=0.9, ec=INK))
        # başlık bloğu
        x0, y0, w, h = 169, 8, 120, 26
        bg.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=0.9, ec=INK))
        for yy in (y0 + 9, y0 + 17):
            bg.plot([x0, x0 + w], [yy, yy], lw=0.5, c=INK)
        bg.plot([x0 + 70, x0 + 70], [y0, y0 + 17], lw=0.5, c=INK)
        bg.plot([x0 + 95, x0 + 95], [y0, y0 + 17], lw=0.5, c=INK)
        bg.text(x0 + 3, y0 + 21.5, "RAPTOR · Araç Hareketi · 3D baskı şase", fontsize=8.5, weight="bold", va="center")
        bg.text(x0 + 3, y0 + 13, part, fontsize=8.5, va="center")
        bg.text(x0 + 3, y0 + 4.5, "Hazırlayan: Şevval Nida Sağır", fontsize=6.5, va="center", color="#333")
        bg.text(x0 + 72, y0 + 13, "Ölçek", fontsize=5.5, va="center", color="#555")
        bg.text(x0 + 72, y0 + 4.5, scale, fontsize=8, va="center")
        bg.text(x0 + 97, y0 + 13, f"Sayfa {sheet_no}/{PAGES_TOTAL}", fontsize=6.5, va="center")
        bg.text(x0 + 97, y0 + 4.5, DATE, fontsize=6.5, va="center")
        bg.text(12, 196, title, fontsize=13, weight="bold", va="top", color=INK)
        if sub: bg.text(12, 189.5, "Ölçüler mm · Genel tolerans ±0,2 · Malzeme PETG (aksi belirtilmedikçe)", fontsize=6.5, va="top", color="#555")

    def axes(self, scale, rect=(12, 36, 273, 148)):
        x, y, w, h = rect
        ax = self.fig.add_axes([x / 297, y / 210, w / 297, h / 210])
        ax.set_xlim(0, w * scale)
        ax.set_ylim(0, h * scale)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.S = scale
        return ax

    def note(self, x, y, lines, fs=6.8, lh=3.6, title=None):
        if title:
            self.bg.text(x, y, title, fontsize=7.5, weight="bold", va="top")
            y -= 4.5
        for ln in lines:
            self.bg.text(x, y, ln, fontsize=fs, va="top")
            y -= lh
        return y

    def save(self):
        self.pdf.savefig(self.fig)
        plt.close(self.fig)


# ---------------- Çizim yardımcıları ----------------
def draw(ax, proj, ox, oy, hidden=True, lw=0.6, color=INK):
    vis, hid = proj
    for p in vis:
        ax.plot(p[:, 0] + ox, p[:, 1] + oy, lw=lw, c=color, solid_capstyle="round")
    if hidden:
        for p in hid:
            ax.plot(p[:, 0] + ox, p[:, 1] + oy, lw=0.3, c=HID, ls=(0, (3, 2)))


def view_label(ax, x, y, text):
    ax.text(x, y, text, fontsize=7, weight="bold", ha="center", va="top", color=INK)


def dim(ax, p1, p2, off, text=None, orient="h", fs=6.5, tol=None):
    S = ax.S
    (x1, y1), (x2, y2) = p1, p2
    if orient == "h":
        L = abs(x2 - x1)
        yd = (max(y1, y2) if off > 0 else min(y1, y2)) + off
        sgn = 1 if off > 0 else -1
        for x, y in ((x1, y1), (x2, y2)):
            ax.plot([x, x], [y + sgn * 0.8 * S, yd + sgn * 1.2 * S], lw=0.3, c=DIM)
        ax.annotate("", xy=(x1, yd), xytext=(x2, yd),
                    arrowprops=dict(arrowstyle="<|-|>", mutation_scale=5, lw=0.4, color=DIM, shrinkA=0, shrinkB=0))
        ax.text((x1 + x2) / 2, yd + 0.6 * S, text if text is not None else num(L), fontsize=fs, ha="center", va="bottom", color=DIM)
    else:
        L = abs(y2 - y1)
        xd = (max(x1, x2) if off > 0 else min(x1, x2)) + off
        sgn = 1 if off > 0 else -1
        for x, y in ((x1, y1), (x2, y2)):
            ax.plot([x + sgn * 0.8 * S, xd + sgn * 1.2 * S], [y, y], lw=0.3, c=DIM)
        ax.annotate("", xy=(xd, y1), xytext=(xd, y2),
                    arrowprops=dict(arrowstyle="<|-|>", mutation_scale=5, lw=0.4, color=DIM, shrinkA=0, shrinkB=0))
        ax.text(xd - 0.7 * S, (y1 + y2) / 2, text if text is not None else num(L), fontsize=fs, ha="center", va="center",
                rotation=90, color=DIM, bbox=dict(fc="white", ec="none", pad=0.4))


def leader(ax, p, dxdy, text, fs=6.3, color=DIM, ha=None):
    S = ax.S
    x, y = p
    tx, ty = x + dxdy[0] * S, y + dxdy[1] * S
    ax.annotate(text, xy=(x, y), xytext=(tx, ty), fontsize=fs, color=color,
                ha=ha or ("left" if dxdy[0] >= 0 else "right"), va="center",
                arrowprops=dict(arrowstyle="-|>", mutation_scale=4.5, lw=0.35, color=color, shrinkA=1, shrinkB=0))


def centerline(ax, p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], lw=0.3, c=ACC, ls=(0, (10, 2, 2, 2)))


def ring(ax, x, y, r, color, lw=0.9):
    ax.add_patch(Circle((x, y), r, fill=False, ec=color, lw=lw))


def table(sheet, x, y, cols, widths, rows, fs=6.3, rh=4.2, head_fs=6.3):
    bg = sheet.bg
    cx = x
    for c, w in zip(cols, widths):
        bg.text(cx + 1, y, c, fontsize=head_fs, weight="bold", va="top")
        cx += w
    y -= rh
    bg.plot([x, x + sum(widths)], [y + 0.6, y + 0.6], lw=0.5, c=INK)
    for r in rows:
        cx = x
        lines = 1
        for v, w in zip(r, widths):
            txt = str(v)
            bg.text(cx + 1, y - 0.3, txt, fontsize=fs, va="top")
            lines = max(lines, txt.count("\n") + 1)
            cx += w
        y -= rh * lines
        bg.plot([x, x + sum(widths)], [y + 0.6, y + 0.6], lw=0.25, c="#bbb")
    return y


# ---------------- Geometri (yerleştirilmiş montaj) ----------------
def asm_shapes(layout, with_elec=False):
    a = rc.assembly(layout)
    keep = []
    for ch in a.children:
        if not with_elec and ch.name.split("_")[0] in ("bts7960", "batarya", "raspberry", "esp32", "kamera", "uwb") and ch.name != "kamera_diregi":
            continue
        keep.append((ch.name, ch.obj.val()))
    return keep


def compound(items):
    return cq.Compound.makeCompound([s for _, s in items])


def sweep_radius(layout):
    axle_y = 0.0 if layout == "B" else rc.AXLE_A
    r = 0
    for name, s in asm_shapes(layout, with_elec=False):
        if name.startswith(("kamera_diregi", "direk_ucu")):
            continue
        vs, _ = s.tessellate(1.0, 0.5)
        for v in vs:
            r = max(r, math.hypot(v.x, v.y - axle_y))
    return r


# =====================================================================
def page_cover(pdf):
    sh = Sheet(pdf, "RAPTOR araç şasesi · Ölçü belgesi", "Kapak ve içindekiler", "—", 1)
    for i, (img, lab) in enumerate((("cover_B.png", "B · Tekerler ortada"), ("cover_A.png", "A · Tekerler önde"))):
        ax = sh.fig.add_axes([(12 + i * 92) / 297, 70 / 210, 88 / 297, 112 / 210])
        im = mpimg.imread(f"{HERE}/doc/{img}")
        h, w = im.shape[:2]
        c = int(w * 0.14)
        ax.imshow(im[:, c:w - c])
        ax.axis("off")
        sh.bg.text(12 + i * 92 + 44, 68, lab, ha="center", fontsize=8, weight="bold", va="top")
    y = sh.note(200, 180, [
        "1  Kapak",
        "2  Genel ölçüler (B düzeni)",
        "3  İki düzen, dönüş alanı ve yerleşim",
        "4  Alt plaka",
        "5  Üst plaka",
        "6  Motor braketi",
        "7  JGB37-520 motor",
        "8  Diğer basılan parçalar",
        "9  Alınacak malzemeler",
    ], fs=7.2, lh=4.4, title="İçindekiler")
    sh.note(200, y - 4, [
        f"Teker Ø{num(rc.WHEEL_D)} mm · Toplam genişlik {num(WIDTH)} mm · Boy 210 mm",
        f"Teker merkezleri arası (L) {num(rc.TRACK)} mm · Yerden yükseklik {num(rc.PLATE_BOT)} mm",
        f"Kat arası 55 mm · Kamera merkezi yerden ~{num(CAM_Z, 0)} mm",
        "Sarhoş: Pololu #953 (1/2\" metal bilya), 1 mm pul ile.",
        "Her basılan parça 220 × 220 mm tablaya sığar.",
        "Koordinat başlangıcı: plakanın merkezi; +x sağ, +y ileri.",
        "Motor ve elektronik modelleri yaklaşıktır;",
        "gerçek parçalar gelince ölçüp kontrol edin.",
    ], fs=6.8, lh=3.8, title="Özet")
    sh.save()


def page_general(pdf):
    sh = Sheet(pdf, "Genel ölçüler", "Montaj · B düzeni (tekerler ortada)", "1:3", 2)
    ax = sh.axes(3.0)
    S = 3.0
    shp = compound(asm_shapes("B"))
    front = project(shp, *VIEWS["on"])
    side = project(shp, *VIEWS["sag"])
    top = project(shp, *VIEWS["ust"])
    # yerleşim (model mm)
    gx = 30 * S   # zemin hattı y
    fo = (55 * S, gx)            # ön görünüş: x merkez, zemin
    so = (150 * S, gx)           # yan görünüş: merkez
    to = (236 * S, gx + 38 * S + 105)   # üst görünüş merkez
    draw(ax, front, *fo, hidden=False)
    draw(ax, side, *so, hidden=False)
    draw(ax, top, *to, hidden=False)
    for ox in (fo[0], so[0]):
        ax.plot([ox - 125, ox + 125], [gx, gx], lw=0.5, c=INK)
    view_label(ax, fo[0], gx - 14 * S, "ÖNDEN")
    view_label(ax, so[0], gx - 14 * S, "SAĞDAN")
    view_label(ax, to[0], to[1] - 105 - 14 * S, "ÜSTTEN")
    R, X, W2 = rc.R, rc.WHEEL_X, rc.WHEEL_W / 2
    # önden
    fx, fy = fo
    dim(ax, (fx - (X + W2), fy), (fx + (X + W2), fy), -7 * S, num(WIDTH))
    sh_ = rc.PLATE_W / 2
    dim(ax, (fx - X, fy), (fx + X, fy), -3.6 * S, "L = 184")
    dim(ax, (fx - sh_, fy + rc.TOP_DECK_Z + rc.PLATE_T), (fx + sh_, fy + rc.TOP_DECK_Z + rc.PLATE_T), 4 * S, "136")
    dim(ax, (fx + X + W2, fy), (fx + X + W2, fy + 2 * R), 4 * S, "Ø" + num(rc.WHEEL_D), orient="v")
    dim(ax, (fx - sh_, fy), (fx - sh_, fy + rc.PLATE_BOT), -16 * S, num(rc.PLATE_BOT), orient="v")
    dim(ax, (fx - sh_, fy), (fx - sh_, fy + rc.TOP_DECK_Z), -22 * S, num(rc.TOP_DECK_Z), orient="v")
    top_z = TOP_Z
    dim(ax, (fx - 10, fy), (fx - 10, fy + top_z), -40 * S, num(top_z, 0), orient="v")
    leader(ax, (fx, fy + CAM_Z), (16, 2), f"kamera merkezi ~{num(CAM_Z, 0)}")
    # sağdan
    sx, sy = so
    L2 = rc.PLATE_L / 2
    dim(ax, (sx - L2, sy + rc.PLATE_BOT), (sx + L2, sy + rc.PLATE_BOT), -(rc.PLATE_BOT + 7 * S), "210")
    dim(ax, (sx - rc.CASTER_Y, sy), (sx + rc.CASTER_Y, sy), -3.6 * S, "2 × 88 (sarhoşlar)")
    dim(ax, (sx + L2, sy + rc.PLATE_TOP), (sx + L2, sy + rc.TOP_DECK_Z), 4 * S, "55", orient="v")
    dim(ax, (sx + L2, sy), (sx + L2, sy + rc.PLATE_TOP), 10 * S, num(rc.PLATE_TOP), orient="v")
    centerline(ax, (sx, sy - 2 * S), (sx, sy + 2 * R + 6 * S))
    ax.text(sx + 1.2 * S, sy + 2 * R + 4 * S, "aks", fontsize=6, color=ACC)
    ax.text(sx + L2 - 2 * S, sy + rc.TOP_DECK_Z + 10 * S, "ön →", fontsize=6.5, ha="right", color=INK)
    # üstten
    tx, ty = to
    dim(ax, (tx - (X + W2), ty + L2), (tx + (X + W2), ty + L2), 5 * S, num(WIDTH))
    dim(ax, (tx + X + W2, ty - L2), (tx + X + W2, ty + L2), 5 * S, "210", orient="v")
    ax.text(tx, ty + L2 + 12 * S, "↑ ön", fontsize=6.5, ha="center")
    sh.note(12, 30, [
        "Montaj görünüşlerinde elektronik gösterilmemiştir (sayfa 3).",
        f"Yükseklikler yerden ölçülmüştür. Aks yüksekliği = teker yarıçapı = {num(rc.R)}.",
    ], fs=6.3, lh=3.5)
    sh.save()


def page_layouts(pdf):
    sh = Sheet(pdf, "İki düzen, dönüş alanı ve elektronik yerleşimi", "Montaj · üstten (üst kat şeffaf)", "1:4", 3)
    ax = sh.axes(4.0)
    S = 4.0
    for i, lay in enumerate(("B", "A")):
        items = [it for it in asm_shapes(lay, with_elec=True) if not it[0].startswith(("ust_plaka", "kamera", "direk_ucu", "uwb", "raspberry", "esp32"))]
        pr = project(compound(items), *VIEWS["ust"])
        ox, oy = (300, 300) if lay == "B" else (790, 250)
        draw(ax, pr, ox, oy, hidden=False, lw=0.45)
        axle_y = 0.0 if lay == "B" else rc.AXLE_A
        r = sweep_radius(lay)
        ax.add_patch(Circle((ox, oy + axle_y), r, fill=False, ec=ACC, lw=0.6, ls=(0, (4, 2))))
        ax.plot([ox], [oy + axle_y], marker="+", c=ACC, ms=6, mew=0.8)
        centerline(ax, (ox - rc.WHEEL_X - 25, oy + axle_y), (ox + rc.WHEEL_X + 25, oy + axle_y))
        leader(ax, (ox + r * math.cos(math.radians(40)), oy + axle_y + r * math.sin(math.radians(40))), (8, 6),
               f"dönüş alanı R{num(r, 0)}", color=ACC)
        # elektronik etiketleri
        if lay == "B":
            lbl = [((-32, 65), "BTS7960"), ((32, 65), "BTS7960"), ((0, -65), "3S batarya")]
        else:
            lbl = [((-32, -7), "BTS7960"), ((32, -7), "BTS7960"), ((0, -65), "3S batarya")]
        for (x, y), t in lbl:
            ax.text(ox + x, oy + y, t, fontsize=5.8, ha="center", va="center", color="#2a5d8a",
                    bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
        if lay == "A":
            dim(ax, (ox + rc.WHEEL_X + rc.WHEEL_W / 2, oy), (ox + rc.WHEEL_X + rc.WHEEL_W / 2, oy + rc.AXLE_A), 6 * S, "62", orient="v")
            centerline(ax, (ox - 70, oy), (ox + 70, oy))
            ax.text(ox - 72, oy, "plaka merkezi", fontsize=5.5, ha="right", va="center", color=ACC)
        view_label(ax, ox, oy - r - 6 * S, "B · Tekerler ortada (aks y = 0)" if lay == "B" else "A · Tekerler önde (aks y = 62)")
        ax.text(ox, oy + 105 + 6 * S, "↑ ön", fontsize=6.5, ha="center")
    sh.note(12, 30, [
        "Aynı plakalar iki düzeni de taşır: braketler B için y = 0'daki, A için y = 62'deki deliklere takılır.",
        "Dönüş alanı: araç yerinde dönerken en dış noktasının çizdiği daire (kamera direği hariç).",
        "Üst katta: Raspberry Pi 4 (arka), ESP32 ve XL4015 (ön sağ), kamera direği B'de ortada / A'da aksın üstünde.",
    ], fs=6.3, lh=3.5)
    sh.save()


def hole_groups_bottom():
    g = []
    g.append(("B braket", "Ø3,4", [(sx * hx, sy * 24) for sx in (1, -1) for hx in rc.FOOT_HOLES_X for sy in (1, -1)], "#1f6fb2"))
    g.append(("A braket", "Ø3,4", [(sx * hx, rc.AXLE_A + sy * 24) for sx in (1, -1) for hx in rc.FOOT_HOLES_X for sy in (1, -1)], ACC))
    g.append(("Kat direği", "Ø3,4", rc.PILLARS, "#2f8a4f"))
    g.append(("Sarhoş Pololu 953", "Ø2,4", [(s * rc.POLOLU_HOLES / 2, cy) for _, cy in rc.CASTERS for s in (1, -1)], "#7a3fa0"))
    return g


def page_bottom(pdf):
    sh = Sheet(pdf, "Alt plaka", "alt_plaka · 1 adet · 5 mm", "1:2", 4)
    S = 2.0
    ax = sh.axes(S, rect=(12, 36, 150, 148))
    part = rc.bottom_plate()
    top = project(part, *VIEWS["ust"])
    ox, oy = 75 * S, 72 * S
    draw(ax, top, ox, oy, hidden=False, lw=0.5)
    for name, d, pts, col in hole_groups_bottom():
        r = {"Ø3,4": 3.6, "Ø2,4": 2.8, "Ø4,4": 4.4}[d]
        for x, y in pts:
            ring(ax, ox + x, oy + y, r, col, lw=0.8)
    centerline(ax, (ox - 75, oy), (ox + 75, oy))
    centerline(ax, (ox, oy - 112), (ox, oy + 112))
    W2, L2 = rc.PLATE_W / 2, rc.PLATE_L / 2
    dim(ax, (ox - W2, oy + L2), (ox + W2, oy + L2), 6 * S, "136")
    dim(ax, (ox + W2, oy - L2), (ox + W2, oy + L2), 6 * S, "210", orient="v")
    leader(ax, (ox - W2 + rc.PLATE_R * (1 - math.cos(math.radians(45))), oy + L2 - rc.PLATE_R * (1 - math.sin(math.radians(45)))), (-6, 6), "R18")
    dim(ax, (ox + 36, oy - L2), (ox + 54, oy - L2), -5 * S, "18")
    dim(ax, (ox, oy - L2), (ox + 36, oy - L2), -5 * S, "36")
    dim(ax, (ox - W2, oy + 24), (ox - W2, oy - 24), -6 * S, "48", orient="v")
    dim(ax, (ox - W2, oy), (ox - W2, oy + rc.AXLE_A), -12 * S, "62", orient="v")
    ax.text(ox, oy + L2 + 13 * S, "↑ ön", fontsize=6.5, ha="center")
    # tablo
    rows = []
    for name, d, pts, col in hole_groups_bottom():
        xs = sorted({abs(round(p[0], 2)) for p in pts})
        ys = sorted({round(p[1], 2) for p in pts})
        rows.append((name, d, len(pts), "±" + " / ±".join(num(v, 2) for v in xs if v) + (" ve 0" if 0 in xs else "") if any(xs) else "0",
                     " / ".join(num(v, 2) for v in ys)))
    gpts = rc.grid_points([(x, y, 9) for x, y in rc.PILLARS] + [(x, y, 8) for x, y in (rc.foot_holes(0) + rc.foot_holes(rc.AXLE_A))],
                          rc.foot_zones(0.0) + rc.foot_zones(rc.AXLE_A) + [(-30, 30, cy - 9, cy + 9) for _, cy in rc.CASTERS])
    rows.append(("Bağlantı ızgarası", "Ø3,4", len(gpts), "15 aralık, x = 0, ±15…", "15 aralık, y = ±7,5…"))
    y = table(sh, 168, 180, ["Delik", "Çap", "Adet", "x", "y"], [27, 11, 9, 32, 38], rows)
    # renk açıklaması
    yy = y - 3
    for name, d, pts, col in hole_groups_bottom():
        sh.bg.add_patch(Circle((171, yy - 1.2), 1.4, fill=False, ec=col, lw=0.9))
        sh.bg.text(175, yy - 1.2, name, fontsize=6.3, va="center")
        yy -= 4.2
    sh.note(168, yy - 2, [
        "Kalınlık 5 mm, düz basılır. 4 duvar, %30 dolgu.",
        "Koordinatlar plakanın merkezinden; +y ön.",
        "Braket delikleri: M3×16 vida + somun.",
        "Sarhoş: Pololu #953 (1/2\"), 2 × M2, 14,7 aralık.",
        "Izgara: modüller için M3 aralayıcı veya kablo bağı.",
        f"Plakanın altı yerden {num(rc.PLATE_BOT)} mm (Ø{num(rc.WHEEL_D)} teker).",
    ], fs=6.3, lh=3.5, title="Notlar")
    sh.save()


def page_top(pdf):
    sh = Sheet(pdf, "Üst plaka", "ust_plaka · 1 adet · 5 mm + çıkıntılar", "1:2", 5)
    S = 2.0
    ax = sh.axes(S, rect=(12, 36, 150, 148))
    part = rc.top_plate()
    top = project(part, *VIEWS["ust"])
    ox, oy = 75 * S, 72 * S
    draw(ax, top, ox, oy, hidden=False, lw=0.5)
    W2, L2 = rc.PLATE_W / 2, rc.PLATE_L / 2
    centerline(ax, (ox - 75, oy), (ox + 75, oy))
    centerline(ax, (ox, oy - 112), (ox, oy + 112))
    for x, y in rc.PILLARS:
        ring(ax, ox + x, oy + y, 3.6, "#2f8a4f")
    pis = [(rc.PI_CENTER[0] + sx * 29, rc.PI_CENTER[1] + sy * 24.5) for sx in (1, -1) for sy in (1, -1)]
    for x, y in pis:
        ring(ax, ox + x, oy + y, 4.2, "#1f6fb2")
    for x, y in rc.MAST_SOCKETS:
        ax.add_patch(Rectangle((ox + x - 16, oy + y - 16), 32, 32, fill=False, ec=ACC, lw=0.8))
    dim(ax, (ox - W2, oy + L2), (ox + W2, oy + L2), 6 * S, "136")
    dim(ax, (ox + W2, oy - L2), (ox + W2, oy + L2), 6 * S, "210", orient="v")
    dim(ax, (ox - 29, oy - 89.5), (ox + 29, oy - 89.5), -14 * S, "58")
    dim(ax, (ox - W2, oy - 40.5), (ox - W2, oy - 89.5), -6 * S, "49", orient="v")
    leader(ax, (ox + 15, oy + rc.AXLE_A), (14, 4), "A yuvası (y = 62)")
    leader(ax, (ox + 15, oy), (14, 2), "B yuvası (merkez)")
    leader(ax, (ox - 45, oy + 18 + 14), (-10, 6), "kablo yarığı 28×10 (4×)")
    ax.text(ox, oy + L2 + 13 * S, "↑ ön", fontsize=6.5, ha="center")
    # yan kesit görünüşü (sağdan)
    ax2 = sh.axes(S, rect=(168, 120, 117, 60))
    side = project(part, *VIEWS["arka"])
    draw(ax2, side, 58 * S, 14 * S, hidden=True, lw=0.5)
    view_label(ax2, 58 * S, 11 * S, "ARKADAN")
    dim(ax2, (58 * S + 25, 14 * S), (58 * S + 25, 14 * S + 19), 30, "19", orient="v")
    dim(ax2, (58 * S - 68, 14 * S), (58 * S - 68, 14 * S + 5), -8, "5", orient="v")
    rows = [
        ("Kat direği", "Ø3,4", 6, "±53 ve 0", "±100 / ±100,5"),
        ("Pi 4 ayağı", "Ø6,4×5, delik Ø2,2", 4, "±29", "−40,5 / −89,5"),
        ("Direk yuvası", "30×30×14, cep 20,6×20,6×12", 2, "0", "0 / 62"),
        ("Kablo yarığı", "28×10", 4, "±45", "±18"),
        ("Izgara", "Ø3,4", "—", "15 aralık", "15 aralık"),
    ]
    y = table(sh, 168, 112, ["Özellik", "Ölçü", "Adet", "x", "y"], [20, 38, 8, 17, 25], rows, fs=5.9)
    sh.note(168, y - 3, [
        "Ayaklar ve yuvalar yukarı bakacak şekilde basılır.",
        "Direk yuvasında yan sıkıştırma deliği Ø2,8 (M3×8).",
        "Pi 4: M2.5×6 vida ayaklara doğrudan diş açar.",
        "Direkler: M3×10, plakadan direğe diş açar.",
    ], fs=6.3, lh=3.5, title="Notlar")
    sh.save()


def page_bracket(pdf):
    sh = Sheet(pdf, "Motor braketi", "motor_braketi · 2 adet (iki taraf aynı parça)", "1:1", 6)
    S = 1.0
    ax = sh.axes(S, rect=(12, 36, 273, 148))
    part = rc.motor_bracket()
    # yerel: x 26..67, y -32..32, z 0..43
    front = project(part, (1, 0, 0), (0, 1, 0))       # dış yüzden: resim x = y, resim y = z
    side = project(part, (0, 1, 0), (-1, 0, 0))       # yandan: resim x = -x
    top = project(part, *VIEWS["ust"])
    fo = (60, 40)
    so = (190, 34)
    to = (190, 114)
    draw(ax, front, *fo)
    draw(ax, side, so[0] + 46, so[1])   # -x: 26..67 -> -67..-26, kaydır
    draw(ax, top, to[0] - 46, to[1], hidden=False)
    view_label(ax, fo[0], fo[1] - 12, "DIŞ YÜZDEN (teker tarafı)")
    view_label(ax, so[0], so[1] - 22, "YANDAN")
    view_label(ax, to[0] + 40, to[1] + 4, "ÜSTTEN")
    fx, fy = fo
    dim(ax, (fx - 32, fy), (fx + 32, fy), -6, "64")
    dim(ax, (fx + 32, fy), (fx + 32, fy + 43), 6, "43", orient="v")
    dim(ax, (fx - 32, fy), (fx - 32, fy + 13), -6, "13", orient="v")
    dim(ax, (fx - 32, fy), (fx - 32, fy + 20), -12, "20", orient="v")
    leader(ax, (fx + 6.3 * math.cos(math.radians(-40)), fy + 13 + 6.3 * math.sin(math.radians(-40))), (24, -8), "Ø12,6 mil çıkıntısı deliği")
    ax.add_patch(Circle((fx, fy + 20), 15.5, fill=False, ec=ACC, lw=0.4, ls=(0, (6, 2, 1, 2))))
    leader(ax, (fx - 15.5 * math.cos(math.radians(30)), fy + 20 + 15.5 * math.sin(math.radians(30))), (-10, 26),
           "6 × M3 yay yarığı, genişlik 3,3\nØ31 üzerinde, her biri 30°")
    ax.plot([fx], [fy + 20], marker="+", c=ACC, ms=5, mew=0.6)
    leader(ax, (fx, fy + 20), (34, 30), "redüktör merkezi")
    # yandan
    sx, sy = so
    x_in = sx + 46 - rc.X_BR      # iç yüz resim x (−X_BR + kaydırma)
    dim(ax, (x_in - rc.BR_T, sy), (x_in + rc.FOOT_LEN, sy), -6, "41")
    dim(ax, (x_in - rc.BR_T, sy + 43), (x_in, sy + 43), 4, "5")
    dim(ax, (x_in, sy), (x_in + 8, sy), -12, "8")
    dim(ax, (x_in, sy), (x_in + 26, sy), -18, "26")
    dim(ax, (x_in + rc.FOOT_LEN, sy), (x_in + rc.FOOT_LEN, sy + 5), 5, "5", orient="v")
    dim(ax, (x_in + 20, sy + 5), (x_in + 20, sy + 30), 12, "kaburga 25", orient="v")
    # üstten
    tx = to[0] - 46
    ty = to[1]
    dim(ax, (tx + 26, ty - 32), (tx + 26, ty + 32), -6, "64", orient="v")
    dim(ax, (tx + 54, ty + 20), (tx + 54, ty + 32), 14, "12", orient="v")
    dim(ax, (tx + 54, ty - 24), (tx + 54, ty + 24), 22, "48", orient="v")
    leader(ax, (tx + 36, ty + 24), (-16, 9), "4 × Ø3,4 (plakaya M3×16)")
    sh.note(12, 30, [
        "Baskı: DIŞ YÜZÜ tablaya gelecek şekilde, 5 duvar, %50 dolgu, destek yok.",
        "Motor mili, redüktör merkezinin 7 mm ALTINDA kalır (büyük delik altta). Motor vidaları M3×8, daha uzun olmamalı.",
    ], fs=6.3, lh=3.5)
    sh.save()


def page_motor(pdf):
    sh = Sheet(pdf, "JGB37-520 12V 530 rpm enkoderli motor", "JGB37-520 · satın alınan · 3 adet (1 yedek)", "1:1", 7)
    S = 1.0
    ax = sh.axes(S, rect=(12, 36, 190, 148))
    m = rc.motor_model()
    side = project(m, (1, 0, 0), (0, 0, 1))     # resim x = z (mil sağda), resim y = -y (mil altta)
    face = project(m, (0, 0, 1), (-1, 0, 0))    # montaj yüzünden, mil altta
    so = (135, 80)
    fo = (35, 80)
    draw(ax, side, *so)
    draw(ax, face, *fo)
    view_label(ax, so[0] - 10, so[1] - 40, "YANDAN")
    view_label(ax, fo[0], fo[1] - 40, "MONTAJ YÜZÜNDEN")
    sx, sy = so
    zf = sx                    # montaj yüzü
    z_end = sx - rc.MOTOR_LEN
    shaft_y = sy - rc.SHAFT_OFF
    dim(ax, (z_end, sy + 18.5), (zf + 21, sy + 18.5), 12, "78,5")
    dim(ax, (zf - 22, sy + 18.5), (zf, sy + 18.5), 5, "22")
    dim(ax, (zf - 44.7, sy + 18.5), (zf - 22, sy + 18.5), 5, "22,7")
    dim(ax, (z_end, sy - 18.5), (zf - 44.7, sy - 18.5), -6, "~12,8 (kapak + enkoder)")
    dim(ax, (zf, shaft_y - 6), (zf + 6, shaft_y - 6), -10, "6")
    dim(ax, (zf + 6, shaft_y - 6), (zf + 21, shaft_y - 6), -10, "15")
    dim(ax, (zf + 9, sy + 18.5), (zf + 21, sy + 18.5), 5, "D 12")
    dim(ax, (zf - 11, sy - 18.5), (zf - 11, sy + 18.5), -0.1, "Ø37", orient="v")
    leader(ax, (zf - 33, sy - 16.5), (6, -16), "Ø33 motor gövdesi")
    leader(ax, (zf + 21, shaft_y + 3), (6, 8), "Ø6 mil (D 5,5)")
    leader(ax, (zf + 3, shaft_y - 6), (22, -20), "Ø12 çıkıntı")
    dim(ax, (zf + 30, sy), (zf + 30, shaft_y), 0.1, "7", orient="v")
    centerline(ax, (z_end - 4, sy), (zf + 26, sy))
    centerline(ax, (zf - 4, shaft_y), (zf + 26, shaft_y))
    fx, fy = fo
    ax.add_patch(Circle((fx, fy), 15.5, fill=False, ec=ACC, lw=0.4, ls=(0, (6, 2, 1, 2))))
    leader(ax, (fx + 15.5 * math.cos(math.radians(60)), fy + 15.5 * math.sin(math.radians(60))), (-4, 24), "6 × M3, 3,5 derin\nØ31 çember (açı yaklaşık)")
    leader(ax, (fx, fy - 7), (-8, 30), "mil: merkezden 7 aşağıda")
    rows = [
        ("Voltaj", "12 V (3S batarya: 10–12,6 V)"),
        ("Dişli oranı", "1:19"),
        ("Yüksüz", "530 rpm, 0,12 A"),
        ("Nominal", "2,2 kg·cm, 407 rpm, 1 A"),
        ("Kilitlenme", "3,1 kg·cm, 2,3 A"),
        ("Enkoder", "Hall, A/B, 11 darbe/motor turu"),
        ("Teker turu", "~836 sayım (11×4×19)"),
        (f"Ø{num(rc.WHEEL_D)} teker", f"sayım başına ~{num(math.pi * rc.WHEEL_D / 836, 2)} mm"),
        ("Kırmızı / Beyaz", "Motor + / −  (BTS7960)"),
        ("Mavi / Siyah", "Enkoder + / −  (3,3–5 V)"),
        ("Sarı / Yeşil", "Enkoder A / B  (ESP32)"),
        ("Fiyat", "665,41 TL (Direnc.net, DSTK22441)"),
    ]
    y = table(sh, 205, 180, ["Özellik", "Değer"], [24, 56], rows, fs=6.2, rh=4.3)
    sh.note(205, y - 3, [
        "Ölçüler datasheet'ten; 3D model yaklaşıktır.",
        "Montaj delik açılarını gerçek motordan ölçün.",
        "Datasheet değerleri tutarsız olabilir;",
        "hız ve sayımı motor gelince ölçün.",
    ], fs=6.3, lh=3.5, title="Not")
    sh.save()


def page_misc(pdf):
    sh = Sheet(pdf, "Diğer basılan parçalar", "Direkler, direk ucu, pullar", "1:1,5", 8)
    S = 1.5
    ax = sh.axes(S)
    # direk
    p = project(rc.pillar(), (0, -1, 0), (1, 0, 0))
    ox, oy = 25 * S, 40 * S
    draw(ax, p, ox, oy)
    dim(ax, (ox - 4.5, oy), (ox + 4.5, oy), -5 * S, "Ø9")
    dim(ax, (ox + 4.5, oy), (ox + 4.5, oy + 55), 5 * S, "55", orient="v")
    dim(ax, (ox - 4.5, oy + 55 - 12), (ox - 4.5, oy + 55), -5 * S, "12", orient="v")
    leader(ax, (ox, oy + 6), (-10, -12), "Ø2,8 her iki uçta")
    view_label(ax, ox, oy - 12 * S, "Kat direği · 6 adet")
    # kamera direği
    m = project(rc.mast(), (0, -1, 0), (1, 0, 0))
    ox, oy = 70 * S, 40 * S
    draw(ax, m, ox, oy)
    dim(ax, (ox - 10, oy), (ox + 10, oy), -5 * S, "20")
    dim(ax, (ox + 10, oy), (ox + 10, oy + 150), 5 * S, "150", orient="v")
    leader(ax, (ox + 7.6, oy + 120), (10, 4), "et 2,4\n(iç 15,2 × 15,2)")
    view_label(ax, ox, oy - 12 * S, "Kamera direği · 1 adet")
    # direk ucu
    t = rc.mast_top()
    f = project(t, (0, 1, 0), (-1, 0, 0))
    s = project(t, (1, 0, 0), (0, 1, 0))
    ox, oy = 125 * S, 70 * S
    draw(ax, f, ox, oy)
    draw(ax, s, ox + 70 * S / 1.0 * 0 + 60 * S, oy)
    dim(ax, (ox - 24, oy + 22), (ox + 24, oy + 22), 32 * S, "48")
    dim(ax, (ox - 24, oy), (ox - 24, oy + 62), -6 * S, "62", orient="v")
    dim(ax, (ox - 13, oy), (ox + 13, oy), -5 * S, "26 (iç 20,6)")
    leader(ax, (ox + 10.5, oy + 46 + 6.25), (14, 10), "Pi Camera V2: 4 × Ø2,2\n21 × 12,5 aralık")
    view_label(ax, ox, oy - 12 * S, "Direk ucu · önden")
    view_label(ax, ox + 60 * S, oy - 12 * S, "Direk ucu · sağdan")
    leader(ax, (ox + 60 * S + 15, oy + 22), (10, 8), "UWB tablası 48×48,\n16 × Ø3,4 (10 aralık)")
    # pul
    sp = project(rc.caster_shim(2.0), *VIEWS["ust"])
    ox, oy = 125 * S, 22 * S
    draw(ax, sp, ox, oy)
    dim(ax, (ox - 12, oy + 6), (ox + 12, oy + 6), 4 * S, "24")
    dim(ax, (ox + 12, oy - 6), (ox + 12, oy + 6), 4 * S, "12", orient="v")
    leader(ax, (ox + 7.35, oy), (16, -8), "2 × Ø2,4 (Pololu 953, 14,7 aralık)")
    view_label(ax, ox, oy - 14, "Sarhoş pulu · 0,5 mm ve 1 mm, 2'şer adet")
    sh.note(12, 30, [
        "Direkler ve kamera direği dik basılır. Direk ucu, kamera plakasının ön yüzü tablaya gelecek şekilde basılır.",
        "Direk ucu, kamera direğinin üstüne 16 mm geçer; direk alt ucu üst plakadaki 12 mm'lik cebe oturur ve yandan M3×8 ile sıkılır.",
    ], fs=6.3, lh=3.5)
    sh.save()


def page_bom(pdf):
    groups = []
    for row in BOM:
        groups.append(row)
    import textwrap
    widths = [18, 62, 78, 11, 46, 22, 36]
    per_page = 40
    pages = [groups[i:i + per_page] for i in range(0, len(groups), per_page)]
    for pi, rows in enumerate(pages):
        sh = Sheet(pdf, "Alınacak malzemeler" + (" (devam)" if pi else ""),
                   "Malzeme listesi (link/fiyat: Excel)", "—", 9 + pi, sub=False)
        body = []
        for r in rows:
            cells = []
            for v, w in zip(r[:7], widths):
                cells.append("\n".join(textwrap.wrap(str(v), max(4, int(w / 1.25)))) if v != "" else "")
            body.append(cells)
        table(sh, 12, 182, BOM_COLUMNS[:7], widths, body, fs=6.2, rh=4.0, head_fs=6.6)
        sh.bg.text(12, 40, "Motor: " + DIRENC_MOTOR + "     Sürücü: " + ROBOTISTAN_BTS, fontsize=6, color=DIM)
        sh.save()
    return len(pages)


if __name__ == "__main__":
    out = f"{HERE}/doc/01_Olcu_Belgesi.pdf"
    with PdfPages(out) as pdf:
        page_cover(pdf)
        page_general(pdf)
        page_layouts(pdf)
        page_bottom(pdf)
        page_top(pdf)
        page_bracket(pdf)
        page_motor(pdf)
        page_misc(pdf)
        n = page_bom(pdf)
        d = pdf.infodict()
        d["Title"] = "RAPTOR araç şasesi · Ölçü belgesi"
        d["Author"] = "Şevval Nida Sağır"
    print("ok", out, "bom sayfa", n)
