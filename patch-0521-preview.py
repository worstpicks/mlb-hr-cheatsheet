#!/usr/bin/env python3
"""Patch preview sheet to 2026-05-21. Does not commit or push."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0520 = ROOT / "preview" / "archive" / "2026-05-20.html"
GAMES_BLOCK = (ROOT / "_games-0521.txt").read_text(encoding="utf-8-sig").strip()

SHEET_DATE = "2026-05-21"
TOTAL_GAMES = 7
TOTAL_ROWS = 35
TOTAL_FAVS = 10

FAVS = [
    "Alec Burleson (L)",
    "Brandon Lowe (L)",
    "Juan Soto (L)",
    "Jakob Marsee (L)",
    "Austin Riley (R)",
    "Aaron Judge (R)",
    "Brandon Valenzuela (S)",
    "George Springer (R)",
    "Nick Kurtz (L)",
    "Corbin Carroll (L)",
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
                    <p class="model-note summary-note">Small-slate view built from weather, pitcher HR risk, current power form, and batter-vs-pitcher history.</p>
                    <div class="best-bets-grid">
                        <div class="best-bets-group">
                            <h4>3 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Aaron Judge HR</strong><small>Fisher's RHB split is the biggest Yankee Stadium attack lane.</small></li>
                                <li><strong>Nick Kurtz HR</strong><small>Soriano LHB risk + Angel Stadium's best HR weather.</small></li>
                                <li><strong>Juan Soto HR</strong><small>7 HR/12 near-HR form with a BvP HR signal vs Cavalli.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Aaron Judge - Over 0.5 homerun", "Nick Kurtz - Over 0.5 homerun", "Juan Soto - Over 0.5 homerun"])}'>Add 3 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>2 Leg Homerun Bet</h4>
                            <ol>
                                <li><strong>Brandon Lowe HR</strong><small>9 HR, 12 near-HR and 21.7% barrels even in Busch drag.</small></li>
                                <li><strong>Mike Trout HR</strong><small>Angel Stadium carry plus a career HR off Severino.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Brandon Lowe - Over 0.5 homerun", "Mike Trout - Over 0.5 homerun"])}'>Add 2 Leg HR to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Hits Parlay</h4>
                            <ul>
                                <li><strong>Judge, Soto, Brandon Lowe, Matt Olson, Mike Trout, Nick Kurtz</strong></li>
                                <li><strong>Corbin Carroll, Ben Rice, James Wood, Ketel Marte, George Springer</strong></li>
                            </ul>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Aaron Judge - Over 0.5 hits", "Juan Soto - Over 0.5 hits", "Brandon Lowe - Over 0.5 hits", "Matt Olson - Over 0.5 hits", "Mike Trout - Over 0.5 hits", "Nick Kurtz - Over 0.5 hits", "Corbin Carroll - Over 0.5 hits", "Ben Rice - Over 0.5 hits", "James Wood - Over 0.5 hits", "Ketel Marte - Over 0.5 hits", "George Springer - Over 0.5 hits"])}'>Add Hits Parlay to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Worst Pickz Favorite 3 Leg</h4>
                            <ol>
                                <li><strong>Aaron Judge HR &#11088; &#127765;</strong><small>Worst Pickz Favorite, elite form, and Fisher's RHB risk.</small></li>
                                <li><strong>Nick Kurtz HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with Soriano LHB risk and Angel carry.</small></li>
                                <li><strong>Juan Soto HR &#11088; &#127765;</strong><small>Worst Pickz Favorite with Cavalli contact risk and BvP signal.</small></li>
                            </ol>
                            <div class="best-bets-actions"><button type="button" class="btn-gambly best-bets-gambly-btn" data-goblin-gambly-lines='{data_attr(["Aaron Judge - Over 0.5 homerun", "Nick Kurtz - Over 0.5 homerun", "Juan Soto - Over 0.5 homerun"])}'>Add Favorite 3 Leg to Gambly</button></div>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Weather Games</h4>
                            <ol>
                                <li><strong>ATH @ LAA</strong><small>Only positive HR model at +5%, mild temps, out-blowing pattern.</small></li>
                                <li><strong>COL @ ARI</strong><small>Roof scheduled open, 90° desert air, 9.5 total.</small></li>
                                <li><strong>ATL @ MIA</strong><small>Roof closed, but stable hitting conditions and power bats.</small></li>
                                <li><strong>TOR @ NYY</strong><small>Model is negative, but short porch keeps elite power live.</small></li>
                                <li><strong>NYM @ WSH</strong><small>Rain risk, but Cavalli/Wood/Soto power still matters.</small></li>
                            </ol>
                        </div>
                        <div class="best-bets-group">
                            <h4>Top 5 Pitchers To Attack</h4>
                            <ol>
                                <li><strong>Braydon Fisher</strong><small>Slate-high RHB HR risk; Judge is the cleanest lane.</small></li>
                                <li><strong>Zach Agnos</strong><small>RHB risk and Chase Field heat/open roof boost Arizona bats.</small></li>
                                <li><strong>Luis Severino</strong><small>RHB damage profile lines up with Trout/Neto/Adell.</small></li>
                                <li><strong>Joey Cantillo</strong><small>RHB split gives Detroit longshots life despite Comerica.</small></li>
                                <li><strong>Jose Soriano</strong><small>LHB risk makes Nick Kurtz the premier A's target.</small></li>
                            </ol>
                        </div>
                    </div>
                </div>"""

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage, opposing starter HR leakage, park/weather, and listed price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Aaron Judge <small>11 HR, Fisher RHB risk, Yankee power lane</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Nick Kurtz <small>Soriano LHB risk, Angel weather, BvP HR</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Juan Soto <small>7 HR, 12 near-HR, Cavalli LHB lane</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Brandon Lowe <small>9 HR, 12 near-HR, 21.7% barrels</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>Mike Trout <small>Angel carry plus BvP HR off Severino</small></span><strong>90</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>ATH @ LAA <small>Angel Stadium +5% HR, mild air, out-blowing tendency</small></span><strong>+5%</strong></div>
                        <div class="summary-item"><span>COL @ ARI <small>Chase open roof, 90° air, slate-high 9.5 total</small></span><strong>-8%</strong></div>
                        <div class="summary-item"><span>ATL @ MIA <small>Roof closed; park suppresses but conditions are stable</small></span><strong>-12%</strong></div>
                        <div class="summary-item"><span>TOR @ NYY <small>Short porch offsets part of the cool/high-pressure drag</small></span><strong>-15%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Nick Kurtz <small>Angel carry + Soriano LHB weak spot</small></span><strong>93</strong></div>
                        <div class="summary-item"><span>#2 Mike Trout <small>Best weather game and BvP HR vs Severino</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#3 Brent Rooker <small>Angel weather plus Soriano BvP damage</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#4 Corbin Carroll <small>Chase open roof and 90° air</small></span><strong>88</strong></div>
                        <div class="summary-item"><span>#5 Ketel Marte <small>Agnos RHB risk in Chase heat</small></span><strong>84</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Hao-Yu Lee <small>+1300 with Cantillo RHB risk</small></span><strong>77</strong></div>
                        <div class="summary-item"><span>A.J. Ewing <small>+1040 with Cavalli LHB path</small></span><strong>80</strong></div>
                        <div class="summary-item"><span>Brandon Valenzuela <small>+920, 96.6 mph EV, 23.1% barrels</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>Jakob Marsee <small>+1040, favorite tag, Strider LHB risk</small></span><strong>71</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>CLE @ DET <small>Comerica -34% HR, cool air, wind in</small></span><strong>-34%</strong></div>
                        <div class="summary-item"><span>PIT @ STL <small>Busch -26% HR with high pressure and wind in</small></span><strong>-26%</strong></div>
                        <div class="summary-item"><span>NYM @ WSH <small>Nationals Park -24% HR plus rain/delay risk</small></span><strong>-24%</strong></div>
                        <div class="summary-item"><span>TOR @ NYY <small>Yankee Stadium -15% HR despite short-porch upside</small></span><strong>-15%</strong></div>
                    """


def archive_relative_assets(text):
    text = text.replace('src="assets/', 'src="../assets/')
    text = text.replace('href="assets/', 'href="../assets/')
    return text


def ensure_archive():
    ARCHIVE_0520.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_0520.exists():
        text = PREVIEW.read_text(encoding="utf-8")
        ARCHIVE_0520.write_text(archive_relative_assets(text), encoding="utf-8")
        print("archived", ARCHIVE_0520.relative_to(ROOT))
    else:
        print("archive exists", ARCHIVE_0520.relative_to(ROOT))


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "May 21, 2026 — current slate", "href": "index.html"},
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
        "<p>Thursday, May 21, 2026 — Worst Pickz HR cheat sheet",
        text,
        count=1,
    )
    count_sentence = (
        f"This board covers <strong>{TOTAL_ROWS} listed HR props</strong> across "
        f"<strong>{TOTAL_GAMES} games</strong>, with <strong>{TOTAL_FAVS} Worst Pickz Favorite</strong> rows (&#11088;)."
    )
    text, count = re.subn(
        r"This board covers <strong>.*?</strong> across <strong>.*?</strong>, with <strong>.*?</strong> rows \(⭐\)\.",
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
