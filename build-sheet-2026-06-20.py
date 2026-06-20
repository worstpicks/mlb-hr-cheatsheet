#!/usr/bin/env python3
"""Generate games[] block for 2026-06-20 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bryan Reynolds (S)",
    "Kyle Schwarber (L)",
    "Max Muncy (R)",
    "Shohei Ohtani (L)",
}

GEMS = {
    "Endy Rodriguez (S)",
    "Travis Bazzana (L)",
}

PLAYER_TEAMS = {
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Carson Benge (L)": "NYM",
    "Christian Walker (R)": "HOU",
    "Corbin Carroll (L)": "ARI",
    "Donovan Walton (L)": "LAA",
    "Endy Rodriguez (S)": "PIT",
    "Freddie Freeman (L)": "LAD",
    "Gabriel Arias (R)": "CLE",
    "Gabriel Moreno (R)": "ARI",
    "Geraldo Perdomo (S)": "ARI",
    "Jarren Duran (L)": "BOS",
    "Jeremy Pena (R)": "HOU",
    "Josh Naylor (L)": "SEA",
    "Julio Rodriguez (R)": "SEA",
    "Kody Clemens (L)": "MIN",
    "Kyle Karros (R)": "COL",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Lawrence Butler (L)": "ATH",
    "Mark Vientos (R)": "NYM",
    "Max Muncy (R)": "ATH",
    "Mitch Garver (R)": "SEA",
    "Mookie Betts (R)": "LAD",
    "Nick Kurtz (L)": "ATH",
    "Rob Refsnyder (R)": "SEA",
    "Royce Lewis (R)": "MIN",
    "Ryan O'Hearn (L)": "PIT",
    "Shohei Ohtani (L)": "LAD",
    "Travis Bazzana (L)": "CLE",
    "Trevor Larnach (L)": "MIN",
    "Tyler Callihan (L)": "PIT",
    "Tyler Soderstrom (L)": "ATH",
    "Wilyer Abreu (L)": "BOS",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Bradley",
    "Early",
    "Sugano",
}

def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"

def row(name, hand, odds, score, emojis, chips, note, blast=None):
    item = {
        "name": f"{name} ({hand})",
        "odds": odds_text(odds),
        "score": score,
        "emojis": emojis,
        "note": note,
        "chips": chips,
    }
    if blast:
        item["blast"] = blast
    return item

def add_bum_row_emojis(entry):
    chip = entry["chips"][0].replace("vs ", "").strip()
    if chip not in BUM_PITCHERS:
        return
    em = entry["emojis"]
    if "⚾" not in em:
        em = f"{em} ⚾".strip()
    if "🕊️" not in em:
        em = f"{em} 🕊️".strip()
    if "🧤" not in em:
        em = f"{em} 🧤".strip()
    entry["emojis"] = em

games = [
    {
        "title": "BAL @ LAD - Trevor Rogers (L, BAL) vs Yoshinobu Yamamoto (R, LAD)",
        "description": "Tail key data: Park boost +6% (stadium +18%, weather -12%). Rogers (HR risk 0.11, vs LHB -0.81, vs RHB +0.47). Yamamoto (HR risk -0.86, vs LHB -0.51, vs RHB -0.55).",
        "rows": [
            row("Shohei Ohtani", "L", "+250", 89, "⭐ 🌕 💣", ["vs Rogers"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.6 mph EV. Rogers LHB split -0.81, HR risk 0.11. tough split lane (-0.81); weather carry headwind (-12%).""", blast="high"),
            row("Mookie Betts", "R", "+420", 66, "", ["vs Rogers"], """0 HR, 91.5 mph EV. Rogers RHB split +0.47, HR risk 0.11. weather carry headwind (-12%); limited recent HR events."""),
            row("Freddie Freeman", "L", "+549", 72, "", ["vs Rogers"], """1 HR, 1 near-HR, 90.3 mph EV. Rogers LHB split -0.81, HR risk 0.11. tough split lane (-0.81); weather carry headwind (-12%).""", blast="good"),
        ],
    },
    {
        "title": "BOS @ SEA - Connelly Early 🧤 (L, BOS) vs Emerson Hancock (R, SEA)",
        "description": "Tail key data: Park boost +2% (stadium +0%, weather +2%). Early 🧤 (HR risk 1.02, vs LHB -0.04, vs RHB +1.22). Hancock (HR risk 0.48, vs LHB +0.73, vs RHB -0.06).",
        "rows": [
            row("Mitch Garver", "R", "+475", 70, "", ["vs Early"], """1 HR, 1 near-HR, 88.5 mph EV. Early RHB split +1.22, HR risk 1.02.""", blast="good"),
            row("Julio Rodriguez", "R", "+435", 78, "", ["vs Early"], """1 HR, 2 near-HR, 94.0 mph EV. Early RHB split +1.22, HR risk 1.02.""", blast="good"),
            row("Josh Naylor", "L", "+760", 76, "", ["vs Early"], """1 HR, 2 near-HR, 91.6 mph EV. Early LHB split -0.04, HR risk 1.02. slight split headwind (-0.04).""", blast="good"),
            row("Rob Refsnyder", "R", "+690", 71, "", ["vs Early"], """1 HR, 1 near-HR, 88.8 mph EV. Early RHB split +1.22, HR risk 1.02.""", blast="good"),
            row("Wilyer Abreu", "L", "+410", 76, "", ["vs Hancock"], """1 HR, 2 near-HR, 91.8 mph EV. Hancock LHB split +0.73, HR risk 0.48.""", blast="good"),
            row("Jarren Duran", "L", "+488", 72, "", ["vs Hancock"], """1 HR, 1 near-HR, 90.0 mph EV. Hancock LHB split +0.73, HR risk 0.48.""", blast="good"),
        ],
    },
    {
        "title": "CLE @ HOU - Joey Cantillo (L, CLE) vs Spencer Arrighetti (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +6%, weather -1%). Cantillo (HR risk 0.86, vs LHB +0.25, vs RHB +0.88). Arrighetti (HR risk -0.85, vs LHB -1.03, vs RHB +0.06).",
        "rows": [
            row("Jeremy Pena", "R", "+680", 77, "", ["vs Cantillo"], """1 HR, 1 near-HR, 95.3 mph EV. Cantillo RHB split +0.88, HR risk 0.86.""", blast="good"),
            row("Yordan Alvarez", "L", "+285", 68, "", ["vs Cantillo"], """0 HR, 92.0 mph EV. Cantillo LHB split +0.25, HR risk 0.86. limited recent HR events.""", blast="good"),
            row("Christian Walker", "R", "+420", 70, "", ["vs Cantillo"], """1 HR, 1 near-HR, 80.7 mph EV. Cantillo RHB split +0.88, HR risk 0.86. lighter EV form (80.7 mph).""", blast="good"),
            row("Kyle Manzardo", "L", "+521", 71, "", ["vs Arrighetti"], """0 HR, 1 near-HR, 92.8 mph EV. Arrighetti LHB split -1.03, HR risk -0.85. tough split lane (-1.03); pitcher suppresses HR (-0.85).""", blast="good"),
            row("Travis Bazzana", "L", "+730", 80, "🌕 💣 💎", ["vs Arrighetti"], """Worst Pickz Hidden Gem. 1 HR, 4 near-HR, 89.7 mph EV. Arrighetti LHB split -1.03, HR risk -0.85. tough split lane (-1.03); pitcher suppresses HR (-0.85).""", blast="high"),
            row("Gabriel Arias", "R", "+590", 70, "", ["vs Arrighetti"], """1 HR, 1 near-HR, 88.5 mph EV. Arrighetti RHB split +0.06, HR risk -0.85. pitcher suppresses HR (-0.85).""", blast="good"),
        ],
    },
    {
        "title": "LAA @ ATH - Walbert Urena (R, LAA) vs J.T. Ginn (R, ATH)",
        "description": "Tail key data: Park boost +34% (stadium +31%, weather +4%). Urena (HR risk -0.66, vs LHB -0.30, vs RHB -0.48). Ginn (HR risk -0.26, vs LHB +0.05, vs RHB -0.23).",
        "rows": [
            row("Max Muncy", "R", "N/A", 72, "⭐", ["vs Urena"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 87.0 mph EV. Urena RHB split -0.48, HR risk -0.66. tough split lane (-0.48); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Lawrence Butler", "L", "+630", 78, "", ["vs Urena"], """1 HR, 3 near-HR, 91.7 mph EV. Urena LHB split -0.30, HR risk -0.66. slight split headwind (-0.30); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Nick Kurtz", "L", "+270", 73, "", ["vs Urena"], """1 HR, 1 near-HR, 91.4 mph EV. Urena LHB split -0.30, HR risk -0.66. slight split headwind (-0.30); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Tyler Soderstrom", "L", "+465", 80, "🌕 💣", ["vs Urena"], """2 HR, 2 near-HR, 89.7 mph EV. Urena LHB split -0.30, HR risk -0.66. slight split headwind (-0.30); pitcher suppresses HR (-0.66).""", blast="high"),
            row("Zach Neto", "R", "+371", 72, "", ["vs Ginn"], """1 HR, 2 near-HR, 87.5 mph EV. Ginn RHB split -0.23, HR risk -0.26. slight split headwind (-0.23); pitcher risk below avg (-0.26).""", blast="good"),
            row("Donovan Walton", "L", "+750", 72, "", ["vs Ginn"], """1 HR, 2 near-HR, 85.5 mph EV. Ginn LHB split +0.05, HR risk -0.26. pitcher risk below avg (-0.26); lighter EV form (85.5 mph).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ ARI - Taj Bradley 🧤 (R, MIN) vs Zac Gallen (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -8%, weather +0%). Bradley 🧤 (HR risk 1.45, vs LHB +1.88, vs RHB -0.34). Gallen (HR risk 0.86, vs LHB +0.80, vs RHB +0.50).",
        "rows": [
            row("Gabriel Moreno", "R", "+800", 86, "🌕 💣", ["vs Bradley"], """2 HR, 2 near-HR, 96.3 mph EV. Bradley RHB split -0.34, HR risk 1.45. slight split headwind (-0.34); park/weather net drag (-8%).""", blast="high"),
            row("Corbin Carroll", "L", "+380", 70, "", ["vs Bradley"], """1 HR, 1 near-HR, 86.6 mph EV. Bradley LHB split +1.88, HR risk 1.45. park/weather net drag (-8%); lighter EV form (86.6 mph).""", blast="good"),
            row("Geraldo Perdomo", "S", "+1060", 76, "", ["vs Bradley"], """1 HR, 2 near-HR, 92.5 mph EV. Bradley RHB split -0.34, HR risk 1.45. slight split headwind (-0.34); park/weather net drag (-8%).""", blast="good"),
            row("Byron Buxton", "R", "+264", 83, "🌕 💣", ["vs Gallen"], """2 HR, 3 near-HR, 90.8 mph EV. Gallen RHB split +0.50, HR risk 0.86. park/weather net drag (-8%).""", blast="high"),
            row("Royce Lewis", "R", "+517", 82, "🌕 💣", ["vs Gallen"], """2 HR, 3 near-HR, 90.1 mph EV. Gallen RHB split +0.50, HR risk 0.86. park/weather net drag (-8%).""", blast="high"),
            row("Kody Clemens", "L", "+397", 82, "🌕 💣", ["vs Gallen"], """2 HR, 3 near-HR, 89.7 mph EV. Gallen LHB split +0.80, HR risk 0.86. park/weather net drag (-8%).""", blast="high"),
            row("Trevor Larnach", "L", "+800", 71, "", ["vs Gallen"], """1 HR, 1 near-HR, 89.1 mph EV. Gallen LHB split +0.80, HR risk 0.86. park/weather net drag (-8%).""", blast="good"),
        ],
    },
    {
        "title": "NYM @ PHI - Freddy Peralta (R, NYM) vs Cristopher Sanchez (L, PHI)",
        "description": "Tail key data: Park boost +13% (stadium +14%, weather -1%). Peralta (HR risk -0.03, vs LHB +0.46, vs RHB -1.10). Sanchez (HR risk -0.39, vs LHB -1.00, vs RHB +0.04).",
        "rows": [
            row("Kyle Schwarber", "L", "+220", 79, "⭐", ["vs Peralta"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.1 mph EV. Peralta LHB split +0.46, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="good"),
            row("Brandon Marsh", "L", "+680", 81, "🌕 💣", ["vs Peralta"], """2 HR, 3 near-HR, 89.2 mph EV. Peralta LHB split +0.46, HR risk -0.03. pitcher risk below avg (-0.03).""", blast="high"),
            row("Bryce Harper", "L", "+410", 72, "", ["vs Peralta"], """1 HR, 2 near-HR, 87.2 mph EV. Peralta LHB split +0.46, HR risk -0.03. pitcher risk below avg (-0.03); lighter EV form (87.2 mph).""", blast="good"),
            row("Mark Vientos", "R", "+700", 70, "", ["vs Sanchez"], """1 HR, 1 near-HR, 84.5 mph EV. Sanchez RHB split +0.04, HR risk -0.39. pitcher risk below avg (-0.39); lighter EV form (84.5 mph).""", blast="good"),
            row("Carson Benge", "L", "+1140", 77, "", ["vs Sanchez"], """1 HR, 1 near-HR, 94.7 mph EV. Sanchez LHB split -1.00, HR risk -0.39. tough split lane (-1.00); pitcher risk below avg (-0.39).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ COL - Paul Skenes (R, PIT) vs Tomoyuki Sugano 🧤 (R, COL)",
        "description": "Tail key data: Park boost +19% (stadium +20%, weather -1%). Skenes (HR risk -0.27, vs LHB -0.25, vs RHB +0.12). Sugano 🧤 (HR risk 1.15, vs LHB +1.45, vs RHB +0.18).",
        "rows": [
            row("Kyle Karros", "R", "+980", 70, "", ["vs Skenes"], """1 HR, 1 near-HR, 86.0 mph EV. Skenes RHB split +0.12, HR risk -0.27. pitcher risk below avg (-0.27); lighter EV form (86.0 mph).""", blast="good"),
            row("Endy Rodriguez", "S", "+470", 88, "🌕 💣 💎", ["vs Sugano"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 98.1 mph EV. Sugano RHB split +0.18, HR risk 1.15.""", blast="high"),
            row("Tyler Callihan", "L", "+491", 78, "", ["vs Sugano"], """1 HR, 2 near-HR, 94.0 mph EV. Sugano LHB split +1.45, HR risk 1.15.""", blast="good"),
            row("Bryan Reynolds", "S", "+350", 84, "⭐ 🌕 💣", ["vs Sugano"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.4 mph EV. Sugano RHB split +0.18, HR risk 1.15.""", blast="high"),
            row("Brandon Lowe", "L", "+235", 71, "", ["vs Sugano"], """1 HR, 1 near-HR, 88.8 mph EV. Sugano LHB split +1.45, HR risk 1.15.""", blast="good"),
            row("Ryan O'Hearn", "L", "+410", 71, "", ["vs Sugano"], """0 HR, 1 near-HR, 92.7 mph EV. Sugano LHB split +1.45, HR risk 1.15. limited recent HR events.""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-20")

if __name__ == '__main__':
    def js_string(value):
        return json.dumps(value, ensure_ascii=False)

    def emit_games_js(games_data):
        out = ['const games = [']
        for game in games_data:
            out.append('    {')
            out.append(f"        title: {js_string(game['title'])},")
            out.append(f"        description: {js_string(game['description'])},")
            if game.get("startTime"):
                out.append(f"        startTime: {js_string(game['startTime'])},")
            out.append('        rows: [')
            for entry in game['rows']:
                parts = [
                    f"name: {js_string(entry['name'])}",
                    f"odds: {js_string(entry['odds'])}",
                    f"score: {entry['score']}",
                    f"emojis: {js_string(entry['emojis'])}",
                    f"note: {js_string(entry['note'])}",
                    f"chips: {js_string(entry['chips'])}",
                ]
                if entry.get('blast'):
                    parts.append(f"blast: {js_string(entry['blast'])}")
                out.append('            { ' + ', '.join(parts) + ' },')
            out.append('        ],')
            out.append('    },')
        out.append('];')
        return '\n'.join(out)

    out = ROOT / '_games-0620.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
