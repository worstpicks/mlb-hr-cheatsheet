#!/usr/bin/env python3
"""Final local audit for 2026-08-11 (do not push)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-11"
PREVIEW = ROOT / "preview" / "index.html"
BUM_MIN = 0.95
PROPCOUNT = 82

errs: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")

    if f'content="{DATE}"' not in html:
        fail(f"sheet-date meta missing {DATE}")
    if "Tuesday, August 11, 2026" not in html:
        fail("hero must be Tuesday, August 11, 2026")
    if "Monday, August 10, 2026 — Worst" in html:
        fail("stale 8/10 hero still on current sheet")
    if "Monday, August 11" in html or "Wednesday, August 11" in html:
        fail("wrong weekday on August 11 (must be Tuesday)")
    if "August 11, 2026 — current slate" not in html:
        fail("manifest missing August 11 current slate")
    if "August 10, 2026 — current slate" in html:
        fail("8/10 still labeled current")

    m = re.search(r"(\d+) listed HR props", html)
    if not m or int(m.group(1)) != PROPCOUNT:
        fail(f"expected {PROPCOUNT} props, got {m.group(0) if m else None}")

    from sheet_data import load_pitcher_risk

    risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    bums = [(row["pitcher"], row["overall"]) for row in risk.values() if row["overall"] >= BUM_MIN]
    if len(bums) < 1:
        fail(f"expected at least 1 bum, got {bums}")
    # Proxy targets: Joe Ryan / Grayson Rodriguez / Zack Littell lead L10 risk.
    expected_bum = {"Tomoyuki Sugano", "Ryan Johnson", "Mason Barnett"}
    if not any(p in expected_bum for p, _ in bums):
        fail(f"expected one of {sorted(expected_bum)} as bum, got {bums}")
    for pname, overall in bums:
        if f"{pname} 🧤" not in html:
            fail(f"bum {pname} ({overall:.2f}) missing 🧤 in titles")

    for base in (
        "Shota Imanaga",
        "Ryan Weathers",
        "Patrick Sandoval",
        "Martin Perez",
        "Nick Lodolo",
        "Cristopher Sanchez",
        "Cody Bradford",
        "Kyle Harrison",
        "Mitch Bratt",
        "Carson Whisenhunt",
        "Blake Snell",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")

    block = re.search(r"const games = \[(.*?)\n\];", html, re.S)
    titles = []
    if not block:
        fail("games block missing")
    else:
        titles = re.findall(r'title:\s*"([^"]+)"', block.group(1))
        metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', block.group(1))
        if len(titles) != 15:
            fail(f"expected 15 games, got {len(titles)}")
        if len(metas) != 15:
            fail(f"expected 15 gameMeta, got {len(metas)}")
        for title, meta in zip(titles, metas):
            s = meta.encode().decode("unicode_escape")
            n = len(re.findall(r"pitcher-meta", s))
            if "Park" not in s:
                fail(f"{title}: missing Park in gameMeta")
            if n != 2:
                fail(f"{title}: expected 2 pitcher metas, got {n}")
            if "LHB" not in s or "RHB" not in s:
                fail(f"{title}: missing LHB/RHB splits in gameMeta")

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
        "propfinder.app/weather",
    ]
    for f in features:
        if f not in html:
            fail(f"feature missing: {f}")

    picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
    if len(picks) < 2:
        fail(f"straights missing: {picks}")

    arch = ROOT / "preview" / "archive" / "2026-08-10.html"
    if not arch.exists():
        fail("8/10 archive missing")
    elif 'content="2026-08-10"' not in arch.read_text(encoding="utf-8"):
        fail("8/10 archive wrong sheet-date")

    research = ROOT / "preview" / "data" / f"research-{DATE}.json"
    park = ROOT / "preview" / "data" / f"park-factors-{DATE}.json"
    if not research.exists():
        fail("research JSON missing")
    if not park.exists():
        fail("park-factors JSON missing")

    print("=== AUDIT 2026-08-11 ===")
    print("bums:", sorted(bums, key=lambda x: -x[1]))
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
