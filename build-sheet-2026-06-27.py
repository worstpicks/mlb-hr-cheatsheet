#!/usr/bin/env python3
"""Generate games[] block for 2026-06-27 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Byron Buxton (R)",
    "Junior Caminero (R)",
    "Logan O'Hoppe (R)",
    "Manny Machado (R)",
    "Max Muncy (L)",
    "Max Muncy (R)",
    "Mookie Betts (R)",
    "Nick Kurtz (L)",
    "Owen Caissie (L)",
    "Rafael Devers (L)",
    "Rowdy Tellez (L)",
    "Seiya Suzuki (R)",
    "Shohei Ohtani (L)",
    "William Contreras (R)",
    "Zach Neto (R)",
}

GEMS = {
    "Denzer Guzman (R)",
    "Jorge Soler (R)",
    "Victor Mesa Jr. (L)",
}

PLAYER_TEAMS = {
    "Byron Buxton (R)": "MIN",
    "Casey Schmitt (R)": "SF",
    "Coby Mayo (R)": "BAL",
    "Corbin Carroll (L)": "ARI",
    "Denzer Guzman (R)": "LAA",
    "Dominic Canzone (L)": "SEA",
    "Griffin Conine (L)": "MIA",
    "Henry Bolte (R)": "ATH",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ian Happ (S)": "CHC",
    "Ivan Herrera (R)": "STL",
    "Jackson Chourio (R)": "MIL",
    "James Wood (L)": "WSH",
    "Jimmy Crooks (L)": "STL",
    "Jorge Mateo (R)": "ATL",
    "Jorge Soler (R)": "LAA",
    "Junior Caminero (R)": "TB",
    "Kahlil Watson (L)": "CLE",
    "Kody Clemens (L)": "MIN",
    "Kyle Stowers (L)": "MIA",
    "Lars Nootbaar (L)": "STL",
    "Logan O'Hoppe (R)": "LAA",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Max Muncy (R)": "ATH",
    "Mickey Moniak (L)": "COL",
    "Mike Yastrzemski (L)": "ATL",
    "Mookie Betts (R)": "LAD",
    "Nick Kurtz (L)": "ATH",
    "Owen Caissie (L)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Rafael Devers (L)": "SF",
    "Rowdy Tellez (L)": "ATL",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Tommy Troy (R)": "ARI",
    "Ty France (R)": "SD",
    "Victor Caratini (S)": "MIN",
    "Victor Mesa Jr. (L)": "TB",
    "William Contreras (R)": "MIL",
    "Zach Neto (R)": "LAA",
}

BUM_MATCHUPS = {
    ("LAD @ SD", "Vasquez"),
    ("WSH @ BAL", "Griffin"),
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

def add_bum_row_emojis(entry, game_key):
    chip = entry["chips"][0].replace("vs ", "").strip()
    if (game_key, chip) not in BUM_MATCHUPS:
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
        "title": "ARI @ TB - Jose Cabrera (R, ARI) vs Cole Sulser (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +1%). Away starter risk unavailable. Sulser (HR risk 0.13, vs LHB -0.80, vs RHB +1.58).",
        "rows": [
            row("Junior Caminero", "R", "+304", 95, "⭐ 🌕 💣", ["vs Cabrera"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 97.2 mph EV. Cabrera split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Victor Mesa Jr.", "L", "N/A", 89, "🌕 💣 💎", ["vs Cabrera"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.9 mph EV, 50.0% barrels. Cabrera split/risk data unavailable. limited split/risk sample.""", blast="good"),
            row("Corbin Carroll", "L", "+390", 68, "", ["vs Sulser"], """0 HR, 1 near-HR, 90.1 mph EV, 6.2% barrels. Sulser LHB split -0.80, HR risk 0.13. tough split lane (-0.80); limited recent HR events."""),
            row("Tommy Troy", "R", "+1120", 70, "", ["vs Sulser"], """1 HR, 1 near-HR, 87.5 mph EV. Sulser RHB split +1.58, HR risk 0.13. lighter EV form (87.5 mph).""", blast="good"),
        ],
    },
    {
        "title": "ATH @ LAA - Jack Perkins (R, ATH) vs Reid Detmers (L, LAA)",
        "description": "Tail key data: Park boost +8% (stadium +9%, weather +0%). Perkins (HR risk 0.52, vs LHB +0.05, vs RHB +0.66). Detmers (HR risk -0.50, vs LHB -0.66, vs RHB -0.11).",
        "rows": [
            row("Max Muncy", "R", "+550", 62, "⭐", ["vs Detmers"], """Worst Pickz Favorite. 0 HR, 86.0 mph EV. Detmers RHB split -0.11, HR risk -0.50. slight split headwind (-0.11); pitcher suppresses HR (-0.50)."""),
            row("Logan O'Hoppe", "R", "+582", 86, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.5 mph EV. Perkins RHB split +0.66, HR risk 0.52.""", blast="high"),
            row("Denzer Guzman", "R", "+630", 65, "💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 88.9 mph EV. Perkins RHB split +0.66, HR risk 0.52. limited recent HR events."""),
            row("Zach Neto", "R", "+400", 94, "⭐ 🌕 💣", ["vs Perkins"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 96.2 mph EV. Perkins RHB split +0.66, HR risk 0.52.""", blast="high"),
            row("Jorge Soler", "R", "+420", 70, "💎", ["vs Perkins"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 88.2 mph EV. Perkins RHB split +0.66, HR risk 0.52.""", blast="good"),
            row("Nick Kurtz", "L", "+370", 84, "🚀 ⭐", ["vs Detmers"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 107.5 mph EV. Detmers LHB split -0.66, HR risk -0.50. tough split lane (-0.66); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Henry Bolte", "R", "+720", 87, "🌕 💣", ["vs Detmers"], """2 HR, 2 near-HR, 97.2 mph EV. Detmers RHB split -0.11, HR risk -0.50. slight split headwind (-0.11); pitcher suppresses HR (-0.50).""", blast="high"),
        ],
    },
    {
        "title": "ATL @ SF - Bryce Elder (R, ATL) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost -12% (stadium -17%, weather +5%). Elder (HR risk 0.13, vs LHB -0.42, vs RHB +0.94). Webb (HR risk -1.10, vs LHB -0.56, vs RHB -0.85).",
        "rows": [
            row("Rafael Devers", "L", "+360", 88, "⭐ 🌕 💣", ["vs Elder"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 96.4 mph EV. Elder LHB split -0.42, HR risk 0.13. tough split lane (-0.42); park/weather net drag (-12%).""", blast="high"),
            row("Casey Schmitt", "R", "+544", 68, "", ["vs Elder"], """0 HR, 92.4 mph EV. Elder RHB split +0.94, HR risk 0.13. park/weather net drag (-12%); limited recent HR events.""", blast="good"),
            row("Matt Olson", "L", "+450", 80, "", ["vs Webb"], """1 HR, 3 near-HR, 94.1 mph EV. Webb LHB split -0.56, HR risk -1.10. tough split lane (-0.56); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Jorge Mateo", "R", "+1060", 78, "", ["vs Webb"], """1 HR, 1 near-HR, 96.3 mph EV. Webb RHB split -0.85, HR risk -1.10. tough split lane (-0.85); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Mike Yastrzemski", "L", "+870", 73, "", ["vs Webb"], """1 HR, 1 near-HR, 91.4 mph EV. Webb LHB split -0.56, HR risk -1.10. tough split lane (-0.56); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Rowdy Tellez", "L", "N/A", 77, "⭐", ["vs Webb"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.9 mph EV. Webb LHB split -0.56, HR risk -1.10. tough split lane (-0.56); pitcher suppresses HR (-1.10).""", blast="good"),
        ],
    },
    {
        "title": "CHC @ MIL - David Peterson (L, CHC) vs Kyle Harrison (L, MIL)",
        "description": "Tail key data: Park boost +2% (stadium +9%, weather -7%). Peterson (HR risk 0.19, vs LHB +0.64, vs RHB -0.09). Harrison (HR risk 0.35, vs LHB -0.28, vs RHB +0.56).",
        "rows": [
            row("Jackson Chourio", "R", "+460", 73, "", ["vs Peterson"], """1 HR, 1 near-HR, 90.6 mph EV. Peterson RHB split -0.09, HR risk 0.19. slight split headwind (-0.09); weather carry headwind (-7%).""", blast="good"),
            row("William Contreras", "R", "+536", 71, "⭐", ["vs Peterson"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.0 mph EV. Peterson RHB split -0.09, HR risk 0.19. slight split headwind (-0.09); weather carry headwind (-7%).""", blast="good"),
            row("Seiya Suzuki", "R", "+491", 83, "⭐", ["vs Harrison"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.7 mph EV. Harrison RHB split +0.56, HR risk 0.35. weather carry headwind (-7%).""", blast="good"),
            row("Ian Happ", "S", "+427", 70, "", ["vs Harrison"], """1 HR, 1 near-HR, 82.7 mph EV. Harrison RHB split +0.56, HR risk 0.35. weather carry headwind (-7%); lighter EV form (82.7 mph).""", blast="good"),
        ],
    },
    {
        "title": "COL @ MIN - Michael Lorenzen (R, COL) vs Mike Paredes (R, MIN)",
        "description": "Tail key data: Park boost -13% (stadium -7%, weather -6%). Lorenzen (HR risk 0.57, vs LHB +0.38, vs RHB +0.47). Paredes (HR risk -0.36, vs LHB +0.02, vs RHB -0.65).",
        "rows": [
            row("Byron Buxton", "R", "+289", 81, "⭐ 🌕 💣", ["vs Lorenzen"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 89.3 mph EV. Lorenzen RHB split +0.47, HR risk 0.57. park/weather net drag (-13%).""", blast="high"),
            row("Victor Caratini", "S", "+770", 85, "🌕 💣", ["vs Lorenzen"], """2 HR, 3 near-HR, 93.2 mph EV. Lorenzen RHB split +0.47, HR risk 0.57. park/weather net drag (-13%).""", blast="high"),
            row("Kody Clemens", "L", "+430", 78, "", ["vs Lorenzen"], """1 HR, 3 near-HR, 91.8 mph EV. Lorenzen LHB split +0.38, HR risk 0.57. park/weather net drag (-13%).""", blast="good"),
            row("Mickey Moniak", "L", "+442", 64, "", ["vs Paredes"], """0 HR, 90.0 mph EV. Paredes LHB split +0.02, HR risk -0.36. pitcher risk below avg (-0.36); park/weather net drag (-13%)."""),
            row("Hunter Goodman", "R", "+369", 81, "", ["vs Paredes"], """1 HR, 3 near-HR, 94.7 mph EV. Paredes RHB split -0.65, HR risk -0.36. tough split lane (-0.65); pitcher risk below avg (-0.36).""", blast="good"),
        ],
    },
    {
        "title": "LAD @ SD - Yoshinobu Yamamoto (R, LAD) vs Randy Vasquez 🧤 (R, SD)",
        "description": "Tail key data: Park boost -8% (stadium -5%, weather -3%). Yamamoto (HR risk -1.02, vs LHB -0.65, vs RHB -0.68). Vasquez 🧤 (HR risk 1.43, vs LHB +0.32, vs RHB +1.78).",
        "rows": [
            row("Manny Machado", "R", "+520", 87, "⭐ 🌕 💣", ["vs Yamamoto"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 93.1 mph EV. Yamamoto RHB split -0.68, HR risk -1.02. tough split lane (-0.68); pitcher suppresses HR (-1.02).""", blast="high"),
            row("Ty France", "R", "+690", 85, "🌕 💣", ["vs Yamamoto"], """3 HR, 3 near-HR, 89.1 mph EV. Yamamoto RHB split -0.68, HR risk -1.02. tough split lane (-0.68); pitcher suppresses HR (-1.02).""", blast="high"),
            row("Shohei Ohtani", "L", "+193", 92, "⭐ 🌕 💣", ["vs Vasquez"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 95.7 mph EV. Vasquez LHB split +0.32, HR risk 1.43. park/weather net drag (-8%).""", blast="high"),
            row("Max Muncy", "L", "+379", 67, "⭐", ["vs Vasquez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 91.0 mph EV. Vasquez LHB split +0.32, HR risk 1.43. park/weather net drag (-8%); limited recent HR events."""),
            row("Mookie Betts", "R", "+544", 88, "⭐ 🌕 💣", ["vs Vasquez"], """Worst Pickz Favorite. 3 HR, 3 near-HR, 91.5 mph EV. Vasquez RHB split +1.78, HR risk 1.43. park/weather net drag (-8%).""", blast="high"),
        ],
    },
    {
        "title": "MIA @ STL - Ryan Gusto (R, MIA) vs Andre Pallante (R, STL)",
        "description": "Tail key data: Park boost +8% (stadium -10%, weather +17%). Gusto (HR risk 0.22, vs LHB +0.38, vs RHB -0.13). Pallante (HR risk -0.51, vs LHB -0.20, vs RHB -0.44).",
        "rows": [
            row("Lars Nootbaar", "L", "+485", 75, "", ["vs Gusto"], """0 HR, 2 near-HR, 94.7 mph EV. Gusto LHB split +0.38, HR risk 0.22. park suppresses carry (-10%).""", blast="good"),
            row("Ivan Herrera", "R", "+600", 76, "", ["vs Gusto"], """1 HR, 1 near-HR, 93.9 mph EV. Gusto RHB split -0.13, HR risk 0.22. slight split headwind (-0.13); park suppresses carry (-10%).""", blast="good"),
            row("Jimmy Crooks", "L", "+670", 71, "", ["vs Gusto"], """0 HR, 1 near-HR, 93.1 mph EV. Gusto LHB split +0.38, HR risk 0.22. park suppresses carry (-10%); limited recent HR events.""", blast="good"),
            row("Griffin Conine", "L", "+650", 82, "🚀", ["vs Pallante"], """1 HR, 1 near-HR, 100.9 mph EV. Pallante LHB split -0.20, HR risk -0.51. slight split headwind (-0.20); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Kyle Stowers", "L", "+476", 70, "", ["vs Pallante"], """1 HR, 1 near-HR, 83.6 mph EV. Pallante LHB split -0.20, HR risk -0.51. slight split headwind (-0.20); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Owen Caissie", "L", "+690", 80, "⭐", ["vs Pallante"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 96.2 mph EV. Pallante LHB split -0.20, HR risk -0.51. slight split headwind (-0.20); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Heriberto Hernandez", "R", "+670", 78, "", ["vs Pallante"], """1 HR, 2 near-HR, 93.9 mph EV. Pallante RHB split -0.44, HR risk -0.51. tough split lane (-0.44); pitcher suppresses HR (-0.51).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ CLE - Logan Gilbert (R, SEA) vs Slade Cecconi (R, CLE)",
        "description": "Tail key data: Park boost +6% (stadium -2%, weather +7%). Gilbert (HR risk 0.72, vs LHB +0.60, vs RHB +0.40). Cecconi (HR risk 0.00, vs LHB +0.47, vs RHB -0.42).",
        "rows": [
            row("Kahlil Watson", "L", "+680", 81, "", ["vs Gilbert"], """1 HR, 2 near-HR, 96.9 mph EV. Gilbert LHB split +0.60, HR risk 0.72.""", blast="good"),
            row("Luke Raley", "L", "+423", 75, "", ["vs Cecconi"], """0 HR, 2 near-HR, 95.0 mph EV. Cecconi LHB split +0.47, HR risk 0.00.""", blast="good"),
            row("Dominic Canzone", "L", "+520", 78, "", ["vs Cecconi"], """1 HR, 1 near-HR, 95.9 mph EV. Cecconi LHB split +0.47, HR risk 0.00.""", blast="good"),
        ],
    },
    {
        "title": "WSH @ BAL - Foster Griffin 🧤 (L, WSH) vs Brandon Young (R, BAL)",
        "description": "Tail key data: Park boost data unavailable. Griffin 🧤 (HR risk 1.02, vs LHB +0.03, vs RHB +0.96). Young (HR risk -0.45, vs LHB -0.15, vs RHB -0.43).",
        "rows": [
            row("Pete Alonso", "R", "+371", 76, "", ["vs Griffin"], """1 HR, 1 near-HR, 94.1 mph EV. Griffin RHB split +0.96, HR risk 1.02.""", blast="good"),
            row("Coby Mayo", "R", "+364", 84, "🌕 💣", ["vs Griffin"], """2 HR, 2 near-HR, 94.1 mph EV. Griffin RHB split +0.96, HR risk 1.02.""", blast="high"),
            row("James Wood", "L", "+287", 76, "", ["vs Young"], """0 HR, 1 near-HR, 98.2 mph EV. Young LHB split -0.15, HR risk -0.45. slight split headwind (-0.15); pitcher suppresses HR (-0.45).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-27")

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

    out = ROOT / '_games-0627.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
