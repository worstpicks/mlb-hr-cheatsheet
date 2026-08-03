#!/usr/bin/env python3
"""Generate games[] block for 2026-08-03 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Enrique Hernandez (R)",
    "George Springer (R)",
    "Jake Bauers (L)",
    "Jeremy Pena (R)",
    "Spencer Horwitz (L)",
    "Spencer Jones (L)",
    "Vladimir Guerrero Jr. (R)",
}

GEMS = {
    "Andres Chaparro (R)",
    "Bryce Eldridge (L)",
    "Geraldo Perdomo (S)",
    "Grant McCray (L)",
    "Jordan Walker (R)",
    "Junior Caminero (R)",
    "Kazuma Okamoto (R)",
    "Kyle Tucker (L)",
    "Luis Garcia Jr. (L)",
    "Manny Machado (R)",
    "Ty France (R)",
}

PLAYER_TEAMS = {
    "Alec Burleson (L)": "STL",
    "Alex Bregman (R)": "CHC",
    "Andres Chaparro (R)": "WSH",
    "Andrew Vaughn (R)": "MIL",
    "Ben Rice (L)": "NYY",
    "Brandon Lowe (L)": "PIT",
    "Brandon Marsh (L)": "PHI",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryce Harper (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Cole Carrigg (S)": "COL",
    "Corbin Carroll (L)": "ARI",
    "Corey Seager (L)": "TEX",
    "Dalton Rushing (L)": "LAD",
    "Dansby Swanson (R)": "CHC",
    "Derek Hill (R)": "PHI",
    "Drew Gilbert (L)": "SF",
    "Dylan Crews (R)": "WSH",
    "Enrique Hernandez (R)": "LAD",
    "Esmerlyn Valdez (R)": "PIT",
    "George Springer (R)": "TOR",
    "Geraldo Perdomo (S)": "ARI",
    "Grant McCray (L)": "SF",
    "Harry Ford (R)": "WSH",
    "Hunter Goodman (R)": "COL",
    "J.T. Realmuto (R)": "PHI",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeremy Pena (R)": "HOU",
    "Joey Ortiz (R)": "MIL",
    "Jordan Walker (R)": "STL",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Luis Garcia Jr. (L)": "NYY",
    "Manny Machado (R)": "SD",
    "Max Muncy (L)": "LAD",
    "Michael Conforto (L)": "CHC",
    "Nick Fortes (R)": "TB",
    "Nico Hoerner (R)": "CHC",
    "Osleivis Basabe (R)": "SF",
    "Pedro Ramirez (S)": "CHC",
    "Rafael Devers (L)": "SF",
    "Ryan McMahon (L)": "NYY",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Jones (L)": "NYY",
    "Taylor Trammell (L)": "HOU",
    "Ty France (R)": "SD",
    "Victor Mesa Jr. (L)": "TB",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Willi Castro (S)": "COL",
    "Wyatt Langford (R)": "TEX",
}

BUM_MATCHUPS = {
    ("WSH @ PHI", "Nola"),
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
        "title": "LAD @ CHC - Justin Wrobleski (L, LAD) vs Matthew Boyd (L, CHC)",
        "description": "Tail key data: Park boost -10% (stadium -2%, weather -8%). Wrobleski (HR risk 0.15, vs LHB +0.05, vs RHB +0.25). Boyd (HR risk -0.56, vs LHB -0.53, vs RHB -0.37).",
        "rows": [
            row("Michael Conforto", "L", "N/A", 73, "🚀 🌕 💣", ["vs Wrobleski"], """2 HR, 2 near-HR, 102.6 mph EV. Wrobleski LHB split +0.05, HR risk 0.15. park/weather net drag (-10%).""", blast="high"),
            row("Dansby Swanson", "R", "+600", 61, "", ["vs Wrobleski"], """1 HR, 1 near-HR, 91.3 mph EV. Wrobleski RHB split +0.25, HR risk 0.15. park/weather net drag (-10%).""", blast="good"),
            row("Pedro Ramirez", "S", "N/A", 65, "", ["vs Wrobleski"], """1 HR, 1 near-HR, 98.9 mph EV. Wrobleski SHB→RHB split +0.25, HR risk 0.15. park/weather net drag (-10%).""", blast="good"),
            row("Alex Bregman", "R", "+540", 63, "", ["vs Wrobleski"], """1 HR, 1 near-HR, 93.5 mph EV. Wrobleski RHB split +0.25, HR risk 0.15. park/weather net drag (-10%).""", blast="good"),
            row("Nico Hoerner", "R", "+1080", 58, "", ["vs Wrobleski"], """0 HR, 1 near-HR, 91.4 mph EV. Wrobleski RHB split +0.25, HR risk 0.15. park/weather net drag (-10%); limited recent HR events."""),
            row("Enrique Hernandez", "R", "N/A", 58, "⭐", ["vs Boyd"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.4 mph EV. Boyd RHB split -0.37, HR risk -0.56. slight split headwind (-0.37); pitcher suppresses HR (-0.56).""", blast="good"),
            row("Shohei Ohtani", "L", "+349", 58, "", ["vs Boyd"], """1 HR, 1 near-HR, 92.4 mph EV. Boyd LHB split -0.53, HR risk -0.56. tough split lane (-0.53); pitcher suppresses HR (-0.56).""", blast="good"),
            row("Kyle Tucker", "L", "+610", 58, "💎", ["vs Boyd"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.2 mph EV. Boyd LHB split -0.53, HR risk -0.56. tough split lane (-0.53); pitcher suppresses HR (-0.56).""", blast="good"),
            row("Max Muncy", "L", "+512", 58, "🌕 💣", ["vs Boyd"], """2 HR, 2 near-HR, 90.0 mph EV. Boyd LHB split -0.53, HR risk -0.56. tough split lane (-0.53); pitcher suppresses HR (-0.56).""", blast="high"),
            row("Dalton Rushing", "L", "+620", 58, "", ["vs Boyd"], """0 HR, 91.2 mph EV. Boyd LHB split -0.53, HR risk -0.56. tough split lane (-0.53); pitcher suppresses HR (-0.56)."""),
        ],
    },
    {
        "title": "PIT @ MIL - Bubba Chandler (R, PIT) vs Brandon Sproat (R, MIL)",
        "description": "Tail key data: Park boost +4% (stadium +11%, weather -7%). Chandler (HR risk -1.10, vs LHB -0.35, vs RHB -1.33). Sproat (HR risk 0.38, vs LHB +0.07, vs RHB +0.53).",
        "rows": [
            row("Jake Bauers", "L", "+431", 67, "🚀 ⭐ 🌕 💣", ["vs Chandler"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 100.5 mph EV. Chandler LHB split -0.35, HR risk -1.10. slight split headwind (-0.35); pitcher suppresses HR (-1.10).""", blast="high"),
            row("Andrew Vaughn", "R", "N/A", 58, "", ["vs Chandler"], """0 HR, 95.0 mph EV. Chandler RHB split -1.33, HR risk -1.10. tough split lane (-1.33); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Joey Ortiz", "R", "N/A", 58, "", ["vs Chandler"], """0 HR, 1 near-HR, 97.8 mph EV. Chandler RHB split -1.33, HR risk -1.10. tough split lane (-1.33); pitcher suppresses HR (-1.10).""", blast="good"),
            row("Brandon Lowe", "L", "+355", 69, "", ["vs Sproat"], """1 HR, 1 near-HR, 98.1 mph EV. Sproat LHB split +0.07, HR risk 0.38. weather carry headwind (-7%).""", blast="good"),
            row("Bryan Reynolds", "S", "+520", 73, "", ["vs Sproat"], """1 HR, 1 near-HR, 97.0 mph EV. Sproat SHB→RHB split +0.53, HR risk 0.38. weather carry headwind (-7%).""", blast="good"),
            row("Spencer Horwitz", "L", "+600", 69, "⭐", ["vs Sproat"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.6 mph EV. Sproat LHB split +0.07, HR risk 0.38. weather carry headwind (-7%).""", blast="good"),
            row("Esmerlyn Valdez", "R", "+400", 68, "", ["vs Sproat"], """1 HR, 1 near-HR, 91.2 mph EV. Sproat RHB split +0.53, HR risk 0.38. weather carry headwind (-7%).""", blast="good"),
        ],
    },
    {
        "title": "SD @ ARI - Michael King (R, SD) vs Brandon Pfaadt (R, ARI)",
        "description": "Tail key data: Park boost -9% (stadium -9%, weather +0%). King (HR risk -0.31, vs LHB -0.32, vs RHB -0.15). Pfaadt (HR risk -0.83, vs LHB -0.63, vs RHB -0.56).",
        "rows": [
            row("Corbin Carroll", "L", "+403", 58, "", ["vs King"], """0 HR, 98.9 mph EV. King LHB split -0.32, HR risk -0.31. slight split headwind (-0.32); pitcher risk below avg (-0.31).""", blast="good"),
            row("Geraldo Perdomo", "S", "+1000", 58, "💎", ["vs King"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 86.8 mph EV. King SHB→RHB split -0.15, HR risk -0.31. slight split headwind (-0.15); pitcher risk below avg (-0.31).""", blast="good"),
            row("Ty France", "R", "+550", 58, "💎", ["vs Pfaadt"], """Worst Pickz Hidden Gem. 0 HR, 94.4 mph EV. Pfaadt RHB split -0.56, HR risk -0.83. tough split lane (-0.56); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Jackson Merrill", "L", "+600", 58, "", ["vs Pfaadt"], """1 HR, 2 near-HR, 91.9 mph EV. Pfaadt LHB split -0.63, HR risk -0.83. tough split lane (-0.63); pitcher suppresses HR (-0.83).""", blast="good"),
            row("Manny Machado", "R", "+436", 58, "💎", ["vs Pfaadt"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 95.8 mph EV. Pfaadt RHB split -0.56, HR risk -0.83. tough split lane (-0.56); pitcher suppresses HR (-0.83).""", blast="good"),
        ],
    },
    {
        "title": "SF @ TEX - Logan Webb (R, SF) vs Cal Quantrill (R, TEX)",
        "description": "Tail key data: Park boost -10% (stadium -10%, weather -1%). Webb (HR risk -0.66, vs LHB -0.54, vs RHB -0.51). Quantrill (HR risk 0.40, vs LHB +0.55, vs RHB +0.25).",
        "rows": [
            row("Corey Seager", "L", "+450", 58, "", ["vs Webb"], """1 HR, 2 near-HR, 93.4 mph EV. Webb LHB split -0.54, HR risk -0.66. tough split lane (-0.54); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Wyatt Langford", "R", "+492", 58, "", ["vs Webb"], """0 HR, 93.6 mph EV. Webb RHB split -0.51, HR risk -0.66. tough split lane (-0.51); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Osleivis Basabe", "R", "N/A", 71, "", ["vs Quantrill"], """1 HR, 1 near-HR, 97.1 mph EV. Quantrill RHB split +0.25, HR risk 0.40. park/weather net drag (-10%).""", blast="good"),
            row("Bryce Eldridge", "L", "+390", 66, "💎", ["vs Quantrill"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 89.5 mph EV. Quantrill LHB split +0.55, HR risk 0.40. park/weather net drag (-10%).""", blast="good"),
            row("Grant McCray", "L", "+640", 63, "💎", ["vs Quantrill"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 85.4 mph EV. Quantrill LHB split +0.55, HR risk 0.40. park/weather net drag (-10%); lighter EV form (85.4 mph).""", blast="good"),
            row("Rafael Devers", "L", "+308", 67, "", ["vs Quantrill"], """1 HR, 1 near-HR, 89.9 mph EV. Quantrill LHB split +0.55, HR risk 0.40. park/weather net drag (-10%).""", blast="good"),
            row("Drew Gilbert", "L", "+625", 64, "", ["vs Quantrill"], """0 HR, 92.6 mph EV. Quantrill LHB split +0.55, HR risk 0.40. park/weather net drag (-10%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "STL @ NYY - Michael McGreevy (R, STL) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost +18% (stadium +3%, weather +15%). McGreevy (HR risk 0.44, vs LHB +0.32, vs RHB +0.30). Schlittler (HR risk -0.71, vs LHB -0.61, vs RHB -0.30).",
        "rows": [
            row("Jazz Chisholm Jr.", "L", "+400", 88, "🌕 💣", ["vs McGreevy"], """2 HR, 2 near-HR, 97.0 mph EV. McGreevy LHB split +0.32, HR risk 0.44.""", blast="high"),
            row("Luis Garcia Jr.", "L", "+381", 70, "💎", ["vs McGreevy"], """Worst Pickz Hidden Gem. 0 HR, 92.6 mph EV. McGreevy LHB split +0.32, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Ryan McMahon", "L", "+480", 73, "", ["vs McGreevy"], """0 HR, 1 near-HR, 94.0 mph EV. McGreevy LHB split +0.32, HR risk 0.44. limited recent HR events.""", blast="good"),
            row("Spencer Jones", "L", "+428", 77, "⭐", ["vs McGreevy"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 93.2 mph EV. McGreevy LHB split +0.32, HR risk 0.44.""", blast="good"),
            row("Ben Rice", "L", "+296", 74, "", ["vs McGreevy"], """1 HR, 2 near-HR, 90.4 mph EV. McGreevy LHB split +0.32, HR risk 0.44.""", blast="good"),
            row("Alec Burleson", "L", "+462", 58, "", ["vs Schlittler"], """0 HR, 1 near-HR, 94.3 mph EV. Schlittler LHB split -0.61, HR risk -0.71. tough split lane (-0.61); pitcher suppresses HR (-0.71).""", blast="good"),
            row("Jordan Walker", "R", "+406", 58, "💎", ["vs Schlittler"], """Worst Pickz Hidden Gem. 0 HR, 91.4 mph EV. Schlittler RHB split -0.30, HR risk -0.71. slight split headwind (-0.30); pitcher suppresses HR (-0.71)."""),
        ],
    },
    {
        "title": "TB @ COL - Ian Seymour (L, TB) vs Michael Lorenzen (R, COL)",
        "description": "Tail key data: Park boost +22% (stadium +18%, weather +4%). Seymour (HR risk 0.79, vs LHB +1.88, vs RHB -0.15). Lorenzen (HR risk 0.36, vs LHB +0.61, vs RHB -0.34).",
        "rows": [
            row("Willi Castro", "S", "+568", 92, "🌕 💣", ["vs Seymour"], """2 HR, 2 near-HR, 80.9 mph EV. Seymour SHB→LHB split +1.88, HR risk 0.79. lighter EV form (80.9 mph).""", blast="high"),
            row("Cole Carrigg", "S", "+500", 87, "", ["vs Seymour"], """0 HR, 2 near-HR, 90.2 mph EV. Seymour SHB→LHB split +1.88, HR risk 0.79.""", blast="good"),
            row("Hunter Goodman", "R", "+321", 69, "", ["vs Seymour"], """1 HR, 1 near-HR, 85.1 mph EV. Seymour RHB split -0.15, HR risk 0.79. slight split headwind (-0.15); lighter EV form (85.1 mph).""", blast="good"),
            row("Junior Caminero", "R", "+310", 76, "💎", ["vs Lorenzen"], """Worst Pickz Hidden Gem. 1 HR, 3 near-HR, 95.1 mph EV. Lorenzen RHB split -0.34, HR risk 0.36. slight split headwind (-0.34).""", blast="good"),
            row("Nick Fortes", "R", "N/A", 62, "", ["vs Lorenzen"], """1 HR, 1 near-HR, 87.5 mph EV. Lorenzen RHB split -0.34, HR risk 0.36. slight split headwind (-0.34); lighter EV form (87.5 mph).""", blast="good"),
            row("Victor Mesa Jr.", "L", "+480", 78, "🌕 💣", ["vs Lorenzen"], """2 HR, 1 near-HR, 88.1 mph EV. Lorenzen LHB split +0.61, HR risk 0.36.""", blast="high"),
        ],
    },
    {
        "title": "TOR @ HOU - Shane Bieber (R, TOR) vs Cristian Javier (R, HOU)",
        "description": "Tail key data: Park boost +5% (stadium +6%, weather -1%). Bieber (HR risk 0.76, vs LHB -0.16, vs RHB +1.41). Javier (HR risk -0.01, vs LHB -1.02, vs RHB +1.12).",
        "rows": [
            row("Jeremy Pena", "R", "+600", 94, "⭐ 🌕 💣", ["vs Bieber"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 94.1 mph EV. Bieber RHB split +1.41, HR risk 0.76.""", blast="high"),
            row("Taylor Trammell", "L", "+750", 65, "", ["vs Bieber"], """1 HR, 1 near-HR, 87.1 mph EV. Bieber LHB split -0.16, HR risk 0.76. slight split headwind (-0.16); lighter EV form (87.1 mph).""", blast="good"),
            row("George Springer", "R", "+440", 77, "⭐ 🌕 💣", ["vs Javier"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 89.2 mph EV. Javier RHB split +1.12, HR risk -0.01. pitcher risk below avg (-0.01).""", blast="high"),
            row("Kazuma Okamoto", "R", "+376", 65, "💎", ["vs Javier"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 83.4 mph EV. Javier RHB split +1.12, HR risk -0.01. pitcher risk below avg (-0.01); lighter EV form (83.4 mph).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "+501", 68, "⭐", ["vs Javier"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 93.6 mph EV. Javier RHB split +1.12, HR risk -0.01. pitcher risk below avg (-0.01); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "WSH @ PHI - Trevor Williams (R, WSH) vs Aaron Nola 🧤 (R, PHI)",
        "description": "Tail key data: Park boost data unavailable. Williams (HR risk 0.20, vs LHB +0.10, vs RHB +0.30). Nola 🧤 (HR risk 1.45, vs LHB +1.28, vs RHB +0.35).",
        "rows": [
            row("Bryce Harper", "L", "+290", 76, "🌕 💣", ["vs Williams"], """2 HR, 2 near-HR, 95.5 mph EV. Williams LHB split +0.10, HR risk 0.20.""", blast="high"),
            row("Kyle Schwarber", "L", "+200", 62, "", ["vs Williams"], """0 HR, 97.1 mph EV. Williams LHB split +0.10, HR risk 0.20. limited recent HR events.""", blast="good"),
            row("Brandon Marsh", "L", "+450", 58, "", ["vs Williams"], """0 HR, 89.4 mph EV. Williams LHB split +0.10, HR risk 0.20. limited recent HR events."""),
            row("Derek Hill", "R", "N/A", 61, "", ["vs Williams"], """1 HR, 1 near-HR, 88.6 mph EV. Williams RHB split +0.30, HR risk 0.20.""", blast="good"),
            row("J.T. Realmuto", "R", "+540", 65, "", ["vs Williams"], """0 HR, 1 near-HR, 97.4 mph EV. Williams RHB split +0.30, HR risk 0.20. limited recent HR events.""", blast="good"),
            row("CJ Abrams", "L", "+320", 88, "🌕 💣", ["vs Nola"], """1 HR, 1 near-HR, 91.7 mph EV. Nola LHB split +1.28, HR risk 1.45.""", blast="good"),
            row("Andres Chaparro", "R", "+390", 89, "🌕 💣 💎", ["vs Nola"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 90.6 mph EV. Nola RHB split +0.35, HR risk 1.45.""", blast="high"),
            row("Harry Ford", "R", "+830", 81, "", ["vs Nola"], """1 HR, 1 near-HR, 92.0 mph EV. Nola RHB split +0.35, HR risk 1.45.""", blast="good"),
            row("Dylan Crews", "R", "+526", 82, "", ["vs Nola"], """1 HR, 1 near-HR, 92.3 mph EV. Nola RHB split +0.35, HR risk 1.45.""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-03")

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

    out = ROOT / '_games-0803.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
