#!/usr/bin/env python3
"""Deep local audit: date, parks, splits, features, picks quality."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
ARCH = ROOT / "preview" / "archive" / "2026-07-30.html"
DATE = "2026-07-31"
BUM_MIN = 0.95

errs: list[str] = []
warns: list[str] = []


def fail(m: str) -> None:
    errs.append(m)


def warn(m: str) -> None:
    warns.append(m)


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")
    arch = ARCH.read_text(encoding="utf-8") if ARCH.exists() else ""

    # Date correctness
    if f'content="{DATE}"' not in html:
        fail("sheet-date meta wrong")
    if "Friday, July 31, 2026" not in html:
        fail("hero date/weekday wrong — must be Friday, July 31, 2026")
    # Hero line only (avoid archive labels)
    hero = re.search(
        r"<p>((?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday), [^<]+)</p>",
        html,
    )
    if not hero or "Friday, July 31, 2026" not in hero.group(1):
        fail(f"hero paragraph wrong: {hero.group(1) if hero else None}")
    if "July 31, 2026 — current slate" not in html:
        fail("manifest current slate not 7/31")
    if "July 30, 2026 — current slate" in html:
        fail("7/30 still current in manifest")

    # Props / games
    m = re.search(r"(\d+) listed HR props", html)
    if not m or int(m.group(1)) != 87:
        fail(f"prop count: {m.group(0) if m else None}")

    block = re.search(r"const games = \[(.*?)\n\];", html, re.S)
    if not block:
        fail("games block missing")
        print("FATAL"); return 1
    body = block.group(1)
    titles = re.findall(r'title:\s*"([^"]+)"', body)
    metas = re.findall(r'gameMeta:\s*"((?:\\.|[^"\\])*)"', body)
    parks = re.findall(r"parkPct:\s*(-?\d+)", body)
    lhb = re.findall(r"parkLhbPct:\s*(-?\d+)", body)
    rhb = re.findall(r"parkRhbPct:\s*(-?\d+)", body)
    zones = len(re.findall(r"zoneScore:\s*[\d.]+", body))
    starts = len(re.findall(r"startTime:", body))

    print(f"games={len(titles)} metas={len(metas)} parkPct={len(parks)} "
          f"LHB={len(lhb)} RHB={len(rhb)} zoneScore={zones} startTime={starts}")

    if len(titles) != 14:
        fail(f"expected 14 games, got {len(titles)}")
    if len(metas) != 14:
        fail(f"expected 14 gameMeta, got {len(metas)}")
    if len(parks) != 14 or len(lhb) != 14 or len(rhb) != 14:
        fail(f"park fields incomplete: park={len(parks)} lhb={len(lhb)} rhb={len(rhb)}")
    if zones < 80:
        fail(f"zone coverage low: {zones}")
    if starts < 14:
        fail(f"startTime missing on some games: {starts}")

    from sheet_data import load_pitcher_risk

    risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")
    bums = [(r["pitcher"], r["overall"]) for r in risk.values() if r["overall"] >= BUM_MIN]
    print("bums:", bums)
    for pname, overall in bums:
        if f"{pname} 🧤" not in html:
            fail(f"bum missing glove: {pname} ({overall})")

    for title, meta in zip(titles, metas):
        s = meta.encode().decode("unicode_escape")
        gk = title.split(" - ")[0]
        n = len(re.findall(r"pitcher-meta", s))
        if "Park" not in s:
            fail(f"{gk}: missing Park in gameMeta")
        if n != 2:
            fail(f"{gk}: expected 2 pitcher metas, got {n}")
        if "LHB" not in s or "RHB" not in s:
            fail(f"{gk}: missing LHB/RHB splits")
        print(f"  OK meta {gk}: park+splits+2SP")

    # Features vs yesterday
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
        "hhSignal",
        "gbSignal",
        "contactRisk",
        "top3Detail",
        "sleeperDetail",
    ]
    missing_feat = [f for f in features if f not in html]
    if missing_feat:
        fail(f"missing features: {missing_feat}")

    if arch:
        # features present yesterday that are gone today
        arch_feats = [f for f in features if f in arch and f not in html]
        if arch_feats:
            fail(f"regressed vs 7/30 archive: {arch_feats}")
        # spot-check UI shells
        for needle in ("Damage Window Stats", "Goblin", "Straights of the Day", "Research"):
            if needle in arch and needle not in html:
                fail(f"UI section missing vs archive: {needle}")

    # Picks
    picks = re.findall(r'class="straight-pick-name">([^<]+)', html)
    print("straights:", picks)
    if len(picks) < 2:
        fail(f"straights incomplete: {picks}")
    if "James Wood" not in picks[0] or "Willi Castro" not in picks[1]:
        warn(f"unexpected straight names: {picks}")

    # Goblin gambly
    lines = re.findall(r"data-goblin-gambly-lines='([^']+)'", html)
    parsed = []
    for raw in lines:
        s = raw.replace("&#39;", "'").replace("&quot;", '"')
        try:
            parsed.append(json.loads(s))
        except Exception:
            fail(f"bad gambly json: {raw[:80]}")
    print("gambly blocks:", len(parsed))
    for i, arr in enumerate(parsed):
        print(f"  [{i}] {arr}")

    # Stale prior-day names that must NOT be primary straights
    for stale in ("Willson Contreras", "Austin Riley — vs Irvin"):
        if stale in " ".join(picks):
            fail(f"stale straight carryover: {stale}")

    # Research / park JSON
    for rel in (f"preview/data/research-{DATE}.json", f"preview/data/park-factors-{DATE}.json"):
        p = ROOT / rel
        if not p.exists():
            fail(f"missing {rel}")
        else:
            data = json.loads(p.read_text(encoding="utf-8"))
            if "park" in rel and data.get("source") not in ("ballpark-pal", "Ballpark Pal", None):
                # accept ballpark-pal
                if data.get("source") != "ballpark-pal":
                    warn(f"park source: {data.get('source')}")

    park_json = json.loads((ROOT / f"preview/data/park-factors-{DATE}.json").read_text(encoding="utf-8"))
    print("park-factors source:", park_json.get("source"), "games:", len(park_json.get("games") or park_json.get("parks") or []))

    # Rank confirmation: Wood #1 O0.5 strict, Castro best O1.5 other-game
    cut = (ROOT / "patch-0731-preview.py").read_text(encoding="utf-8").split("THREE_LEG_HR =")[0]
    g: dict = {"__file__": str(ROOT / "patch-0731-preview.py"), "__name__": "x"}
    exec(compile(cut + "\n", "patch-0731-preview.py", "exec"), g)
    o05 = g["straight_o05"]
    o15 = g["straight_o15"]
    pool = g["straight_o05_pool"](g["straight_rows"], strict=True)
    if pool and pool[0]["name_plain"] != o05["name_plain"]:
        fail(f"O0.5 not top of strict pool: sheet={o05['name_plain']} top={pool[0]['name_plain']}")
    else:
        print(f"O0.5 confirmed top strict: {o05['name_plain']} vs {o05['chip']}")
    if o05["game_key"] == o15["game_key"]:
        fail("O0.5 and O1.5 same game")
    print(f"O1.5: {o15['name_plain']} vs {o15['chip']} ({o15['hr']}HR/{o15['near']}near) game={o15['game_key']}")

    # Favorite 3 must be favorites only
    fav_set = set(g["FAVS"])
    # parse favorite 3 from gambly — usually last HR 3-leg of stars
    fav3 = None
    for arr in parsed:
        if len(arr) == 3 and all("homerun" in x.lower() and "0.5" in x for x in arr):
            names = [x.split(" - ")[0] for x in arr]
            if all(any(n == f or n.startswith(f) for f in fav_set) for n in names):
                fav3 = names
    print("favorite3 detected:", fav3, "favs:", sorted(fav_set))

    print("\n=== DEEP AUDIT RESULT ===")
    for w in warns:
        print("WARN:", w)
    if errs:
        for e in errs:
            print("ERROR:", e)
        return 1
    print("OK all deep checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
