#!/usr/bin/env python3
"""Patch index.html (and preview copy) for 2026-05-18 slate — local only, do not deploy."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GAMES_BLOCK = (ROOT / "_games-0518.txt").read_text(encoding="utf-8").strip()

FAV_SET = """            const WORST_PICKZ_FAVORITE_NAMES = new Set([
                "Kyle Schwarber (L)",
                "JJ Bleday (L)",
                "Will Benson (L)",
                "James Wood (L)",
                "Juan Soto (L)",
                "Byron Buxton (R)",
                "Yordan Alvarez (L)",
                "Bobby Witt Jr. (R)",
    "Ian Happ (S)",
    "Seiya Suzuki (R)",
    "Michael Busch (L)",
                "Michael Conforto (L)",
                "Hunter Goodman (R)",
                "Miguel Vargas (R)",
                "Gavin Sheets (L)",
                "Jackson Merrill (L)",
                "Julio Rodriguez (R)",
                "Will Smith (R)",
                "Shohei Ohtani (L)"
            ]);"""

MANIFEST_FB = (
    '<script type="application/json" id="sheets-manifest-fallback">'
    + __import__("json").dumps(
        __import__("json").loads(
            (ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8")
        ),
        ensure_ascii=False,
    ).replace("</", "<\\/")
    + "</script>"
)

TOP5 = """                    <div class="top-five-list">
                        <div class="top-five-item"><span>Shea Langeliers <small>Four HR vs Urena at Angel Stadium</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Austin Riley <small>Three HR vs Meyer in Miami</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Byron Buxton <small>.842 SLG vs Rojas at Target</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Coby Mayo <small>Rogers RHB lane at Tropicana</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                    </div>"""

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Kyle Schwarber <small>Citizens Bank +31% vs Lodolo</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#2 James Wood <small>Nationals Park 92°F vs Irvin</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#3 Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#4 Michael Conforto <small>Wrigley wind row vs Sproat</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#5 Michael Massey <small>Kauffman +35% vs Gray</small></span><strong>84</strong></div>
                    """

PARK_INNER = """
                        <div class="summary-item"><span>MIL @ CHC <small>Wrigley +42% HR, 17 mph out</small></span><strong>+42%</strong></div>
                        <div class="summary-item"><span>BOS @ KC <small>Kauffman +35% HR, 18 mph out</small></span><strong>+35%</strong></div>
                        <div class="summary-item"><span>CIN @ PHI <small>Citizens Bank +31% HR, 88°F</small></span><strong>+31%</strong></div>
                        <div class="summary-item"><span>NYM @ WSH <small>Nationals Park +9% HR, 92°F</small></span><strong>+9%</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>Travis Bazzana <small>+1500 vs Valdez</small></span><strong>72</strong></div>
                        <div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray</small></span><strong>68</strong></div>
                        <div class="summary-item"><span>Harrison Bader <small>+1200 vs Ray</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Ernie Clement <small>+1120 vs Weathers</small></span><strong>68</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>CHW @ SEA <small>T-Mobile -21% HR, 61°F dome</small></span><strong>-21%</strong></div>
                        <div class="summary-item"><span>LAD @ SD <small>Petco -7% HR row</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>BAL @ TB <small>Tropicana dome -6% HR</small></span><strong>-6%</strong></div>
                        <div class="summary-item"><span>TEX @ COL <small>Coors 36°F — weather suppresses carry</small></span><strong>~flat</strong></div>
                    """


def replace_summary_list(text, heading, inner):
    # Replace only summary-list inner HTML; do not capture the summary-card closing tag.
    pat = (
        rf'(<h3>{re.escape(heading)}</h3>\s*<div class="summary-list">)'
        rf'[\s\S]*?'
        rf'(\s*</div>\s*</div>\s*<div class="summary-card")'
    )
    return re.sub(pat, r"\1" + inner + r"\2", text, count=1)


def patch_file(path: Path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"const games = \[.*?\];",
        lambda _: GAMES_BLOCK,
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);",
        FAV_SET,
        text,
        count=1,
    )
    text = re.sub(
        r'<meta name="sheet-date" content="[^"]*">',
        '<meta name="sheet-date" content="2026-05-18">',
        text,
        count=1,
    )
    text = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        lambda _m: MANIFEST_FB,
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p>(?:Friday|Saturday|Sunday|Monday), May \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Monday, May 18, 2026 — Worst Pickz HR cheat sheet",
        text,
        count=1,
    )
    text = re.sub(
        r'(\s*)<div class="top-five-list">.*?</div>',
        lambda m: m.group(1) + TOP5.strip(),
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = replace_summary_list(text, "Best Park / Weather HR Rows (slate)", PARK_INNER)
    text = replace_summary_list(text, "Top 5 Weather Heavy HR Plays", WEATHER5_INNER)
    text = replace_summary_list(text, "Best longshot HR (listed +700+)", LONGSHOT_INNER)
    text = replace_summary_list(text, "Harsh Environment Fades", FADES_INNER)
    path.write_text(text, encoding="utf-8")
    print("patched", path)


for p in [ROOT / "index.html", ROOT / "preview" / "index.html"]:
    patch_file(p)
