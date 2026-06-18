#!/usr/bin/env python3
"""Generate games[] block for 2026-06-18 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Drake Baldwin (L)",
    "Jordan Walker (R)",
    "Randal Grichuk (R)",
}

GEMS = {
    "Andrew Vaughn (R)",
    "Brandon Nimmo (L)",
    "Daniel Schneemann (L)",
    "J.P. Crawford (L)",
    "Jazz Chisholm Jr. (L)",
    "Nick Kurtz (L)",
    "Zach Neto (R)",
}

PLAYER_TEAMS = {
    "Adley Rutschman (S)": "BAL",
    "Alec Bohm (R)": "PHI",
    "Andrew Vaughn (R)": "MIL",
    "Ben Rice (L)": "NYY",
    "Bo Bichette (R)": "NYM",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Marsh (L)": "PHI",
    "Brandon Nimmo (L)": "TEX",
    "Brandon Valenzuela (S)": "TOR",
    "Brett Baty (L)": "NYM",
    "Bryce Harper (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "Casey Schmitt (R)": "SF",
    "Colson Montgomery (L)": "CWS",
    "Colton Cowser (L)": "BAL",
    "Daniel Schneemann (L)": "CLE",
    "Dominic Canzone (L)": "SEA",
    "Drake Baldwin (L)": "ATL",
    "Elias Diaz (R)": "TEX",
    "Ivan Herrera (R)": "STL",
    "J.P. Crawford (L)": "SEA",
    "JJ Wetherholt (L)": "STL",
    "Jac Caglianone (L)": "KC",
    "Jackson Chourio (R)": "MIL",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Jeremiah Jackson (R)": "BAL",
    "Jesus Sanchez (L)": "TOR",
    "Jimmy Crooks (L)": "STL",
    "John Rave (L)": "KC",
    "Jordan Walker (R)": "STL",
    "Jose Siri (R)": "LAA",
    "Juan Soto (L)": "NYM",
    "Kazuma Okamoto (R)": "TOR",
    "Kody Clemens (L)": "MIN",
    "Kyle Schwarber (L)": "PHI",
    "Lars Nootbaar (L)": "STL",
    "Luisangel Acuna (R)": "CWS",
    "Maikel Garcia (R)": "KC",
    "Matt Chapman (R)": "SF",
    "Matt Olson (L)": "ATL",
    "Mauricio Dubon (R)": "ATL",
    "Michael Harris II (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Miguel Vargas (R)": "CWS",
    "Nelson Velazquez (R)": "STL",
    "Nick Kurtz (L)": "ATH",
    "Paul Goldschmidt (R)": "NYY",
    "Pete Alonso (R)": "BAL",
    "Randal Grichuk (R)": "CWS",
    "Rhys Hoskins (R)": "CLE",
    "Samuel Basallo (L)": "BAL",
    "Spencer Jones (L)": "NYY",
    "Victor Bericoto (R)": "SF",
    "Victor Caratini (S)": "MIN",
    "William Contreras (R)": "MIL",
    "Willson Contreras (R)": "BOS",
    "Willy Adames (R)": "SF",
    "Wilyer Abreu (L)": "BOS",
    "Zach Neto (R)": "LAA",
    "Zack Gelof (R)": "ATH",
}

BUM_RISK_MIN = 0.95

BUM_PITCHERS = {
    "Liberatore",
    "Weathers",
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
        "title": "BAL @ SEA - Shane Baz (R, BAL) vs Bryan Woo (R, SEA)",
        "description": "Tail key data: Park boost -1% (stadium +0%, weather -1%). Baz (HR risk -0.24, vs LHB -0.29, vs RHB -0.19). Woo (HR risk 0.06, vs LHB +0.07, vs RHB -0.07).",
        "rows": [
            row("Dominic Canzone", "L", "+420", 87, "🌕 💣", ["vs Baz"], """2 HR, 3 near-HR, 94.8 mph EV. Baz LHB split -0.29, HR risk -0.24. slight split headwind (-0.29); pitcher risk below avg (-0.24).""", blast="high"),
            row("J.P. Crawford", "L", "+810", 88, "🌕 💣 💎", ["vs Baz"], """Worst Pickz Hidden Gem. 3 HR, 3 near-HR, 92.3 mph EV. Baz LHB split -0.29, HR risk -0.24. slight split headwind (-0.29); pitcher risk below avg (-0.24).""", blast="high"),
            row("Pete Alonso", "R", "+375", 90, "🌕 💣", ["vs Woo"], """3 HR, 3 near-HR, 93.5 mph EV. Woo RHB split -0.07, HR risk 0.06. slight split headwind (-0.07).""", blast="high"),
            row("Samuel Basallo", "L", "+390", 77, "", ["vs Woo"], """1 HR, 2 near-HR, 93.1 mph EV. Woo LHB split +0.07, HR risk 0.06.""", blast="good"),
            row("Adley Rutschman", "S", "+510", 70, "", ["vs Woo"], """1 HR, 1 near-HR, 86.8 mph EV. Woo RHB split -0.07, HR risk 0.06. slight split headwind (-0.07); lighter EV form (86.8 mph).""", blast="good"),
            row("Jeremiah Jackson", "R", "N/A", 77, "", ["vs Woo"], """1 HR, 1 near-HR, 94.9 mph EV. Woo RHB split -0.07, HR risk 0.06. slight split headwind (-0.07).""", blast="good"),
            row("Colton Cowser", "L", "+540", 81, "🌕 💣", ["vs Woo"], """2 HR, 3 near-HR, 88.6 mph EV. Woo LHB split +0.07, HR risk 0.06.""", blast="high"),
        ],
    },
    {
        "title": "CLE @ MIL - Parker Messick (L, CLE) vs Shane Drohan (L, MIL)",
        "description": "Tail key data: Park boost +11% (stadium +8%, weather +2%). Messick (HR risk -0.36, vs LHB -0.44, vs RHB -0.16). Drohan (HR risk 0.28, vs LHB -1.03, vs RHB +1.43).",
        "rows": [
            row("William Contreras", "R", "+540", 75, "", ["vs Messick"], """1 HR, 2 near-HR, 91.0 mph EV. Messick RHB split -0.16, HR risk -0.36. slight split headwind (-0.16); pitcher risk below avg (-0.36).""", blast="good"),
            row("Andrew Vaughn", "R", "+520", 78, "💎", ["vs Messick"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 96.0 mph EV. Messick RHB split -0.16, HR risk -0.36. slight split headwind (-0.16); pitcher risk below avg (-0.36).""", blast="good"),
            row("Jackson Chourio", "R", "+490", 86, "🌕 💣", ["vs Messick"], """2 HR, 3 near-HR, 94.4 mph EV. Messick RHB split -0.16, HR risk -0.36. slight split headwind (-0.16); pitcher risk below avg (-0.36).""", blast="high"),
            row("Daniel Schneemann", "L", "N/A", 76, "💎", ["vs Drohan"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 93.9 mph EV. Drohan LHB split -1.03, HR risk 0.28. tough split lane (-1.03).""", blast="good"),
            row("Rhys Hoskins", "R", "+350", 74, "", ["vs Drohan"], """1 HR, 1 near-HR, 92.5 mph EV. Drohan RHB split +1.43, HR risk 0.28.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ NYY - Sean Burke (R, CWS) vs Ryan Weathers 🧤 (L, NYY)",
        "description": "Tail key data: Park boost data unavailable. Burke (HR risk 0.17, vs LHB +0.31, vs RHB -0.30). Weathers 🧤 (HR risk 1.75, vs LHB +1.08, vs RHB +1.67).",
        "rows": [
            row("Spencer Jones", "L", "+438", 74, "", ["vs Burke"], """0 HR, 98.5 mph EV. Burke LHB split +0.31, HR risk 0.17. limited recent HR events.""", blast="good"),
            row("Jazz Chisholm Jr.", "L", "+321", 74, "💎", ["vs Burke"], """Worst Pickz Hidden Gem. 1 HR, 1 near-HR, 91.5 mph EV. Burke LHB split +0.31, HR risk 0.17.""", blast="good"),
            row("Paul Goldschmidt", "R", "+346", 84, "🌕 💣", ["vs Burke"], """3 HR, 3 near-HR, 87.7 mph EV. Burke RHB split -0.30, HR risk 0.17. slight split headwind (-0.30); lighter EV form (87.7 mph).""", blast="high"),
            row("Ben Rice", "L", "+265", 75, "", ["vs Burke"], """0 HR, 1 near-HR, 97.1 mph EV. Burke LHB split +0.31, HR risk 0.17. limited recent HR events.""", blast="good"),
            row("Randal Grichuk", "R", "+299", 78, "⭐ 🌕 💣", ["vs Weathers"], """Worst Pickz Favorite. 2 HR, 2 near-HR, 87.9 mph EV. Weathers RHB split +1.67, HR risk 1.75. lighter EV form (87.9 mph).""", blast="high"),
            row("Colson Montgomery", "L", "+391", 87, "🌕 💣", ["vs Weathers"], """2 HR, 4 near-HR, 93.3 mph EV. Weathers LHB split +1.08, HR risk 1.75.""", blast="high"),
            row("Miguel Vargas", "R", "+287", 73, "", ["vs Weathers"], """0 HR, 97.0 mph EV. Weathers RHB split +1.67, HR risk 1.75. limited recent HR events.""", blast="good"),
            row("Luisangel Acuna", "R", "+1140", 70, "", ["vs Weathers"], """0 HR, 1 near-HR, 92.3 mph EV. Weathers RHB split +1.67, HR risk 1.75. limited recent HR events.""", blast="good"),
        ],
    },
    {
        "title": "LAA @ ATH - Jose Soriano (R, LAA) vs Gage Jump (L, ATH)",
        "description": "Tail key data: Park boost +38% (stadium +31%, weather +8%). Away starter risk unavailable. Jump (HR risk -2.07, vs LHB -1.54, vs RHB -1.64).",
        "rows": [
            row("Nick Kurtz", "L", "N/A", 96, "🌕 💣 💎", ["vs Soriano"], """Worst Pickz Hidden Gem. 4 HR, 4 near-HR, 93.5 mph EV. Soriano split/risk data unavailable. limited split/risk sample.""", blast="high"),
            row("Zack Gelof", "R", "N/A", 72, "", ["vs Soriano"], """1 HR, 2 near-HR, 83.5 mph EV. Soriano split/risk data unavailable. limited split/risk sample; lighter EV form (83.5 mph).""", blast="good"),
            row("Zach Neto", "R", "N/A", 78, "🌕 💣 💎", ["vs Jump"], """Worst Pickz Hidden Gem. 2 HR, 2 near-HR, 86.0 mph EV. Jump RHB split -1.64, HR risk -2.07. tough split lane (-1.64); pitcher suppresses HR (-2.07).""", blast="high"),
            row("Jose Siri", "R", "N/A", 73, "", ["vs Jump"], """0 HR, 1 near-HR, 95.0 mph EV. Jump RHB split -1.64, HR risk -2.07. tough split lane (-1.64); pitcher suppresses HR (-2.07).""", blast="good"),
        ],
    },
    {
        "title": "MIN @ TEX - Joe Ryan (R, MIN) vs Jack Leiter (R, TEX)",
        "description": "Tail key data: Park boost -11% (stadium -10%, weather -1%). Ryan (HR risk 0.62, vs LHB +0.96, vs RHB -0.27). Leiter (HR risk 0.40, vs LHB +0.61, vs RHB -0.05).",
        "rows": [
            row("Brandon Nimmo", "L", "+373", 73, "💎", ["vs Ryan"], """Worst Pickz Hidden Gem. 0 HR, 97.4 mph EV. Ryan LHB split +0.96, HR risk 0.62. park/weather net drag (-11%); limited recent HR events.""", blast="good"),
            row("Elias Diaz", "R", "N/A", 62, "", ["vs Ryan"], """0 HR, 85.1 mph EV. Ryan RHB split -0.27, HR risk 0.62. slight split headwind (-0.27); park/weather net drag (-11%)."""),
            row("Victor Caratini", "S", "+610", 84, "🌕 💣", ["vs Leiter"], """2 HR, 4 near-HR, 90.2 mph EV. Leiter RHB split -0.05, HR risk 0.40. slight split headwind (-0.05); park/weather net drag (-11%).""", blast="high"),
            row("Byron Buxton", "R", "+264", 92, "🌕 💣", ["vs Leiter"], """3 HR, 3 near-HR, 95.5 mph EV. Leiter RHB split -0.05, HR risk 0.40. slight split headwind (-0.05); park/weather net drag (-11%).""", blast="high"),
            row("Kody Clemens", "L", "+340", 84, "🌕 💣", ["vs Leiter"], """2 HR, 3 near-HR, 92.2 mph EV. Leiter LHB split +0.61, HR risk 0.40. park/weather net drag (-11%).""", blast="high"),
        ],
    },
    {
        "title": "NYM @ PHI - Sean Manaea (L, NYM) vs Aaron Nola (R, PHI)",
        "description": "Tail key data: Park boost +25% (stadium +13%, weather +12%). Manaea (HR risk 0.37, vs LHB -0.06, vs RHB +0.70). Nola (HR risk 0.51, vs LHB +0.52, vs RHB +0.35).",
        "rows": [
            row("Brandon Marsh", "L", "+790", 75, "", ["vs Manaea"], """1 HR, 1 near-HR, 93.2 mph EV. Manaea LHB split -0.06, HR risk 0.37. slight split headwind (-0.06).""", blast="good"),
            row("Kyle Schwarber", "L", "+223", 65, "", ["vs Manaea"], """0 HR, 1 near-HR, 89.3 mph EV. Manaea LHB split -0.06, HR risk 0.37. slight split headwind (-0.06); limited recent HR events."""),
            row("Alec Bohm", "R", "+610", 65, "", ["vs Manaea"], """0 HR, 91.4 mph EV. Manaea RHB split +0.70, HR risk 0.37. limited recent HR events."""),
            row("Bryce Harper", "L", "+430", 67, "", ["vs Manaea"], """0 HR, 1 near-HR, 90.6 mph EV. Manaea LHB split -0.06, HR risk 0.37. slight split headwind (-0.06); limited recent HR events."""),
            row("Juan Soto", "L", "+235", 72, "", ["vs Nola"], """1 HR, 2 near-HR, 85.2 mph EV. Nola LHB split +0.52, HR risk 0.51. lighter EV form (85.2 mph).""", blast="good"),
            row("Bo Bichette", "R", "+640", 74, "", ["vs Nola"], """1 HR, 1 near-HR, 91.6 mph EV. Nola RHB split +0.35, HR risk 0.51.""", blast="good"),
            row("Brett Baty", "L", "+600", 65, "", ["vs Nola"], """0 HR, 1 near-HR, 89.4 mph EV. Nola LHB split +0.52, HR risk 0.51. limited recent HR events."""),
        ],
    },
    {
        "title": "SF @ ATL - Landen Roupp (R, SF) vs Martin Perez (L, ATL)",
        "description": "Tail key data: Park boost -3% (stadium -3%, weather +0%). Roupp (HR risk -1.00, vs LHB -0.78, vs RHB -0.77). Perez (HR risk -0.32, vs LHB -0.05, vs RHB -0.34).",
        "rows": [
            row("Matt Olson", "L", "+440", 73, "", ["vs Roupp"], """1 HR, 1 near-HR, 91.4 mph EV. Roupp LHB split -0.78, HR risk -1.00. tough split lane (-0.78); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Drake Baldwin", "L", "+570", 84, "⭐", ["vs Roupp"], """Worst Pickz Favorite. 1 HR, 3 near-HR, 97.9 mph EV. Roupp LHB split -0.78, HR risk -1.00. tough split lane (-0.78); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Michael Harris II", "L", "+570", 80, "", ["vs Roupp"], """1 HR, 2 near-HR, 96.1 mph EV. Roupp LHB split -0.78, HR risk -1.00. tough split lane (-0.78); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Mauricio Dubon", "R", "+1400", 75, "", ["vs Roupp"], """1 HR, 1 near-HR, 92.6 mph EV. Roupp RHB split -0.77, HR risk -1.00. tough split lane (-0.77); pitcher suppresses HR (-1.00).""", blast="good"),
            row("Casey Schmitt", "R", "+513", 84, "🌕 💣", ["vs Perez"], """2 HR, 3 near-HR, 92.1 mph EV. Perez RHB split -0.34, HR risk -0.32. slight split headwind (-0.34); pitcher risk below avg (-0.32).""", blast="high"),
            row("Willy Adames", "R", "+508", 62, "", ["vs Perez"], """0 HR, 85.9 mph EV. Perez RHB split -0.34, HR risk -0.32. slight split headwind (-0.34); pitcher risk below avg (-0.32)."""),
            row("Victor Bericoto", "R", "N/A", 82, "", ["vs Perez"], """1 HR, 1 near-HR, 99.7 mph EV. Perez RHB split -0.34, HR risk -0.32. slight split headwind (-0.34); pitcher risk below avg (-0.32).""", blast="good"),
            row("Matt Chapman", "R", "+650", 72, "", ["vs Perez"], """1 HR, 1 near-HR, 90.1 mph EV. Perez RHB split -0.34, HR risk -0.32. slight split headwind (-0.34); pitcher risk below avg (-0.32).""", blast="good"),
        ],
    },
    {
        "title": "STL @ KC - Matthew Liberatore 🧤 (L, STL) vs Noah Cameron (L, KC)",
        "description": "Tail key data: Park boost +4% (stadium +12%, weather -8%). Liberatore 🧤 (HR risk 1.09, vs LHB +1.10, vs RHB +1.03). Cameron (HR risk -0.30, vs LHB +0.20, vs RHB -0.12).",
        "rows": [
            row("Jac Caglianone", "L", "+467", 80, "🌕 💣", ["vs Liberatore"], """2 HR, 3 near-HR, 86.9 mph EV. Liberatore LHB split +1.10, HR risk 1.09. weather carry headwind (-8%); lighter EV form (86.9 mph).""", blast="high"),
            row("John Rave", "L", "N/A", 76, "", ["vs Liberatore"], """0 HR, 1 near-HR, 97.6 mph EV. Liberatore LHB split +1.10, HR risk 1.09. weather carry headwind (-8%); limited recent HR events.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+352", 72, "", ["vs Liberatore"], """0 HR, 96.1 mph EV. Liberatore RHB split +1.03, HR risk 1.09. weather carry headwind (-8%); limited recent HR events.""", blast="good"),
            row("Michael Massey", "L", "N/A", 74, "", ["vs Liberatore"], """1 HR, 3 near-HR, 79.2 mph EV. Liberatore LHB split +1.10, HR risk 1.09. weather carry headwind (-8%); lighter EV form (79.2 mph).""", blast="good"),
            row("Maikel Garcia", "R", "+820", 72, "", ["vs Liberatore"], """0 HR, 1 near-HR, 93.7 mph EV. Liberatore RHB split +1.03, HR risk 1.09. weather carry headwind (-8%); limited recent HR events.""", blast="good"),
            row("Nelson Velazquez", "R", "+441", 80, "", ["vs Cameron"], """1 HR, 1 near-HR, 97.7 mph EV. Cameron RHB split -0.12, HR risk -0.30. slight split headwind (-0.12); pitcher risk below avg (-0.30).""", blast="good"),
            row("Jordan Walker", "R", "+340", 73, "⭐", ["vs Cameron"], """Worst Pickz Favorite. 1 HR, 1 near-HR, 91.3 mph EV. Cameron RHB split -0.12, HR risk -0.30. slight split headwind (-0.12); pitcher risk below avg (-0.30).""", blast="good"),
            row("JJ Wetherholt", "L", "+574", 62, "", ["vs Cameron"], """0 HR, 86.3 mph EV. Cameron LHB split +0.20, HR risk -0.30. pitcher risk below avg (-0.30); weather carry headwind (-8%)."""),
            row("Lars Nootbaar", "L", "+470", 63, "", ["vs Cameron"], """0 HR, 89.3 mph EV. Cameron LHB split +0.20, HR risk -0.30. pitcher risk below avg (-0.30); weather carry headwind (-8%)."""),
            row("Jimmy Crooks", "L", "N/A", 78, "🚀", ["vs Cameron"], """0 HR, 1 near-HR, 103.9 mph EV. Cameron LHB split +0.20, HR risk -0.30. pitcher risk below avg (-0.30); weather carry headwind (-8%).""", blast="good"),
            row("Ivan Herrera", "R", "+546", 70, "", ["vs Cameron"], """1 HR, 1 near-HR, 88.4 mph EV. Cameron RHB split -0.12, HR risk -0.30. slight split headwind (-0.12); pitcher risk below avg (-0.30).""", blast="good"),
        ],
    },
    {
        "title": "TOR @ BOS - Trey Yesavage (R, TOR) vs Sonny Gray (R, BOS)",
        "description": "Tail key data: Park boost +5% (stadium -8%, weather +13%). Yesavage (HR risk -0.51, vs LHB -0.52, vs RHB -0.43). Gray (HR risk -0.46, vs LHB -0.16, vs RHB -0.84).",
        "rows": [
            row("Wilyer Abreu", "L", "+410", 75, "", ["vs Yesavage"], """1 HR, 1 near-HR, 93.2 mph EV. Yesavage LHB split -0.52, HR risk -0.51. tough split lane (-0.52); pitcher suppresses HR (-0.51).""", blast="good"),
            row("Willson Contreras", "R", "+430", 78, "🌕 💣", ["vs Yesavage"], """2 HR, 2 near-HR, 86.4 mph EV. Yesavage RHB split -0.43, HR risk -0.51. tough split lane (-0.43); pitcher suppresses HR (-0.51).""", blast="high"),
            row("Brandon Valenzuela", "S", "+800", 74, "", ["vs Gray"], """1 HR, 3 near-HR, 88.3 mph EV. Gray RHB split -0.84, HR risk -0.46. tough split lane (-0.84); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Jesus Sanchez", "L", "+540", 76, "", ["vs Gray"], """1 HR, 1 near-HR, 93.5 mph EV. Gray LHB split -0.16, HR risk -0.46. slight split headwind (-0.16); pitcher suppresses HR (-0.46).""", blast="good"),
            row("Kazuma Okamoto", "R", "+520", 64, "", ["vs Gray"], """0 HR, 1 near-HR, 87.7 mph EV. Gray RHB split -0.84, HR risk -0.46. tough split lane (-0.84); pitcher suppresses HR (-0.46)."""),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

from game_start_times import annotate_and_sort_games
games = annotate_and_sort_games(games, "2026-06-18")

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

    out = ROOT / '_games-0618.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
