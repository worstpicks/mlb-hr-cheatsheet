#!/usr/bin/env python3
"""Create Saturday 2026-05-16 archive HTML from 2026-05-15 template + _games-0516.txt."""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "preview" / "archive" / "2026-05-15.html"
DST = ROOT / "preview" / "archive" / "2026-05-16.html"
GAMES_BLOCK = (ROOT / "_games-0516.txt").read_text(encoding="utf-8").strip()

FAV_SET = """            const WORST_PICKZ_FAVORITE_NAMES = new Set([
                "Angel Martinez (S)",
                "Sal Stewart (R)",
                "Colson Montgomery (L)",
                "Jarred Kelenic (L)",
                "Ian Happ (S)",
                "Alex Bregman (R)",
                "Paul Goldschmidt (R)",
                "Matt Olson (L)",
                "Jo Adell (R)"
            ]);"""

MANIFEST_FB = (
    '<script type="application/json" id="sheets-manifest-fallback">'
    '{"version":1,"sheets":['
    '{"date":"2026-05-18","label":"May 18, 2026 \\u2014 current slate","href":"/index.html"},'
    '{"date":"2026-05-16","label":"May 16, 2026","href":"/archive/2026-05-16.html"},'
    '{"date":"2026-05-15","label":"May 15, 2026","href":"/archive/2026-05-15.html"},'
    '{"date":"2026-05-14","label":"May 14, 2026","href":"/archive/2026-05-14.html"}'
    "]}</script>"
)

TOP5 = """                    <div class="top-five-list">
                        <div class="top-five-item"><span>Colson Montgomery <small>Rate Field + Taillon RHB leak</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Shea Langeliers <small>Sutter +18% vs McDonald LHB</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Jo Adell <small>Wrobleski LHB lane at Angel Stadium</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Sal Stewart <small>100.4 EV vs Cantillo</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Drake Baldwin <small>Four HR in window vs Tolle</small></span><strong>92</strong></div>
                    </div>"""

PARK_INNER = """
                        <div class="summary-item"><span>SF @ ATH <small>Sutter Health +18% HR, very high receptivity</small></span><strong>+18%</strong></div>
                        <div class="summary-item"><span>CIN @ CLE <small>Progressive +16% HR, 74°F</small></span><strong>+16%</strong></div>
                        <div class="summary-item"><span>BAL @ WAS <small>Nationals Park +11% HR</small></span><strong>+11%</strong></div>
                        <div class="summary-item"><span>TEX @ HOU <small>Daikin roof closed, +5% HR</small></span><strong>+5%</strong></div>
                    """

WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Shea Langeliers <small>Sutter carry vs McDonald</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#2 Colson Montgomery <small>Rate Field + Taillon leak</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#3 Lawrence Butler <small>Sacramento wind receptivity</small></span><strong>83</strong></div>
                        <div class="summary-item"><span>#4 Nick Kurtz <small>Sutter + McDonald LHB</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#5 Kyle Manzardo <small>Progressive +16% row</small></span><strong>84</strong></div>
                    """

LONGSHOT_INNER = """
                        <div class="summary-item"><span>J.P. Crawford <small>+980 vs Buehler</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>Ezequiel Duran <small>+820 vs deGrom</small></span><strong>78</strong></div>
                        <div class="summary-item"><span>Spencer Steer <small>+750 vs Cantillo</small></span><strong>79</strong></div>
                        <div class="summary-item"><span>Teoscar Hernandez <small>+790 vs Soriano</small></span><strong>82</strong></div>
                    """

FADES_INNER = """
                        <div class="summary-item"><span>SD @ SEA <small>T-Mobile -11% HR, 55°F, 57% rain</small></span><strong>-11%</strong></div>
                        <div class="summary-item"><span>MIL @ MIN <small>Target Field -7% HR</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>BOS @ ATL <small>Truist -8% HR row</small></span><strong>-8%</strong></div>
                        <div class="summary-item"><span>PHI @ PIT <small>PNC -8% HR row</small></span><strong>-8%</strong></div>
                    """


def replace_summary_list(text, heading, inner):
    pat = rf'(<h3>{re.escape(heading)}</h3>\s*<div class="summary-list">)(.*?)(</div>)'
    return re.sub(pat, r"\1" + inner + r"\3", text, count=1, flags=re.DOTALL)


def main() -> None:
    shutil.copy2(SRC, DST)
    text = DST.read_text(encoding="utf-8")
    text = re.sub(r"const games = \[.*?\];", GAMES_BLOCK, text, count=1, flags=re.DOTALL)
    text = re.sub(
        r"const WORST_PICKZ_FAVORITE_NAMES = new Set\(\[[\s\S]*?\]\);",
        FAV_SET,
        text,
        count=1,
    )
    text = text.replace('content="2026-05-15"', 'content="2026-05-16"')
    text = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        lambda _m: MANIFEST_FB,
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p>(?:Friday|Saturday|Sunday|Monday), May \d+, 2026 — Worst Pickz HR cheat sheet",
        "<p>Saturday, May 16, 2026 — Worst Pickz HR cheat sheet",
        text,
        count=1,
    )
    text = re.sub(
        r"This board covers <strong>\d+ listed HR props</strong> across <strong>\d+ games</strong>, with <strong>\d+ Worst Pickz Favorite</strong>",
        "This board covers <strong>41 listed HR props</strong> across <strong>9 games</strong>, with <strong>9 Worst Pickz Favorite</strong>",
        text,
        count=1,
    )
    text = re.sub(
        r'<div class="top-five-list">.*?</motion.div>\s*(?=\s*</motion.div>\s*<div class="summary-card">)|'
        r'<div class="top-five-list">.*?</div>\s*(?=\s*</motion.div>\s*<div class="summary-card">)|'
        r'<div class="top-five-list">.*?</div>\s*(?=\s*</div>\s*<div class="summary-card">)',
        TOP5 + "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = replace_summary_list(text, "Best Park / Weather HR Rows (slate)", PARK_INNER)
    text = replace_summary_list(text, "Top 5 Weather Heavy HR Plays", WEATHER5_INNER)
    text = replace_summary_list(text, "Best longshot HR (listed +700+)", LONGSHOT_INNER)
    text = replace_summary_list(text, "Harsh Environment Fades", FADES_INNER)
    DST.write_text(text, encoding="utf-8")
    print("Wrote", DST)


if __name__ == "__main__":
    main()
