#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
g: dict = {"__file__": str(ROOT / "patch-0611-preview.py"), "__name__": "__main__"}
cut = (ROOT / "patch-0611-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
exec(compile(cut + "\n", "patch-0611-preview.py", "exec"), g)


def show(r):
    zs = r.get("zone_score")
    park = g["effective_park_pct"](r)
    return (
        f"{r['name_plain']} vs {r['chip']} | score {r['score']} "
        f"split {r['split']:+.2f} risk {r['risk']:+.2f} park {park}% "
        f"hr {r['hr']}/{r['near']} zone {zs}"
    )


print("O0.5", show(g["straight_o05"]))
print("O1.5", show(g["straight_o15"]))
print("3-leg")
for x in g["top3"]:
    print(" ", show(x))
print("2-leg")
for x in g["two_leg"]:
    print(" ", show(x))
print("Fav3")
for x in g["fav3"]:
    print(" ", show(x))
print("Top5")
for x in g["top5"]:
    print(" ", show(x))
print("Weather5")
for x in g["weather5"]:
    print(" ", show(x))
print("Pitchers:", [p["pitcher"] for p in g["load_pitchers_to_attack"]()[:5]])
