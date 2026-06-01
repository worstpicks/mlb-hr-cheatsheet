#!/usr/bin/env python3
"""Patch preview sheet to 2026-06-01. Does not commit or push."""
from __future__ import annotations

import csv
import importlib.util
import json
import re
import shutil
from pathlib import Path

from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0531 = ROOT / "preview" / "archive" / "2026-05-31.html"
GAMES_BLOCK = (ROOT / "_games-0601.txt").read_text(encoding="utf-8-sig").strip()

SHEET_DATE = "2026-06-01"

spec = importlib.util.spec_from_file_location("build0601", ROOT / "build-sheet-2026-06-01.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

TOTAL_GAMES = len(build.games)
TOTAL_ROWS = sum(len(g["rows"]) for g in build.games)
TOTAL_FAVS = len(build.FAVS)
FAVS = sorted(build.FAVS)

PITCHER_RISK = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{SHEET_DATE}.csv")


def data_attr(lines):
    return json.dumps(lines).replace('"', "&quot;")


def parse_odds_value(odds_text: str) -> int | None:
    m = re.search(r"Listed ([+-]\d+)", odds_text)
    return int(m.group(1)) if m else None


def note_hr_count(note: str) -> int:
    m = re.search(r"(\d+)\s+HR", note)
    return int(m.group(1)) if m else 0


def collect_rows():
    rows = []
    for g in build.games:
        game_key = g["title"].split(" - ")[0]
        park_m = re.search(r"HR environment\s*([+-]?\d+)%", g["description"])
        park_pct = int(park_m.group(1)) if park_m else 0
        for r in g["rows"]:
            chip = r["chips"][0].replace("vs ", "")
            hand = r["name"].split("(")[-1].rstrip(")")
            risk_row = resolve_pitcher(PITCHER_RISK, chip)
            if risk_row:
                split = risk_row["vs_lhb"] if hand == "L" else risk_row["vs_rhb"]
                risk = risk_row["overall"]
            else:
                split = 0.0
                risk = 0.0
            rank = r["score"] + split * 8.0 + risk * 4.0 + park_pct * 0.20
            rows.append(
                {
                    "game_key": game_key,
                    "name": r["name"],
                    "name_plain": r["name"].rsplit(" (", 1)[0],
                    "odds": r["odds"],
                    "odds_value": parse_odds_value(r["odds"]),
                    "score": r["score"],
                    "chip": chip,
                    "note": r["note"],
                    "hr": note_hr_count(r["note"]),
                    "split": split,
                    "risk": risk,
                    "park_pct": park_pct,
                    "rank": rank,
                }
            )
    rows.sort(key=lambda x: (x["rank"], x["score"], x["odds_value"] or -9999), reverse=True)
    return rows


def load_pitchers_to_attack():
    out = [
        {
            "pitcher": row["pitcher"],
            "risk": row["overall"],
            "vs_lhb": f"{row['vs_lhb']:+.2f}",
            "vs_rhb": f"{row['vs_rhb']:+.2f}",
        }
        for row in PITCHER_RISK.values()
    ]
    out.sort(key=lambda x: x["risk"], reverse=True)
    return out[:5]


def load_weather_rows():
    path = ROOT / "data" / f"ParkFactors_{SHEET_DATE}.csv"
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            game = " ".join(row["Game"].replace("  ", " ").split())
            try:
                hr_pct = int(row["HR %"].replace("%", ""))
            except ValueError:
                continue
            rows.append(
                {
                    "game": game,
                    "venue": row["Venue"],
                    "hr_pct": hr_pct,
                    "hr_pct_text": row["HR %"],
                    "hr_stadium": row["HR % Stadium"],
                    "hr_weather": row["HR % Weather"],
                }
            )
    return rows


rows = collect_rows()
listed_rows = [r for r in rows if r["odds_value"] is not None]
if not listed_rows:
    listed_rows = rows

# Guard rails for "best pick" quality: avoid low-score outliers.
straight_pool = [r for r in listed_rows if r["score"] >= 88 and r["hr"] >= 1 and r["split"] >= -0.10]
if not straight_pool:
    straight_pool = listed_rows

straight_o05 = straight_pool[0]
o15_pool = [
    r
    for r in straight_pool
    if r["name"] != straight_o05["name"] and r["hr"] >= 2 and r["score"] >= 85 and r["split"] >= -0.05
]
if not o15_pool:
    o15_pool = [r for r in straight_pool if r["name"] != straight_o05["name"] and r["score"] >= 90]
straight_o15 = o15_pool[0] if o15_pool else (straight_pool[1] if len(straight_pool) > 1 else straight_pool[0])

top3, seen = [], set()
for r in listed_rows:
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    top3.append(r)
    if len(top3) == 3:
        break

fav_rows = [r for r in rows if r["name"] in FAVS and r["name"] not in {x["name"] for x in top3}]
fav3, seen = [], set()
for r in fav_rows:
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    fav3.append(r)
    if len(fav3) == 3:
        break

top5, seen = [], set()
for r in rows:
    if r["name"] in seen:
        continue
    seen.add(r["name"])
    top5.append(r)
    if len(top5) == 5:
        break

longshots = [r for r in listed_rows if (r["odds_value"] or 0) >= 700][:4]
if len(longshots) < 4:
    extra = [r for r in listed_rows if r not in longshots]
    longshots.extend(extra[: 4 - len(longshots)])

weather_rows = load_weather_rows()
weather_top = sorted(weather_rows, key=lambda x: x["hr_pct"], reverse=True)[:5]
weather_fades = sorted(weather_rows, key=lambda x: x["hr_pct"])[:4]

THREE_LEG_HR = [f"{r['name_plain']} - Over 0.5 homerun" for r in top3]
FAV_THREE_LEG = [f"{r['name_plain']} - Over 0.5 homerun" for r in fav3]
STRAIGHT_OF_DAY = f"{straight_o05['name_plain']} - Over 0.5 homerun"
STRAIGHT_O15_DAY = f"{straight_o15['name_plain']} - Over 1.5 homeruns"
TWO_LEG_HR = [
    f"{straight_o05['name_plain']} - Over 0.5 homerun",
    f"{straight_o15['name_plain']} - Over 0.5 homerun",
]

pitchers_attack = load_pitchers_to_attack()

FAV_SET = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f"                {json.dumps(name)}" for name in FAVS)
    + "\n            ]);"
)

STRAIGHT_OF_DAY_CARD = f"""                <div class="summary-card full-width straight-of-day-card">
                    <h3>Worst Pickz Straights of the Day</h3>
                    <p class="model-note summary-note">Best tail/fade edges from current CSVs: power form + pitcher split + run environment.</p>
                    <div class="straight-picks-grid">
                        <div class="straight-pick-hero">
                            <span class="straight-pick-tag">Over 0.5 HR Straight</span>
                            <div class="straight-pick-header">
                                <strong class="straight-pick-name">{straight_o05['name_plain']} &mdash; vs {straight_o05['chip']}</strong>
                                <span class="straight-pick-meta">{straight_o05['odds']} &middot; Score {straight_o05['score']} &middot; {straight_o05['game_key']}</span>
                            </div>
                            <ul class="straight-pick-factors">
                                <li><strong>Primary edge</strong><small>Opposing split {straight_o05['split']:+.2f} with park impact {straight_o05['park_pct']}%.</small></li>
                                <li><strong>Form check</strong><small>{straight_o05['note']}</small></li>
                            </ul>
                            <div class="straight-pick-actions">
                                <button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([STRAIGHT_OF_DAY])}'>Add O0.5 Straight to Gambly</button>
                            </div>
                        </div>
                        <div class="straight-pick-hero straight-pick-hero--o15">
                            <span class="straight-pick-tag">Over 1.5 HR Straight</span>
                            <div class="straight-pick-header">
                                <strong class="straight-pick-name">{straight_o15['name_plain']} &mdash; vs {straight_o15['chip']}</strong>
                                <span class="straight-pick-meta">{straight_o15['odds']} &middot; Score {straight_o15['score']} &middot; {straight_o15['game_key']}</span>
                            </div>
                            <ul class="straight-pick-factors">
                                <li><strong>Primary edge</strong><small>Needs multi-HR upside: split {straight_o15['split']:+.2f}, park {straight_o15['park_pct']}%.</small></li>
                                <li><strong>Form check</strong><small>{straight_o15['note']}</small></li>
                            </ul>
                            <div class="straight-pick-actions">
                                <button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([STRAIGHT_O15_DAY])}'>Add O1.5 Straight to Gambly</button>
                            </div>
                        </div>
                    </div>
                </div>"""

GOBLIN_CARD = f"""                <div class="summary-card full-width best-bets-card">
                    <h3>Goblin's Insight</h3>
                    <p class="model-note summary-note">Neutral slate view: strongest tail reasons first; fade risk is the opposing split/park profile shown in each bullet.</p>
                    <div class="best-bets-grid">
                        <div class="best-bets-group">
                            <h4>3 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>{top3[0]['name_plain']} HR</strong><small>{top3[0]['note']} Split {top3[0]['split']:+.2f}; park {top3[0]['park_pct']}%.</small></li>
                                <li><strong>{top3[1]['name_plain']} HR</strong><small>{top3[1]['note']} Split {top3[1]['split']:+.2f}; park {top3[1]['park_pct']}%.</small></li>
                                <li><strong>{top3[2]['name_plain']} HR</strong><small>{top3[2]['note']} Split {top3[2]['split']:+.2f}; park {top3[2]['park_pct']}%.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(THREE_LEG_HR)}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>{straight_o05['name_plain']} HR</strong><small>{straight_o05['note']}</small></li>
                                <li><strong>{straight_o15['name_plain']} HR</strong><small>{straight_o15['note']}</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(TWO_LEG_HR)}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>{", ".join(r['name_plain'] for r in top5[:3])}</strong><small>Highest combined rank from score/split/park.</small></li>
                                <li><strong>{", ".join(r['name_plain'] for r in top5[3:5])}</strong><small>Next best balance of form and matchup.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([f"{r['name_plain']} - Over 0.5 hits" for r in top5])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>{fav3[0]['name_plain']} HR &#11088; &#127765;</strong><small>{fav3[0]['note']}</small></li>
                                <li><strong>{fav3[1]['name_plain']} HR &#11088; &#127765;</strong><small>{fav3[1]['note']}</small></li>
                                <li><strong>{fav3[2]['name_plain']} HR &#11088; &#127765;</strong><small>{fav3[2]['note']}</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(FAV_THREE_LEG)}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                {''.join(f"<li><strong>{p['pitcher']}</strong><small>HR risk {p['risk']:.2f}; vs LHB {p['vs_lhb']}, vs RHB {p['vs_rhb']}.</small></li>" for p in pitchers_attack)}
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranked by model score, opposing split leakage, and park context.</p>
                    <div class="top-five-list">
""" + "\n".join(
    f'                        <div class="top-five-item"><span>{r["name_plain"]} <small>vs {r["chip"]} • split {r["split"]:+.2f} • park {r["park_pct"]}%</small></span><strong>{r["score"]}</strong></div>'
    for r in top5
) + """
                    </div>
                </div>"""

PARK_INNER = "\n".join(
    f'                        <div class="summary-item"><span>{w["game"]} <small>{w["venue"]} (stadium {w["hr_stadium"]}, weather {w["hr_weather"]})</small></span><strong>{w["hr_pct_text"]}</strong></div>'
    for w in weather_top
)
WEATHER5_INNER = "\n".join(
    f'                        <div class="summary-item"><span>#{i+1} {r["name_plain"]} <small>{r["game_key"]} vs {r["chip"]}</small></span><strong>{r["score"]}</strong></div>'
    for i, r in enumerate(top5)
)
LONGSHOT_INNER = "\n".join(
    f'                        <div class="summary-item"><span>{r["name_plain"]} <small>{r["odds"]} vs {r["chip"]}</small></span><strong>{r["score"]}</strong></div>'
    for r in longshots
)
FADES_INNER = "\n".join(
    f'                        <div class="summary-item"><span>{w["game"]} <small>{w["venue"]} lower HR carry</small></span><strong>{w["hr_pct_text"]}</strong></div>'
    for w in weather_fades
)

SUMMARY_BLOCK = (
    STRAIGHT_OF_DAY_CARD
    + "\n"
    + GOBLIN_CARD
    + "\n"
    + TOP_CARD
    + """
                <div class="summary-card">
                    <h3>Top 5 Weather Games</h3>
                    <div class="summary-list">"""
    + PARK_INNER
    + """
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Top 5 Weather Heavy HR Plays</h3>
                    <div class="summary-list">"""
    + WEATHER5_INNER
    + """
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Best longshot HR (listed +700+)</h3>
                    <div class="summary-list">"""
    + LONGSHOT_INNER
    + """
                    </div>
                </div>
                <div class="summary-card">
                    <h3>Harsh Environment Fades</h3>
                    <div class="summary-list">"""
    + FADES_INNER
    + """
                    </div>
                </div>
"""
)


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "June 1, 2026 — current slate", "href": "index.html"},
        {"date": "2026-05-31", "label": "May 31, 2026", "href": "archive/2026-05-31.html"},
        {"date": "2026-05-30", "label": "May 30, 2026", "href": "archive/2026-05-30.html"},
        {"date": "2026-05-29", "label": "May 29, 2026", "href": "archive/2026-05-29.html"},
        {"date": "2026-05-28", "label": "May 28, 2026", "href": "archive/2026-05-28.html"},
        {"date": "2026-05-27", "label": "May 27, 2026", "href": "archive/2026-05-27.html"},
        {"date": "2026-05-25", "label": "May 25, 2026", "href": "archive/2026-05-25.html"},
        {"date": "2026-05-21", "label": "May 21, 2026", "href": "archive/2026-05-21.html"},
    ]
    for date in ["2026-05-20", "2026-05-19", "2026-05-18", "2026-05-16", "2026-05-15", "2026-05-14"]:
        if date in old:
            ordered.append(old[date])
    payload = {"version": 1, "sheets": ordered}
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def manifest_fallback(manifest):
    return (
        '<script type="application/json" id="sheets-manifest-fallback">'
        + json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
        + "</script>"
    )


def patch_preview(manifest):
    text = PREVIEW.read_text(encoding="utf-8")
    games_pat = r"const games = \[.*?\];"
    if re.search(games_pat, text, flags=re.DOTALL):
        text = re.sub(games_pat, lambda _: GAMES_BLOCK, text, count=1, flags=re.DOTALL)
    else:
        insert_pat = r'\(\(\) => \{\s*\n\s*const grid = document\.getElementById\("gamesGrid"\);'
        insert_repl = "(() => {\n" + GAMES_BLOCK + '\n\n            const grid = document.getElementById("gamesGrid");'
        text, n = re.subn(insert_pat, insert_repl, text, count=1)
        if n != 1:
            raise SystemExit("Could not insert games block")

    text = re.sub(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);", FAV_SET, text, count=1)
    text = re.sub(r'<meta name="sheet-date" content="[^"]*">', f'<meta name="sheet-date" content="{SHEET_DATE}">', text, count=1)
    text = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        lambda _m: manifest_fallback(manifest),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p>(?:Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday), \w+ \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Monday, June 1, 2026 — Worst Pickz HR cheat sheet",
        text,
        count=1,
    )

    count_sentence = (
        f"This board covers <strong>{TOTAL_ROWS} listed HR props</strong> across "
        f"<strong>{TOTAL_GAMES} games</strong>, with <strong>{TOTAL_FAVS} Worst Pickz Favorite</strong> rows (&#11088;)."
    )
    text, count = re.subn(
        r"This board covers <strong>.*?</strong> across <strong>.*?</strong>, with <strong>.*?</strong> rows \((?:&#11088;|⭐)\)\.",
        count_sentence,
        text,
        count=1,
    )
    if count == 0:
        text = text.replace(
            'PropFinder Weather</a>. Designated <strong>Worst Pickz Favorites</strong>',
            f'PropFinder Weather</a>. {count_sentence} Designated <strong>Worst Pickz Favorites</strong>',
            1,
        )

    start_m = re.search(r'\s*<div class="summary-card full-width straight-of-day-card">', text)
    end_m = re.search(r'<div class="summary-card emoji-key-card">', text)
    if not start_m or not end_m or end_m.start() <= start_m.start():
        raise SystemExit("Could not locate summary block anchors")
    text = text[: start_m.start()] + SUMMARY_BLOCK + text[end_m.start() :]

    PREVIEW.write_text(text, encoding="utf-8")
    print("patched", PREVIEW.relative_to(ROOT))


def sync_root_index():
    shutil.copy2(PREVIEW, ROOT / "index.html")
    print("synced root index.html")


def main():
    ARCHIVE_0531.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PREVIEW, ARCHIVE_0531)
    print("archived current preview to", ARCHIVE_0531.relative_to(ROOT))
    manifest = update_manifest()
    patch_preview(manifest)
    sync_root_index()


if __name__ == "__main__":
    main()
