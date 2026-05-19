#!/usr/bin/env python3
"""Patch current sheet to 2026-05-19 locally. Does not push/deploy."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAMES_BLOCK = (ROOT / "_games-0519.txt").read_text(encoding="utf-8").strip()
ARCHIVE_0518 = ROOT / "preview" / "archive" / "2026-05-18.html"

FAVS = [
    "Drake Baldwin (L)",
    "Matt Olson (L)",
    "Pete Alonso (R)",
    "Kyle Schwarber (L)",
    "Spencer Steer (R)",
    "Ben Rice (L)",
    "Ryan Jeffers (R)",
    "Christian Walker (R)",
    "Yordan Alvarez (L)",
    "Willson Contreras (R)",
    "Ian Happ (S)",
    "Michael Conforto (L)",
    "Jo Adell (R)",
    "Gavin Sheets (L)",
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
                        <div class="top-five-item"><span>Ryan Jeffers <small>3 HR, 1.000 ISO vs McCullers</small></span><strong>96</strong></div>
                        <div class="top-five-item"><span>Yordan Alvarez <small>100.4 mph EV vs Matthews</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Drake Baldwin <small>37.5% barrels vs Garrett</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Kyle Schwarber <small>Citizens Bank +37% HR vs Burns</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Gavin Sheets <small>3 HR vs Sheehan's LHB leak</small></span><strong>92</strong></div>
                    </div>
                </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>CIN @ PHI <small>Citizens Bank +37% HR, 91°F, wind out</small></span><strong>+37%</strong></div>
                        <div class="summary-item"><span>TOR @ NYY <small>Yankee Stadium +18% HR, 89°F, wind out</small></span><strong>+18%</strong></div>
                        <div class="summary-item"><span>NYM @ WSH <small>Nationals Park +5% HR, 93°F</small></span><strong>+5%</strong></div>
                        <div class="summary-item"><span>ATH @ LAA <small>Angel Stadium +5% HR, mild out-blowing pattern</small></span><strong>+5%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Kyle Schwarber <small>91°F and +37% HR at Citizens Bank</small></span><strong>92</strong></div>
                        <div class="summary-item"><span>#2 Bryce Harper <small>same Phillies lefty lane vs Burns</small></span><strong>87</strong></div>
                        <div class="summary-item"><span>#3 Aaron Judge <small>Yankee Stadium +18% HR, wind out</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#4 Mark Vientos <small>Nationals Park heat vs Griffin</small></span><strong>84</strong></div>
                        <div class="summary-item"><span>#5 Jo Adell <small>Angel Stadium plus Lopez's RHB leak</small></span><strong>90</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Yohendrick Pinango <small>+700 vs Will Warren at Yankee Stadium</small></span><strong>78</strong></div>
                        <div class="summary-item"><span>Justin Crawford <small>+1160 in Citizens Bank weather</small></span><strong>82</strong></div>
                        <div class="summary-item"><span>Harrison Bader <small>+800 vs Ryne Nelson's RHB split</small></span><strong>82</strong></div>
                        <div class="summary-item"><span>Nick Loftin <small>+1280 contact dart vs Suarez</small></span><strong>72</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>HOU @ MIN <small>Target Field -22% HR and cold 50°F air</small></span><strong>-22%</strong></div>
                        <div class="summary-item"><span>BOS @ KC <small>Kauffman -21% HR with projected wind in</small></span><strong>-21%</strong></div>
                        <div class="summary-item"><span>PIT @ STL <small>Busch -20% HR plus delay risk</small></span><strong>-20%</strong></div>
                        <div class="summary-item"><span>T-Mobile Park <small>SEA dome/roof environment and -11% HR</small></span><strong>-11%</strong></div>
                    """


def ensure_archive():
    ARCHIVE_0518.parent.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_0518.exists():
        ARCHIVE_0518.write_text((ROOT / "preview" / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
        print("archived", ARCHIVE_0518.relative_to(ROOT))
    else:
        print("archive exists", ARCHIVE_0518.relative_to(ROOT))


def update_manifest():
    path = ROOT / "preview" / "sheets-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    old = {s["date"]: s for s in manifest.get("sheets", [])}
    ordered = [
        {"date": "2026-05-19", "label": "May 19, 2026 — current slate", "href": "index.html"},
        {"date": "2026-05-18", "label": "May 18, 2026", "href": "archive/2026-05-18.html"},
    ]
    for date in ["2026-05-16", "2026-05-15", "2026-05-14"]:
        if date in old:
            ordered.append(old[date])
    path.write_text(json.dumps({"version": 1, "sheets": ordered}, indent=2) + "\n", encoding="utf-8")
    return {"version": 1, "sheets": ordered}


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
        rf'(\s*</div>\s*</div>\s*<div class="summary-card")'
    )
    return re.sub(pat, r"\1" + inner + r"\2", text, count=1)


def patch_file(path: Path, manifest):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"const games = \[.*?\];", lambda _m: GAMES_BLOCK, text, count=1, flags=re.DOTALL)
    text = re.sub(r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);", FAV_SET, text, count=1)
    text = re.sub(r'<meta name="sheet-date" content="[^"]*">', '<meta name="sheet-date" content="2026-05-19">', text, count=1)
    text = re.sub(r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>', lambda _m: manifest_fallback(manifest), text, count=1, flags=re.DOTALL)
    text = re.sub(r"<p>(?:Friday|Saturday|Sunday|Monday|Tuesday), May \d+, 2026 — Worst Pickz HR cheat sheet", "<p>Tuesday, May 19, 2026 — Worst Pickz HR cheat sheet", text, count=1)
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
    path.write_text(text, encoding="utf-8")
    print("patched", path.relative_to(ROOT))


def main():
    ensure_archive()
    manifest = update_manifest()
    for path in [ROOT / "index.html", ROOT / "preview" / "index.html"]:
        patch_file(path, manifest)


if __name__ == "__main__":
    main()
