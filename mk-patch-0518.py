#!/usr/bin/env python3
"""Build patch-0518-index.py from patch-0516-index.py template."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
src = (ROOT / "patch-0516-index.py").read_text(encoding="utf-8")
src = src.replace("2026-05-16", "2026-05-18")
src = src.replace("_games-0516.txt", "_games-0518.txt")
src = src.replace("local only.", "local only, do not deploy.")

src = re.sub(
    r"FAV_SET = \"\"\"[\s\S]*?\"\"\";",
    '''FAV_SET = """            const WORST_PICKZ_FAVORITE_NAMES = new Set([
                "JJ Bleday (L)",
                "Will Benson (L)",
                "James Wood (L)",
                "Juan Soto (L)",
                "Byron Buxton (R)",
                "Yordan Alvarez (L)",
                "Bobby Witt Jr. (R)",
                "Ian Happ (S)",
                "Michael Busch (L)",
                "Michael Conforto (L)",
                "Hunter Goodman (R)",
                "Miguel Vargas (R)",
                "Gavin Sheets (L)",
                "Jackson Merrill (L)",
                "Julio Rodriguez (R)",
                "Will Smith (R)",
                "Shohei Ohtani (L)"
            ]);"""''',
    src,
    count=1,
)

src = re.sub(
    r"MANIFEST_FB = \([\s\S]*?\)",
    '''MANIFEST_FB = (
    '<script type="application/json" id="sheets-manifest-fallback">'
    '{"version":1,"sheets":[{"date":"2026-05-18","label":"May 18, 2026 \\\\u2014 current slate","href":"/index.html"},'
    '{"date":"2026-05-16","label":"May 16, 2026","href":"/archive/2026-05-16.html"},'
    '{"date":"2026-05-15","label":"May 15, 2026","href":"/archive/2026-05-15.html"}]}'
    "</script>"
)''',
    src,
    count=1,
)

src = re.sub(
    r"TOP5 = \"\"\"[\s\S]*?\"\"\"",
    '''TOP5 = """                    <div class="top-five-list">
                        <motion.div class="top-five-item"><span>Shea Langeliers <small>Four HR vs Urena at Angel Stadium</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Austin Riley <small>Three HR vs Meyer in Miami</small></span><strong>93</strong></div>
                        <motion.div class="top-five-item"><span>Byron Buxton <small>.842 SLG vs Rojas at Target</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Coby Mayo <small>Rogers RHB lane at Tropicana</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                    </div>"""''',
    src,
    count=1,
)

src = re.sub(
    r"WEATHER5_INNER = \"\"\"[\s\S]*?\"\"\"",
    '''WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Kyle Schwarber <small>Citizens Bank +31% vs Lodolo</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#2 James Wood <small>Nationals Park 92°F vs Irvin</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#3 Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#4 Michael Conforto <small>Wrigley wind row vs Sproat</small></span><strong>86</strong></div>
                        <div class="summary-item"><span>#5 Michael Massey <small>Kauffman +35% vs Gray</small></span><strong>84</strong></motion.div>
                    """''',
    src,
    count=1,
)

src = re.sub(
    r"PARK_INNER = \"\"\"[\s\S]*?\"\"\"",
    '''PARK_INNER = """
                        <div class="summary-item"><span>MIL @ CHC <small>Wrigley +42% HR, 17 mph out</small></span><strong>+42%</strong></div>
                        <div class="summary-item"><span>BOS @ KC <small>Kauffman +35% HR, 18 mph out</small></span><strong>+35%</strong></div>
                        <div class="summary-item"><span>CIN @ PHI <small>Citizens Bank +31% HR, 88°F</small></span><strong>+31%</strong></div>
                        <div class="summary-item"><span>NYM @ WSH <small>Nationals Park +9% HR, 92°F</small></span><strong>+9%</strong></div>
                    """''',
    src,
    count=1,
)

src = re.sub(
    r"LONGSHOT_INNER = \"\"\"[\s\S]*?\"\"\"",
    '''LONGSHOT_INNER = """
                        <div class="summary-item"><span>Travis Bazzana <small>+1500 vs Valdez</small></span><strong>72</strong></div>
                        <div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray</small></span><strong>68</strong></div>
                        <div class="summary-item"><span>Harrison Bader <small>+1200 vs Ray</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Ernie Clement <small>+1120 vs Weathers</small></span><strong>68</strong></div>
                    """''',
    src,
    count=1,
)

src = re.sub(
    r"FADES_INNER = \"\"\"[\s\S]*?\"\"\"",
    '''FADES_INNER = """
                        <div class="summary-item"><span>CHW @ SEA <small>T-Mobile -21% HR, 61°F dome</small></span><strong>-21%</strong></div>
                        <div class="summary-item"><span>LAD @ SD <small>Petco -7% HR row</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>BAL @ TB <small>Tropicana dome -6% HR</small></span><strong>-6%</strong></div>
                        <div class="summary-item"><span>TEX @ COL <small>Coors 36°F — weather suppresses carry</small></span><strong>~flat</strong></div>
                    """''',
    src,
    count=1,
)

# patch_file tweaks for 5/18
src = src.replace(
    'text = text.replace(\'content="2026-05-15"\', \'content="2026-05-18"\')',
    '''text = re.sub(
        r'<meta name="sheet-date" content="[^"]*">',
        '<meta name="sheet-date" content="2026-05-18">',
        text,
        count=1,
    )''',
)
src = src.replace(
    "<p>Saturday, May 16, 2026 — Worst Pickz HR cheat sheet",
    '<p>Monday, May 18, 2026 — Worst Pickz HR cheat sheet',
)
src = src.replace(
    "This board covers <strong>41 listed HR props</strong> across <strong>9 games</strong>, with <strong>9 Worst Pickz Favorite</strong>",
    "This board covers <strong>91 listed HR props</strong> across <strong>14 games</strong>, with <strong>17 Worst Pickz Favorite</strong>",
)

# strip accidental motion.div from generator strings
src = src.replace("<motion.div", "<motion.div").replace("<motion.div", "<div").replace("</motion.div>", "</div>")
src = src.replace("<motion.div", "<div")

out = ROOT / "patch-0518-index.py"
out.write_text(src, encoding="utf-8")
print("wrote", out)
