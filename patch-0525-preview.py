#!/usr/bin/env python3
"""Patch preview sheet to 2026-05-25. Does not commit or push."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0521 = ROOT / "preview" / "archive" / "2026-05-21.html"
GAMES_BLOCK = (ROOT / "_games-0525.txt").read_text(encoding="utf-8-sig").strip()

SHEET_DATE = "2026-05-25"
TOTAL_GAMES = 13
TOTAL_ROWS = 53
TOTAL_FAVS = 8

FAVS = [
    "Brandon Lowe (L)",
    "Michael Conforto (L)",
    "Pete Alonso (R)",
    "Ivan Herrera (R)",
    "Jordan Walker (R)",
    "Miguel Vargas (R)",
    "Jac Caglianone (L)",
    "Kyle Schwarber (L)",
]

FAV_SET = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f'                "{name}"' for name in FAVS)
    + "\n            ]);"
)


def data_attr(lines):
    return json.dumps(lines).replace('"', "&quot;")


GOBLIN_CARD = f"""                <div class="summary-card full-width best-bets-card">
                    <h3>Goblin's Insight</h3>
                    <p class="model-note summary-note">Full-slate view built from weather, pitcher HR risk, current power form, and batter-vs-pitcher history.</p>
                    <div class="best-bets-grid">
                        <div class="best-bets-group">
                            <h4>3 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Colson Montgomery HR</strong><small>Three HR plus warm Rate Field stack; Kay RHB lane for Vargas sets the table.</small></li>
                                <li><strong>James Wood HR</strong><small>Littell LHB 4.63 HR/9 and four near-HR in the window.</small></li>
                                <li><strong>Ben Rice HR</strong><small>Three HR vs Warren with Kauffman +11% carry.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Colson Montgomery - Over 0.5 homerun", "James Wood - Over 0.5 homerun", "Ben Rice - Over 0.5 homerun"])}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Miguel Vargas HR</strong><small>Kay RHB HR-risk lane in a warm small park.</small></li>
                                <li><strong>Brent Rooker HR</strong><small>Sutter +34% HR row versus Miller.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Miguel Vargas - Over 0.5 homerun", "Brent Rooker - Over 0.5 homerun"])}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>Ben Rice, Aaron Judge, Bo Bichette, Rafael Devers, George Springer</strong><small>Top attack-pitcher lanes with recent contact.</small></li>
                                <li><strong>James Wood, Kyle Schwarber, Brent Rooker, Luke Raley, Yandy Diaz</strong><small>Hot hitters vs Littell, Vasquez, Miller, Civale, Bradish.</small></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Ben Rice - Over 0.5 hits", "Aaron Judge - Over 0.5 hits", "Bo Bichette - Over 0.5 hits", "Rafael Devers - Over 0.5 hits", "George Springer - Over 0.5 hits", "James Wood - Over 0.5 hits", "Kyle Schwarber - Over 0.5 hits", "Brent Rooker - Over 0.5 hits", "Luke Raley - Over 0.5 hits", "Yandy Diaz - Over 0.5 hits"])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>Kyle Schwarber HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with two HR and 25% barrels.</small></li>
                                <li><strong>Pete Alonso HR &#11088;</strong><small>99.4 mph EV versus McClanahan.</small></li>
                                <li><strong>Miguel Vargas HR &#11088;</strong><small>Kay RHB HR-risk lane at a playable price.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Kyle Schwarber - Over 0.5 homerun", "Pete Alonso - Over 0.5 homerun", "Miguel Vargas - Over 0.5 homerun"])}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Weather Games</h4>
                            <ol>
                                <li><strong>SEA @ ATH</strong><small>+34% HR at Sutter with 15+ mph out-blowing wind.</small></li>
                                <li><strong>NYY @ KC</strong><small>+11% HR at Kauffman with 88°F heat.</small></li>
                                <li><strong>COL @ LAD</strong><small>+12% HR at Dodger Stadium.</small></li>
                                <li><strong>MIN @ CWS</strong><small>+5% combined at Rate Field with 84°F air.</small></li>
                                <li><strong>WSH @ CLE</strong><small>Cold park row but Littell is slate #1 HR-risk arm.</small></li>
                            </ol>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                <li><strong>Zack Littell</strong><small>2.85 HR/9 and 4.63 HR/9 vs LHB.</small></li>
                                <li><strong>Nick Lodolo</strong><small>1.69 vs-RHB HR-risk split.</small></li>
                                <li><strong>Tatsuya Imai</strong><small>2.89 HR/9 vs LHB.</small></li>
                                <li><strong>Tanner Gordon</strong><small>1.80 vs-LHB HR-risk split.</small></li>
                                <li><strong>Anthony Kay</strong><small>1.17 HR/9 with RHB leak.</small></li>
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage profile, matchup leakage, park/weather, lineup slot, and price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Colson Montgomery (L) <small>Three HR + warm Rate Field stack</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Yordan Alvarez (L) <small>Elite power window vs Rocker</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>James Wood (L) <small>Littell LHB 4.63 HR/9 + four near-HR</small></span><strong>90</strong></div>
                        <div class="top-five-item"><span>Ben Rice (L) <small>Three HR vs Warren LHB lane + Kauffman</small></span><strong>89</strong></div>
                        <div class="top-five-item"><span>Brent Rooker (R) <small>Sutter +34% HR vs Miller</small></span><strong>88</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>SEA @ ATH <small>Sutter +34% HR, 15+ mph out</small></span><strong>+34%</strong></div>
                        <div class="summary-item"><span>NYY @ KC <small>Kauffman +11% HR, 88°F wind out L</small></span><strong>+11%</strong></div>
                        <div class="summary-item"><span>COL @ LAD <small>Dodger Stadium +12% HR</small></span><strong>+12%</strong></div>
                        <div class="summary-item"><span>MIN @ CWS <small>Rate Field +5% combined</small></span><strong>+5%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Brent Rooker <small>Sutter heat vs Miller</small></span><strong>88</strong></div>
                        <div class="summary-item"><span>#2 Nick Kurtz <small>Sacramento carry vs Miller</small></span><strong>84</strong></div>
                        <div class="summary-item"><span>#3 Luke Raley <small>Sutter + Civale LHB lane</small></span><strong>83</strong></div>
                        <div class="summary-item"><span>#4 Ben Rice <small>Kauffman heat vs Warren</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#5 Jac Caglianone <small>88°F + Warren LHB leak</small></span><strong>82</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Jarred Kelenic <small>+550 vs Kay</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>James Wood <small>+390 vs Littell</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>Andrew Vaughn <small>+520 vs Liberatore</small></span><strong>78</strong></div>
                        <div class="summary-item"><span>Ezequiel Duran <small>+900 vs Imai</small></span><strong>76</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>WSH @ CLE <small>Progressive -13% HR row</small></span><strong>-13%</strong></div>
                        <div class="summary-item"><span>PHI @ SD <small>Petco -9% HR, marine layer</small></span><strong>-9%</strong></div>
                        <div class="summary-item"><span>ARI @ SF <small>Oracle -6% HR (ignore wind forecast)</small></span><strong>-6%</strong></div>
                        <div class="summary-item"><span>MIA @ TOR <small>Rogers -8% HR, roof open cold</small></span><strong>-8%</strong></div>
                    """


def archive_relative_assets(text):
    text = text.replace('src="assets/', 'src="../assets/')
    text = text.replace('href="assets/', 'href="../assets/')
    return text


def ensure_archive():
    ARCHIVE_0521.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_0521.exists():
        text = PREVIEW.read_text(encoding="utf-8")
        ARCHIVE_0521.write_text(archive_relative_assets(text), encoding="utf-8")
        print("archived", ARCHIVE_0521.relative_to(ROOT))
    else:
        print("archive exists", ARCHIVE_0521.relative_to(ROOT))


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "May 25, 2026 — current slate", "href": "index.html"},
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


def replace_summary_list(text, heading, inner):
    pat = (
        rf'(<h3>{re.escape(heading)}</h3>\s*<div class="summary-list">)'
        rf"[\s\S]*?"
        rf'(\s*</div>\s*</div>\s*<div class="summary-card(?: emoji-key-card)?")'
    )
    text, count = re.subn(pat, r"\1" + inner + r"\2", text, count=1)
    if count != 1:
        raise SystemExit(f"Could not replace summary list: {heading}")
    return text


def patch_preview(manifest):
    text = PREVIEW.read_text(encoding="utf-8")
    text = re.sub(r"const games = \[.*?\];", lambda _m: GAMES_BLOCK, text, count=1, flags=re.DOTALL)
    text = re.sub(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);", FAV_SET, text, count=1)
    text = re.sub(r'<meta name="sheet-date" content="[^"]*">', f'<meta name="sheet-date" content="{SHEET_DATE}">', text, count=1)
    text = re.sub(r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>', lambda _m: manifest_fallback(manifest), text, count=1, flags=re.DOTALL)
    text = re.sub(
        r"<p>(?:Friday|Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday), May \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Sunday, May 25, 2026 — Worst Pickz HR cheat sheet",
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
    text = re.sub(
        r'                <div class="summary-card full-width best-bets-card">[\s\S]*?\n                </div>\n                <div class="summary-card full-width top-five-card">',
        GOBLIN_CARD + '\n                <div class="summary-card full-width top-five-card">',
        text,
        count=1,
    )
    text = re.sub(
        r'                <div class="summary-card full-width top-five-card">[\s\S]*?\n                </div>\n                <div class="summary-card">',
        TOP_CARD + '\n                <div class="summary-card">',
        text,
        count=1,
    )
    text = replace_summary_list(text, "Best Park / Weather HR Rows (slate)", PARK_INNER)
    text = replace_summary_list(text, "Top 5 Weather Heavy HR Plays", WEATHER5_INNER)
    text = replace_summary_list(text, "Best longshot HR (listed +700+)", LONGSHOT_INNER)
    text = replace_summary_list(text, "Harsh Environment Fades", FADES_INNER)
    PREVIEW.write_text(text, encoding="utf-8")
    print("patched", PREVIEW.relative_to(ROOT))


def main():
    ensure_archive()
    manifest = update_manifest()
    patch_preview(manifest)


if __name__ == "__main__":
    main()
