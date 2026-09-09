#!/usr/bin/env python3
"""Deep local audit for 2026-08-01 before push."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
ARCH = ROOT / "preview" / "archive" / "2026-07-31.html"
DATE = "2026-08-01"
BUM_MIN = 0.95

errs: list[str] = []


def fail(m: str) -> None:
    errs.append(m)


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")
    arch = ARCH.read_text(encoding="utf-8") if ARCH.exists() else ""

    if f'content="{DATE}"' not in html:
        fail("sheet-date meta wrong")
    if "Saturday, August 1, 2026" not in html:
        fail("hero must be Saturday, August 1, 2026")
    if "Friday, July 31, 2026 — Worst" in html:
        fail("stale Friday 7/31 hero still on current sheet")
    if "Friday, August 1" in html:
        fail("wrong weekday Friday on August 1 (must be Saturday)")
    if "August 1, 2026 — current slate" not in html:
        fail("manifest current slate not 8/1")
    if "July 31, 2026 — current slate" in html:
        fail("7/31 still labeled current")

    m = re.search(r"(\d+) listed HR props", html)
    if not m or int(m.group(1)) != 90:
        fail(f"prop count: {m.group(0) if m else None}")

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
    if len(titles) != 15 or len(metas) != 15:
        fail(f"expected 15 games/metas, got {len(titles)}/{len(metas)}")
    if len(parks) != 15 or len(lhb) != 15 or len(rhb) != 15:
        fail(f"park fields incomplete park={len(parks)} lhb={len(lhb)} rhb={len(rhb)}")
    if zones < 80:
        fail(f"zone coverage low: {zones}")
    if starts < 15:
        fail(f"startTime missing: {starts}")

    from sheet_data import load_pitcher_risk

    risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    bums = [(r["pitcher"], r["overall"]) for r in risk.values() if r["overall"] >= BUM_MIN]
    print("bums:", bums)
    if len(bums) < 3:
        fail(f"expected 3+ bums, got {bums}")
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
        print(f"  OK {gk}")

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
        "blast:",
        "parkLhbPct",
        "parkRhbPct",
        "zoneScore",
        "gameMeta:",
        "formTrend",
        "top3Detail",
        "sleeperDetail",
    ]
    missing_feat = [f for f in features if f not in html]
    if missing_feat:
        fail(f"missing features: {missing_feat}")
    if arch:
        regressed = [f for f in features if f in arch and f not in html]
        if regressed:
            fail(f"regressed vs 7/31: {regressed}")

    picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
    print("straights:", picks)
    if len(picks) < 2:
        fail(f"straights incomplete: {picks}")

    # Confirm O0.5 is top strict
    cut = (ROOT / "patch-0801-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
    g: dict = {"__file__": str(ROOT / "patch-0801-preview.py"), "__name__": "x"}
    exec(compile(cut + "\n", "patch-0801-preview.py", "exec"), g)
    o05, o15 = g["straight_o05"], g["straight_o15"]
    pool = g["straight_o05_pool"](g["straight_rows"], strict=True)
    print(f"O0.5 {o05['name_plain']} vs {o05['chip']} | O1.5 {o15['name_plain']} vs {o15['chip']}")
    print(f"top3 {[x['name_plain'] for x in g['top3']]}")
    print(f"two {[x['name_plain'] for x in g['two_leg']]}")
    print(f"fav3 {[x['name_plain'] for x in g['fav3']]}")
    if pool and pool[0]["name_plain"] != o05["name_plain"]:
        fail(f"O0.5 not top strict: sheet={o05['name_plain']} top={pool[0]['name_plain']}")
    if o05["game_key"] == o15["game_key"]:
        fail("O0.5 and O1.5 same game")

    for rel in (f"preview/data/research-{DATE}.json", f"preview/data/park-factors-{DATE}.json"):
        if not (ROOT / rel).exists():
            fail(f"missing {rel}")

    if not ARCH.exists() or 'content="2026-07-31"' not in arch:
        fail("7/31 archive missing/wrong")

    print("\n=== DEEP AUDIT ===")
    if errs:
        for e in errs:
            print("ERROR:", e)
        return 1
    print("OK all deep checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
