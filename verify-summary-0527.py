#!/usr/bin/env python3
from pathlib import Path

t = Path("preview/index.html").read_text(encoding="utf-8")

checks = [
    ("3-leg Lowe/Schwarber/Alvarez", "Brandon Lowe HR</strong><small>Jameson Taillon" in t and "Kyle Schwarber HR" in t and "Yordan Alvarez HR" in t),
    ("Top5 Schwarber 96", "Kyle Schwarber <small>10 HR, 28.3% barrels vs Buehler</small></span><strong>96</strong>" in t),
    ("Weather NYY +9%", "NYY @ KC <small>+9% HR at Kauffman" in t),
    ("Weather section title", "<h3>Top 5 Weather Games</h3>" in t),
    ("Weather MIN @ CWS row", "MIN @ CWS <small>+1% combined at Rate Field" in t),
    ("No Goblin weather box", "best-bets-group\">\n                            <h4>Top 5 Weather Games</h4>" not in t),
    ("HRRBI play box", "2 Hits + Runs + RBI Play</h4>" in t),
    ("HRRBI 8 legs", t.count("Over 1.5 hits + runs + RBIs") == 8),
    ("No old park card title", "Best Park / Weather HR Rows (slate)" not in t),
    ("Attack Gibson", "Trey Gibson</strong><small>Slate-high HR risk" in t),
    ("Longshot McLain vs Tong", "Matt McLain <small>+900 with 2 HR versus Tong</small>" in t),
    ("Fade PHI -7%", "PHI @ SD <small>Petco -7% HR" in t),
    ("No stale James Wood 3-leg", "James Wood HR</strong><small>Littell" not in t),
    ("Mayo clean emojis", 'Coby Mayo (R)", odds: "Listed +500 - Over 0.5 HR", score: 78, emojis: "🚀 💎"' in t),
    ("Goldschmidt no stray ball", 'Paul Goldschmidt (R)", odds: "Listed +590 - Over 0.5 HR", score: 91, emojis: "🚀 ⭐ 🌕 💣"' in t),
    ("Sheet date meta", 'content="2026-05-27"' in t),
    ("48 props count", "48 listed HR props" in t),
    ("10 games count", "10 games</strong>" in t),
    ("12 favorites count", "12 Worst Pickz Favorite" in t),
]

import goblin_parlay_rules as gpr

checks.append(("3-leg vs fav 3-leg distinct", len(gpr.validate_three_leg_parlays(t)) == 0))
checks.append(("Fav 3-leg Aranda/Duran/EDC", all(
    x in t for x in (
        "Jonathan Aranda HR",
        "Jarren Duran HR",
        "Elly De La Cruz HR",
    )
)))
checks.append(("Fav 3-leg not Lowe/Schwarber/Alvarez", "Kyle Schwarber HR &#11088;" not in t.split("Worst Pickz Favorite 3 Leg")[1].split("Top 5 Pitchers")[0]))

failed = []
for name, ok in checks:
    status = "OK" if ok else "FAIL"
    print(f"{status}  {name}")
    if not ok:
        failed.append(name)

if failed:
    raise SystemExit(f"{len(failed)} check(s) failed")
print("\nAll summary checks passed.")
