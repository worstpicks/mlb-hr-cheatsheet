#!/usr/bin/env python3
"""Final local audit for 2026-07-30 (do not push)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-07-30"
PREVIEW = ROOT / "preview" / "index.html"
BUM_MIN = 0.95

errs: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")

    if f'content="{DATE}"' not in html:
        fail(f"sheet-date meta missing {DATE}")
    if "Thursday, July 30, 2026" not in html:
        fail("hero must be Thursday, July 30, 2026")
    if re.search(r"(Monday|Tuesday|Wednesday|Sunday|Saturday), July (29|30), 2026", html):
        # allow Thursday only for 7/30
        if "Thursday, July 30, 2026" not in html or "Wednesday, July" in html:
            fail("stale weekday/date in hero")
    if "July 30, 2026 — current slate" not in html:
        fail("manifest missing July 30 current slate")
    if "July 29, 2026 — current slate" in html:
        fail("7/29 still labeled current")

    m = re.search(r"(\d+) listed HR props", html)
    if not m or int(m.group(1)) != 60:
        fail(f"expected 60 props, got {m.group(0) if m else None}")

    from sheet_data import load_pitcher_risk

    risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    bums = [(row["pitcher"], row["overall"]) for row in risk.values() if row["overall"] >= BUM_MIN]
    if len(bums) < 3:
        fail(f"expected 3+ bums, got {bums}")
    for pname, overall in bums:
        if f"{pname} 🧤" not in html:
            fail(f"bum {pname} ({overall:.2f}) missing 🧤 in titles")

    block = re.search(r"const games = \[(.*?)\n\];", html, re.S)
    if not block:
        fail("games block missing")
    else:
        titles = re.findall(r'title:\s*"([^"]+)"', block.group(1))
        metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', block.group(1))
        if len(titles) != 10:
            fail(f"expected 10 games, got {len(titles)}")
        if len(metas) != 10:
            fail(f"expected 10 gameMeta, got {len(metas)}")
        for title, meta in zip(titles, metas):
            s = meta.encode().decode("unicode_escape")
            n = len(re.findall(r"pitcher-meta", s))
            if "Park" not in s:
                fail(f"{title}: missing Park in gameMeta")
            if n != 2:
                fail(f"{title}: expected 2 pitcher metas, got {n}")
            if "LHB" not in s or "RHB" not in s:
                fail(f"{title}: missing LHB/RHB splits in gameMeta")

    if "ATL @ NYM (G1)" in html or "ATL @ NYM (G2)" in html:
        fail("unexpected ATL@NYM doubleheader on 7/30 slate")

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

    picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
    if len(picks) < 2:
        fail(f"straights missing: {picks}")

    arch = ROOT / "preview" / "archive" / "2026-07-29.html"
    if not arch.exists():
        fail("7/29 archive missing")
    if 'content="2026-07-29"' not in arch.read_text(encoding="utf-8"):
        fail("7/29 archive wrong sheet-date")

    research = ROOT / "preview" / "data" / f"research-{DATE}.json"
    park = ROOT / "preview" / "data" / f"park-factors-{DATE}.json"
    if not research.exists():
        fail("research JSON missing")
    if not park.exists():
        fail("park-factors JSON missing")

    print("=== AUDIT 2026-07-30 ===")
    print(
        "bums:",
        sorted(
            ((r["pitcher"], r["overall"]) for r in risk.values() if r["overall"] >= BUM_MIN),
            key=lambda x: -x[1],
        ),
    )
    print("straights:", picks)
    print("games:", len(titles) if block else "?")
    if errs:
        print("ERRORS:")
        for e in errs:
            print(" ", e)
        return 1
    print("OK all audit checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
