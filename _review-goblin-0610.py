#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
g: dict = {"__file__": str(ROOT / "patch-0610-preview.py"), "__name__": "__main__"}
cut = (ROOT / "patch-0610-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
exec(compile(cut + "\n", "patch-0610-preview.py", "exec"), g)


def show(r):
    zs = r.get("zone_score")
    return (
        f"{r['name_plain']} vs {r['chip']} | score {r['score']} "
        f"split {r['split']:+.2f} risk {r['risk']:+.2f} park {r['park_pct']}% "
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
print("Longshots")
for x in g["longshots"]:
    print(" ", show(x))
print("Pitchers attack:", g["load_pitchers_to_attack"]()[:5])

print("\n--- Top O0.5 candidates ---")
for r in g["straight_o05_pool"](g["straight_rows"], exclude_name=g["straight_o15"]["name"], exclude_game=g["straight_o15"]["game_key"])[:8]:
    print(" ", show(r))

print("\n--- Top O1.5 candidates ---")
for r in sorted(g["o15_candidates"], key=g["multi_hr_rank"], reverse=True)[:8]:
    print(" ", show(r))

print("\n--- Top 3-leg pool ---")
pool = [r for r in g["straight_rows"] if r["name"] not in g["straight_names"] and g["goblin_top3_ok"](r)]
pool.sort(key=lambda x: (g["straight_attack_rank"](x), x["rank"], x["score"]), reverse=True)
for r in pool[:10]:
    print(" ", show(r))
