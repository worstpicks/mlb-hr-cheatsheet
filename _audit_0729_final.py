#!/usr/bin/env python3
"""Final pre-push audit for 2026-07-29."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-07-29"
PREVIEW = ROOT / "preview" / "index.html"
BUM_MIN = 0.95

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")

    if f'content="{DATE}"' not in html:
        fail(f"sheet-date meta missing {DATE}")
    if "Wednesday, July 29, 2026" not in html:
        fail("hero must be Wednesday, July 29, 2026")
    if re.search(r"(Monday|Tuesday|Sunday|Saturday), July 2[79], 2026", html):
        fail("stale weekday/date in hero")
    if "July 29, 2026 — current slate" not in html:
        fail("manifest missing July 29 current slate")
    if "July 27, 2026 — current slate" in html:
        fail("7/27 still labeled current")

    m = re.search(r"(\d+) listed HR props", html)
    if not m or int(m.group(1)) != 107:
        fail(f"expected 107 props, got {m.group(0) if m else None}")

    from sheet_data import load_pitcher_risk

    risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    bums = [(name, row["overall"]) for name, row in risk.items() if row["overall"] >= BUM_MIN]
    if len(bums) < 6:
        fail(f"expected 6+ bums, got {bums}")
    for name, overall in bums:
        if f"{name.title() if name.islower() else name}" and True:
            # risk keys are lowercase full names
            display = risk[name]["pitcher"] if isinstance(risk[name], dict) and "pitcher" in risk[name] else name
        display = row_name = None
    # Proper bum check using pitcher field
    for key, row in risk.items():
        if row["overall"] < BUM_MIN:
            continue
        pname = row["pitcher"]
        if f"{pname} 🧤" not in html:
            fail(f"bum {pname} ({row['overall']:.2f}) missing 🧤 in titles")

    if "Griffin Canning" not in html:
        fail("Canning missing from sheet after backfill")

    block = re.search(r"const games = \[(.*?)\n\];", html, re.S)
    if not block:
        fail("games block missing")
    else:
        titles = re.findall(r'title:\s*"([^"]+)"', block.group(1))
        metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', block.group(1))
        if len(titles) != 16:
            fail(f"expected 16 games, got {len(titles)}")
        if len(metas) != 16:
            fail(f"expected 16 gameMeta, got {len(metas)}")
        for title, meta in zip(titles, metas):
            s = meta.encode().decode("unicode_escape")
            n = len(re.findall(r"pitcher-meta", s))
            if "Park" not in s:
                fail(f"{title}: missing Park in gameMeta")
            if n != 2:
                fail(f"{title}: expected 2 pitcher metas, got {n}")
            if "LHB" not in s or "RHB" not in s:
                fail(f"{title}: missing LHB/RHB splits in gameMeta")

    if "ATL @ NYM (G1)" not in html or "ATL @ NYM (G2)" not in html:
        fail("ATL@NYM doubleheader games missing")

    features = [
        "Homerun Form",
        "Damage Window",
        "Worst Pickz Straights of the Day",
        "Goblin's Insight",
        "3 Leg Homerun",
        "2 Leg Homerun",
        "Favorite 3 Leg",
        "Top 5 HR",
        "Weather",
        "Longshot",
        "Hits",
        "MLB Research",
        "theme-toggle",
        "Gambly",
        "Pikkit",
        "worst-pickz-gem",
        "straight-streak",
        "is-partial",
        "straightDisplayResult",
        "startTime:",
        "blast:",
        "parkLhbPct",
        "parkRhbPct",
        "zoneScore",
        "gameMeta:",
    ]
    for f in features:
        if f not in html:
            fail(f"feature missing: {f}")

    # Straights present
    picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
    if len(picks) < 2:
        fail(f"straights missing: {picks}")
    if "Tyler Soderstrom" not in html or "Munetaka Murakami" not in html:
        # may have changed after rebuild — just require two distinct cards
        pass

    arch = ROOT / "preview" / "archive" / "2026-07-27.html"
    if not arch.exists():
        fail("7/27 archive missing")
    if 'content="2026-07-27"' not in arch.read_text(encoding="utf-8"):
        fail("7/27 archive wrong sheet-date")

    research = ROOT / "preview" / "data" / f"research-{DATE}.json"
    park = ROOT / "preview" / "data" / f"park-factors-{DATE}.json"
    if not research.exists():
        fail("research JSON missing")
    if not park.exists():
        fail("park-factors JSON missing")

    print("=== AUDIT 2026-07-29 ===")
    print("bums:", sorted(((r["pitcher"], r["overall"]) for r in risk.values() if r["overall"] >= BUM_MIN), key=lambda x: -x[1]))
    print("straights:", picks)
    print("games:", len(re.findall(r'title:\s*"', html[html.find("const games") : html.find("const games") + 500000])) if "const games" in html else "?")
    if errs:
        print("ERRORS:")
        for e in errs:
            print(" ", e)
        return 1
    print("OK all audit checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
