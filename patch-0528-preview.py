#!/usr/bin/env python3
"""Patch preview sheet to 2026-05-28. Does not commit or push."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0527 = ROOT / "preview" / "archive" / "2026-05-27.html"
GAMES_BLOCK = (ROOT / "_games-0528.txt").read_text(encoding="utf-8-sig").strip()

SHEET_DATE = "2026-05-28"
TOTAL_GAMES = 6
TOTAL_ROWS = 35
TOTAL_FAVS = 7

FAVS = [
    "Wilyer Abreu (L)",
    "Pete Alonso (R)",
    "Yohendrick Pinango (L)",
    "Brandon Lowe (L)",
    "Spencer Horwitz (L)",
    "Brandon Nimmo (L)",
    "Yordan Alvarez (L)",
]

FAV_SET = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f"                {json.dumps(name)}" for name in FAVS)
    + "\n            ]);"
)


def data_attr(lines):
    return json.dumps(lines).replace('"', "&quot;")


HRRBI_PLAY = [
    "Brandon Lowe - Over 1.5 hits + runs + RBIs",
    "Spencer Horwitz - Over 1.5 hits + runs + RBIs",
    "Oneil Cruz - Over 1.5 hits + runs + RBIs",
    "Coby Mayo - Over 1.5 hits + runs + RBIs",
    "Pete Alonso - Over 1.5 hits + runs + RBIs",
    "Brandon Nimmo - Over 1.5 hits + runs + RBIs",
    "Yordan Alvarez - Over 1.5 hits + runs + RBIs",
    "Marcell Ozuna - Over 1.5 hits + runs + RBIs",
]

THREE_LEG_HR = [
    "Brandon Lowe - Over 0.5 homerun",
    "Yordan Alvarez - Over 0.5 homerun",
    "Byron Buxton - Over 0.5 homerun",
]

FAV_THREE_LEG = [
    "Yohendrick Pinango - Over 0.5 homerun",
    "Pete Alonso - Over 0.5 homerun",
    "Brandon Nimmo - Over 0.5 homerun",
]


def _gambly_batter(line: str) -> str:
    return line.split(" - ", 1)[0].strip()


def assert_goblin_hr_parlays_distinct() -> None:
    three = {_gambly_batter(x) for x in THREE_LEG_HR}
    fav = {_gambly_batter(x) for x in FAV_THREE_LEG}
    overlap = three & fav
    if overlap:
        raise SystemExit(f"3 Leg HR and Favorite 3 Leg share batters: {sorted(overlap)}")


assert_goblin_hr_parlays_distinct()


GOBLIN_CARD = f"""                <div class="summary-card full-width best-bets-card">
                    <h3>Goblin's Insight</h3>
                    <p class="model-note summary-note">Full-slate view built from weather, pitcher HR risk, current power form, and batter-vs-pitcher history.</p>
                    <div class="best-bets-grid">
                        <div class="best-bets-group">
                            <h4>3 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Brandon Lowe HR</strong><small>Colin Rea is the slate's top HR-risk arm; Lowe has 3 HR, 38.5% barrels, and 98.3 mph EV in the window.</small></li>
                                <li><strong>Yordan Alvarez HR</strong><small>Nathan Eovaldi LHB HR risk plus BvP HR history at the dome.</small></li>
                                <li><strong>Byron Buxton HR</strong><small>3 HR, 3 near-HR, and 95.1 mph EV versus Davis Martin's RHB split.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(THREE_LEG_HR)}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Coby Mayo HR</strong><small>Patrick Corbin RHB HR leakage with 2 HR and 93.1 mph EV at Camden.</small></li>
                                <li><strong>Yohendrick Pinango HR</strong><small>105.4 mph EV and 40.0% barrels versus Chris Bassitt.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Coby Mayo - Over 0.5 homerun", "Yohendrick Pinango - Over 0.5 homerun"])}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>Lowe, Horwitz, Cruz, Mayo, Alonso, Pinango</strong><small>Top attack-pitcher lanes versus Rea and Corbin.</small></li>
                                <li><strong>Alvarez, Nimmo, Buxton, Vargas, Neto, Olson</strong><small>Hot hitters versus Eovaldi, Arrighetti, Martin, Bradley, Rodriguez, and Tolle.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Brandon Lowe - Over 0.5 hits", "Spencer Horwitz - Over 0.5 hits", "Oneil Cruz - Over 0.5 hits", "Coby Mayo - Over 0.5 hits", "Pete Alonso - Over 0.5 hits", "Yohendrick Pinango - Over 0.5 hits", "Yordan Alvarez - Over 0.5 hits", "Brandon Nimmo - Over 0.5 hits", "Byron Buxton - Over 0.5 hits", "Miguel Vargas - Over 0.5 hits", "Zach Neto - Over 0.5 hits", "Matt Olson - Over 0.5 hits"])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Hits + Runs + RBI Play</h4>
                            <ul>
                                <li><strong>Lowe, Horwitz, Cruz, Ozuna</strong><small>Top contact versus Colin Rea — slate #1 pitcher to attack.</small></li>
                                <li><strong>Mayo, Alonso, Nimmo, Alvarez</strong><small>Run/RBI upside versus Corbin, Arrighetti, and Eovaldi.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(HRRBI_PLAY)}'>Add 2 Hits + Runs + RBI to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>Yohendrick Pinango HR &#11088; &#127765;</strong><small>Worst Pickz Favorite moonshot with slate-best 105.4 mph EV versus Bassitt.</small></li>
                                <li><strong>Pete Alonso HR &#11088; &#127765;</strong><small>Worst Pickz Favorite moonshot versus Corbin RHB HR leakage.</small></li>
                                <li><strong>Brandon Nimmo HR &#11088; &#127765;</strong><small>Worst Pickz Favorite moonshot with 2 HR versus Spencer Arrighetti.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(FAV_THREE_LEG)}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                <li><strong>Colin Rea</strong><small>Slate-high HR risk (1.21); 1.70 vs-RHB split — Pirates righties and lefties both live.</small></li>
                                <li><strong>Jack Flaherty</strong><small>0.98 HR risk with 0.92 vs-RHB split; Tigers face the cleaner LAA attack lane.</small></li>
                                <li><strong>Nathan Eovaldi</strong><small>0.80 HR risk; Alvarez is the Houston anchor versus Eovaldi LHB leakage.</small></li>
                                <li><strong>Grayson Rodriguez</strong><small>0.62 HR risk with 1.58 vs-LHB split; Angels righties fit the Comerica lane.</small></li>
                                <li><strong>Patrick Corbin</strong><small>0.27 vs-RHB HR risk; Mayo and Alonso are the Oriole righty anchors.</small></li>
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage, opposing starter HR leakage, park/weather, and listed price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Brandon Lowe <small>3 HR, Rea HR risk, 38.5% barrels</small></span><strong>96</strong></div>
                        <div class="top-five-item"><span>Yohendrick Pinango <small>105.4 mph EV, 40.0% barrels vs Bassitt</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Yordan Alvarez <small>1 HR, Eovaldi LHB risk, BvP HR</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Byron Buxton <small>3 HR, 95.1 mph EV vs Martin</small></span><strong>90</strong></div>
                        <div class="top-five-item"><span>Brandon Nimmo <small>2 HR vs Arrighetti, 92.2 mph EV</small></span><strong>88</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>MIN @ CWS <small>Rate Field -3% HR, -1% combined, 64°F high pressure</small></span><strong>-1%</strong></div>
                        <div class="summary-item"><span>CHC @ PIT <small>PNC -18% HR but +7% 2B/3B row, cooling air</small></span><strong>-3% runs</strong></div>
                        <div class="summary-item"><span>ATL @ BOS <small>Fenway -18% HR, in-blowing 6 mph wind</small></span><strong>-4% runs</strong></div>
                        <div class="summary-item"><span>LAA @ DET <small>Comerica -13% HR, 15 mph L-R, 1022 mb pressure</small></span><strong>-5%</strong></div>
                        <div class="summary-item"><span>TOR @ BAL <small>Oriole Park -22% HR, slate-worst HR row</small></span><strong>-6%</strong></div>
                        <div class="summary-item"><span>HOU @ TEX <small>Globe Life -11% HR, roof closed</small></span><strong>-7%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Brandon Lowe <small>Rea HR leakage despite PNC -18% drag</small></span><strong>96</strong></div>
                        <div class="summary-item"><span>#2 Yohendrick Pinango <small>105.4 mph EV versus Bassitt</small></span><strong>93</strong></div>
                        <div class="summary-item"><span>#3 Yordan Alvarez <small>Eovaldi LHB risk at the dome</small></span><strong>92</strong></div>
                        <div class="summary-item"><span>#4 Byron Buxton <small>3 HR versus Martin at Rate Field</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#5 Coby Mayo <small>Corbin RHB HR risk at Camden</small></span><strong>86</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Isiah Kiner-Falefa <small>+1700 versus Chris Sale</small></span><strong>63</strong></div>
                        <div class="summary-item"><span>Ernie Clement <small>+1220 with 1 HR versus Bassitt</small></span><strong>69</strong></div>
                        <div class="summary-item"><span>Vaughn Grissom <small>+1000 versus Rodriguez RHB split</small></span><strong>71</strong></div>
                        <div class="summary-item"><span>Spencer Horwitz <small>+870 with 2 HR versus Rea</small></span><strong>81</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>TOR @ BAL <small>Oriole Park -22% HR, slate-worst row</small></span><strong>-22%</strong></div>
                        <div class="summary-item"><span>ATL @ BOS <small>Fenway -18% HR, in-blowing wind</small></span><strong>-18%</strong></div>
                        <div class="summary-item"><span>CHC @ PIT <small>PNC -18% HR, cool evening air</small></span><strong>-18%</strong></div>
                        <div class="summary-item"><span>LAA @ DET <small>Comerica -13% HR, high pressure</small></span><strong>-13%</strong></div>
                    """

SUMMARY_BLOCK = (
    GOBLIN_CARD
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


def archive_relative_assets(text):
    text = text.replace('src="assets/', 'src="../assets/')
    text = text.replace('href="assets/', 'href="../assets/')
    return text


def ensure_archive():
    ARCHIVE_0527.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_0527.exists():
        text = PREVIEW.read_text(encoding="utf-8")
        ARCHIVE_0527.write_text(archive_relative_assets(text), encoding="utf-8")
        print("archived", ARCHIVE_0527.relative_to(ROOT))
    else:
        print("archive exists", ARCHIVE_0527.relative_to(ROOT))


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "May 28, 2026 — current slate", "href": "index.html"},
        {"date": "2026-05-27", "label": "May 27, 2026", "href": "archive/2026-05-27.html"},
        {"date": "2026-05-25", "label": "May 25, 2026", "href": "archive/2026-05-25.html"},
        {"date": "2026-05-21", "label": "May 21, 2026", "href": "archive/2026-05-21.html"},
        {"date": "2026-05-20", "label": "May 20, 2026", "href": "archive/2026-05-20.html"},
    ]
    for date in ["2026-05-19", "2026-05-18", "2026-05-16", "2026-05-15", "2026-05-14"]:
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
        text = re.sub(games_pat, GAMES_BLOCK, text, count=1, flags=re.DOTALL)
    else:
        insert_pat = r'\(\(\) => \{\s*\n\s*const grid = document\.getElementById\("gamesGrid"\);'
        insert_repl = "(() => {\n" + GAMES_BLOCK + '\n\n            const grid = document.getElementById("gamesGrid");'
        text, n = re.subn(insert_pat, insert_repl, text, count=1)
        if n != 1:
            raise SystemExit("Could not insert games block")
    text = re.sub(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);", FAV_SET, text, count=1)
    text = re.sub(r'<meta name="sheet-date" content="[^"]*">', f'<meta name="sheet-date" content="{SHEET_DATE}">', text, count=1)
    text = re.sub(r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>', lambda _m: manifest_fallback(manifest), text, count=1, flags=re.DOTALL)
    text = re.sub(
        r"<p>(?:Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday), May \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Thursday, May 28, 2026 — Worst Pickz HR cheat sheet",
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
    summary_pat = (
        r'<div class="summary-card full-width best-bets-card">[\s\S]*?'
        r'<div class="summary-card emoji-key-card">'
    )
    text = re.sub(
        summary_pat,
        SUMMARY_BLOCK + '\n                <div class="summary-card emoji-key-card">',
        text,
        count=1,
    )
    if "Brandon Lowe HR</strong><small>Colin Rea" not in text:
        start = text.index('<div class="summary-card full-width best-bets-card">')
        end = text.index('<div class="summary-card emoji-key-card">')
        text = text[:start] + SUMMARY_BLOCK + text[end:]
    assert_goblin_hr_parlays_distinct()
    PREVIEW.write_text(text, encoding="utf-8")
    print("patched", PREVIEW.relative_to(ROOT))


def main():
    # Always snapshot current preview before replacing slate.
    ARCHIVE_0527.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PREVIEW, ARCHIVE_0527)
    print("archived current preview to", ARCHIVE_0527.relative_to(ROOT))
    manifest = update_manifest()
    patch_preview(manifest)


if __name__ == "__main__":
    main()
