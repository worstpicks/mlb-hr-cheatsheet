#!/usr/bin/env python3
"""Generate games[] block for 2026-05-21 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Alec Burleson (L)",
    "Brandon Lowe (L)",
    "Juan Soto (L)",
    "Jakob Marsee (L)",
    "Austin Riley (R)",
    "Aaron Judge (R)",
    "Brandon Valenzuela (S)",
    "George Springer (R)",
    "Nick Kurtz (L)",
    "Corbin Carroll (L)",
}

PLAYER_TEAMS = {
    "Hao-Yu Lee (R)": "DET",
    "Matt Vierling (R)": "DET",
    "Chase DeLauter (L)": "CLE",
    "Patrick Bailey (S)": "CLE",
    "Alec Burleson (L)": "STL",
    "Pedro Pages (R)": "STL",
    "Nolan Gorman (L)": "STL",
    "Brandon Lowe (L)": "PIT",
    "Marcell Ozuna (R)": "PIT",
    "Jacob Young (R)": "WSH",
    "James Wood (L)": "WSH",
    "Juan Soto (L)": "NYM",
    "Marcus Semien (R)": "NYM",
    "A.J. Ewing (L)": "NYM",
    "MJ Melendez (L)": "NYM",
    "Jakob Marsee (L)": "MIA",
    "Xavier Edwards (S)": "MIA",
    "Liam Hicks (L)": "MIA",
    "Austin Riley (R)": "ATL",
    "Matt Olson (L)": "ATL",
    "Ben Rice (L)": "NYY",
    "Aaron Judge (R)": "NYY",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Ryan McMahon (L)": "NYY",
    "Brandon Valenzuela (S)": "TOR",
    "George Springer (R)": "TOR",
    "Ernie Clement (R)": "TOR",
    "Zach Neto (R)": "LAA",
    "Jo Adell (R)": "LAA",
    "Mike Trout (R)": "LAA",
    "Nick Kurtz (L)": "ATH",
    "Brent Rooker (R)": "ATH",
    "Corbin Carroll (L)": "ARI",
    "Ketel Marte (S)": "ARI",
    "Hunter Goodman (R)": "COL",
}


def display(name, hand):
    return f"{name} ({hand})"


def odds_text(odds):
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"


def row(name, hand, odds, score, emojis, chips, note, blast=None):
    item = {
        "name": display(name, hand),
        "odds": odds_text(odds),
        "score": score,
        "emojis": emojis,
        "note": note,
        "chips": chips,
    }
    if blast:
        item["blast"] = blast
    return item


def n(player, pitcher, park, angle):
    angle = angle.rstrip(".")
    return f"{angle}. Draws opposing starter {pitcher}; {park}."


games = [
    {
        "title": "CLE @ DET - Joey Cantillo (L, CLE) vs Casey Mize (R, DET)",
        "description": "Comerica Park — the slate's harshest HR environment: -34% HR, cool air, high pressure, wind in and a huge outfield. Detroit righties still get Cantillo's RHB weak spot, while Cleveland props must beat Casey Mize's run prevention.",
        "rows": [
            row("Hao-Yu Lee", "R", "+1300", 77, "🚀 💎", ["vs Cantillo"], n("Hao-Yu Lee", "Cantillo", "Comerica caps the carry but Cantillo is weaker to RHB damage", "1 HR, 2 near-HR, 91.4 mph EV and 21.4% barrels at a massive price")),
            row("Matt Vierling", "R", "+1040", 70, "💎 📜", ["vs Cantillo"], n("Matt Vierling", "Cantillo", "righty split helps, park hurts", "1 HR and a BvP extra-base signal, but only 5.3% barrels in the selected sample")),
            row("Chase DeLauter", "L", "+760", 78, "🚀 💎", ["vs Mize"], n("Chase DeLauter", "Mize", "Mize is tough to LHB, so this is bat-form over matchup", "4 HR, 5 near-HR, .268 ISO and 93.2 mph EV keep him playable despite Comerica")),
            row("Patrick Bailey", "S", "+1720", 60, "💎", ["vs Mize"], n("Patrick Bailey", "Mize", "deep longshot in a bad HR park", "0 HR in the pitch-mix sample, but 94.3 mph EV and 10.0% barrels keep him barely listed")),
        ],
    },
    {
        "title": "PIT @ STL - Braxton Ashcraft (R, PIT) vs Dustin May (R, STL)",
        "description": "Busch Stadium — pitcher-friendly: -26% HR with cool/high-pressure air and wind in. Lefty power is the only real path, especially against Ashcraft's LHB risk and Brandon Lowe's loud form versus May.",
        "rows": [
            row("Alec Burleson", "L", "+725", 86, "🚀 ⭐ 💎", ["vs Ashcraft"], n("Alec Burleson", "Ashcraft", "Busch is a drag, but Ashcraft's LHB lane is attackable", "Worst Pickz favorite with 4 HR, 10 near-HR, 93.8 mph EV and 19.5% barrels"), "good"),
            row("Pedro Pages", "R", "+1120", 68, "💎", ["vs Ashcraft"], n("Pedro Pages", "Ashcraft", "righty split is not the preferred side", "4 HR in form, but lower EV and park/weather keep him a thin dart")),
            row("Nolan Gorman", "L", "+800", 84, "🚀 🌕 💎", ["vs Ashcraft"], n("Nolan Gorman", "Ashcraft", "lefty power is the Cardinals path", "4 HR, 5 near-HR, 95.0 mph EV and 41.7% pull-air")),
            row("Brandon Lowe", "L", "+600", 91, "🚀 ⭐ 🌕 💣", ["vs Dustin May"], n("Brandon Lowe", "Dustin May", "park is bad but the bat form is slate-best tier", "Worst Pickz favorite with 9 HR, 12 near-HR, .467 ISO and 21.7% barrels"), "high"),
            row("Marcell Ozuna", "R", "+850", 72, "💎 📜", ["vs Dustin May"], n("Marcell Ozuna", "Dustin May", "righty split is neutral and Busch suppresses", "3 HR, 5 near-HR and a career HR off May keep him alive at price")),
        ],
    },
    {
        "title": "NYM @ WSH - David Peterson (L, NYM) vs Cade Cavalli (R, WSH)",
        "description": "Nationals Park — -24% HR with rain/delay risk and high pressure. The weather is ugly, but Cade Cavalli gives up enough LHB quality contact for the Mets lefties, while James Wood is the clear Washington ceiling bat.",
        "rows": [
            row("Jacob Young", "R", "+1650", 62, "💎", ["vs Peterson"], n("Jacob Young", "Peterson", "Peterson's RHB split is pitcher-friendly", "1 HR at a big number, but power indicators are light")),
            row("James Wood", "L", "+555", 85, "🚀 🌕 💎", ["vs Peterson"], n("James Wood", "Peterson", "weather is the only major drawback", "3 HR, 4 near-HR, 98.5 mph EV and 20.0% barrels")),
            row("Juan Soto", "L", "+484", 92, "🚀 ⭐ 🌕 💣 📜", ["vs Cavalli"], n("Juan Soto", "Cavalli", "Cavalli is beatable by LHB contact quality", "Worst Pickz favorite with 7 HR, 12 near-HR, 95.3 mph EV and a BvP HR signal"), "high"),
            row("Marcus Semien", "R", "+800", 74, "💎", ["vs Cavalli"], n("Marcus Semien", "Cavalli", "righty split is closer to neutral", "3 HR and 8 near-HR keep him in play, but the current EV is lighter")),
            row("A.J. Ewing", "L", "+1040", 80, "🚀 💎", ["vs Cavalli"], n("A.J. Ewing", "Cavalli", "lefty lane plus price make the longshot interesting", "1 HR with .445 wOBA, 90.8 mph EV and 16.7% barrels")),
            row("MJ Melendez", "L", "+775", 78, "🚀 💎", ["vs Cavalli"], n("MJ Melendez", "Cavalli", "lefty contact quality fits the matchup", "2 HR, 4 near-HR, 94.1 mph EV and 16.2% barrels")),
        ],
    },
    {
        "title": "ATL @ MIA - Spencer Strider (R, ATL) vs Sandy Alcantara (R, MIA)",
        "description": "loanDepot park — roof closed and -12% HR. Atlanta has the better raw bats but faces a suppressive Sandy Alcantara profile; Miami lefties get Strider's LHB risk, but strikeouts are a major tax.",
        "rows": [
            row("Jakob Marsee", "L", "+1040", 71, "⭐ 💎", ["vs Strider"], n("Jakob Marsee", "Strider", "Strider has LHB HR risk but elite strikeout pressure", "Worst Pickz favorite with 2 HR and 5 near-HR, though barrel rate is light")),
            row("Xavier Edwards", "S", "+1400", 73, "💎", ["vs Strider"], n("Xavier Edwards", "Strider", "roof park suppresses, price helps", "2 HR and 5 near-HR with strong on-base form")),
            row("Liam Hicks", "L", "+875", 82, "🚀 💎", ["vs Strider"], n("Liam Hicks", "Strider", "lefty HR-risk lane is real if he handles the whiffs", "6 HR, .256 ISO and steady contact skills")),
            row("Austin Riley", "R", "+630", 81, "🚀 ⭐ 💎", ["vs Alcantara"], n("Austin Riley", "Alcantara", "BvP is poor but current power keeps him listed", "Worst Pickz favorite with 7 HR, 10 near-HR, 92.8 mph EV and 14.1% barrels")),
            row("Matt Olson", "L", "+375", 89, "🚀 🌕 💣", ["vs Alcantara"], n("Matt Olson", "Alcantara", "Sandy suppresses, but Olson has the loudest Braves power indicators", "10 HR, 15 near-HR, .333 ISO and 19.8% barrels"), "high"),
        ],
    },
    {
        "title": "TOR @ NYY - Braydon Fisher (R, TOR) vs Carlos Rodon (L, NYY)",
        "description": "Yankee Stadium — official weather model is -15% HR due to cool/high-pressure air, but the short porch still gives elite power a path. Braydon Fisher's RHB risk is the clear attack point; Rodon is tougher, making Toronto mostly BvP/price.",
        "rows": [
            row("Ben Rice", "L", "+360", 87, "🚀 🌕", ["vs Fisher"], n("Ben Rice", "Fisher", "lefty porch helps even with Fisher's better LHB split", "11 HR, 15 near-HR, 94.0 mph EV and 22.0% barrels"), "good"),
            row("Aaron Judge", "R", "+290", 94, "🚀 ⭐ 🌕 💣 🏟️", ["vs Fisher"], n("Aaron Judge", "Fisher", "Fisher owns the slate's loudest RHB risk", "Worst Pickz favorite with 11 HR, 12 near-HR and 23.2% barrels"), "high"),
            row("Jazz Chisholm Jr.", "L", "+550", 78, "💎 🏟️", ["vs Fisher"], n("Jazz Chisholm Jr.", "Fisher", "park helps lefty lift but the split is less friendly", "4 HR, 5 near-HR and 22.5% pull-air")),
            row("Ryan McMahon", "L", "+600", 76, "💎 🏟️", ["vs Fisher"], n("Ryan McMahon", "Fisher", "Yankee porch is the hook", "4 HR, 7 near-HR and 90.6 mph EV")),
            row("Brandon Valenzuela", "S", "+920", 86, "🚀 ⭐ 🌕", ["vs Rodon"], n("Brandon Valenzuela", "Rodon", "Rodon is strong overall, but the switch bat's contact is loud", "Worst Pickz favorite with 2 HR, 96.6 mph EV and 23.1% barrels"), "good"),
            row("George Springer", "R", "+512", 84, "🚀 ⭐ 💎 📜", ["vs Rodon"], n("George Springer", "Rodon", "BvP history gives him the Toronto edge", "Worst Pickz favorite with 1 recent HR, 3 near-HR and 2 career HR off Rodon"), "good"),
            row("Ernie Clement", "R", "+1000", 68, "💎", ["vs Rodon"], n("Ernie Clement", "Rodon", "contact profile is better than HR profile", "2 HR in form, but only 2.2% barrels")),
        ],
    },
    {
        "title": "ATH @ LAA - Luis Severino (R, ATH) vs Jose Soriano (R, LAA)",
        "description": "Angel Stadium — the best pure HR weather on the slate at +5% HR with mild temps and typical out-blowing carry. Angels righties attack Severino's RHB damage, while A's lefty power gets Soriano's LHB weak spot.",
        "rows": [
            row("Zach Neto", "R", "+518", 82, "🚀 💎 🏟️", ["vs Severino"], n("Zach Neto", "Severino", "Angel Stadium gives the best weather lift today", "6 HR, 8 near-HR and 28.9% pull-air")),
            row("Jo Adell", "R", "+525", 72, "💎 🏟️", ["vs Severino"], n("Jo Adell", "Severino", "righty split is good but recent HR form is lighter", "90.1 mph EV with 42.0% hard-hit")),
            row("Mike Trout", "R", "+370", 90, "🚀 🌕 💣 🏟️ 📜", ["vs Severino"], n("Mike Trout", "Severino", "weather and BvP both help", "9 HR, 16 near-HR, 21.6% barrels and a career HR off Severino"), "high"),
            row("Nick Kurtz", "L", "+401", 93, "🚀 ⭐ 🌕 💣 🏟️ 📜", ["vs Soriano"], n("Nick Kurtz", "Soriano", "Soriano's LHB HR-risk plus Angel carry is premium", "Worst Pickz favorite with 4 HR, 5 near-HR, 97.6 mph EV and a BvP HR"), "high"),
            row("Brent Rooker", "R", "+460", 86, "🚀 🌕 💎 🏟️ 📜", ["vs Soriano"], n("Brent Rooker", "Soriano", "righty split is tougher but form and BvP are strong", "4 HR, 6 near-HR, 20.9% barrels and a career HR off Soriano"), "good"),
        ],
    },
    {
        "title": "COL @ ARI - Zach Agnos (R, COL) vs Eduardo Rodriguez (L, ARI)",
        "description": "Chase Field — roof scheduled open, 90° desert air and a 9.5 total. Ballpark Pal still grades HR at -8%, but altitude/temperature and Agnos' RHB risk keep Arizona bats live.",
        "rows": [
            row("Corbin Carroll", "L", "+410", 88, "🚀 ⭐ 🌕 💎", ["vs Agnos"], n("Corbin Carroll", "Agnos", "Agnos is better vs LHB, but Chase open/heat helps", "Worst Pickz favorite with 6 HR, 10 near-HR, .289 ISO and 16.7% barrels"), "high"),
            row("Ketel Marte", "S", "+425", 84, "🚀 🌕 💎", ["vs Agnos"], n("Ketel Marte", "Agnos", "RHB/S switch-hit lane is helped by Agnos' RHB risk", "6 HR, 12 near-HR and 21.8% pull-air")),
            row("Hunter Goodman", "R", "+460", 82, "🚀 💎", ["vs Eduardo Rodriguez"], n("Hunter Goodman", "Eduardo Rodriguez", "roof-open Chase helps counter a neutral split", "3 HR, 4 near-HR, 91.5 mph EV and 16.0% barrels")),
        ],
    },
]

PROP_NAMES = {name.split(" (")[0] for name in PLAYER_TEAMS}
found = {r["name"].split(" (")[0] for g in games for r in g["rows"]}
missing = sorted(PROP_NAMES - found)
if missing:
    raise SystemExit(f"Missing props: {missing}")

for game in games:
    for entry in game["rows"]:
        apply_inferred_due(entry, game)


def js_string(value):
    return json.dumps(value, ensure_ascii=False)


def emit_games_js(games_data):
    lines = ["const games = ["]
    for game in games_data:
        lines.append("    {")
        lines.append(f"        title: {js_string(game['title'])},")
        lines.append(f"        description: {js_string(game['description'])},")
        lines.append("        rows: [")
        for entry in game["rows"]:
            parts = [
                f"name: {js_string(entry['name'])}",
                f"odds: {js_string(entry['odds'])}",
                f"score: {entry['score']}",
                f"emojis: {js_string(entry['emojis'])}",
                f"note: {js_string(entry['note'])}",
                f"chips: {js_string(entry['chips'])}",
            ]
            if entry.get("blast"):
                parts.append(f"blast: {js_string(entry['blast'])}")
            lines.append("            { " + ", ".join(parts) + " },")
        lines.append("        ],")
        lines.append("    },")
    lines.append("];")
    return "\n".join(lines)


if __name__ == "__main__":
    print(emit_games_js(games))
