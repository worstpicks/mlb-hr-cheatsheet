#!/usr/bin/env python3
"""Generate games[] block for 2026-06-08 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Ben Rice (L)",
    "Bryce Harper (L)",
    "Colby Thomas (R)",
    "Jackson Chourio (R)",
    "James Wood (L)",
    "Jonathan Aranda (L)",
    "Jose Ramirez (S)",
    "Julio Rodriguez (R)",
    "LaMonte Wade Jr. (L)",
    "Nick Kurtz (L)",
    "Samuel Basallo (L)",
    "Shea Langeliers (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Adolis Garcia (R)": "PHI",
    "Andrew Vaughn (R)": "MIL",
    "Ben Rice (L)": "NYY",
    "Brandon Marsh (L)": "PHI",
    "Brandon Valenzuela (S)": "TOR",
    "Bryce Harper (L)": "PHI",
    "CJ Abrams (L)": "WSH",
    "Chase DeLauter (L)": "CLE",
    "Cody Bellinger (L)": "NYY",
    "Colby Thomas (R)": "ATH",
    "David Fry (R)": "CLE",
    "Daylen Lile (L)": "WSH",
    "Dominic Canzone (L)": "SEA",
    "Eric Haase (R)": "SF",
    "Fernando Tatis Jr. (R)": "SD",
    "Hunter Feduccia (L)": "TB",
    "Isaac Paredes (R)": "HOU",
    "J.P. Crawford (L)": "SEA",
    "JJ Bleday (L)": "CIN",
    "Jackson Chourio (R)": "MIL",
    "Jackson Holliday (L)": "BAL",
    "Jackson Merrill (L)": "SD",
    "James Wood (L)": "WSH",
    "Jonathan Aranda (L)": "TB",
    "Jose Ramirez (S)": "CLE",
    "Julio Rodriguez (R)": "SEA",
    "Junior Caminero (R)": "TB",
    "Kazuma Okamoto (R)": "TOR",
    "LaMonte Wade Jr. (L)": "HOU",
    "Luke Raley (L)": "SEA",
    "Matt McLain (R)": "CIN",
    "Mike Trout (R)": "LAA",
    "Nathaniel Lowe (L)": "CIN",
    "Nick Kurtz (L)": "ATH",
    "Pete Alonso (R)": "BAL",
    "Sal Stewart (R)": "CIN",
    "Samuel Basallo (L)": "BAL",
    "Shea Langeliers (R)": "ATH",
    "Spencer Jones (L)": "NYY",
    "Travis Bazzana (L)": "CLE",
    "Trent Grisham (L)": "NYY",
    "Vaughn Grissom (R)": "LAA",
    "Will Benson (L)": "CIN",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_PITCHERS = {
    "Mikolas",
    "Rodriguez",
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
        "title": "BOS @ TB - Connelly Early (R, BOS) vs Ian Seymour (R, TB)",
        "description": "Tail key data: Park boost -2% (stadium -2%, weather +1%). Early (HR risk 0.55, vs LHB +0.99, vs RHB +0.25). Seymour (HR risk -0.23, vs LHB +0.36, vs RHB -0.48).",
        "rows": [
            row("Junior Caminero", "R", "+340", 80, "💎", ["vs Early"], """1 HR, 1 near-HR, 98.2 mph EV. Early RHB split +0.25, HR risk 0.55.""", blast="good"),
            row("Yandy Diaz", "R", "+450", 74, "💎", ["vs Early"], """0 HR, 2 near-HR, 93.8 mph EV. Early RHB split +0.25, HR risk 0.55.""", blast="good"),
            row("Jonathan Aranda", "L", "+690", 74, "⭐ 💎", ["vs Early"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 96.5 mph EV. Early LHB split +0.99, HR risk 0.55. limited recent HR events.""", blast="good"),
            row("Hunter Feduccia", "L", "N/A", 64, "💎", ["vs Early"], """0 HR, 89.7 mph EV. Early LHB split +0.99, HR risk 0.55. limited recent HR events."""),
            row("Willson Contreras", "R", "+350", 77, "💎", ["vs Seymour"], """1 HR, 2 near-HR, 93.1 mph EV. Seymour RHB split -0.48, HR risk -0.23. tough split lane (-0.48); pitcher risk below avg (-0.23).""", blast="good"),
        ],
    },
    {
        "title": "CIN @ SD - Andrew Abbott (R, CIN) vs Walker Buehler (R, SD)",
        "description": "Tail key data: Park boost -6% (stadium -4%, weather -3%). Abbott (HR risk -0.13, vs LHB -0.15, vs RHB +0.04). Buehler (HR risk -0.17, vs LHB -0.40, vs RHB +0.26).",
        "rows": [
            row("Fernando Tatis Jr.", "R", "+520", 70, "💎", ["vs Abbott"], """1 HR, 1 near-HR, 82.0 mph EV. Abbott RHB split +0.04, HR risk -0.13. pitcher risk below avg (-0.13); park/weather net drag (-6%).""", blast="good"),
            row("Jackson Merrill", "L", "+720", 70, "💎", ["vs Abbott"], """0 HR, 93.6 mph EV. Abbott LHB split -0.15, HR risk -0.13. slight split headwind (-0.15); pitcher risk below avg (-0.13).""", blast="good"),
            row("Nathaniel Lowe", "L", "+880", 72, "💎", ["vs Buehler"], """1 HR, 2 near-HR, 84.8 mph EV. Buehler LHB split -0.40, HR risk -0.17. tough split lane (-0.40); pitcher risk below avg (-0.17).""", blast="good"),
            row("Will Benson", "L", "N/A", 70, "💎", ["vs Buehler"], """1 HR, 1 near-HR, 84.3 mph EV. Buehler LHB split -0.40, HR risk -0.17. tough split lane (-0.40); pitcher risk below avg (-0.17).""", blast="good"),
            row("JJ Bleday", "L", "+492", 82, "🌕 💣", ["vs Buehler"], """2 HR, 2 near-HR, 91.9 mph EV. Buehler LHB split -0.40, HR risk -0.17. tough split lane (-0.40); pitcher risk below avg (-0.17).""", blast="high"),
            row("Sal Stewart", "R", "+574", 66, "💎", ["vs Buehler"], """0 HR, 1 near-HR, 90.5 mph EV. Buehler RHB split +0.26, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-6%)."""),
            row("Matt McLain", "R", "+960", 80, "🌕 💣", ["vs Buehler"], """2 HR, 2 near-HR, 90.3 mph EV. Buehler RHB split +0.26, HR risk -0.17. pitcher risk below avg (-0.17); park/weather net drag (-6%).""", blast="high"),
        ],
    },
    {
        "title": "HOU @ LAA - Spencer Arrighetti (R, HOU) vs Grayson Rodriguez 🧤 (R, LAA)",
        "description": "Tail key data: Park boost +8% (stadium +6%, weather +2%). Arrighetti (HR risk -0.86, vs LHB -0.96, vs RHB -0.04). Rodriguez 🧤 (HR risk 1.35, vs LHB +1.59, vs RHB +0.02).",
        "rows": [
            row("Vaughn Grissom", "R", "N/A", 88, "🌕 💣", ["vs Arrighetti"], """2 HR, 4 near-HR, 93.7 mph EV. Arrighetti RHB split -0.04, HR risk -0.86. slight split headwind (-0.04); pitcher suppresses HR (-0.86).""", blast="high"),
            row("Mike Trout", "R", "+320", 86, "🌕 💣", ["vs Arrighetti"], """1 HR, 4 near-HR, 96.1 mph EV. Arrighetti RHB split -0.04, HR risk -0.86. slight split headwind (-0.04); pitcher suppresses HR (-0.86).""", blast="high"),
            row("Zach Neto", "R", "+410", 72, "💎", ["vs Arrighetti"], """1 HR, 2 near-HR, 85.6 mph EV. Arrighetti RHB split -0.04, HR risk -0.86. slight split headwind (-0.04); pitcher suppresses HR (-0.86).""", blast="good"),
            row("Yordan Alvarez", "L", "+225", 93, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 99.4 mph EV. Rodriguez LHB split +1.59, HR risk 1.35.""", blast="high"),
            row("Isaac Paredes", "R", "+525", 78, "🌕 💣", ["vs Rodriguez"], """2 HR, 2 near-HR, 86.3 mph EV. Rodriguez RHB split +0.02, HR risk 1.35. lighter EV form (86.3 mph).""", blast="high"),
            row("LaMonte Wade Jr.", "L", "N/A", 80, "⭐ 💎", ["vs Rodriguez"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 98.0 mph EV. Rodriguez LHB split +1.59, HR risk 1.35.""", blast="good"),
        ],
    },
    {
        "title": "MIL @ ATH - Kyle Harrison (R, MIL) vs Jeffrey Springs (R, ATH)",
        "description": "Tail key data: Park boost +44% (stadium +35%, weather +9%). Harrison (HR risk -0.93, vs LHB -1.22, vs RHB -0.43). Springs (HR risk 0.93, vs LHB +0.61, vs RHB +0.88).",
        "rows": [
            row("Nick Kurtz", "L", "+300", 90, "🚀 ⭐ 🌕 💣", ["vs Harrison"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 100.7 mph EV. Harrison LHB split -1.22, HR risk -0.93. tough split lane (-1.22); pitcher suppresses HR (-0.93).""", blast="high"),
            row("Shea Langeliers", "R", "+250", 75, "⭐ 💎", ["vs Harrison"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 92.6 mph EV. Harrison RHB split -0.43, HR risk -0.93. tough split lane (-0.43); pitcher suppresses HR (-0.93).""", blast="good"),
            row("Colby Thomas", "R", "+380", 79, "⭐ 💎", ["vs Harrison"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.8 mph EV. Harrison RHB split -0.43, HR risk -0.93. tough split lane (-0.43); pitcher suppresses HR (-0.93).""", blast="good"),
            row("Jackson Chourio", "R", "+300", 79, "⭐ 💎", ["vs Springs"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 94.6 mph EV. Springs RHB split +0.88, HR risk 0.93.""", blast="good"),
            row("Andrew Vaughn", "R", "+340", 68, "💎", ["vs Springs"], """0 HR, 92.2 mph EV. Springs RHB split +0.88, HR risk 0.93. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "NYY @ CLE - Will Warren (R, NYY) vs Gavin Williams (R, CLE)",
        "description": "Tail key data: Park boost -7% (stadium -2%, weather -5%). Warren (HR risk -0.16, vs LHB +0.16, vs RHB -0.29). Williams (HR risk 0.38, vs LHB +0.59, vs RHB -0.28).",
        "rows": [
            row("Jose Ramirez", "S", "+450", 84, "⭐ 🌕 💣", ["vs Warren"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 94.1 mph EV. Warren RHB split -0.29, HR risk -0.16. slight split headwind (-0.29); pitcher risk below avg (-0.16).""", blast="high"),
            row("Travis Bazzana", "L", "+710", 73, "💎", ["vs Warren"], """1 HR, 1 near-HR, 91.2 mph EV. Warren LHB split +0.16, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-7%).""", blast="good"),
            row("Chase DeLauter", "L", "+599", 65, "💎", ["vs Warren"], """0 HR, 90.9 mph EV. Warren LHB split +0.16, HR risk -0.16. pitcher risk below avg (-0.16); park/weather net drag (-7%)."""),
            row("David Fry", "R", "N/A", 66, "💎", ["vs Warren"], """0 HR, 1 near-HR, 90.1 mph EV. Warren RHB split -0.29, HR risk -0.16. slight split headwind (-0.29); pitcher risk below avg (-0.16)."""),
            row("Ben Rice", "L", "+310", 75, "⭐ 💎", ["vs Williams"], """Worst Pickz Favorite. 1 HR, 2 near-HR, 91.1 mph EV. Williams LHB split +0.59, HR risk 0.38. park/weather net drag (-7%).""", blast="good"),
            row("Trent Grisham", "L", "+428", 70, "💎", ["vs Williams"], """1 HR, 1 near-HR, 88.4 mph EV. Williams LHB split +0.59, HR risk 0.38. park/weather net drag (-7%).""", blast="good"),
            row("Cody Bellinger", "L", "+525", 72, "💎", ["vs Williams"], """1 HR, 1 near-HR, 89.6 mph EV. Williams LHB split +0.59, HR risk 0.38. park/weather net drag (-7%).""", blast="good"),
            row("Spencer Jones", "L", "+710", 73, "💎", ["vs Williams"], """0 HR, 96.6 mph EV. Williams LHB split +0.59, HR risk 0.38. park/weather net drag (-7%); limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "PHI @ TOR - Cristopher Sanchez (R, PHI) vs Patrick Corbin (R, TOR)",
        "description": "Tail key data: Park boost +2% (stadium +6%, weather -4%). Sanchez (HR risk -1.27, vs LHB -1.06, vs RHB -1.04). Corbin (HR risk -0.17, vs LHB -1.10, vs RHB +0.33).",
        "rows": [
            row("Kazuma Okamoto", "R", "+720", 72, "💎", ["vs Sanchez"], """1 HR, 2 near-HR, 87.4 mph EV. Sanchez RHB split -1.04, HR risk -1.27. tough split lane (-1.04); pitcher suppresses HR (-1.27).""", blast="good"),
            row("Brandon Valenzuela", "S", "+800", 76, "🚀 💎", ["vs Sanchez"], """0 HR, 101.5 mph EV. Sanchez RHB split -1.04, HR risk -1.27. tough split lane (-1.04); pitcher suppresses HR (-1.27).""", blast="good"),
            row("Adolis Garcia", "R", "+559", 71, "💎", ["vs Corbin"], """1 HR, 1 near-HR, 89.2 mph EV. Corbin RHB split +0.33, HR risk -0.17. pitcher risk below avg (-0.17); weather carry headwind (-4%).""", blast="good"),
            row("Brandon Marsh", "L", "+920", 73, "💎", ["vs Corbin"], """1 HR, 1 near-HR, 91.4 mph EV. Corbin LHB split -1.10, HR risk -0.17. tough split lane (-1.10); pitcher risk below avg (-0.17).""", blast="good"),
            row("Bryce Harper", "L", "+544", 73, "⭐ 💎", ["vs Corbin"], """Worst Pickz Favorite. 0 HR, 1 near-HR, 95.2 mph EV. Corbin LHB split -1.10, HR risk -0.17. tough split lane (-1.10); pitcher risk below avg (-0.17).""", blast="good"),
        ],
    },
    {
        "title": "SEA @ BAL - Emerson Hancock (R, SEA) vs Chris Bassitt (R, BAL)",
        "description": "Tail key data: Park boost -6% (stadium +0%, weather -6%). Hancock (HR risk 0.34, vs LHB +0.56, vs RHB -0.24). Home starter risk unavailable.",
        "rows": [
            row("Pete Alonso", "R", "+378", 86, "🌕 💣", ["vs Hancock"], """2 HR, 2 near-HR, 95.5 mph EV. Hancock RHB split -0.24, HR risk 0.34. slight split headwind (-0.24); park/weather net drag (-6%).""", blast="high"),
            row("Adley Rutschman", "S", "+540", 79, "💎", ["vs Hancock"], """1 HR, 1 near-HR, 96.8 mph EV. Hancock RHB split -0.24, HR risk 0.34. slight split headwind (-0.24); park/weather net drag (-6%).""", blast="good"),
            row("Samuel Basallo", "L", "+428", 82, "🚀 ⭐ 💎", ["vs Hancock"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 100.8 mph EV. Hancock LHB split +0.56, HR risk 0.34. park/weather net drag (-6%).""", blast="good"),
            row("Jackson Holliday", "L", "+870", 71, "💎", ["vs Hancock"], """0 HR, 94.7 mph EV. Hancock LHB split +0.56, HR risk 0.34. park/weather net drag (-6%); limited recent HR events.""", blast="good"),
            row("Luke Raley", "L", "+395", 72, "💎", ["vs Bassitt"], """1 HR, 2 near-HR, 73.6 mph EV. Bassitt split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("Dominic Canzone", "L", "+479", 84, "🌕 💣", ["vs Bassitt"], """2 HR, 2 near-HR, 94.2 mph EV. Bassitt split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="high"),
            row("Julio Rodriguez", "R", "+441", 82, "⭐ 💎", ["vs Bassitt"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 99.6 mph EV. Bassitt split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
            row("J.P. Crawford", "L", "N/A", 74, "💎", ["vs Bassitt"], """1 HR, 1 near-HR, 91.7 mph EV. Bassitt split/risk data unavailable. limited split/risk sample; park/weather net drag (-6%).""", blast="good"),
        ],
    },
    {
        "title": "WSH @ SF - Miles Mikolas 🧤 (R, WSH) vs Logan Webb (R, SF)",
        "description": "Tail key data: Park boost data unavailable. Mikolas 🧤 (HR risk 1.28, vs LHB +0.61, vs RHB +1.72). Webb (HR risk -0.91, vs LHB -0.56, vs RHB -0.70).",
        "rows": [
            row("Eric Haase", "R", "+473", 85, "🌕 💣", ["vs Mikolas"], """2 HR, 3 near-HR, 92.9 mph EV. Mikolas RHB split +1.72, HR risk 1.28.""", blast="high"),
            row("Willy Adames", "R", "+490", 87, "🌕 💣", ["vs Mikolas"], """2 HR, 4 near-HR, 93.2 mph EV. Mikolas RHB split +1.72, HR risk 1.28.""", blast="high"),
            row("James Wood", "L", "+650", 86, "⭐ 🌕 💣", ["vs Webb"], """Worst Pickz Favorite. 2 HR, 4 near-HR, 92.4 mph EV. Webb LHB split -0.56, HR risk -0.91. tough split lane (-0.56); pitcher suppresses HR (-0.91).""", blast="high"),
            row("CJ Abrams", "L", "+850", 74, "💎", ["vs Webb"], """1 HR, 1 near-HR, 92.2 mph EV. Webb LHB split -0.56, HR risk -0.91. tough split lane (-0.56); pitcher suppresses HR (-0.91).""", blast="good"),
            row("Daylen Lile", "L", "+1200", 70, "💎", ["vs Webb"], """1 HR, 1 near-HR, 84.0 mph EV. Webb LHB split -0.56, HR risk -0.91. tough split lane (-0.56); pitcher suppresses HR (-0.91).""", blast="good"),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-08")

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

    out = ROOT / '_games-0608.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
