import os
import itertools
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import raptor_chassis as rc

for lay in ("B", "A"):
    asm = rc.assembly(lay)
    solids = {}
    for name, obj in [(c.name, c.obj) for c in asm.children]:
        solids[name] = obj.val() if hasattr(obj, "val") else obj
    bad = []
    for (n1, s1), (n2, s2) in itertools.combinations(solids.items(), 2):
        b1, b2 = s1.BoundingBox(), s2.BoundingBox()
        if (b1.xmax < b2.xmin or b2.xmax < b1.xmin or b1.ymax < b2.ymin or b2.ymax < b1.ymin
                or b1.zmax < b2.zmin or b2.zmax < b1.zmin):
            continue
        v = s1.intersect(s2).Volume()
        if v > 0.5:
            bad.append((round(v, 1), n1, n2))
    print(f"--- {lay}: {len(solids)} parca, cakisan ciftler:")
    for b in sorted(bad, reverse=True):
        print("  ", b)

    # gaps
    def gap(n1, n2):
        return solids[n1].distance(solids[n2]) if hasattr(solids[n1], "distance") else None
    for p in [("motor_sag", "alt_plaka"), ("motor_sag", "motor_sol"), ("teker_sag", "alt_plaka"),
              ("teker_sag", "braket_sag"), ("motor_sag", "ust_plaka"), ("bts7960_0", "ust_plaka"),
              ("braket_sag", "direk_2"), ("braket_sag", "direk_5"), ("bts7960_1", "braket_sag"),
              ("batarya_3s", "direk_4"), ("batarya_3s", "direk_3"), ("batarya_3s", "bts7960_0"), ("batarya_3s", "motor_sag"), ("batarya_3s", "braket_sag")]:
        try:
            d = solids[p[0]].distance(solids[p[1]])
            print(f"   bosluk {p[0]} - {p[1]}: {d:.1f} mm")
        except Exception as e:
            print("   ", p, e)
    bb = solids["teker_sag"].BoundingBox()
    print(f"   toplam genislik {2*bb.xmax:.0f} mm, teker alt z {bb.zmin:.2f}")
    for n in solids:
        if n.startswith("sarhos_") and "pulu" not in n:
            print(f"   {n} alt z = {solids[n].BoundingBox().zmin:.2f}")
