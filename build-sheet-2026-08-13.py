#!/usr/bin/env python3
"""Generate games[] block for 2026-08-13 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Brice Turang (L)",
    "Bryce Harper (L)",
    "Endy Rodriguez (S)",
    "Griffin Conine (L)",
    "Jackson Chourio (R)",
    "Kody Clemens (L)",
    "Kyle Schwarber (L)",
    "Munetaka Murakami (L)",
}

GEMS = {
    "Brandon Lowe (L)",
    "Dylan Crews (R)",
    "Jarren Duran (L)",
    "Joc Pederson (L)",
    "Miguel Vargas (R)",
    "Nathaniel Lowe (L)",
    "Rhys Hoskins (R)",
    "Spencer Jones (L)",
    "Tyler Stephenson (R)",
    "William Contreras (R)",
}

PLAYER_TEAMS = {
    "Abimelec Ortiz (L)": "WSH",
    "Alejandro Kirk (R)": "TOR",
    "Andy Pages (R)": "LAD",
    "Angel Genao (S)": "CLE",
    "Ben Rice (L)": "NYY",
    "Brady House (R)": "WSH",
    "Brandon Lowe (L)": "PIT",
    "Brice Turang (L)": "MIL",
    "Bryan De La Cruz (R)": "PHI",
    "Bryce Harper (L)": "PHI",
    "Bryson Stott (L)": "PHI",
    "Chase DeLauter (L)": "CLE",
    "Corey Seager (L)": "TEX",
    "Daylen Lile (L)": "WSH",
    "Derek Hill (R)": "PHI",
    "Dillon Dingler (R)": "DET",
    "Dylan Crews (R)": "WSH",
    "Eduardo Valencia (R)": "DET",
    "Endy Rodriguez (S)": "PIT",
    "Enrique Hernandez (R)": "LAD",
    "Ernie Clement (R)": "TOR",
    "Ezequiel Duran (R)": "TEX",
    "Garrett Mitchell (L)": "MIL",
    "Griffin Conine (L)": "MIA",
    "Heliot Ramos (R)": "NYY",
    "JJ Bleday (L)": "CIN",
    "Jackson Chourio (R)": "MIL",
    "Jacob Gonzalez (L)": "PIT",
    "Jake Bauers (L)": "MIL",
    "James Outman (L)": "DET",
    "Jarren Duran (L)": "BOS",
    "Jo Adell (R)": "CLE",
    "Joc Pederson (L)": "TEX",
    "Josh Bell (S)": "MIN",
    "Kazuma Okamoto (R)": "TOR",
    "Keibert Ruiz (S)": "WSH",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Kyle Tucker (L)": "LAD",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Moises Ballesteros (L)": "LAA",
    "Mookie Betts (R)": "LAD",
    "Munetaka Murakami (L)": "CWS",
    "Nathaniel Lowe (L)": "CLE",
    "Owen Caissie (L)": "MIA",
    "Rhys Hoskins (R)": "CLE",
    "Royce Lewis (R)": "MIN",
    "Spencer Jones (L)": "NYY",
    "Teoscar Hernandez (R)": "LAD",
    "Travis d'Arnaud (R)": "LAA",
    "Trent Grisham (L)": "NYY",
    "Tyler Stephenson (R)": "CIN",
    "Vaughn Grissom (R)": "LAA",
    "Victor Caratini (S)": "MIN",
    "William Contreras (R)": "MIL",
    "Wilyer Abreu (L)": "BOS",
}

BUM_MATCHUPS = {
    ("BOS @ TOR", "Scherzer"),
    ("PHI @ MIN", "Nola"),
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
    chip_last = chip.split()[-1] if chip else chip
    if (game_key, chip) not in BUM_MATCHUPS and (game_key, chip_last) not in BUM_MATCHUPS:
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
        "title": "BOS @ TOR - Payton Tolle (L, BOS) vs Max Scherzer 🧤 (R, TOR)",
        "description": "Tail key data: Park boost +10% (stadium +7%, weather +3%). Tolle (HR risk 0.34, vs LHB +0.31, vs RHB +0.31). Scherzer 🧤 (HR risk 1.73, vs LHB +1.54, vs RHB +1.59).",
        "rows": [
            row("Kazuma Okamoto", "R", "+432", 72, "", ["vs Tolle"], """1 HR, 2 near-HR, 94.3 mph EV. Tolle RHB split +0.31, HR risk 0.34.""", blast="good"),
            row("Alejandro Kirk", "R", "+650", 70, "", ["vs Tolle"], """1 HR, 1 near-HR, 93.2 mph EV. Tolle RHB split +0.31, HR risk 0.34.""", blast="good"),
            row("Ernie Clement", "R", "+870", 68, "", ["vs Tolle"], """1 HR, 1 near-HR, 91.9 mph EV. Tolle RHB split +0.31, HR risk 0.34.""", blast="good"),
            row("Jarren Duran", "L", "+437", 93, "🌕 💣 💎", ["vs Scherzer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 97.5 mph EV. Scherzer LHB split +1.54, HR risk 1.73.""", blast="good"),
            row("Wilyer Abreu", "L", "+329", 95, "🌕 💣", ["vs Scherzer"], """2 HR, 2 near-HR, 92.5 mph EV. Scherzer LHB split +1.54, HR risk 1.73.""", blast="high"),
        ],
    },
    {
        "title": "CHC @ WSH - Kevin Gausman (R, CHC) vs Cade Cavalli (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Gausman (HR risk -0.75, vs LHB -0.78, vs RHB -0.37). Cavalli (HR risk 0.46, vs LHB +0.33, vs RHB +0.43).",
        "rows": [
            row("Brady House", "R", "N/A", 58, "", ["vs Gausman"], """0 HR, 2 near-HR, 92.8 mph EV. Gausman RHB split -0.37, HR risk -0.75. slight split headwind (-0.37); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Dylan Crews", "R", "+475", 58, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 91.8 mph EV. Gausman RHB split -0.37, HR risk -0.75. slight split headwind (-0.37); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Abimelec Ortiz", "L", "+541", 58, "", ["vs Gausman"], """1 HR, 1 near-HR, 92.9 mph EV. Gausman LHB split -0.78, HR risk -0.75. tough split lane (-0.78); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Daylen Lile", "L", "+528", 58, "", ["vs Gausman"], """1 HR, 2 near-HR, 93.3 mph EV. Gausman LHB split -0.78, HR risk -0.75. tough split lane (-0.78); pitcher suppresses HR (-0.75).""", blast="good"),
            row("Keibert Ruiz", "S", "+750", 58, "", ["vs Gausman"], """0 HR, 91.4 mph EV. Gausman SHB→RHB split -0.37, HR risk -0.75. slight split headwind (-0.37); pitcher suppresses HR (-0.75)."""),
        ],
    },
    {
        "title": "CIN @ CWS - Andrew Abbott (L, CIN) vs Davis Martin (R, CWS)",
        "description": "Tail key data: Park boost data unavailable. Abbott (HR risk -0.59, vs LHB -0.56, vs RHB -0.40). Martin (HR risk -0.02, vs LHB +0.30, vs RHB -0.39).",
        "rows": [
            row("Munetaka Murakami", "L", "+381", 58, "⭐", ["vs Abbott"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 97.7 mph EV. Abbott LHB split -0.56, HR risk -0.59. tough split lane (-0.56); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Miguel Vargas", "R", "+389", 58, "💎", ["vs Abbott"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.9 mph EV. Abbott RHB split -0.40, HR risk -0.59. tough split lane (-0.40); pitcher suppresses HR (-0.59).""", blast="good"),
            row("Tyler Stephenson", "R", "+700", 61, "💎", ["vs Martin"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.5 mph EV. Martin RHB split -0.39, HR risk -0.02. slight split headwind (-0.39); pitcher risk below avg (-0.02).""", blast="good"),
            row("JJ Bleday", "L", "+450", 63, "", ["vs Martin"], """1 HR, 1 near-HR, 91.8 mph EV. Martin LHB split +0.30, HR risk -0.02. pitcher risk below avg (-0.02).""", blast="good"),
        ],
    },
    {
        "title": "CLE @ DET - Parker Messick (L, CLE) vs Keider Montero (R, DET)",
        "description": "Tail key data: Park boost -3% (stadium -9%, weather +6%). Messick (HR risk -0.66, vs LHB -0.64, vs RHB -0.47). Montero (HR risk 0.06, vs LHB +0.28, vs RHB -0.06).",
        "rows": [
            row("Eduardo Valencia", "R", "N/A", 63, "🌕 💣", ["vs Messick"], """2 HR, 2 near-HR, 95.2 mph EV. Messick RHB split -0.47, HR risk -0.66. tough split lane (-0.47); pitcher suppresses HR (-0.66).""", blast="high"),
            row("James Outman", "L", "N/A", 58, "", ["vs Messick"], """1 HR, 2 near-HR, 95.2 mph EV. Messick LHB split -0.64, HR risk -0.66. tough split lane (-0.64); pitcher suppresses HR (-0.66).""", blast="good"),
            row("Dillon Dingler", "R", "+540", 58, "", ["vs Messick"], """0 HR, 88.0 mph EV. Messick RHB split -0.47, HR risk -0.66. tough split lane (-0.47); pitcher suppresses HR (-0.66)."""),
            row("Jo Adell", "R", "+535", 62, "", ["vs Montero"], """1 HR, 1 near-HR, 93.8 mph EV. Montero RHB split -0.06, HR risk 0.06. slight split headwind (-0.06); park suppresses carry (-9%).""", blast="good"),
            row("Rhys Hoskins", "R", "N/A", 64, "💎", ["vs Montero"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 95.9 mph EV. Montero RHB split -0.06, HR risk 0.06. slight split headwind (-0.06); park suppresses carry (-9%).""", blast="good"),
            row("Nathaniel Lowe", "L", "+475", 66, "💎", ["vs Montero"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 94.1 mph EV. Montero LHB split +0.28, HR risk 0.06. park suppresses carry (-9%).""", blast="good"),
            row("Angel Genao", "S", "+800", 63, "", ["vs Montero"], """0 HR, 1 near-HR, 97.0 mph EV. Montero SHB→LHB split +0.28, HR risk 0.06. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
            row("Chase DeLauter", "L", "+524", 61, "", ["vs Montero"], """0 HR, 1 near-HR, 94.2 mph EV. Montero LHB split +0.28, HR risk 0.06. park suppresses carry (-9%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ LAD - Shane Drohan (L, MIL) vs Roki Sasaki (R, LAD)",
        "description": "Tail key data: Park boost +12% (stadium +19%, weather -6%). Drohan (HR risk 0.12, vs LHB -0.81, vs RHB +0.49). Sasaki (HR risk 0.19, vs LHB -0.24, vs RHB +0.91).",
        "rows": [
            row("Teoscar Hernandez", "R", "+438", 82, "🌕 💣", ["vs Drohan"], """2 HR, 3 near-HR, 91.4 mph EV. Drohan RHB split +0.49, HR risk 0.12. weather carry headwind (-6%).""", blast="high"),
            row("Mookie Betts", "R", "+470", 72, "", ["vs Drohan"], """1 HR, 2 near-HR, 93.8 mph EV. Drohan RHB split +0.49, HR risk 0.12. weather carry headwind (-6%).""", blast="good"),
            row("Andy Pages", "R", "+400", 68, "", ["vs Drohan"], """1 HR, 1 near-HR, 91.6 mph EV. Drohan RHB split +0.49, HR risk 0.12. weather carry headwind (-6%).""", blast="good"),
            row("Enrique Hernandez", "R", "N/A", 69, "", ["vs Drohan"], """1 HR, 1 near-HR, 92.7 mph EV. Drohan RHB split +0.49, HR risk 0.12. weather carry headwind (-6%).""", blast="good"),
            row("Kyle Tucker", "L", "+560", 58, "", ["vs Drohan"], """0 HR, 1 near-HR, 92.6 mph EV. Drohan LHB split -0.81, HR risk 0.12. tough split lane (-0.81); weather carry headwind (-6%).""", blast="good"),
            row("Jackson Chourio", "R", "+360", 90, "⭐ 🌕 💣", ["vs Sasaki"], """Worst Pickz Favorite. 2 HR, 3 near-HR, 99.3 mph EV. Sasaki RHB split +0.91, HR risk 0.19. weather carry headwind (-6%).""", blast="high"),
            row("William Contreras", "R", "+540", 75, "💎", ["vs Sasaki"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 93.5 mph EV. Sasaki RHB split +0.91, HR risk 0.19. weather carry headwind (-6%).""", blast="good"),
            row("Brice Turang", "L", "+565", 62, "⭐", ["vs Sasaki"], """Worst Pickz Favorite. 0 HR, 96.4 mph EV. Sasaki LHB split -0.24, HR risk 0.19. slight split headwind (-0.24); weather carry headwind (-6%).""", blast="good"),
            row("Jake Bauers", "L", "+419", 61, "", ["vs Sasaki"], """0 HR, 1 near-HR, 94.1 mph EV. Sasaki LHB split -0.24, HR risk 0.19. slight split headwind (-0.24); weather carry headwind (-6%).""", blast="good"),
            row("Garrett Mitchell", "L", "+574", 60, "", ["vs Sasaki"], """0 HR, 94.6 mph EV. Sasaki LHB split -0.24, HR risk 0.19. slight split headwind (-0.24); weather carry headwind (-6%).""", blast="good"),
        ],
    },
    {
        "title": "PHI @ MIN - Aaron Nola 🧤 (R, PHI) vs Taj Bradley (R, MIN)",
        "description": "Tail key data: Park boost data unavailable. Nola 🧤 (HR risk 1.23, vs LHB +1.05, vs RHB +0.87). Bradley (HR risk -0.16, vs LHB +0.35, vs RHB -0.79).",
        "rows": [
            row("Kody Clemens", "L", "+354", 87, "⭐", ["vs Nola"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 94.2 mph EV. Nola LHB split +1.05, HR risk 1.23.""", blast="good"),
            row("Josh Bell", "S", "+470", 74, "", ["vs Nola"], """0 HR, 90.9 mph EV. Nola SHB→LHB split +1.05, HR risk 1.23. limited recent HR events."""),
            row("Royce Lewis", "R", "+450", 85, "", ["vs Nola"], """1 HR, 2 near-HR, 91.7 mph EV. Nola RHB split +0.87, HR risk 1.23.""", blast="good"),
            row("Victor Caratini", "S", "N/A", 81, "", ["vs Nola"], """0 HR, 1 near-HR, 92.0 mph EV. Nola SHB→LHB split +1.05, HR risk 1.23. limited recent HR events.""", blast="good"),
            row("Bryce Harper", "L", "+403", 67, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 98.2 mph EV. Bradley LHB split +0.35, HR risk -0.16. pitcher risk below avg (-0.16).""", blast="good"),
            row("Kyle Schwarber", "L", "+250", 62, "⭐", ["vs Bradley"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.3 mph EV. Bradley LHB split +0.35, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", blast="good"),
            row("Derek Hill", "R", "N/A", 58, "", ["vs Bradley"], """1 HR, 1 near-HR, 86.9 mph EV. Bradley RHB split -0.79, HR risk -0.16. tough split lane (-0.79); pitcher risk below avg (-0.16).""", blast="good"),
            row("Bryson Stott", "L", "+725", 59, "", ["vs Bradley"], """0 HR, 94.3 mph EV. Bradley LHB split +0.35, HR risk -0.16. pitcher risk below avg (-0.16); limited recent HR events.""", blast="good"),
            row("Bryan De La Cruz", "R", "N/A", 58, "", ["vs Bradley"], """0 HR, 93.5 mph EV. Bradley RHB split -0.79, HR risk -0.16. tough split lane (-0.79); pitcher risk below avg (-0.16).""", blast="good"),
        ],
    },
    {
        "title": "PIT @ MIA - Braxton Ashcraft (R, PIT) vs Tyler Phillips (R, MIA)",
        "description": "Tail key data: Park boost -13% (stadium -13%, weather +0%). Ashcraft (HR risk 0.46, vs LHB +0.45, vs RHB +0.27). Phillips (HR risk 0.21, vs LHB -0.30, vs RHB +0.61).",
        "rows": [
            row("Griffin Conine", "L", "+501", 89, "🚀 ⭐ 🌕 💣", ["vs Ashcraft"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 102.2 mph EV. Ashcraft LHB split +0.45, HR risk 0.46. park/weather net drag (-13%).""", blast="high"),
            row("Owen Caissie", "L", "+650", 79, "🌕 💣", ["vs Ashcraft"], """2 HR, 2 near-HR, 93.5 mph EV. Ashcraft LHB split +0.45, HR risk 0.46. park/weather net drag (-13%).""", blast="high"),
            row("Brandon Lowe", "L", "+390", 61, "💎", ["vs Phillips"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.4 mph EV. Phillips LHB split -0.30, HR risk 0.21. slight split headwind (-0.30); park/weather net drag (-13%).""", blast="good"),
            row("Jacob Gonzalez", "L", "+780", 61, "", ["vs Phillips"], """1 HR, 1 near-HR, 97.2 mph EV. Phillips LHB split -0.30, HR risk 0.21. slight split headwind (-0.30); park/weather net drag (-13%).""", blast="good"),
            row("Endy Rodriguez", "S", "N/A", 68, "⭐", ["vs Phillips"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.0 mph EV. Phillips SHB→RHB split +0.61, HR risk 0.21. park/weather net drag (-13%).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ NYY - Logan Gilbert (R, SEA) vs Max Fried (L, NYY)",
        "description": "Tail key data: Park boost +22% (stadium +6%, weather +16%). Gilbert (HR risk 0.46, vs LHB +0.20, vs RHB +0.58). Fried (HR risk -1.83, vs LHB -1.16, vs RHB -1.52).",
        "rows": [
            row("Ben Rice", "L", "+310", 72, "⭐", ["vs Gilbert"], """Worst Pickz Favorite. 0 HR, 95.2 mph EV. Gilbert LHB split +0.20, HR risk 0.46. limited recent HR events.""", blast="good"),
            row("Trent Grisham", "L", "+313", 71, "", ["vs Gilbert"], """1 HR, 1 near-HR, 88.0 mph EV. Gilbert LHB split +0.20, HR risk 0.46.""", blast="good"),
            row("Spencer Jones", "L", "+496", 71, "💎", ["vs Gilbert"], """Worst Pickz Hidden Gem. 0 HR, 1 near-HR, 92.2 mph EV. Gilbert LHB split +0.20, HR risk 0.46. limited recent HR events.""", blast="good"),
            row("Heliot Ramos", "R", "+440", 67, "", ["vs Gilbert"], """0 HR, 91.2 mph EV. Gilbert RHB split +0.58, HR risk 0.46. limited recent HR events."""),
        ],
    },
    {
        "title": "TEX @ LAA - Jacob deGrom (R, TEX) vs Walbert Urena (R, LAA)",
        "description": "Tail key data: Park boost -7% (stadium -8%, weather +2%). deGrom (HR risk 0.05, vs LHB +0.54, vs RHB -0.70). Urena (HR risk -1.30, vs LHB -0.85, vs RHB -1.36).",
        "rows": [
            row("Moises Ballesteros", "L", "+630", 58, "", ["vs deGrom"], """0 HR, 88.6 mph EV. deGrom LHB split +0.54, HR risk 0.05. park/weather net drag (-7%); limited recent HR events."""),
            row("Mike Trout", "R", "+354", 58, "", ["vs deGrom"], """1 HR, 1 near-HR, 96.8 mph EV. deGrom RHB split -0.70, HR risk 0.05. tough split lane (-0.70); park/weather net drag (-7%).""", blast="good"),
            row("Travis d'Arnaud", "R", "N/A", 58, "", ["vs deGrom"], """0 HR, 1 near-HR, 94.8 mph EV. deGrom RHB split -0.70, HR risk 0.05. tough split lane (-0.70); park/weather net drag (-7%).""", blast="good"),
            row("Vaughn Grissom", "R", "+950", 62, "🌕 💣", ["vs deGrom"], """2 HR, 2 near-HR, 89.9 mph EV. deGrom RHB split -0.70, HR risk 0.05. tough split lane (-0.70); park/weather net drag (-7%).""", blast="high"),
            row("Ezequiel Duran", "R", "+900", 58, "", ["vs Urena"], """1 HR, 1 near-HR, 93.9 mph EV. Urena RHB split -1.36, HR risk -1.30. tough split lane (-1.36); pitcher suppresses HR (-1.30).""", blast="good"),
            row("Joc Pederson", "L", "+345", 58, "💎", ["vs Urena"], """Worst Pickz Hidden Gem. 0 HR, 91.8 mph EV. Urena LHB split -0.85, HR risk -1.30. tough split lane (-0.85); pitcher suppresses HR (-1.30)."""),
            row("Corey Seager", "L", "+401", 58, "", ["vs Urena"], """0 HR, 92.1 mph EV. Urena LHB split -0.85, HR risk -1.30. tough split lane (-0.85); pitcher suppresses HR (-1.30).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-08-13")

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

    out = ROOT / '_games-0813.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
