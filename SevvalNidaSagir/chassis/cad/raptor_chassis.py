"""
RAPTOR - 3D baskı şase (parametrik, CadQuery)

Eksenler: x = sağ, y = ileri, z = yukarı. Ölçüler mm.
Her parça 220x220 mm tablaya sığar. İki teker düzeni desteklenir:
  B: tekerler ortada (aks y=0), önde ve arkada birer sarhoş
  A: tekerler önde (aks y=AXLE_A), arkada bir sarhoş
Çalıştırma: python3 raptor_chassis.py  -> out/ klasörüne STL, STEP ve GLB yazar.
"""
import math
import os
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# ---------------- ANA PARAMETRELER ----------------
WHEEL_D = 65.0          # teker çapı (Motorobit 65x27 + 6 mm hex kaplin); plaka altı = R - 18
WHEEL_W = 27.0          # teker genişliği (sadece önizleme için)
PLATE_W = 136.0         # plaka genişliği (x)
PLATE_L = 210.0         # plaka boyu (y)
PLATE_T = 5.0           # plaka kalınlığı
PLATE_R = 18.0          # köşe yuvarlatma
DECK_GAP = 55.0         # iki kat arası (direk boyu)
AXLE_A = 62.0           # A düzeninde aks konumu (y)
CASTER_Y = 88.0         # sarhoş konumları (y = +/-)
GRID = 15.0             # bağlantı ızgarası aralığı
M3 = 3.4                # M3 geçme deliği
M3_TAP = 2.8            # M3 vidanın doğrudan diş açacağı delik (PETG)

# Motor: JGB37-520, mil redüktör merkezinden 7 mm kaçık
GB_R = 18.5             # redüktör yarıçapı (Ø37)
GB_LEN = 22.0           # redüktör boyu
BODY_R = 16.5           # motor gövdesi yarıçapı (Ø33)
BODY_LEN = 35.0         # motor + enkoder kartı boyu
SHAFT_OFF = 7.0         # mil kaçıklığı (mil, redüktör merkezinin ALTINDA kalacak)
BOSS_D = 12.0           # mil çevresindeki çıkıntı Ø12, boy 6
BOSS_L = 6.0
HOLE_PCD = 31.0         # 6xM3 montaj delikleri Ø31 çember üzerinde

# Braket (motoru plakaya bağlar). Değerler plaka üst yüzeyine göre.
X_BR = 62.0             # braket iç yüzü (motorun yaslandığı yüz) x konumu
BR_T = 5.0              # braket dikey plaka kalınlığı
GC_H = 20.0             # redüktör merkezinin plaka üstünden yüksekliği (alt boşluk 1.5 mm)
BR_H = 43.0             # braket yüksekliği
FOOT_Y0, FOOT_Y1 = 20.0, 32.0   # ayakların y aralığı (motordan uzak)
FOOT_LEN = 36.0
FOOT_T = 5.0
FOOT_HOLES_X = (X_BR - 26.0, X_BR - 8.0)   # 36 ve 54
FOOT_HOLE_Y = 24.0

# Türetilenler
R = WHEEL_D / 2
AXLE_Z = R
PLATE_TOP = AXLE_Z + SHAFT_OFF - GC_H                 # plaka üst yüzü (yerden)
PLATE_BOT = PLATE_TOP - PLATE_T                        # plaka alt yüzü = sarhoşun sığacağı yükseklik
TOP_DECK_Z = PLATE_TOP + DECK_GAP                      # üst plaka alt yüzü
WHEEL_X = X_BR + 30.0                                  # teker merkezi (hex kaplin ile yaklaşık)
TRACK = 2 * WHEEL_X

PILLARS = [(-53, 100), (0, 100.5), (53, 100), (-53, -100), (0, -100.5), (53, -100)]
CASTERS = [(0, CASTER_Y), (0, -CASTER_Y)]
POLOLU_HOLES = 14.7      # Pololu #953 1/2" metal bilyalı sarhoş, M2 (0,58")
CASTER_H = 13.5          # Pololu #953 pulsuz yüksekliği (0,53")
PI_HOLES = (58.0, 49.0)  # Raspberry Pi 5 (M2.5)
PI_CENTER = (0.0, -65.0)
MAST_SOCKETS = [(0.0, 0.0), (0.0, AXLE_A)]
CABLE_SLOTS = [(-45, 18), (45, 18), (-45, -18), (45, -18)]


def rounded_plate(w, l, t, r):
    return cq.Workplane("XY").box(w, l, t, centered=(True, True, False)).edges("|Z").fillet(r)


def cyl(r, h, pnt, axis):
    """Silindir: pnt taban merkezi, axis yön vektörü."""
    return cq.Workplane(cq.Plane(origin=pnt, xDir=_perp(axis), normal=axis)).circle(r).extrude(h)


def _perp(a):
    a = cq.Vector(*a)
    return (cq.Vector(0, 0, 1).cross(a) if abs(a.z) < 0.9 else cq.Vector(1, 0, 0).cross(a)).normalized()


def foot_holes(axle_y):
    pts = []
    for sx in (1, -1):
        for hx in FOOT_HOLES_X:
            for sy in (1, -1):
                pts.append((sx * hx, axle_y + sy * FOOT_HOLE_Y))
    return pts


def foot_zones(axle_y):
    """Braket ayaklarının plakaya oturduğu dikdörtgenler (ızgara deliği açılmaz)."""
    z = []
    for sx in (1, -1):
        x0, x1 = sorted((sx * (X_BR - FOOT_LEN), sx * (X_BR + BR_T)))
        for sy in (1, -1):
            y0, y1 = sorted((axle_y + sy * FOOT_Y0, axle_y + sy * FOOT_Y1))
            z.append((x0 - 3, x1 + 3, y0 - 3, y1 + 3))
    return z


def grid_points(keep_out_circles, keep_out_rects, margin=9.0):
    pts = []
    nx = int((PLATE_W / 2 - margin) // GRID)
    ny = int((PLATE_L / 2 - margin) // GRID)
    for i in range(-nx, nx + 1):
        for j in range(-ny, ny + 1):
            x, y = i * GRID, j * GRID + GRID / 2
            if abs(y) > PLATE_L / 2 - margin:
                continue
            # köşe yuvarlatması
            cx, cy = PLATE_W / 2 - PLATE_R, PLATE_L / 2 - PLATE_R
            if abs(x) > cx and abs(y) > cy and math.hypot(abs(x) - cx, abs(y) - cy) > PLATE_R - margin:
                continue
            if any(math.hypot(x - a, y - b) < r for a, b, r in keep_out_circles):
                continue
            if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, x1, y0, y1 in keep_out_rects):
                continue
            pts.append((x, y))
    return pts


# ---------------- PARÇALAR ----------------
def bottom_plate():
    p = rounded_plate(PLATE_W, PLATE_L, PLATE_T, PLATE_R)
    # braket delikleri: B (aks 0) ve A (aks AXLE_A)
    holes = foot_holes(0.0) + foot_holes(AXLE_A)
    p = p.faces(">Z").workplane().pushPoints(holes).hole(M3)
    # direk delikleri
    p = p.faces(">Z").workplane().pushPoints(PILLARS).hole(M3)
    # sarhoş delikleri: Pololu #953 (M2)
    pol = [(cx + s * POLOLU_HOLES / 2, cy) for cx, cy in CASTERS for s in (1, -1)]
    p = p.faces(">Z").workplane().pushPoints(pol).hole(2.4)
    # bağlantı ızgarası
    circles = [(x, y, 9) for x, y in PILLARS] + [(x, y, 8) for x, y in holes]
    rects = foot_zones(0.0) + foot_zones(AXLE_A) + [(-18, 18, cy - 9, cy + 9) for _, cy in CASTERS]
    g = grid_points(circles, rects)
    p = p.faces(">Z").workplane().pushPoints(g).hole(M3)
    return p


def top_plate():
    p = rounded_plate(PLATE_W, PLATE_L, PLATE_T, PLATE_R)
    p = p.faces(">Z").workplane().pushPoints(PILLARS).hole(M3)
    # kablo geçiş yarıkları
    for x, y in CABLE_SLOTS:
        p = p.cut(cq.Workplane("XY").center(x, y).slot2D(28, 10, 90).extrude(PLATE_T + 1).translate((0, 0, -0.5)))
    # Raspberry Pi 5 ayakları
    pis = [(PI_CENTER[0] + sx * PI_HOLES[0] / 2, PI_CENTER[1] + sy * PI_HOLES[1] / 2) for sx in (1, -1) for sy in (1, -1)]
    bosses = cq.Workplane("XY").pushPoints(pis).circle(3.2).extrude(5).translate((0, 0, PLATE_T))
    p = p.union(bosses)
    p = p.cut(cq.Workplane("XY").pushPoints(pis).circle(1.1).extrude(PLATE_T + 6))
    # direk (kamera/UWB) yuvaları: B için merkezde, A için aks üstünde
    for x, y in MAST_SOCKETS:
        boss = cq.Workplane("XY").center(x, y).rect(30, 30).extrude(14).edges("|Z").fillet(3).translate((0, 0, PLATE_T))
        p = p.union(boss)
        p = p.cut(cq.Workplane("XY").center(x, y).rect(20.6, 20.6).extrude(12).translate((0, 0, PLATE_T + 2.0001)))
        # yan sıkıştırma vidası
        p = p.cut(cyl(M3_TAP / 2, 20, (x, y, PLATE_T + 9), (1, 0, 0)))
    # ızgara
    circles = ([(x, y, 9) for x, y in PILLARS] + [(x, y, 21) for x, y in MAST_SOCKETS] +
               [(x, y, 8) for x, y in pis] + [(x, y, 19) for x, y in CABLE_SLOTS])
    g = grid_points(circles, [])
    p = p.faces("<Z").workplane().pushPoints(g).hole(M3)
    return p


def motor_bracket():
    """Sağ taraf braketi; sol taraf için aynı parça z ekseninde 180° döndürülür."""
    gc = (0.0, GC_H)                    # (y, z) redüktör merkezi
    shaft = (0.0, GC_H - SHAFT_OFF)     # mil, merkezin altında
    plate = cq.Workplane("XY").box(BR_T, 2 * FOOT_Y1, BR_H, centered=False).translate((X_BR, -FOOT_Y1, 0))
    br = plate
    for s in (1, -1):
        y0, y1 = sorted((s * FOOT_Y0, s * FOOT_Y1))
        foot = cq.Workplane("XY").box(FOOT_LEN, y1 - y0, FOOT_T, centered=False).translate((X_BR - FOOT_LEN, y0, 0))
        # takviye kaburgası (dış kenarda, vida başlarından uzak)
        ry0 = s * (FOOT_Y1 - 3.0)
        rib = (cq.Workplane("XZ", origin=(0, ry0 if s > 0 else ry0 + 3.0, 0))
               .polyline([(X_BR, FOOT_T), (X_BR, 30.0), (X_BR - 20.0, FOOT_T)]).close().extrude(3.0))
        br = br.union(foot).union(rib)
    # ayak delikleri
    pts = [(hx, s * FOOT_HOLE_Y) for hx in FOOT_HOLES_X for s in (1, -1)]
    br = br.cut(cq.Workplane("XY").pushPoints(pts).circle(M3 / 2).extrude(FOOT_T + 1).translate((0, 0, -0.5)))
    # mil çıkıntısı deliği
    br = br.cut(cyl(6.3, BR_T + 2, (X_BR - 1, shaft[0], shaft[1]), (1, 0, 0)))
    # 6 adet yay şeklinde M3 yarığı (delik açısı belirsiz: 0° ve 30° desenlerinin ikisine de uyar)
    for k in range(6):
        for a in [15 + 60 * k + d for d in range(-15, 16, 3)]:
            t = math.radians(a)
            y = gc[0] + HOLE_PCD / 2 * math.cos(t)
            z = gc[1] + HOLE_PCD / 2 * math.sin(t)
            br = br.cut(cyl(1.65, BR_T + 2, (X_BR - 1, y, z), (1, 0, 0)))
    return br


def pillar():
    p = cq.Workplane("XY").circle(4.5).extrude(DECK_GAP)
    p = p.cut(cq.Workplane("XY").circle(M3_TAP / 2).extrude(12).translate((0, 0, -0.01)))
    p = p.cut(cq.Workplane("XY").circle(M3_TAP / 2).extrude(12).translate((0, 0, DECK_GAP - 11.99)))
    return p


def caster_shim(t):
    """Pololu #953 için yükseklik pulu (14,7 mm aralıklı 2 x M2)."""
    s = cq.Workplane("XY").box(24, 12, t, centered=(True, True, False)).edges("|Z").fillet(4)
    s = s.cut(cq.Workplane("XY").pushPoints([(s_ * POLOLU_HOLES / 2, 0) for s_ in (1, -1)]).circle(1.2).extrude(t + 1).translate((0, 0, -0.5)))
    return s


MAST_LEN = 150.0


def mast():
    m = cq.Workplane("XY").rect(20, 20).extrude(MAST_LEN).edges("|Z").fillet(1.5)
    m = m.cut(cq.Workplane("XY").rect(15.2, 15.2).extrude(MAST_LEN + 2).translate((0, 0, -1)))
    return m


def mast_top():
    """Direğin ucuna geçer: üstte UWB tablası, önde kamera (Pi Camera Module 3) plakası."""
    sleeve = cq.Workplane("XY").rect(26, 26).extrude(18).edges("|Z").fillet(3)
    sleeve = sleeve.cut(cq.Workplane("XY").rect(20.6, 20.6).extrude(16.5).translate((0, 0, -0.01)))
    plat = cq.Workplane("XY").box(48, 48, 4, centered=(True, True, False)).edges("|Z").fillet(4).translate((0, 0, 18))
    pts = [(x, y) for x in (-15, -5, 5, 15) for y in (-15, -5, 5, 15)]
    plat = plat.cut(cq.Workplane("XY").pushPoints(pts).circle(1.7).extrude(10).translate((0, 0, 15)))
    cam = cq.Workplane("XY").box(36, 4, 40, centered=(True, False, False)).translate((0, 20, 22))
    cam = cam.edges("|Y").fillet(3)
    # Pi Camera Module 3: 21 x 12.5 mm, M2
    cz = 22 + 24
    for sx in (1, -1):
        for sz in (1, -1):
            cam = cam.cut(cyl(1.1, 6, (sx * 10.5, 19, cz + sz * 6.25), (0, 1, 0)))
    cam = cam.cut(cq.Workplane("XZ", origin=(0, 25, 0)).center(0, 28).slot2D(18, 3, 0).extrude(7))  # kamera kablosu
    gus = (cq.Workplane("YZ", origin=(-2, 0, 0)).polyline([(8, 22), (20, 22), (20, 34)]).close().extrude(4))
    return sleeve.union(plat).union(cam).union(gus)


# ---------------- ÖNİZLEME İÇİN BASİT MODELLER ----------------
def motor_dummy():
    gcz = PLATE_TOP + GC_H
    gb = cyl(GB_R, GB_LEN, (X_BR - GB_LEN, 0, gcz), (1, 0, 0))
    body = cyl(BODY_R, BODY_LEN, (X_BR - GB_LEN - BODY_LEN, 0, gcz), (1, 0, 0))
    boss = cyl(BOSS_D / 2, BOSS_L, (X_BR, 0, AXLE_Z), (1, 0, 0))
    shaft = cyl(3.0, BOSS_L + 15.5, (X_BR, 0, AXLE_Z), (1, 0, 0))
    return gb.union(body).union(boss).union(shaft)


def wheel_dummy():
    w = cyl(R, WHEEL_W, (WHEEL_X - WHEEL_W / 2, 0, AXLE_Z), (1, 0, 0))
    hub = cyl(7, WHEEL_X - WHEEL_W / 2 - (X_BR + BR_T + 2), (X_BR + BR_T + 2, 0, AXLE_Z), (1, 0, 0))
    return w.union(hub)


MOTOR_LEN = 22.0 + 22.7 + 3.5 + 9.3     # montaj yüzünden enkoder konnektörüne ~57.5 mm


def motor_model():
    """JGB37-520 12V 530 rpm (19:1) enkoderli motor, datasheet ölçülerinden yaklaşık model.
    Yerel eksen: mil +Z yönünde, montaj yüzü z=0, redüktör merkezi orijin, mil +Y yönünde 7 mm kaçık."""
    gb = cq.Workplane("XY").circle(GB_R).extrude(-GB_LEN)
    # 6 x M3, 3.5 mm derin, Ø31 çember (açılar yaklaşık)
    pts = [(HOLE_PCD / 2 * math.cos(math.radians(a)), HOLE_PCD / 2 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    gb = gb.cut(cq.Workplane("XY").pushPoints(pts).circle(1.25).extrude(-3.5))
    body = cq.Workplane("XY").circle(BODY_R).extrude(-22.7).translate((0, 0, -GB_LEN))
    cap = cq.Workplane("XY").circle(15.0).extrude(-3.5).translate((0, 0, -GB_LEN - 22.7))
    z_board = -GB_LEN - 22.7 - 3.5 - 2.0
    magnet = cq.Workplane("XY").circle(6.0).extrude(-2.0).translate((0, 0, -GB_LEN - 22.7 - 3.5))
    board = cq.Workplane("XY").circle(32.3 / 2).extrude(-1.6).translate((0, 0, z_board))
    conn = cq.Workplane("XY").box(10, 6, 5.7, centered=(True, True, False)).translate((0, -9, z_board - 1.6 - 5.7))
    tabs = cq.Workplane("XY").pushPoints([(-9, 0), (9, 0)]).rect(1.0, 3.0).extrude(-2.0).translate((0, 0, -GB_LEN - 22.7 - 3.5))
    boss = cq.Workplane("XY").center(0, SHAFT_OFF).circle(BOSS_D / 2).extrude(BOSS_L)
    shaft = cq.Workplane("XY").center(0, SHAFT_OFF).circle(3.0).extrude(15.0).translate((0, 0, BOSS_L))
    # D düzlüğü: 5.5 mm, uçtan 12 mm
    flat = cq.Workplane("XY").center(0, SHAFT_OFF + 2.5 + 2.0).rect(8, 4).extrude(12.0).translate((0, 0, BOSS_L + 3.0))
    shaft = shaft.cut(flat)
    return gb.union(body).union(cap).union(magnet).union(board).union(conn).union(tabs).union(boss).union(shaft)


def motor_placed(axle_y=0.0):
    """Sağ motoru dünya koordinatına yerleştir: mil +X (dışa), mil redüktör merkezinin altında."""
    return (motor_model().rotate((0, 0, 0), (0, 1, 0), 90).rotate((0, 0, 0), (1, 0, 0), -90)
            .translate((X_BR, axle_y, PLATE_TOP + GC_H)))


def box(x0, x1, y0, y1, z0, h):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, h, centered=False).translate((x0, y0, z0))


def caster_dummy(x, y):
    hc = CASTER_H
    shim = PLATE_BOT - hc
    br = 12.7 / 2
    body = cq.Workplane("XY").box(20, 16, hc - br, centered=(True, True, False)).edges("|Z").fillet(3).translate((x, y, br))
    ball = cq.Workplane("XY").sphere(br).translate((x, y, br))
    return body.union(ball), shim


def rot180(w):
    return w.rotate((0, 0, 0), (0, 0, 1), 180)


def assembly(layout):
    axle_y = 0.0 if layout == "B" else AXLE_A
    a = cq.Assembly(name=f"raptor_{layout}")
    gray, blue, dark, orange = cq.Color(0.82, 0.83, 0.85), cq.Color(0.22, 0.45, 0.80), cq.Color(0.15, 0.15, 0.17), cq.Color(0.86, 0.40, 0.16)
    a.add(bottom_plate().translate((0, 0, PLATE_BOT)), name="alt_plaka", color=gray)
    a.add(top_plate().translate((0, 0, TOP_DECK_Z)), name="ust_plaka", color=gray)
    for i, (x, y) in enumerate(PILLARS):
        a.add(pillar().translate((x, y, PLATE_TOP)), name=f"direk_{i}", color=gray)
    br = motor_bracket().translate((0, axle_y, PLATE_TOP))
    a.add(br, name="braket_sag", color=orange)
    a.add(rot180(motor_bracket()).translate((0, axle_y, PLATE_TOP)), name="braket_sol", color=orange)
    a.add(motor_placed(axle_y), name="motor_sag", color=cq.Color(0.70, 0.71, 0.74))
    a.add(rot180(motor_placed(0.0)).translate((0, axle_y, 0)), name="motor_sol", color=cq.Color(0.70, 0.71, 0.74))
    a.add(wheel_dummy().translate((0, axle_y, 0)), name="teker_sag", color=dark)
    a.add(rot180(wheel_dummy()).translate((0, axle_y, 0)), name="teker_sol", color=dark)
    casters = CASTERS if layout == "B" else [CASTERS[1]]
    for i, (x, y) in enumerate(casters):
        c, shim = caster_dummy(x, y)
        a.add(c, name=f"sarhos_{i}", color=cq.Color(0.55, 0.56, 0.6))
        if shim > 0.2:
            a.add(caster_shim(shim).translate((x, y, PLATE_BOT - shim)), name=f"sarhos_pulu_{i}", color=orange)
    # elektronik (yaklaşık kutular)
    if layout == "B":
        drv = [(-57, -7, 40, 90), (7, 57, 40, 90)]
    else:
        drv = [(-57, -7, -32, 18), (7, 57, -32, 18)]
    for i, (x0, x1, y0, y1) in enumerate(drv):
        a.add(box(x0, x1, y0, y1, PLATE_TOP, 43), name=f"bts7960_{i}", color=cq.Color(0.20, 0.42, 0.62))
    bat = (-38.5, 38.5, -95.0, -35.0)
    a.add(box(*bat, PLATE_TOP, 21), name="batarya_3s", color=cq.Color(0.25, 0.55, 0.35))
    a.add(box(-42.5, 42.5, PI_CENTER[1] - 28, PI_CENTER[1] + 28, TOP_DECK_Z + PLATE_T + 5, 18), name="raspberry_pi5", color=cq.Color(0.15, 0.50, 0.30))
    a.add(box(22, 50, 35, 90, TOP_DECK_Z + PLATE_T, 12), name="esp32", color=cq.Color(0.12, 0.12, 0.14))
    mx, my = MAST_SOCKETS[0] if layout == "B" else MAST_SOCKETS[1]
    mz = TOP_DECK_Z + PLATE_T + 2
    a.add(mast().translate((mx, my, mz)), name="kamera_diregi", color=gray)
    a.add(mast_top().translate((mx, my, mz + MAST_LEN - 16)), name="direk_ucu", color=orange)
    a.add(box(mx - 12.5, mx + 12.5, my + 24, my + 26, mz + MAST_LEN - 16 + 34, 24), name="kamera", color=cq.Color(0.1, 0.4, 0.2))
    a.add(box(mx - 15, mx + 15, my - 22, my + 7, mz + MAST_LEN - 16 + 22, 6), name="uwb_tag", color=cq.Color(0.6, 0.15, 0.15))
    return a


PARTS = {
    "alt_plaka": (bottom_plate, 1),
    "ust_plaka": (top_plate, 1),
    "motor_braketi": (motor_bracket, 2),
    "kat_diregi": (pillar, 6),
    "kamera_diregi": (mast, 1),
    "direk_ucu_kamera_uwb": (mast_top, 1),
    "sarhos_pulu_0_5mm": (lambda: caster_shim(0.5), 2),
    "sarhos_pulu_1mm": (lambda: caster_shim(1.0), 2),
}

if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    for name, (fn, n) in PARTS.items():
        w = fn()
        cq.exporters.export(w, os.path.join(OUT, "stl", f"{name}.stl"), tolerance=0.05, angularTolerance=0.15)
        cq.exporters.export(w, os.path.join(OUT, "step", f"{name}.step"))
        bb = w.val().BoundingBox()
        print(f"{name:24s} x{n}  {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f} mm  hacim {w.val().Volume()/1000:6.1f} cm3")
    os.makedirs(os.path.join(OUT, "motor"), exist_ok=True)
    mm = motor_model()
    cq.exporters.export(mm, os.path.join(OUT, "motor", "JGB37-520_12V_530rpm.step"))
    cq.exporters.export(mm, os.path.join(OUT, "motor", "JGB37-520_12V_530rpm.stl"), tolerance=0.05, angularTolerance=0.15)
    bb = mm.val().BoundingBox()
    print(f"motor {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
    for lay in ("B", "A"):
        asm = assembly(lay)
        asm.save(os.path.join(OUT, f"montaj_{lay}.glb"), tolerance=0.2, angularTolerance=0.3)
        asm.save(os.path.join(OUT, "step", f"montaj_{lay}.step"))
    print(f"teker Ø{WHEEL_D}: aks {AXLE_Z}, plaka üstü {PLATE_TOP}, plaka altı (sarhoş yüksekliği) {PLATE_BOT}, "
          f"üst kat {TOP_DECK_Z}, iz genişliği {TRACK}")
