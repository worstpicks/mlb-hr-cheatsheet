#!/usr/bin/env python3
from pathlib import Path

cut = (Path("patch-0614-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0])
g = {"__file__": "patch-0614-preview.py", "__name__": "__main__"}
exec(compile(cut + "\n", "p", "exec"), g)
rows = g["rows"]


def show(label, items, n=15):
    print(f"\n== {label} ==")
    for r in items[:n]:
        z = r.get("zone_score") or 0
        print(
            f"{r['name_plain']:22} {r['game_key']:10} vs {r['chip']:12} "
            f"sc={r['score']:2} hr={r['hr']} near={r['near']} ev={r['ev']:.0f} "
            f"split={r['split']:+.2f} risk={r['risk']:.2f} park={r['park_pct']:+d} zone={z:.0f} "
            f"atk={g['straight_attack_rank'](r):.1f}"
        )


ranked = sorted(rows, key=lambda r: r["rank"], reverse=True)
print("CURRENT O0.5", g["straight_o05"]["name_plain"], "vs", g["straight_o05"]["chip"])
print("CURRENT O1.5", g["straight_o15"]["name_plain"], "vs", g["straight_o15"]["chip"])
print("3leg", [x["name_plain"] for x in g["top3"]])
print("2leg", [x["name_plain"] for x in g["two_leg"]])
print("fav3", [x["name_plain"] for x in g["fav3"]])
print("top5", [x["name_plain"] for x in g["top5"]])
print("weather5", [x["name_plain"] for x in g["weather5"]])
show("TOP OVERALL", ranked)
show("STRICT O0.5 POOL", g["straight_o05_pool"](rows, strict=True))
show("O15 CANDIDATES", g["o15_candidates"] if "o15_candidates" in g else sorted([r for r in rows if r["hr"] >= 2], key=g["multi_hr_rank"], reverse=True))
show("vs MIKOLAS/SPRINGS/WILLIAMS", [r for r in ranked if r["chip"] in ("Mikolas", "Springs", "Williams", "Rodriguez", "Sugano")])
show("FAVORITES", [r for r in ranked if r["name"] in g["FAVS"]])
show("COL @ ATH", [r for r in ranked if r["game_key"] == "COL @ ATH"])
