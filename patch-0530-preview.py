#!/usr/bin/env python3
"""Patch preview sheet to 2026-05-30. Does not commit or push."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0529 = ROOT / "preview" / "archive" / "2026-05-29.html"
GAMES_BLOCK = (ROOT / "_games-0530.txt").read_text(encoding="utf-8-sig").strip()

SHEET_DATE = "2026-05-30"
TOTAL_GAMES = 15
TOTAL_ROWS = 78
TOTAL_FAVS = 19

FAVS = [
    "Alec Burleson (L)",
    "Brandon Lowe (L)",
    "Brandon Nimmo (L)",
    "Bryce Harper (L)",
    "Dillon Dingler (R)",
    "Garrett Mitchell (L)",
    "Ian Happ (S)",
    "Jackson Chourio (R)",
    "Jac Caglianone (L)",
    "James Wood (L)",
    "Jesus Sanchez (L)",
    "Jordan Walker (R)",
    "Ketel Marte (S)",
    "Kyle Schwarber (L)",
    "Luke Raley (L)",
    "Randal Grichuk (R)",
    "Trea Turner (R)",
    "Willy Adames (R)",
    "Yordan Alvarez (L)",
]

FAV_SET = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f"                {json.dumps(name)}" for name in FAVS)
    + "\n            ]);"
)


def data_attr(lines):
    return json.dumps(lines).replace('"', "&quot;")


THREE_LEG_HR = [
    "Pete Alonso - Over 0.5 homerun",
    "Brandon Lowe - Over 0.5 homerun",
    "Byron Buxton - Over 0.5 homerun",
]

FAV_THREE_LEG = [
    "Kyle Schwarber - Over 0.5 homerun",
    "Willy Adames - Over 0.5 homerun",
    "Jordan Walker - Over 0.5 homerun",
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

STRAIGHT_OF_DAY = "Pete Alonso - Over 0.5 homerun"
STRAIGHT_O15_DAY = "Kyle Schwarber - Over 1.5 homeruns"

TWO_LEG_HR = [
    "Kyle Schwarber - Over 0.5 homerun",
    "Pete Alonso - Over 0.5 homerun",
]

STRAIGHT_OF_DAY_CARD = f"""                <div class="summary-card full-width straight-of-day-card">
                    <h3>Worst Pickz Straights of the Day</h3>
                    <p class="model-note summary-note">Our highest-rated HR straight picks on the slate.</p>
                    <div class="straight-picks-grid">
                        <div class="straight-pick-hero">
                            <span class="straight-pick-tag">Over 0.5 HR Straight</span>
                            <div class="straight-pick-header">
                                <strong class="straight-pick-name">Pete Alonso &mdash; vs Trey Yesavage</strong>
                                <span class="straight-pick-meta">Listed +410 &middot; Score 98 &middot; TOR @ BAL</span>
                            </div>
                            <ul class="straight-pick-factors">
                                <li><strong>Recent form</strong><small><strong>3 HR, 3 near-HR</strong>, 97.8 mph EV, 20.0% barrels on the slate.</small></li>
                                <li><strong>Matchup</strong><small>Yesavage is a rookie righty with limited HR suppression in the CSV pool.</small></li>
                                <li><strong>Park</strong><small>Camden Yards short right field supports Alonso&apos;s pull-side power lane.</small></li>
                            </ul>
                            <div class="straight-pick-actions">
                                <button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([STRAIGHT_OF_DAY])}'>Add O0.5 Straight to Gambly</button>
                            </div>
                        </div>
                        <div class="straight-pick-hero straight-pick-hero--o15">
                            <span class="straight-pick-tag">Over 1.5 HR Straight</span>
                            <div class="straight-pick-header">
                                <strong class="straight-pick-name">Kyle Schwarber &mdash; vs Roki Sasaki</strong>
                                <span class="straight-pick-meta">Listed +680 &middot; Score 98 &middot; PHI @ LAD</span>
                            </div>
                            <ul class="straight-pick-factors">
                                <li><strong>Multi-HR form</strong><small>Worst Pickz Favorite with <strong>3 HR, 3 near-HR</strong>, 101.7 mph EV, 30.0% barrels.</small></li>
                                <li><strong>Pitcher target</strong><small>Sasaki is the Dodger attack lane with Luzardo on the other side.</small></li>
                                <li><strong>Weather</strong><small>Dodger Stadium +6% HR row with consistent out-blowing wind.</small></li>
                            </ul>
                            <div class="straight-pick-actions">
                                <button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr([STRAIGHT_O15_DAY])}'>Add O1.5 Straight to Gambly</button>
                            </div>
                        </div>
                    </div>
                </div>"""

GOBLIN_CARD = f"""                <div class="summary-card full-width best-bets-card">
                    <h3>Goblin's Insight</h3>
                    <p class="model-note summary-note">Full-slate view built from weather, pitcher HR risk, current power form, and batter-vs-pitcher history.</p>
                    <div class="best-bets-grid">
                        <div class="best-bets-group">
                            <h4>3 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Pete Alonso HR</strong><small>3 HR, 3 near-HR, and 97.8 mph EV versus Trey Yesavage at Camden Yards.</small></li>
                                <li><strong>Brandon Lowe HR</strong><small>2 HR, 4 near-HR, and 30.8% barrels versus Bailey Ober.</small></li>
                                <li><strong>Byron Buxton HR</strong><small>3 HR, 3 near-HR, and 91.5 mph EV versus Mitch Keller at PNC Park.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(THREE_LEG_HR)}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Kyle Schwarber HR</strong><small>3 HR and 30.0% barrels versus Roki Sasaki at Dodger Stadium.</small></li>
                                <li><strong>Pete Alonso HR</strong><small>3 HR versus Trey Yesavage with HR-friendly Camden right field.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(TWO_LEG_HR)}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>Lowe, Adames, Schwarber, Devers, Mitchell, Olson</strong><small>Top attack lanes versus Ober, Feltner, Sasaki, Singer, Lambert, and Brown.</small></li>
                                <li><strong>Alonso, Buxton, Freeman, Neto, Judge, Riley</strong><small>Hot hitters versus Yesavage, Keller, Griffin, Rasmussen, Ginn, and Perez.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Juan Soto - Over 0.5 hits", "Brandon Lowe - Over 0.5 hits", "Austin Riley - Over 0.5 hits", "Manny Machado - Over 0.5 hits", "Kyle Schwarber - Over 0.5 hits", "Rafael Devers - Over 0.5 hits", "Pete Alonso - Over 0.5 hits", "Byron Buxton - Over 0.5 hits", "Freddie Freeman - Over 0.5 hits", "Zach Neto - Over 0.5 hits", "Fernando Tatis - Over 0.5 hits", "Matt Olson - Over 0.5 hits"])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>Kyle Schwarber HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with 3 HR versus Roki Sasaki LHB split.</small></li>
                                <li><strong>Willy Adames HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with 4 HR versus Ryan Feltner at Coors Field.</small></li>
                                <li><strong>Jordan Walker HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with 95.3 mph EV versus Ben Brown.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(FAV_THREE_LEG)}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                <li><strong>Brady Singer</strong><small>Slate-high HR risk (2.44); 2.61 vs LHB at GABP — Elly and Suarez are live.</small></li>
                                <li><strong>Ryan Feltner</strong><small>1.64 HR risk with 1.79 vs RHB; Adames and Devers anchor the Giants at Coors.</small></li>
                                <li><strong>Roki Sasaki</strong><small>0.91 HR risk; Schwarber, Turner, and Harper attack the Dodger lane.</small></li>
                                <li><strong>Ryne Nelson</strong><small>0.66 HR risk with 1.19 vs RHB; Marte and Carroll at T-Mobile.</small></li>
                                <li><strong>Kyle Leahy</strong><small>0.65 HR risk with 1.15 vs LHB; Burleson and Walker at Busch.</small></li>
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage, opposing starter HR leakage, park/weather, and listed price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Pete Alonso <small>3 HR, Yesavage RHB split, 97.8 mph EV</small></span><strong>98</strong></div>
                        <div class="top-five-item"><span>Willy Adames <small>4 HR, Feltner at Coors, 22.0% barrels</small></span><strong>98</strong></div>
                        <div class="top-five-item"><span>Kyle Schwarber <small>3 HR, Sasaki LHB split, 30.0% barrels</small></span><strong>98</strong></div>
                        <div class="top-five-item"><span>Brandon Lowe <small>2 HR, Ober matchup, 30.8% barrels</small></span><strong>98</strong></div>
                        <div class="top-five-item"><span>Byron Buxton <small>3 HR, 91.5 mph EV versus Keller</small></span><strong>95</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>SF @ COL <small>Coors +29 altitude boost, 76°F, 7 mph</small></span><strong>+29</strong></div>
                        <div class="summary-item"><span>NYY @ ATH <small>Sutter Health very high wind receptivity, 73°F</small></span><strong>+9%</strong></div>
                        <div class="summary-item"><span>PHI @ LAD <small>Dodger Stadium +6% HR, 13 mph out wind, 67°F</small></span><strong>+6%</strong></div>
                        <div class="summary-item"><span>ATL @ CIN <small>GABP smallest outfield, 76°F partially cloudy</small></span><strong>+0</strong></div>
                        <div class="summary-item"><span>SD @ WSH <small>Nationals great contact row, 75°F clear</small></span><strong>-2</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Pete Alonso <small>3 HR versus Yesavage at Camden</small></span><strong>98</strong></div>
                        <div class="summary-item"><span>#2 Willy Adames <small>4 HR versus Feltner at Coors</small></span><strong>98</strong></div>
                        <div class="summary-item"><span>#3 Kyle Schwarber <small>3 HR versus Sasaki at Dodger Stadium</small></span><strong>98</strong></div>
                        <div class="summary-item"><span>#4 Brandon Lowe <small>2 HR versus Ober at PNC</small></span><strong>98</strong></div>
                        <div class="summary-item"><span>#5 Byron Buxton <small>3 HR, 91.5 mph EV versus Keller</small></span><strong>95</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Garrett Mitchell <small>+790 with 2 HR versus Lambert</small></span><strong>98</strong></div>
                        <div class="summary-item"><span>Spencer Horwitz <small>+730 with 3 HR versus Ober</small></span><strong>82</strong></div>
                        <div class="summary-item"><span>Jackson Holliday <small>+850 versus Yesavage at Camden</small></span><strong>87</strong></div>
                        <div class="summary-item"><span>Jesus Sanchez <small>+720 versus Brandon Young</small></span><strong>86</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>ARI @ SEA <small>T-Mobile -6 altitude drag, 57°F dome</small></span><strong>-6</strong></div>
                        <div class="summary-item"><span>MIA @ NYM <small>Citi Field poor contact, 12 mph out wind</small></span><strong>-1</strong></div>
                        <div class="summary-item"><span>CHC @ STL <small>Busch large outfield, deep corners</small></span><strong>-3</strong></div>
                        <div class="summary-item"><span>KC @ TEX <small>Globe Life roof closed, -11% HR row</small></span><strong>-11</strong></div>
                    """

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


def archive_relative_assets(text):
    text = text.replace('src="assets/', 'src="../assets/')
    text = text.replace('href="assets/', 'href="../assets/')
    return text


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "May 30, 2026 — current slate", "href": "index.html"},
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
    text = re.sub(r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>', lambda _m: manifest_fallback(manifest), text, count=1, flags=re.DOTALL)
    text = re.sub(
        r"<p>(?:Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday), May \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Saturday, May 30, 2026 — Worst Pickz HR cheat sheet",
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
    start_m = re.search(
        r'\s*<div class="summary-card full-width straight-of-day-card">',
        text,
    )
    end_m = re.search(r'<div class="summary-card emoji-key-card">', text)
    if not start_m or not end_m or end_m.start() <= start_m.start():
        raise SystemExit("Could not locate summary block anchors")
    text = text[: start_m.start()] + SUMMARY_BLOCK + text[end_m.start() :]
    if "Pete Alonso HR</strong>" not in text or "Munetaka Murakami" in text:
        raise SystemExit("Summary block patch failed — stale Goblin content detected")
    assert_goblin_hr_parlays_distinct()
    PREVIEW.write_text(text, encoding="utf-8")
    print("patched", PREVIEW.relative_to(ROOT))


def sync_root_index():
    shutil.copy2(PREVIEW, ROOT / "index.html")
    print("synced root index.html")


def main():
    ARCHIVE_0529.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PREVIEW, ARCHIVE_0529)
    print("archived current preview to", ARCHIVE_0529.relative_to(ROOT))
    manifest = update_manifest()
    patch_preview(manifest)
    sync_root_index()


if __name__ == "__main__":
    main()
