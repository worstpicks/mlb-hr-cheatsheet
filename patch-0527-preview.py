#!/usr/bin/env python3
"""Patch preview sheet to 2026-05-27. Does not commit or push."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0525 = ROOT / "preview" / "archive" / "2026-05-25.html"
GAMES_BLOCK = (ROOT / "_games-0527.txt").read_text(encoding="utf-8-sig").strip()

SHEET_DATE = "2026-05-27"
TOTAL_GAMES = 10
TOTAL_ROWS = 48
TOTAL_FAVS = 12

FAVS = [
    "Kyle Schwarber (L)",
    "Bryce Harper (L)",
    "Jonathan Aranda (L)",
    "Brandon Lowe (L)",
    "Michael Busch (L)",
    "Jarren Duran (L)",
    "Elly De La Cruz (S)",
    "Salvador Perez (R)",
    "Jac Caglianone (L)",
    "Paul Goldschmidt (R)",
    "Miguel Vargas (R)",
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
    "Jonathan Aranda - Over 1.5 hits + runs + RBIs",
    "Brandon Lowe - Over 1.5 hits + runs + RBIs",
    "Yordan Alvarez - Over 1.5 hits + runs + RBIs",
    "Junior Caminero - Over 1.5 hits + runs + RBIs",
    "Oneil Cruz - Over 1.5 hits + runs + RBIs",
    "Shohei Ohtani - Over 1.5 hits + runs + RBIs",
    "Matt Olson - Over 1.5 hits + runs + RBIs",
    "Jarren Duran - Over 1.5 hits + runs + RBIs",
]

THREE_LEG_HR = [
    "Brandon Lowe - Over 0.5 homerun",
    "Kyle Schwarber - Over 0.5 homerun",
    "Yordan Alvarez - Over 0.5 homerun",
]

FAV_THREE_LEG = [
    "Jonathan Aranda - Over 0.5 homerun",
    "Jarren Duran - Over 0.5 homerun",
    "Elly De La Cruz - Over 0.5 homerun",
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
                                <li><strong>Brandon Lowe HR</strong><small>Jameson Taillon is the board's loudest HR-leaky arm; Lowe has 10 HR and 23.4% barrels in the window.</small></li>
                                <li><strong>Kyle Schwarber HR</strong><small>Schwarber's slate-best power form versus Walker Buehler's RHB split keeps Philly live even in Petco drag.</small></li>
                                <li><strong>Yordan Alvarez HR</strong><small>Jacob deGrom LHB HR risk plus BvP HR history; Alvarez has 7 HR and 18.0% barrels.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(THREE_LEG_HR)}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Jarren Duran HR</strong><small>Fenway +19% runs row with high receptivity and 11 mph L-R wind versus Bryce Elder.</small></li>
                                <li><strong>Jonathan Aranda HR</strong><small>Oriole Park +8% HR row versus Trey Gibson, the slate's top HR-risk starter.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Jarren Duran - Over 0.5 homerun", "Jonathan Aranda - Over 0.5 homerun"])}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>Schwarber, Harper, Lowe, Aranda, Alvarez, Goldschmidt</strong><small>Top attack-pitcher lanes with recent contact quality.</small></li>
                                <li><strong>Duran, Cruz, Olson, Witt, Vargas, Nimmo</strong><small>Hot hitters versus Taillon, Gibson, Early, Cameron, Prielipp, Burrows.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Kyle Schwarber - Over 0.5 hits", "Bryce Harper - Over 0.5 hits", "Brandon Lowe - Over 0.5 hits", "Jonathan Aranda - Over 0.5 hits", "Yordan Alvarez - Over 0.5 hits", "Paul Goldschmidt - Over 0.5 hits", "Jarren Duran - Over 0.5 hits", "Oneil Cruz - Over 0.5 hits", "Matt Olson - Over 0.5 hits", "Bobby Witt Jr. - Over 0.5 hits", "Miguel Vargas - Over 0.5 hits", "Brandon Nimmo - Over 0.5 hits"])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Hits + Runs + RBI Play</h4>
                            <ul>
                                <li><strong>Aranda, Caminero, Lowe, Cruz</strong><small>Top contact versus Gibson and Taillon — the slate's #1 and #2 pitchers to attack.</small></li>
                                <li><strong>Alvarez, Ohtani, Olson, Duran</strong><small>Run/RBI upside versus deGrom, Sugano, Early, and Elder in the best run environments.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(HRRBI_PLAY)}'>Add 2 Hits + Runs + RBI to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>Jonathan Aranda HR &#11088; &#127765;</strong><small>Worst Pickz Favorite moonshot versus Gibson at Oriole Park (+8% HR) — slate #1 pitcher to attack.</small></li>
                                <li><strong>Jarren Duran HR &#11088; &#127765;</strong><small>Worst Pickz Favorite moonshot at Fenway (+19% runs) versus Elder in the board's best run environment.</small></li>
                                <li><strong>Elly De La Cruz HR &#11088; &#127765;</strong><small>Worst Pickz Favorite moonshot versus Tong RHB HR leakage — clean attack-pitcher lane.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(FAV_THREE_LEG)}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                <li><strong>Trey Gibson</strong><small>Slate-high HR risk (1.71); Rays lefties and righties both live.</small></li>
                                <li><strong>Jameson Taillon</strong><small>1.61 HR risk with 1.76 LHB split; Pittsburgh lefties are premium.</small></li>
                                <li><strong>Jacob deGrom</strong><small>1.13 HR risk; Alvarez and Walker are the Houston anchors.</small></li>
                                <li><strong>Mike Burrows</strong><small>0.64 HR risk with LHB leakage; Nimmo is the Rangers lefty lane.</small></li>
                                <li><strong>Tomoyuki Sugano</strong><small>1.27 LHB HR risk; Ohtani and Freeman fit the Dodger lefty angle.</small></li>
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage, opposing starter HR leakage, park/weather, and listed price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Kyle Schwarber <small>10 HR, 28.3% barrels vs Buehler</small></span><strong>96</strong></div>
                        <div class="top-five-item"><span>Brandon Lowe <small>10 HR, Taillon HR risk, 23.4% barrels</small></span><strong>95</strong></div>
                        <div class="top-five-item"><span>Jonathan Aranda <small>8 HR, Gibson HR risk, 17.1% barrels</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Yordan Alvarez <small>7 HR, deGrom LHB risk, BvP HR</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Jarren Duran <small>6 HR, Fenway +19% runs vs Elder</small></span><strong>93</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>NYY @ KC <small>+9% HR at Kauffman with mild air and X-Large outfield</small></span><strong>+9%</strong></div>
                        <div class="summary-item"><span>TB @ BAL <small>+8% HR at Oriole Park with warm 82°F air</small></span><strong>+8%</strong></div>
                        <div class="summary-item"><span>ATL @ BOS <small>+1% HR but +19% runs at Fenway with high receptivity</small></span><strong>+19% runs</strong></div>
                        <div class="summary-item"><span>CHC @ PIT <small>+5% runs row despite -4% HR at PNC</small></span><strong>+5% runs</strong></div>
                        <div class="summary-item"><span>MIN @ CWS <small>+1% combined at Rate Field with 11 mph L-R wind</small></span><strong>+1%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Jarren Duran <small>Fenway +19% runs plus Elder RHB lane</small></span><strong>93</strong></div>
                        <div class="summary-item"><span>#2 Jonathan Aranda <small>Oriole +8% HR versus Gibson HR risk</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#3 Bobby Witt Jr. <small>Kauffman +9% carry versus Cameron</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#4 Brandon Lowe <small>PNC +5% runs plus Taillon HR leakage</small></span><strong>95</strong></div>
                        <div class="summary-item"><span>#5 Coby Mayo <small>Oriole +8% HR versus Matz RHB split</small></span><strong>78</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Ceddanne Rafaela <small>+850 at Fenway versus Elder</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Vaughn Grissom <small>+880 versus Mize RHB split</small></span><strong>72</strong></div>
                        <div class="summary-item"><span>Matt McLain <small>+900 with 2 HR versus Tong</small></span><strong>72</strong></div>
                        <div class="summary-item"><span>TJ Rumfield <small>+850 with 4 HR in Dodger drag</small></span><strong>74</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>PHI @ SD <small>Petco -7% HR, cool marine air</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>HOU @ TEX <small>Globe Life -7% HR, roof closed</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>COL @ LAD <small>Dodger Stadium -6% HR, 62°F air</small></span><strong>-6%</strong></div>
                        <div class="summary-item"><span>CIN @ NYM <small>Citi Field -6% HR, out-blowing wind</small></span><strong>-6%</strong></div>
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
    ARCHIVE_0525.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_0525.exists():
        text = PREVIEW.read_text(encoding="utf-8")
        ARCHIVE_0525.write_text(archive_relative_assets(text), encoding="utf-8")
        print("archived", ARCHIVE_0525.relative_to(ROOT))
    else:
        print("archive exists", ARCHIVE_0525.relative_to(ROOT))


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "May 27, 2026 — current slate", "href": "index.html"},
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
        "<p>Wednesday, May 27, 2026 — Worst Pickz HR cheat sheet",
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
    if "Brandon Lowe HR</strong><small>Jameson Taillon" not in text:
        start = text.index('<div class="summary-card full-width best-bets-card">')
        end = text.index('<div class="summary-card emoji-key-card">')
        text = text[:start] + SUMMARY_BLOCK + text[end:]
    assert_goblin_hr_parlays_distinct()
    PREVIEW.write_text(text, encoding="utf-8")
    print("patched", PREVIEW.relative_to(ROOT))


def main():
    ensure_archive()
    manifest = update_manifest()
    patch_preview(manifest)


if __name__ == "__main__":
    main()
