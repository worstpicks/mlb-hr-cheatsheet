#!/usr/bin/env python3
from pathlib import Path

import goblin_parlay_rules as gpr

t = Path("preview/index.html").read_text(encoding="utf-8")

checks = [
    ("3-leg Soto/Lowe/Machado", all(x in t for x in ("Juan Soto HR</strong><small>6 HR", "Brandon Lowe HR</strong><small>2 HR", "Manny Machado HR</strong><small>100.5 mph"))),
    ("Top5 Soto 95", "Juan Soto <small>6 HR, Meyer RHB split, 43.8% barrels</small></span><strong>95</strong>" in t),
    ("Weather section title", "<h3>Top 5 Weather Games</h3>" in t),
    ("Weather Coors row", "SF @ COL <small>Coors +14% HR" in t),
    ("No Goblin weather box", "best-bets-group\">\n                            <h4>Top 5 Weather Games</h4>" not in t),
    ("Attack Fedde", "Erick Fedde</strong><small>Slate-high HR risk (1.69)" in t),
    ("Longshot Horwitz", "Spencer Horwitz <small>+730 with 3 HR versus Bradley</small>" in t),
    ("Fade T-Mobile", "ARI @ SEA <small>T-Mobile Park -12% HR" in t),
    ("Holmes bum title", "Grant Holmes 🧤 (R, ATL)" in t),
    ("Fedde bum title", "Erick Fedde 🧤 (R, CWS)" in t),
    ("Sheet date meta", 'content="2026-05-29"' in t),
    ("94 props count", "94 listed HR props" in t),
    ("15 games count", "15 games</strong>" in t),
    ("24 favorites count", "24 Worst Pickz Favorite" in t),
    ("May 29 header", "Friday, May 29, 2026 — Worst Pickz HR cheat sheet" in t),
]

checks.append(("3-leg vs fav 3-leg distinct", len(gpr.validate_three_leg_parlays(t)) == 0))
checks.append(("Fav 3-leg Schwarber/Murakami/Duran", all(
    x in t for x in (
        "Kyle Schwarber HR &#11088;",
        "Munetaka Murakami HR &#11088;",
        "Jarren Duran HR &#11088;",
    )
)))
fav_block = t.split("Worst Pickz Favorite 3 Leg")[1].split("Top 5 Pitchers")[0]
checks.append(("Fav 3-leg not Soto/Lowe/Machado", all(
    x not in fav_block for x in ("Juan Soto HR &#11088;", "Brandon Lowe HR &#11088;", "Manny Machado HR &#11088;")
)))

failed = []
for name, ok in checks:
    status = "OK" if ok else "FAIL"
    print(f"{status}  {name}")
    if not ok:
        failed.append(name)

if failed:
    raise SystemExit(f"{len(failed)} check(s) failed")
print("\nAll summary checks passed.")
