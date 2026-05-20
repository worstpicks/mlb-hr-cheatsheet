#!/usr/bin/env python3
"""Patch preview sheet to 2026-05-20. Does not touch root live index or push/deploy."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREVIEW = ROOT / "preview" / "index.html"
MANIFEST_PATH = ROOT / "preview" / "sheets-manifest.json"
ARCHIVE_0519 = ROOT / "preview" / "archive" / "2026-05-19.html"
GAMES_BLOCK = (ROOT / "_games-0520.txt").read_text(encoding="utf-8").strip()

SHEET_DATE = "2026-05-20"
TOTAL_GAMES = 15
TOTAL_ROWS = 77
TOTAL_FAVS = 11

FAVS = [
    "Kyle Schwarber (L)",
    "Jonathan Aranda (L)",
    "Coby Mayo (R)",
    "Yordan Alvarez (L)",
    "Corbin Carroll (L)",
    "Colson Montgomery (L)",
    "Angel Martinez (S)",
    "Ben Rice (L)",
    "Nolan Gorman (L)",
    "Brandon Lowe (L)",
    "Will Smith (R)",
]

FAV_SET = (
    "            const WORST_PICKZ_FAVORITE_NAMES = new Set([\n"
    + ",\n".join(f"                {json.dumps(name)}" for name in FAVS)
    + "\n            ]);"
)

TOP_CARD = """                <div class="summary-card full-width top-five-card">
                    <h3>Top 5 HR Tickets (Holistic)</h3>
                    <p class="model-note summary-note">Ranks blend batter damage, opposing starter HR leakage, park/weather, and listed price.</p>
                    <div class="top-five-list">
                        <div class="top-five-item"><span>Kyle Schwarber <small>101.6 mph EV, 50% barrels, CBP heat</small></span><strong>96</strong></div>
                        <div class="top-five-item"><span>Corbin Carroll <small>3 HR, 57.1% barrels in roof game</small></span><strong>95</strong></div>
                        <div class="top-five-item"><span>Yordan Alvarez <small>2 recent HR plus 3 HR BvP off Ryan</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Max Muncy <small>2 HR, 4 near-HR, 50% barrels</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Juan Soto <small>Littell is slate's No. 1 HR target arm</small></span><strong>91</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>CIN @ PHI <small>Citizens Bank +28% HR, 90°F, strong wind</small></span><strong>+28%</strong></div>
                        <div class="summary-item"><span>ATH @ LAA <small>Angel Stadium +7% HR, late out-blowing pattern</small></span><strong>+7%</strong></div>
                        <div class="summary-item"><span>TEX @ COL <small>Coors Field +4% HR, huge run/contact boost</small></span><strong>+4%</strong></div>
                        <div class="summary-item"><span>NYM @ WSH <small>Warm/rainy Nationals Park with Littell HR leak</small></span><strong>+1%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Kyle Schwarber <small>CBP heat/wind plus 50% barrels</small></span><strong>96</strong></div>
                        <div class="summary-item"><span>#2 Elly De La Cruz <small>Nola HR-risk in best HR weather</small></span><strong>87</strong></div>
                        <div class="summary-item"><span>#3 Brent Rooker <small>Angel Stadium late carry vs Kochanowicz</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#4 Nick Kurtz <small>Angel weather plus BvP HR signal</small></span><strong>88</strong></div>
                        <div class="summary-item"><span>#5 TJ Rumfield <small>Coors longshot with 3 near-HR</small></span><strong>81</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Alec Bohm <small>+840 in Citizens Bank weather</small></span><strong>82</strong></div>
                        <div class="summary-item"><span>A.J. Ewing <small>+800 vs Littell's LHB disaster split</small></span><strong>84</strong></div>
                        <div class="summary-item"><span>Brice Turang <small>+1050 vs Cabrera, weather discount</small></span><strong>78</strong></div>
                        <div class="summary-item"><span>TJ Rumfield <small>+820 at Coors with barrel signal</small></span><strong>81</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>MIL @ CHC <small>Wrigley -41% HR, 48-50°F, wind in hard</small></span><strong>-41%</strong></div>
                        <div class="summary-item"><span>HOU @ MIN <small>Target Field -33% HR and cool air</small></span><strong>-33%</strong></div>
                        <div class="summary-item"><span>CLE @ DET <small>Comerica -32% HR, large outfield</small></span><strong>-32%</strong></div>
                        <div class="summary-item"><span>PIT @ STL <small>Busch -26% HR with wind in</small></span><strong>-26%</strong></div>
                    """


def ensure_archive():
    ARCHIVE_0519.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_0519.exists():
        shutil.copy2(PREVIEW, ARCHIVE_0519)
        print("archived", ARCHIVE_0519.relative_to(ROOT))
    else:
        print("archive exists", ARCHIVE_0519.relative_to(ROOT))


def update_manifest():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    old = {sheet["date"]: sheet for sheet in manifest.get("sheets", [])}
    ordered = [
        {"date": SHEET_DATE, "label": "May 20, 2026 — current slate", "href": "index.html"},
        {"date": "2026-05-19", "label": "May 19, 2026", "href": "archive/2026-05-19.html"},
    ]
    for date in ["2026-05-18", "2026-05-16", "2026-05-15", "2026-05-14"]:
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
        r"<p>(?:Friday|Saturday|Sunday|Monday|Tuesday|Wednesday), May \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Wednesday, May 20, 2026 — Worst Pickz HR cheat sheet",
        text,
        count=1,
    )
    text = re.sub(
        r"This board covers <strong>.*?</strong> across <strong>.*?</strong>, with <strong>.*?</strong> rows \(⭐\)\.",
        f"This board covers <strong>{TOTAL_ROWS} listed HR props</strong> across <strong>{TOTAL_GAMES} games</strong>, with <strong>{TOTAL_FAVS} Worst Pickz Favorite</strong> rows (⭐).",
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
