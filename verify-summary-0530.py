#!/usr/bin/env python3
from pathlib import Path

import goblin_parlay_rules as gpr

t = Path("preview/index.html").read_text(encoding="utf-8")

checks = [
    ("Straights of the Day section", "Worst Pickz Straights of the Day" in t),
    ("Straight pick Adames O0.5", "Willy Adames &mdash; vs Ryan Feltner" in t),
    ("Straight pick Schwarber O1.5", "Kyle Schwarber &mdash; vs Roki Sasaki" in t),
    ("Straight Gambly O0.5", "Willy Adames - Over 0.5 homerun" in t),
    ("Straight Gambly O1.5", "Kyle Schwarber - Over 1.5 homeruns" in t),
    ("Not yesterday Lowe straight", "Brandon Lowe &mdash; vs Taj Bradley" not in t.split("Worst Pickz Straights of the Day")[1].split("Goblin")[0]),
    ("Not yesterday Horwitz straight", "Spencer Horwitz &mdash; vs Taj Bradley" not in t.split("Worst Pickz Straights of the Day")[1].split("Goblin")[0]),
    ("Not yesterday Soto straight", "Juan Soto &mdash; vs Max Meyer" not in t.split("Worst Pickz Straights of the Day")[1].split("Goblin")[0]),
    ("3-leg Adames/Schwarber/Lowe", all(
        x in t for x in (
            "Willy Adames HR</strong><small>98 score",
            "Kyle Schwarber HR</strong><small>98 score",
            "Brandon Lowe HR</strong><small>98 score",
        )
    )),
    ("2-leg Adames/Schwarber", all(
        x in t for x in (
            "Willy Adames HR</strong><small>Best O0.5 lane",
            "Kyle Schwarber HR</strong><small>Best multi-HR profile",
        )
    )),
    ("Fav 3-leg Mitchell/Walker/Jac", all(
        x in t for x in (
            "Garrett Mitchell HR &#11088;",
            "Jordan Walker HR &#11088;",
            "Jac Caglianone HR &#11088;",
        )
    )),
    ("No Murakami on sheet", "Murakami" not in t),
    ("No Duran fav 3-leg", "Jarren Duran HR &#11088;" not in t.split("Worst Pickz Favorite 3 Leg")[1].split("Top 5 Pitchers")[0]),
    ("Top5 Adames not Alonso", "Willy Adames <small>4 HR, Feltner +1.79 vs RHB" in t),
    ("Weather Coors +29", "Coors +29 altitude boost" in t),
    ("Weather Turner #5", "#5 Trea Turner <small>Sasaki +0.91 vs RHB</small>" in t),
    ("Longshot Haase/Horwitz/Sanchez/Rumfield", all(
        x in t for x in (
            "Eric Haase <small>+950 versus Feltner",
            "Spencer Horwitz <small>+730 with 3 HR versus Ober",
            "Jesus Sanchez <small>+720 versus Brandon Young",
            "Tj Rumfield <small>+880 at Coors versus Houser",
        )
    )),
    ("Singer bum title", "Brady Singer 🧤 (R, CIN)" in t),
    ("Feltner bum title", "Ryan Feltner 🧤 (R, COL)" in t),
    ("No stale Holmes title", "Grant Holmes 🧤 (R, ATL)" not in t),
    ("No stale Bradley title", "Taj Bradley (R, MIN)" not in t),
    ("Sheet date meta", 'content="2026-05-30"' in t),
    ("78 props count", "78 listed HR props" in t),
    ("15 games count", "15 games</strong>" in t),
    ("19 favorites count", "19 Worst Pickz Favorite" in t),
    ("May 30 header", "Saturday, May 30, 2026 — Worst Pickz HR cheat sheet" in t),
]
longshot_block = t.split("Best longshot HR")[1].split("Harsh Environment")[0]
checks.append(("No stale longshots in summary", all(
    x not in longshot_block for x in ("Jacob Young", "Bryan Rocchio", "Jackson Holliday", "versus Bradley")
)))

checks.append(("3-leg vs fav 3-leg distinct", len(gpr.validate_three_leg_parlays(t)) == 0))

failed = []
for name, ok in checks:
    status = "OK" if ok else "FAIL"
    print(f"{status}  {name}")
    if not ok:
        failed.append(name)

if failed:
    raise SystemExit(f"{len(failed)} check(s) failed")
print("\nAll summary checks passed.")
