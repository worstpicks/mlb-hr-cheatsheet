#!/usr/bin/env python3
"""Deep local audit for 2026-08-03 before push."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from sheet_data import load_pitcher_risk

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
ARCH = ROOT / "preview" / "archive" / "2026-08-02.html"
DATE = "2026-08-03"
BUM_MIN = 0.95

errs: list[str] = []


def fail(m: str) -> None:
    errs.append(m)


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")

    if f'content="{DATE}"' not in html:
        fail("sheet-date meta wrong")
    if "Monday, August 3, 2026" not in html:
        fail("hero must be Monday, August 3, 2026")
    if "Sunday, August 2, 2026 — Worst" in html:
        fail("stale Sunday 8/2 hero still on current sheet")
    if "Sunday, August 3" in html or "Tuesday, August 3" in html:
        fail("wrong weekday on August 3 (must be Monday)")
    if "August 3, 2026 — current slate" not in html:
        fail("manifest current slate not 8/3")
    if "August 2, 2026 — current slate" in html:
        fail("8/2 still labeled current")

    m = re.search(r"(\d+) listed HR props", html)
    if not m or int(m.group(1)) != 56:
        fail(f"prop count: {m.group(0) if m else None}")
    if "7 Worst Pickz Favorite" not in html:
        fail("hero fav count wrong")
    if "11 Worst Pickz Hidden Gemz" not in html:
        fail("hero gem count wrong")

    block = re.search(r"const games = \[(.*?)\n\];", html, re.S)
    if not block:
        fail("games block missing")
        return 1
    body = block.group(1)
    titles = re.findall(r'title:\s*"([^"]+)"', body)
    metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', body)
    parks = re.findall(r"parkPct:\s*(-?\d+)", body)
    lhb = re.findall(r"parkLhbPct:\s*(-?\d+)", body)
    rhb = re.findall(r"parkRhbPct:\s*(-?\d+)", body)
    zones = len(re.findall(r"zoneScore:\s*[\d.]+", body))
    starts = len(re.findall(r"startTime:", body))
    print(
        f"games={len(titles)} metas={len(metas)} park={len(parks)} "
        f"LHB={len(lhb)} RHB={len(rhb)} zone={zones} start={starts}"
    )
    if len(titles) != 8 or len(metas) != 8:
        fail(f"expected 8 games/metas, got {len(titles)}/{len(metas)}")
    if len(parks) != 8 or len(lhb) != 8 or len(rhb) != 8:
        fail(f"park fields incomplete park={len(parks)} lhb={len(lhb)} rhb={len(rhb)}")
    if zones < 50:
        fail(f"zone coverage low: {zones}")
    if starts < 8:
        fail(f"startTime missing: {starts}")

    for must_l in ("Justin Wrobleski (L", "Matthew Boyd (L", "Ian Seymour (L"):
        if must_l not in html:
            fail(f"LHP hand missing/wrong: {must_l}")

    risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    bums = [(r["pitcher"], r["overall"]) for r in risk.values() if r["overall"] >= BUM_MIN]
    print("bums:", bums)
    if not any(p == "Aaron Nola" for p, _ in bums):
        fail(f"Aaron Nola should be bum, got {bums}")
    for pname, overall in bums:
        if f"{pname} 🧤" not in html:
            fail(f"bum missing glove: {pname} ({overall})")

    for title, meta in zip(titles, metas):
        s = meta.encode().decode("unicode_escape")
        gk = title.split(" - ")[0]
        n = len(re.findall(r"pitcher-meta", s))
        if "Park" not in s:
            fail(f"{gk}: missing Park")
        if n != 2:
            fail(f"{gk}: pitcher metas={n}")
        if "LHB" not in s or "RHB" not in s:
            fail(f"{gk}: missing LHB/RHB")
        print(f"  OK {gk} park+splits")

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
    print("straights:", picks)
    if "CJ Abrams" not in picks[0]:
        fail(f"O0.5 should be Abrams, got {picks}")
    if "Jeremy Pena" not in picks[1]:
        fail(f"O1.5 should be Pena, got {picks}")
    if "Over 1.5 homeruns" not in html:
        fail("O1.5 Gambly line missing")

    if not ARCH.exists():
        fail("8/2 archive missing")
    else:
        arch = ARCH.read_text(encoding="utf-8")
        if 'content="2026-08-02"' not in arch:
            fail("8/2 archive wrong sheet-date")
        if "Sunday, August 2, 2026" not in arch:
            fail("8/2 archive hero wrong")
        if "Monday, August 3" in arch:
            fail("8/2 archive polluted with 8/3")

    for path in (
        ROOT / "preview" / "data" / f"research-{DATE}.json",
        ROOT / "preview" / "data" / f"park-factors-{DATE}.json",
    ):
        if not path.exists():
            fail(f"missing {path.name}")

    for sp in (
        "Aaron Nola",
        "Trevor Williams",
        "Justin Wrobleski",
        "Matthew Boyd",
        "Ian Seymour",
        "Cal Quantrill",
    ):
        if sp not in html:
            fail(f"SP missing: {sp}")

    print("=== DEEP AUDIT 2026-08-03 ===")
    if errs:
        print("ERRORS:")
        for e in errs:
            print(" ", e)
        return 1
    print("OK deep audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
