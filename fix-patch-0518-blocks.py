#!/usr/bin/env python3
import re
from pathlib import Path

p = Path(__file__).parent / "patch-0518-index.py"
t = p.read_text(encoding="utf-8")

blocks = {
    "TOP5": '''TOP5 = """                    <div class="top-five-list">
                        <div class="top-five-item"><span>Shea Langeliers <small>Four HR vs Urena at Angel Stadium</small></span><strong>94</strong></div>
                        <div class="top-five-item"><span>Austin Riley <small>Three HR vs Meyer in Miami</small></span><strong>93</strong></div>
                        <div class="top-five-item"><span>Coby Mayo <small>Rogers RHB lane at Tropicana</small></span><strong>91</strong></div>
                        <div class="top-five-item"><span>Byron Buxton <small>.842 SLG vs Rojas at Target</small></span><strong>92</strong></div>
                        <div class="top-five-item"><span>Seiya Suzuki <small>Wrigley +42% vs Sproat</small></span><strong>90</strong></div>
                    </div>"""''',
    "WEATHER5_INNER": '''WEATHER5_INNER = """
                        <div class="summary-item"><span>#1 Shea Langeliers <small>Angel Stadium carry vs Urena</small></span><strong>94</strong></div>
                        <div class="summary-item"><span>#2 Seiya Suzuki <small>Wrigley +42% HR row</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#3 Kyle Schwarber <small>Citizens Bank +31% vs Lodolo</small></span><strong>90</strong></div>
                        <div class="summary-item"><span>#4 James Wood <small>Nationals Park 92°F vs Irvin</small></span><strong>89</strong></div>
                        <div class="summary-item"><span>#5 Bobby Witt Jr. <small>Kauffman +35% wind out</small></span><strong>87</strong></div>
                    """''',
    "PARK_INNER": '''PARK_INNER = """
                        <div class="summary-item"><span>MIL @ CHC <small>Wrigley +42% HR, 17 mph out</small></span><strong>+42%</strong></div>
                        <div class="summary-item"><span>BOS @ KC <small>Kauffman +35% HR, 18 mph out</small></span><strong>+35%</strong></div>
                        <div class="summary-item"><span>CIN @ PHI <small>Citizens Bank +31% HR, 88°F</small></span><strong>+31%</strong></div>
                        <div class="summary-item"><span>NYM @ WSH <small>Nationals Park +9% HR, 92°F</small></span><strong>+9%</strong></div>
                    """''',
    "LONGSHOT_INNER": '''LONGSHOT_INNER = """
                        <div class="summary-item"><span>Luis Arraez <small>+1800 vs Ray at Chase</small></span><strong>68</strong></div>
                        <div class="summary-item"><span>Harrison Bader <small>+1200 vs Ray</small></span><strong>70</strong></div>
                        <div class="summary-item"><span>Kyle Karros <small>+1050 vs Quintana at Coors</small></span><strong>76</strong></div>
                        <div class="summary-item"><span>Travis Bazzana <small>+1500 vs Valdez</small></span><strong>72</strong></div>
                    """''',
    "FADES_INNER": '''FADES_INNER = """
                        <div class="summary-item"><span>CHW @ SEA <small>T-Mobile -21% runs row, dome</small></span><strong>-21%</strong></div>
                        <div class="summary-item"><span>LAD @ SD <small>Petco -7% HR row</small></span><strong>-7%</strong></div>
                        <div class="summary-item"><span>BAL @ TB <small>Tropicana dome -6% HR</small></span><strong>-6%</strong></div>
                        <div class="summary-item"><span>TEX @ COL <small>Coors cold 36°F suppresses carry</small></span><strong>~flat</strong></div>
                    """''',
}

for name, block in blocks.items():
    t = re.sub(rf"{name} = .*?(?=\n\n[A-Z_]+ = |\ndef )", block + "\n\n", t, count=1, flags=re.DOTALL)

t = re.sub(
    r"MANIFEST_FB = \(.*?\)\n",
    """MANIFEST_FB = (
    '<script type="application/json" id="sheets-manifest-fallback">'
    '{"version":1,"sheets":[{"date":"2026-05-18","label":"May 18, 2026 \\u2014 current slate","href":"/index.html"},'
    '{"date":"2026-05-16","label":"May 16, 2026","href":"/archive/2026-05-16.html"},'
    '{"date":"2026-05-15","label":"May 15, 2026","href":"/archive/2026-05-15.html"}]}'
    "</script>"
)

""",
    t,
    count=1,
    flags=re.DOTALL,
)

if "sheet-date" not in t:
    t = t.replace(
        "    text = text.replace('content=\"2026-05-16\"', 'content=\"2026-05-18\"')",
        "    text = text.replace('content=\"2026-05-16\"', 'content=\"2026-05-18\"')\n"
        "    text = re.sub(r'<meta name=\"sheet-date\" content=\"2026-05-\\d+\">', "
        "'<meta name=\"sheet-date\" content=\"2026-05-18\">', text, count=1)",
    )

t = re.sub(
    r"text = text\.replace\(\s*\"<p>[^\"]+Worst Pickz HR cheat sheet\"[^)]+\)",
    'text = re.sub(\n        r"<p>(?:Friday|Saturday|Monday), May \\d+, 2026 — Worst Pickz HR cheat sheet",\n        "<p>Monday, May 18, 2026 — Worst Pickz HR cheat sheet",\n        text,\n        count=1,\n    )',
    t,
    count=1,
    flags=re.DOTALL,
)

t = t.replace(
    "41 listed HR props</strong> across <strong>9 games</strong>, with <strong>9 Worst Pickz Favorite</strong>",
    "88 listed HR props</strong> across <strong>14 games</strong>, with <strong>17 Worst Pickz Favorite</strong>",
)

p.write_text(t, encoding="utf-8")
print("ok", t.count("motion.div"))
