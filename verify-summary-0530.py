#!/usr/bin/env python3
from pathlib import Path

import goblin_parlay_rules as gpr

t = Path("preview/index.html").read_text(encoding="utf-8")

checks = [
    ("Straights of the Day section", "Worst Pickz Straights of the Day" in t),
    ("Straight pick Soto O0.5", "Juan Soto &mdash; vs Max Meyer" in t),
    ("Straight pick Schwarber O1.5", "Kyle Schwarber &mdash; vs Justin Wrobleski" in t),
    ("Straight Gambly O0.5", "Juan Soto - Over 0.5 homerun" in t),
    ("Straight Gambly O1.5", "Kyle Schwarber - Over 1.5 homeruns" in t),
    ("Not yesterday Lowe straight", "Brandon Lowe &mdash; vs Taj Bradley" not in t.split("Worst Pickz Straights of the Day")[1].split("Goblin")[0]),
    ("Not yesterday Horwitz straight", "Spencer Horwitz &mdash; vs Taj Bradley" not in t.split("Worst Pickz Straights of the Day")[1].split("Goblin")[0]),
    ("3-leg Soto/Lowe/Alonso", all(
        x in t for x in (
            "Juan Soto HR</strong><small>6 HR",
            "Brandon Lowe HR</strong><small>2 HR",
            "Pete Alonso HR</strong><small>2 HR and 97.5 mph EV versus Austin Voth",
        )
    )),
    ("2-leg Schwarber/Alonso", all(
        x in t for x in (
            "Kyle Schwarber HR</strong><small>3 HR and 30.0% barrels versus Justin Wrobleski",
            "Pete Alonso HR</strong><small>2 HR versus Austin Voth",
        )
    )),
    ("Fav 3-leg Schwarber/Adames/Walker", all(
        x in t for x in (
            "Kyle Schwarber HR &#11088;",
            "Willy Adames HR &#11088;",
            "Jordan Walker HR &#11088;",
        )
    )),
    ("No Murakami on sheet", "Murakami" not in t),
    ("No Duran fav 3-leg", "Jarren Duran HR &#11088;" not in t.split("Worst Pickz Favorite 3 Leg")[1].split("Top 5 Pitchers")[0]),
    ("Top5 Ohtani not Murakami", "Shohei Ohtani <small>2 HR, 96.6 mph EV versus Zack Wheeler</small>" in t),
    ("Weather Coors +29", "Coors +29 altitude boost" in t),
    ("Weather Ohtani #4", "#4 Shohei Ohtani <small>2 HR, 96.6 mph EV versus Wheeler</small>" in t),
    ("Longshot Horwitz/Baty/Bailey/Torres", all(
        x in t for x in (
            "Spencer Horwitz <small>+730 with 3 HR versus Bradley</small>",
            "Brett Baty <small>+710 with 1 HR versus Meyer</small>",
            "Patrick Bailey <small>+1140 with 1 HR versus Bello</small>",
            "Bryan Torres <small>+1120 versus Imanaga LHB leak</small>",
        )
    )),
    ("Holmes bum title", "Grant Holmes 🧤 (R, ATL)" in t),
    ("Imanaga bum title", "Shota Imanaga 🧤 (L, CHC)" in t),
    ("Fedde bum title", "Erick Fedde 🧤 (R, CWS)" in t),
    ("Lorenzen bum title", "Michael Lorenzen 🧤 (R, COL)" in t),
    ("Sheet date meta", 'content="2026-05-30"' in t),
    ("78 props count", "78 listed HR props" in t),
    ("15 games count", "15 games</strong>" in t),
    ("19 favorites count", "19 Worst Pickz Favorite" in t),
    ("May 30 header", "Saturday, May 30, 2026 — Worst Pickz HR cheat sheet" in t),
]
longshot_block = t.split("Best longshot HR")[1].split("Harsh Environment")[0]
checks.append(("No stale longshots in summary", all(
    x not in longshot_block for x in ("Jacob Young", "Bryan Rocchio", "Tj Rumfield")
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
