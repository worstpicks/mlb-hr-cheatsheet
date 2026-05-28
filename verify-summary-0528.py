#!/usr/bin/env python3
from pathlib import Path

import goblin_parlay_rules as gpr

t = Path("preview/index.html").read_text(encoding="utf-8")

checks = [
    ("3-leg Lowe/Alvarez/Buxton", all(x in t for x in ("Brandon Lowe HR</strong><small>Colin Rea", "Yordan Alvarez HR</strong><small>Nathan Eovaldi", "Byron Buxton HR</strong><small>3 HR"))),
    ("Top5 Lowe 96", "Brandon Lowe <small>3 HR, Rea HR risk, 38.5% barrels</small></span><strong>96</strong>" in t),
    ("Weather section title", "<h3>Top 5 Weather Games</h3>" in t),
    ("Weather MIN @ CWS row", "MIN @ CWS <small>Rate Field flat +0% HR" in t),
    ("No Goblin weather box", "best-bets-group\">\n                            <h4>Top 5 Weather Games</h4>" not in t),
    ("HRRBI play box", "2 Hits + Runs + RBI Play</h4>" in t),
    ("HRRBI 8 legs", t.count("Over 1.5 hits + runs + RBIs") == 8),
    ("No old park card title", "Best Park / Weather HR Rows (slate)" not in t),
    ("Attack Rea", "Colin Rea</strong><small>Slate-high HR risk" in t),
    ("Longshot IK-F", "Isiah Kiner-Falefa <small>+1700 versus Chris Sale</small>" in t),
    ("Fade TOR @ BAL -19%", "TOR @ BAL <small>Oriole Park -19% HR" in t),
    ("Mayo bum emojis", 'Coby Mayo (R)", odds: "Listed +500 - Over 0.5 HR", score: 86, emojis: "🌕 💣 ⚾ 🕊️ 🧤"' in t),
    ("Joc clean emojis", 'Joc Pederson (L)", odds: "Listed +548 - Over 0.5 HR", score: 75, emojis: "💎"' in t),
    ("Pinango only 100+ rocket", 'Yohendrick Pinango (L)", odds: "Listed +840 - Over 0.5 HR", score: 93, emojis: "🚀 ⭐ 🌕 💣"' in t),
    ("No Busch favorite star", 'Michael Busch (L)", odds: "Listed +630 - Over 0.5 HR", score: 72, emojis: "💎 📜"' in t),
    ("Sheet date meta", 'content="2026-05-28"' in t),
    ("35 props count", "35 listed HR props" in t),
    ("6 games count", "6 games</strong>" in t),
    ("7 favorites count", "7 Worst Pickz Favorite" in t),
    ("Eovaldi title not deGrom", "Nathan Eovaldi 🧤 (R, TEX)" in t and "deGrom" not in t),
    ("Rea title clean", "Colin Rea 🧤 (R, CHC)" in t and "Jameson" not in t),
]

checks.append(("3-leg vs fav 3-leg distinct", len(gpr.validate_three_leg_parlays(t)) == 0))
checks.append(("Fav 3-leg Pinango/Alonso/Nimmo", all(
    x in t for x in (
        "Yohendrick Pinango HR &#11088;",
        "Pete Alonso HR &#11088;",
        "Brandon Nimmo HR &#11088;",
    )
)))
fav_block = t.split("Worst Pickz Favorite 3 Leg")[1].split("Top 5 Pitchers")[0]
checks.append(("Fav 3-leg not Lowe/Alvarez/Buxton", all(
    x not in fav_block for x in ("Brandon Lowe HR &#11088;", "Yordan Alvarez HR &#11088;", "Byron Buxton HR &#11088;")
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
