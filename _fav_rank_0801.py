#!/usr/bin/env python3
from pathlib import Path

cut = Path("patch-0801-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
g: dict = {"__file__": "p", "__name__": "x"}
exec(compile(cut + "\n", "p", "exec"), g)
fav = {x.rsplit(" (", 1)[0] for x in g["FAVS"]}
rows = sorted(
    [r for r in g["rows"] if r["name_plain"] in fav],
    key=lambda r: r.get("straight_attack_rank", 0),
    reverse=True,
)
for r in rows[:15]:
    print(
        f"{r['name_plain']:22} attack={r.get('straight_attack_rank',0):6.1f} "
        f"zone={r.get('hr_zone_fit',0):5.1f} split={r['split']:+.2f} "
        f"risk={r['risk']:+.2f} {r['hr']}HR/{r['near']}near score={r['score']}"
    )
print("fav3", [x["name_plain"] for x in g["fav3"]])
print("straights", g["straight_o05"]["name_plain"], g["straight_o15"]["name_plain"])
