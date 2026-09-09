#!/usr/bin/env python3
"""Final pre-push audit for 2026-07-27 cheat sheet."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-07-27"
PREV = "2026-07-26"
PREVIEW = ROOT / "preview" / "index.html"
ARCHIVE_PREV = ROOT / "preview" / "archive" / f"{PREV}.html"
BUM_MIN = 0.95

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def warn(msg: str) -> None:
    warns.append(msg)


def load_risk() -> dict[str, float]:
    path = ROOT / "data" / f"hr-targets-overall-{DATE}.csv"
    out: dict[str, float] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    # PropFinder quirky header: find pitcher rows after meta
    for row in rows:
        if len(row) < 5:
            continue
        # formats vary; try common layout after import via sheet_data
        pass
    from sheet_data import load_pitcher_risk

    risk = load_pitcher_risk(path)
    return {k: float(v["overall"]) for k, v in risk.items()}


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")
    arch = ARCHIVE_PREV.read_text(encoding="utf-8") if ARCHIVE_PREV.exists() else ""

    # --- Date ---
    if f'content="{DATE}"' not in html:
        fail(f"sheet-date meta missing {DATE}")
    if "Monday, July 27, 2026" not in html:
        fail("hero date must be Monday, July 27, 2026")
    if re.search(r"(Sunday|Saturday|Friday), July 2[67], 2026", html):
        fail("stale weekday/date still in hero")
    if "July 26, 2026 — current slate" in html:
        fail("manifest still labels 7/26 as current")
    if "July 27, 2026 — current slate" not in html:
        fail("manifest missing July 27 current slate label")

    # --- Counts ---
    m = re.search(r"(\d+) listed HR props", html)
    if not m or int(m.group(1)) != 53:
        fail(f"expected 53 props, got {m.group(0) if m else None}")
    games = re.findall(r'title:\s*"([^"]+)"', html)
    # games block titles
    game_titles = re.findall(r'title:\s*"((?:SEA|ARI|BAL|PHI|TOR|ATL|CLE|NYY|CHC|HOU|BOS|MIL) @ [^"]+)"', html)
    if len(game_titles) != 12:
        # fallback: count game objects in const games
        block = re.search(r"const games = \[(.*?)\];", html, re.S)
        if not block:
            fail("games block missing")
        else:
            titles = re.findall(r'title:\s*"([^"]+)"', block.group(1))
            if len(titles) != 12:
                fail(f"expected 12 games, got {len(titles)}")
            game_titles = titles

    # --- Favorites / gems ---
    favs = [
        "Joc Pederson",
        "Esmerlyn Valdez",
        "Bryce Harper",
        "Riley Greene",
        "James Wood",
        "Luis Garcia Jr.",
        "Yohendrick Pinango",
        "Austin Riley",
        "JJ Bleday",
        "Tyler Stephenson",
        "Chase DeLauter",
        "Willson Contreras",
        "Rafael Devers",
        "Andrew Vaughn",
    ]
    gems = ["Patrick Bailey", "Nelson Velazquez"]
    for name in favs:
        m = re.search(rf'name:\s*"{re.escape(name)}[^"]*".{{0,160}}emojis:\s*"([^"]*)"', html)
        if not m:
            fail(f"missing favorite row {name}")
        elif "⭐" not in m.group(1):
            fail(f"{name} missing ⭐ emoji (got {m.group(1)})")
    for name in gems:
        m = re.search(rf'name:\s*"{re.escape(name)}[^"]*".{{0,160}}emojis:\s*"([^"]*)"', html)
        if not m:
            fail(f"missing gem row {name}")
        elif "💎" not in m.group(1):
            fail(f"{name} missing 💎 emoji (got {m.group(1)})")

    # --- Bums ---
    from sheet_data import load_pitcher_risk, resolve_pitcher

    risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    expected_bums = []
    for name, row in risk.items():
        if row["overall"] >= BUM_MIN:
            expected_bums.append((name, row["overall"]))
    if not expected_bums:
        warn("no bums >= 0.95 — unexpected for this slate (Scherzer should qualify)")
    for name, overall in expected_bums:
        last = name.split()[-1]
        if f"{name} 🧤" not in html and f"{last} 🧤" not in html:
            fail(f"bum {name} ({overall:.2f}) missing 🧤 in titles")
        # rows vs that SP should get glove chip emojis somewhere
        if html.count("🧤") < 2:
            fail("too few 🧤 markers on sheet")

    # Scherzer specifically
    if "Max Scherzer 🧤" not in html:
        fail("Max Scherzer must have 🧤 in game title")

    # --- Park % + splits in every game description ---
    block = re.search(r"const games = \[(.*?)\];", html, re.S)
    if not block:
        fail("const games missing")
    else:
        games_js = block.group(1)
        titles = re.findall(r'title:\s*"([^"]+)"', games_js)
        descs = re.findall(r'description:\s*"([^"]*)"', games_js)
        if len(titles) != len(descs):
            fail(f"title/desc count mismatch {len(titles)}/{len(descs)}")
        for title, desc in zip(titles, descs):
            if "Park boost" not in desc and "Park" not in desc:
                fail(f"{title}: missing park boost in description")
            if "HR risk" not in desc:
                fail(f"{title}: missing HR risk in description")
            if "vs LHB" not in desc or "vs RHB" not in desc:
                fail(f"{title}: missing pitcher splits in description")
            # LHB/RHB hand park on rows
            gkey = title.split(" - ")[0]
            # at least one row in game should carry parkLhb/parkRhb after enrich — check in emitted JS
        park_l = games_js.count("parkLhbPct:") + games_js.count("park_lhb_pct")
        park_r = games_js.count("parkRhbPct:") + games_js.count("park_rhb_pct")
        # enrich uses parkLhbPct / parkRhbPct or similar — inspect
        if "parkLhb" not in games_js and "lhbPark" not in games_js and "park_lhb" not in games_js:
            # check alternate keys used by emit_games_js
            if "handParkPct" not in games_js and "parkPct" not in games_js:
                warn("hand/park pct fields not found in games JS (may be server-only enrich)")

    # Check enriched park fields more carefully
    if "zoneScore:" not in html:
        fail("zoneScore missing from games")
    zone_n = html.count("zoneScore:")
    if zone_n < 45:
        fail(f"zone coverage low: {zone_n}")

    # --- Feature parity vs yesterday archive ---
    features = [
        ("Homerun Form", "Homerun Form"),
        ("Damage Window", "Damage Window"),
        ("Straights of the Day", "Worst Pickz Straights of the Day"),
        ("Goblin Insight", "Goblin's Insight"),
        ("3 Leg Homerun", "3 Leg Homerun"),
        ("2 Leg Homerun", "2 Leg Homerun"),
        ("Favorite 3 Leg", "Favorite 3 Leg"),
        ("Top 5 HR", "Top 5 HR"),
        ("Weather Heavy", "Weather"),
        ("Longshots", "Longshot"),
        ("Hits parlay", "Hits"),
        ("Research tab", "MLB Research"),
        ("theme toggle", "theme-toggle"),
        ("Gambly", "Gambly"),
        ("Pikkit", "Pikkit"),
        ("Hidden Gem UI", "worst-pickz-gem"),
        ("straight streak", "straight-streak"),
        ("startTime", "startTime:"),
        ("formTrend or blast", "blast:"),
    ]
    for label, needle in features:
        if needle not in html:
            fail(f"feature missing on 7/27: {label} ({needle})")
        if arch and needle not in arch and label not in {"Hidden Gem UI"}:
            warn(f"feature {label} also missing on 7/26 archive (maybe rename)")

    # Straights present and not yesterday's
    if "James Wood" not in html or "Esmerlyn Valdez" not in html:
        fail("straights heroes missing expected names")
    if "Derek Hill - Over 0.5" in html:
        fail("stale 7/26 O0.5 straight still present")

    # Keller matchup present for ARI props
    for name in ["Corbin Carroll", "Ketel Marte", "Ryan Waldschmidt"]:
        m = re.search(rf'name:\s*"{re.escape(name)}[^"]*".{{0,400}}chips:\s*\["vs ([^\"]+)"\]', html, re.S)
        if not m:
            fail(f"{name} missing from sheet")
        elif m.group(1) != "Keller":
            fail(f"{name} should be vs Keller, got {m.group(1)}")

    # Research JSON
    research = ROOT / "preview" / "data" / f"research-{DATE}.json"
    park = ROOT / "preview" / "data" / f"park-factors-{DATE}.json"
    if not research.exists():
        fail("research JSON missing")
    else:
        data = json.loads(research.read_text(encoding="utf-8"))
        gcount = len(data.get("games") or data.get("slate") or [])
        if gcount < 12:
            # structure varies
            if isinstance(data, dict) and "games" in data and len(data["games"]) < 12:
                fail(f"research games {len(data['games'])} < 12")
    if not park.exists():
        fail("park-factors JSON missing")
    else:
        pdata = json.loads(park.read_text(encoding="utf-8"))
        if pdata.get("source") not in (None, "ballpark-pal") and "ballpark" not in str(pdata.get("source", "")).lower():
            # accept various
            if "ballpark-pal" not in json.dumps(pdata):
                warn(f"park factors source={pdata.get('source')}")

    # Manifest archive 7/26 exists
    if not ARCHIVE_PREV.exists():
        fail("7/26 archive missing")
    if f'content="{PREV}"' not in arch:
        fail("7/26 archive has wrong sheet-date")

    print("=== AUDIT 2026-07-27 ===")
    print(f"bums expected: {sorted(expected_bums, key=lambda x: -x[1])}")
    print(f"zoneScore fields: {zone_n}")
    print(f"game titles: {len(game_titles)}")
    if warns:
        print("WARNINGS:")
        for w in warns:
            print(" ", w)
    if errs:
        print("ERRORS:")
        for e in errs:
            print(" ", e)
        return 1
    print("OK all audit checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
