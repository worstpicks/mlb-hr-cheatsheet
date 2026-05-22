#!/usr/bin/env python3
"""Patch preview sheet to 2026-05-22. Does not commit or push."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0521 = ROOT / "preview" / "archive" / "2026-05-21.html"
GAMES_BLOCK = (ROOT / "_games-0522.txt").read_text(encoding="utf-8-sig").strip()

SHEET_DATE = "2026-05-22"
TOTAL_GAMES = 15
TOTAL_ROWS = 73
TOTAL_FAVS = 17

FAVS = [
    "Kyle Schwarber (L)",
    "Rhys Hoskins (R)",
    "Elly De La Cruz (S)",
    "Ben Rice (L)",
    "Yandy Diaz (R)",
    "Brandon Lowe (L)",
    "Owen Caissie (L)",
    "Juan Soto (L)",
    "Byron Buxton (R)",
    "Pete Alonso (R)",
    "Mike Yastrzemski (L)",
    "Jose Tena (L)",
    "Jacob Young (R)",
    "Josh Jung (R)",
    "Nick Kurtz (L)",
    "Corbin Carroll (L)",
    "Colson Montgomery (L)",
]

FAV_SET = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f"                {json.dumps(name)}" for name in FAVS)
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
                                <li><strong>Yordan Alvarez HR</strong><small>Jameson Taillon is slate-high HR risk; Alvarez is the cleanest attack lane.</small></li>
                                <li><strong>Bobby Witt Jr. HR</strong><small>Logan Gilbert RHB HR risk at Kauffman; Witt has BvP HR history off Gilbert.</small></li>
                                <li><strong>Austin Riley HR</strong><small>Miles Mikolas LHB/RHB HR risk; Riley's form is slate-elite versus the glove arm.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Yordan Alvarez - Over 0.5 homerun", "Bobby Witt Jr. - Over 0.5 homerun", "Austin Riley - Over 0.5 homerun"])}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Julio Rodriguez HR</strong><small>Kauffman +6% carry with out-blowing wind fits his pull-side power vs Cameron.</small></li>
                                <li><strong>Elly De La Cruz HR</strong><small>GABP +5% HR row plus Leahy RHB split; switch pull-air matches the wind lane.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Julio Rodriguez - Over 0.5 homerun", "Elly De La Cruz - Over 0.5 homerun"])}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>Schwarber, Soto, Rice, Carroll, Muncy, Julio Rodriguez</strong></li>
                                <li><strong>Brandon Lowe, Yordan Alvarez, Austin Riley, Mike Yastrzemski, Nick Kurtz, Pete Alonso</strong></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Kyle Schwarber - Over 0.5 hits", "Juan Soto - Over 0.5 hits", "Ben Rice - Over 0.5 hits", "Corbin Carroll - Over 0.5 hits", "Max Muncy - Over 0.5 hits", "Julio Rodriguez - Over 0.5 hits", "Brandon Lowe - Over 0.5 hits", "Yordan Alvarez - Over 0.5 hits", "Austin Riley - Over 0.5 hits", "Mike Yastrzemski - Over 0.5 hits", "Nick Kurtz - Over 0.5 hits"])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>Kyle Schwarber HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with slate-best power form.</small></li>
                                <li><strong>Juan Soto HR &#11088; &#127765;</strong><small>Worst Pickz Favorite vs Perez RHB HR risk.</small></li>
                                <li><strong>Ben Rice HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with 4 HR in the pitch-mix window.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Kyle Schwarber - Over 0.5 homerun", "Juan Soto - Over 0.5 homerun", "Ben Rice - Over 0.5 homerun"])}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Weather Games</h4>
                            <ol>
                                <li><strong>SEA @ KC</strong><small>+6% HR at Kauffman with mild air and X-Large outfield.</small></li>
                                <li><strong>STL @ CIN</strong><small>+5% HR at GABP despite rain risk.</small></li>
                                <li><strong>TEX @ LAA</strong><small>+4% HR at Angel Stadium with out-blowing pattern.</small></li>
                                <li><strong>PIT @ TOR</strong><small>+2% HR with Rogers Centre roof closed.</small></li>
                                <li><strong>COL @ ARI</strong><small>Roof closed but 92°F desert air keeps carry live.</small></li>
                            </ol>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                <li><strong>Jameson Taillon</strong><small>Slate-high HR risk; Yordan Alvarez is the cleanest lane.</small></li>
                                <li><strong>Logan Gilbert</strong><small>RHB HR risk at Kauffman; Julio Rodriguez fits best.</small></li>
                                <li><strong>Miles Mikolas</strong><small>LHB HR risk; Yastrzemski/Riley/Harris all live.</small></li>
                                <li><strong>Jacob deGrom</strong><small>LHB HR risk in Angel Stadium carry.</small></li>
                                <li><strong>Eury Perez</strong><small>Best RHB HR-risk split; Juan Soto is the Mets anchor.</small></li>
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage, opposing starter HR leakage, park/weather, and listed price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Kyle Schwarber <small>5 HR, 36.8% barrels vs Williams</small></span><strong>96</strong></div>
                        <div class="top-five-item"><span>Juan Soto <small>4 HR, Perez RHB HR risk, 27.8% barrels</small></span><strong>95</strong></div>
                        <div class="top-five-item"><span>Corbin Carroll <small>3 HR, Sugano LHB risk, 50% barrels</small></span><strong>95</strong></div>
                        <div class="top-five-item"><span>Ben Rice <small>4 HR, Martinez LHB split, short porch</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Max Muncy <small>2 HR, 40% barrels vs Henderson</small></span><strong>94</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>SEA @ KC <small>Kauffman +6% HR, mild air, X-Large outfield</small></span><strong>+6%</strong></div>
                        <div class="summary-item"><span>STL @ CIN <small>GABP +5% HR, warm air, small park</small></span><strong>+5%</strong></div>
                        <div class="summary-item"><span>TEX @ LAA <small>Angel Stadium +4% HR, out-blowing pattern</small></span><strong>+4%</strong></div>
                        <div class="summary-item"><span>PIT @ TOR <small>Rogers Centre +2% HR, roof closed</small></span><strong>+2%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Julio Rodriguez <small>Kauffman +6% HR plus Cameron RHB lane</small></span><strong>93</strong></div>
                        <div class="summary-item"><span>#2 Yordan Alvarez <small>Taillon HR risk even in Wrigley drag</small></span><strong>88</strong></div>
                        <div class="summary-item"><span>#3 Elly De La Cruz <small>GABP +5% HR plus Leahy RHB split</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#4 Brandon Lowe <small>103.5 mph EV, 42.9% barrels</small></span><strong>93</strong></div>
                        <div class="summary-item"><span>#5 Ezequiel Duran <small>Angel +4% HR plus deGrom LHB risk</small></span><strong>83</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Travis Bazzana <small>+1260 with .778 SLG vs Sanchez</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>A.J. Ewing <small>+860 with Perez RHB HR risk</small></span><strong>81</strong></div>
                        <div class="summary-item"><span>James Outman <small>+825 in Fenway drag, 50% hard-hit</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Jakob Marsee <small>+1040 with Myers RHB split</small></span><strong>76</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>MIN @ BOS <small>Fenway -36% HR, slate-worst environment</small></span><strong>-36%</strong></div>
                        <div class="summary-item"><span>TB @ NYY <small>Yankee Stadium -30% HR despite short porch</small></span><strong>-30%</strong></div>
                        <div class="summary-item"><span>CWS @ SF <small>Oracle Park -26% HR, cool air, wind</small></span><strong>-26%</strong></div>
                        <div class="summary-item"><span>DET @ BAL <small>Oriole Park -27% HR with rain/overcast</small></span><strong>-27%</strong></div>
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
        {"date": SHEET_DATE, "label": "May 22, 2026 — current slate", "href": "index.html"},
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
        rf'[\s\S]*?'
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
        "<p>Friday, May 22, 2026 — Worst Pickz HR cheat sheet",
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
