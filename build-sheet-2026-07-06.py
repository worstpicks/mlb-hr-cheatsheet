#!/usr/bin/env python3
"""Generate games[] block for 2026-07-06 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Carter Jensen (L)",
    "Dalton Rushing (L)",
    "Garrett Mitchell (L)",
    "Hunter Goodman (R)",
    "JJ Wetherholt (L)",
    "Matt Olson (L)",
    "Max Schuemann (R)",
    "Nelson Velazquez (R)",
    "Rafael Devers (L)",
    "Yordan Alvarez (L)",
}

GEMS = {
    "Casey Schmitt (R)",
    "Cole Carrigg (S)",
    "Trent Grisham (L)",
}

PLAYER_TEAMS = {
    "Adrian Del Castillo (L)": "ARI",
    "Andy Pages (R)": "LAD",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Marsh (L)": "PHI",
    "Brandon Valenzuela (S)": "TOR",
    "Bryce Eldridge (L)": "SF",
    "CJ Abrams (L)": "WSH",
    "Cam Smith (R)": "HOU",
    "Carter Jensen (L)": "KC",
    "Casey Schmitt (R)": "SF",
    "Cole Carrigg (S)": "COL",
    "Corbin Carroll (L)": "ARI",
    "Dalton Rushing (L)": "LAD",
    "Drake Baldwin (L)": "ATL",
    "Fernando Tatis Jr. (R)": "SD",
    "Francisco Alvarez (R)": "NYM",
    "Francisco Lindor (S)": "NYM",
    "Garrett Mitchell (L)": "MIL",
    "Gary Sanchez (R)": "MIL",
    "Heliot Ramos (R)": "SF",
    "Hunter Feduccia (L)": "TB",
    "Hunter Goodman (R)": "COL",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jackson Merrill (L)": "SD",
    "Jake Bauers (L)": "MIL",
    "James Wood (L)": "WSH",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "Ketel Marte (S)": "ARI",
    "Kyle Karros (R)": "COL",
    "Kyle Schwarber (L)": "PHI",
    "Luis Garcia Jr. (L)": "WSH",
    "Manny Machado (R)": "SD",
    "Mark Vientos (R)": "NYM",
    "Matt Olson (L)": "ATL",
    "Max Kepler (L)": "ARI",
    "Max Muncy (L)": "LAD",
    "Max Schuemann (R)": "NYY",
    "Michael Harris II (L)": "ATL",
    "Nelson Velazquez (R)": "STL",
    "Rafael Devers (L)": "SF",
    "Sean Keys (L)": "TOR",
    "Trent Grisham (L)": "NYY",
    "Vladimir Guerrero Jr. (R)": "TOR",
    "Yordan Alvarez (L)": "HOU",
}

BUM_MATCHUPS = {
    ("ARI @ SD", "Pfaadt"),
    ("TOR @ SF", "Gausman"),
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
        "title": "ARI @ SD - Brandon Pfaadt 🧤 (R, ARI) vs Walker Buehler (R, SD)",
        "description": "Tail key data: Park boost -2% (stadium -5%, weather +4%). Pfaadt 🧤 (HR risk 1.33, vs LHB +1.65, vs RHB -0.48). Buehler (HR risk 0.49, vs LHB -0.80, vs RHB +1.66).",
        "rows": [
            row("Manny Machado", "R", "+432", 90, "🌕 💣", ["vs Pfaadt"], """2 HR, 4 near-HR, 93.9 mph EV. Pfaadt RHB split -0.48, HR risk 1.33. tough split lane (-0.48).""", blast="high"),
            row("Fernando Tatis Jr.", "R", "+454", 72, "", ["vs Pfaadt"], """0 HR, 97.3 mph EV. Pfaadt RHB split -0.48, HR risk 1.33. tough split lane (-0.48); limited recent HR events.""", blast="good"),
            row("Jackson Merrill", "L", "+500", 90, "🌕 💣", ["vs Pfaadt"], """1 HR, 1 near-HR, 91.9 mph EV. Pfaadt LHB split +1.65, HR risk 1.33.""", blast="good"),
            row("Ketel Marte", "S", "+353", 91, "🌕 💣", ["vs Buehler"], """2 HR, 3 near-HR, 90.6 mph EV. Buehler RHB split +1.66, HR risk 0.49.""", blast="high"),
            row("Corbin Carroll", "L", "+420", 58, "", ["vs Buehler"], """0 HR, 1 near-HR, 87.9 mph EV. Buehler LHB split -0.80, HR risk 0.49. tough split lane (-0.80); limited recent HR events."""),
            row("Max Kepler", "L", "+568", 58, "", ["vs Buehler"], """0 HR, 2 near-HR, 87.9 mph EV. Buehler LHB split -0.80, HR risk 0.49. tough split lane (-0.80); lighter EV form (87.9 mph).""", blast="good"),
            row("Adrian Del Castillo", "L", "N/A", 64, "", ["vs Buehler"], """1 HR, 1 near-HR, 93.6 mph EV. Buehler LHB split -0.80, HR risk 0.49. tough split lane (-0.80).""", blast="good"),
        ],
    },
    {
        "title": "COL @ LAD - Kyle Freeland (L, COL) vs Eric Lauer (L, LAD)",
        "description": "Tail key data: Park boost +16% (stadium +17%, weather -1%). Freeland (HR risk 0.43, vs LHB -0.62, vs RHB +0.55). Lauer (HR risk 0.67, vs LHB +0.91, vs RHB +0.21).",
        "rows": [
            row("Max Muncy", "L", "+320", 63, "", ["vs Freeland"], """1 HR, 1 near-HR, 88.9 mph EV. Freeland LHB split -0.62, HR risk 0.43. tough split lane (-0.62).""", blast="good"),
            row("Dalton Rushing", "L", "+400", 62, "⭐", ["vs Freeland"], """Worst Pickz Favorite. 0 HR, 93.1 mph EV. Freeland LHB split -0.62, HR risk 0.43. tough split lane (-0.62); limited recent HR events.""", blast="good"),
            row("Andy Pages", "R", "+300", 63, "", ["vs Freeland"], """0 HR, 1 near-HR, 87.5 mph EV. Freeland RHB split +0.55, HR risk 0.43. limited recent HR events; lighter EV form (87.5 mph)."""),
            row("Hunter Goodman", "R", "+200", 79, "⭐", ["vs Lauer"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.1 mph EV. Lauer RHB split +0.21, HR risk 0.67.""", blast="good"),
            row("Kyle Karros", "R", "+552", 60, "", ["vs Lauer"], """0 HR, 83.0 mph EV. Lauer RHB split +0.21, HR risk 0.67. limited recent HR events; lighter EV form (83.0 mph)."""),
            row("Cole Carrigg", "S", "+535", 75, "💎", ["vs Lauer"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 60.2 mph EV. Lauer RHB split +0.21, HR risk 0.67. lighter EV form (60.2 mph).""", blast="good"),
        ],
    },
    {
        "title": "HOU @ WSH - Mike Burrows (R, HOU) vs Miles Mikolas (R, WSH)",
        "description": "Tail key data: Park boost +3% (stadium +3%, weather +0%). Burrows (HR risk 0.22, vs LHB +0.37, vs RHB -0.15). Mikolas (HR risk 0.18, vs LHB -0.10, vs RHB +0.54).",
        "rows": [
            row("James Wood", "L", "+270", 69, "", ["vs Burrows"], """1 HR, 1 near-HR, 94.7 mph EV. Burrows LHB split +0.37, HR risk 0.22.""", blast="good"),
            row("Luis Garcia Jr.", "L", "N/A", 85, "🌕 💣", ["vs Burrows"], """5 HR, 6 near-HR, 93.7 mph EV. Burrows LHB split +0.37, HR risk 0.22.""", blast="high"),
            row("CJ Abrams", "L", "+360", 67, "", ["vs Burrows"], """1 HR, 3 near-HR, 87.1 mph EV. Burrows LHB split +0.37, HR risk 0.22. lighter EV form (87.1 mph).""", blast="good"),
            row("Yordan Alvarez", "L", "+228", 83, "⭐ 🌕 💣", ["vs Mikolas"], """Worst Pickz Favorite. 4 HR, 4 near-HR, 95.3 mph EV. Mikolas LHB split -0.10, HR risk 0.18. slight split headwind (-0.10).""", blast="high"),
            row("Cam Smith", "R", "+520", 81, "🌕 💣", ["vs Mikolas"], """2 HR, 3 near-HR, 91.5 mph EV. Mikolas RHB split +0.54, HR risk 0.18.""", blast="high"),
        ],
    },
    {
        "title": "MIL @ STL - Shane Drohan (L, MIL) vs Dustin May (R, STL)",
        "description": "Tail key data: Park boost -8% (stadium -9%, weather +2%). Drohan (HR risk -0.70, vs LHB -0.82, vs RHB -0.24). May (HR risk -0.60, vs LHB -0.22, vs RHB -0.21).",
        "rows": [
            row("Nelson Velazquez", "R", "+670", 58, "⭐", ["vs Drohan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 96.4 mph EV. Drohan RHB split -0.24, HR risk -0.70. slight split headwind (-0.24); pitcher suppresses HR (-0.70).""", blast="good"),
            row("JJ Wetherholt", "L", "+850", 58, "⭐", ["vs Drohan"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.8 mph EV. Drohan LHB split -0.82, HR risk -0.70. tough split lane (-0.82); pitcher suppresses HR (-0.70).""", blast="good"),
            row("Gary Sanchez", "R", "N/A", 69, "🌕 💣", ["vs May"], """2 HR, 3 near-HR, 98.4 mph EV. May RHB split -0.21, HR risk -0.60. slight split headwind (-0.21); pitcher suppresses HR (-0.60).""", blast="high"),
            row("Garrett Mitchell", "L", "+810", 73, "🚀 ⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. 3 HR, 4 near-HR, 100.5 mph EV. May LHB split -0.22, HR risk -0.60. slight split headwind (-0.22); pitcher suppresses HR (-0.60).""", blast="high"),
            row("Jackson Chourio", "R", "+510", 63, "🌕 💣", ["vs May"], """2 HR, 4 near-HR, 88.5 mph EV. May RHB split -0.21, HR risk -0.60. slight split headwind (-0.21); pitcher suppresses HR (-0.60).""", blast="high"),
            row("Jake Bauers", "L", "+472", 58, "", ["vs May"], """0 HR, 88.7 mph EV. May LHB split -0.22, HR risk -0.60. slight split headwind (-0.22); pitcher suppresses HR (-0.60)."""),
        ],
    },
    {
        "title": "NYM @ ATL - Freddy Peralta (R, NYM) vs Reynaldo Lopez (R, ATL)",
        "description": "Tail key data: Park boost +8% (stadium -1%, weather +9%). Peralta (HR risk -0.39, vs LHB +0.38, vs RHB -1.37). Lopez (HR risk -1.28, vs LHB -0.38, vs RHB -0.79).",
        "rows": [
            row("Matt Olson", "L", "+310", 58, "⭐", ["vs Peralta"], """Worst Pickz Favorite. 0 HR, 91.5 mph EV. Peralta LHB split +0.38, HR risk -0.39. pitcher risk below avg (-0.39); limited recent HR events."""),
            row("Michael Harris II", "L", "+425", 60, "", ["vs Peralta"], """1 HR, 1 near-HR, 90.0 mph EV. Peralta LHB split +0.38, HR risk -0.39. pitcher risk below avg (-0.39).""", blast="good"),
            row("Drake Baldwin", "L", "+393", 58, "", ["vs Peralta"], """0 HR, 88.5 mph EV. Peralta LHB split +0.38, HR risk -0.39. pitcher risk below avg (-0.39); limited recent HR events."""),
            row("Juan Soto", "L", "+301", 58, "", ["vs Lopez"], """0 HR, 1 near-HR, 93.8 mph EV. Lopez LHB split -0.38, HR risk -1.28. slight split headwind (-0.38); pitcher suppresses HR (-1.28).""", blast="good"),
            row("Francisco Lindor", "S", "+430", 61, "🌕 💣", ["vs Lopez"], """2 HR, 2 near-HR, 98.2 mph EV. Lopez RHB split -0.79, HR risk -1.28. tough split lane (-0.79); pitcher suppresses HR (-1.28).""", blast="high"),
            row("Francisco Alvarez", "R", "+406", 58, "", ["vs Lopez"], """1 HR, 1 near-HR, 92.0 mph EV. Lopez RHB split -0.79, HR risk -1.28. tough split lane (-0.79); pitcher suppresses HR (-1.28).""", blast="good"),
            row("Mark Vientos", "R", "N/A", 58, "", ["vs Lopez"], """0 HR, 92.2 mph EV. Lopez RHB split -0.79, HR risk -1.28. tough split lane (-0.79); pitcher suppresses HR (-1.28).""", blast="good"),
        ],
    },
    {
        "title": "NYY @ TB - Cam Schlittler (R, NYY) vs Griffin Jax (R, TB)",
        "description": "Tail key data: Park boost -3% (stadium -4%, weather +0%). Schlittler (HR risk 0.25, vs LHB +0.37, vs RHB +0.20). Jax (HR risk 0.50, vs LHB +0.85, vs RHB -0.08).",
        "rows": [
            row("Junior Caminero", "R", "+346", 83, "🌕 💣", ["vs Schlittler"], """4 HR, 4 near-HR, 93.6 mph EV. Schlittler RHB split +0.20, HR risk 0.25.""", blast="high"),
            row("Hunter Feduccia", "L", "+1200", 71, "", ["vs Schlittler"], """0 HR, 3 near-HR, 97.6 mph EV. Schlittler LHB split +0.37, HR risk 0.25.""", blast="good"),
            row("Trent Grisham", "L", "+417", 90, "🌕 💣 💎", ["vs Jax"], """Worst Pickz Hidden Gem. 2 HR, 3 near-HR, 95.0 mph EV. Jax LHB split +0.85, HR risk 0.50.""", blast="high"),
            row("Ben Rice", "L", "+357", 75, "", ["vs Jax"], """1 HR, 2 near-HR, 91.6 mph EV. Jax LHB split +0.85, HR risk 0.50.""", blast="good"),
            row("Max Schuemann", "R", "+900", 71, "⭐", ["vs Jax"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.8 mph EV. Jax RHB split -0.08, HR risk 0.50. slight split headwind (-0.08).""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+473", 70, "", ["vs Jax"], """0 HR, 93.2 mph EV. Jax LHB split +0.85, HR risk 0.50. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PHI @ KC - Cristopher Sanchez (L, PHI) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost +12% (stadium +11%, weather +1%). Sanchez (HR risk -0.50, vs LHB -1.21, vs RHB -0.13). Cameron (HR risk -0.36, vs LHB +0.14, vs RHB -0.37).",
        "rows": [
            row("Carter Jensen", "L", "+800", 58, "⭐", ["vs Sanchez"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 99.7 mph EV. Sanchez LHB split -1.21, HR risk -0.50. tough split lane (-1.21); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Jac Caglianone", "L", "+860", 58, "🚀", ["vs Sanchez"], """1 HR, 1 near-HR, 100.8 mph EV. Sanchez LHB split -1.21, HR risk -0.50. tough split lane (-1.21); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Bobby Witt Jr.", "R", "+575", 58, "", ["vs Sanchez"], """0 HR, 96.7 mph EV. Sanchez RHB split -0.13, HR risk -0.50. slight split headwind (-0.13); pitcher suppresses HR (-0.50).""", blast="good"),
            row("Brandon Marsh", "L", "+680", 74, "🌕 💣", ["vs Cameron"], """2 HR, 3 near-HR, 90.4 mph EV. Cameron LHB split +0.14, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="high"),
            row("Kyle Schwarber", "L", "+288", 69, "🌕 💣", ["vs Cameron"], """2 HR, 2 near-HR, 90.3 mph EV. Cameron LHB split +0.14, HR risk -0.36. pitcher risk below avg (-0.36).""", blast="high"),
        ],
    },
    {
        "title": "TOR @ SF - Kevin Gausman 🧤 (R, TOR) vs Landen Roupp (R, SF)",
        "description": "Tail key data: Park boost -22% (stadium -17%, weather -6%). Gausman 🧤 (HR risk 0.95, vs LHB +0.08, vs RHB +1.61). Roupp (HR risk -1.20, vs LHB -0.59, vs RHB -0.94).",
        "rows": [
            row("Rafael Devers", "L", "+440", 90, "⭐ 🌕 💣", ["vs Gausman"], """Worst Pickz Favorite. 4 HR, 5 near-HR, 97.5 mph EV. Gausman LHB split +0.08, HR risk 0.95. park/weather net drag (-22%).""", blast="high"),
            row("Casey Schmitt", "R", "+584", 84, "💎", ["vs Gausman"], """Worst Pickz Hidden Gem. 1 HR, 2 near-HR, 92.3 mph EV. Gausman RHB split +1.61, HR risk 0.95. park/weather net drag (-22%).""", blast="good"),
            row("Bryce Eldridge", "L", "+725", 68, "", ["vs Gausman"], """0 HR, 97.7 mph EV. Gausman LHB split +0.08, HR risk 0.95. park/weather net drag (-22%); limited recent HR events.""", blast="good"),
            row("Heliot Ramos", "R", "+610", 70, "", ["vs Gausman"], """0 HR, 1 near-HR, 87.7 mph EV. Gausman RHB split +1.61, HR risk 0.95. park/weather net drag (-22%); limited recent HR events."""),
            row("Brandon Valenzuela", "S", "N/A", 58, "", ["vs Roupp"], """1 HR, 2 near-HR, 87.2 mph EV. Roupp RHB split -0.94, HR risk -1.20. tough split lane (-0.94); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Kazuma Okamoto", "R", "+571", 58, "", ["vs Roupp"], """1 HR, 1 near-HR, 74.3 mph EV. Roupp RHB split -0.94, HR risk -1.20. tough split lane (-0.94); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Vladimir Guerrero Jr.", "R", "+960", 58, "", ["vs Roupp"], """0 HR, 92.3 mph EV. Roupp RHB split -0.94, HR risk -1.20. tough split lane (-0.94); pitcher suppresses HR (-1.20).""", blast="good"),
            row("Sean Keys", "L", "N/A", 58, "", ["vs Roupp"], """0 HR, 97.0 mph EV. Roupp LHB split -0.59, HR risk -1.20. tough split lane (-0.59); pitcher suppresses HR (-1.20).""", blast="good"),
        ],
    },
]

for game in games:
    game_key = game["title"].split(" - ")[0]
    for entry in game['rows']:
        add_bum_row_emojis(entry, game_key)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-07-06")

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

    out = ROOT / '_games-0706.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
