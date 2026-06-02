#!/usr/bin/env python3
"""Generate games[] block for 2026-06-02 MLB HR cheat sheet."""
import json
from pathlib import Path

from overdue_eval import apply_inferred_due

ROOT = Path(__file__).resolve().parent

FAVS = {
    "Bobby Witt Jr. (R)",
    "Brandon Lowe (L)",
    "Brandon Nimmo (L)",
    "Casey Schmitt (R)",
    "Coby Mayo (R)",
    "Curtis Mead (R)",
    "Hunter Goodman (R)",
    "JJ Bleday (L)",
    "Jackson Chourio (R)",
    "James Wood (L)",
    "Jarren Duran (L)",
    "Jesus Sanchez (L)",
    "Jonathan Aranda (L)",
    "Luke Raley (L)",
    "Max Muncy (L)",
    "Michael Massey (L)",
    "Miguel Vargas (R)",
    "Spencer Horwitz (L)",
    "Trea Turner (R)",
    "Will Smith (R)",
    "Willy Adames (R)",
    "Yordan Alvarez (L)",
}

PLAYER_TEAMS = {
    "Anthony Volpe (R)": "NYY",
    "Ben Rice (L)": "NYY",
    "Bobby Witt Jr. (R)": "KC",
    "Brandon Lowe (L)": "PIT",
    "Brandon Nimmo (L)": "TEX",
    "Bryan Reynolds (S)": "PIT",
    "Bryce Eldridge (L)": "SF",
    "Bryson Stott (L)": "PHI",
    "Byron Buxton (R)": "MIN",
    "CJ Abrams (L)": "WSH",
    "Carlos Cortes (L)": "ATH",
    "Casey Schmitt (R)": "SF",
    "Christian Walker (R)": "HOU",
    "Coby Mayo (R)": "BAL",
    "Colson Montgomery (L)": "CWS",
    "Colt Emerson (L)": "SEA",
    "Curtis Mead (R)": "WSH",
    "Daulton Varsho (L)": "TOR",
    "Dominic Canzone (L)": "SEA",
    "Eugenio Suarez (R)": "CIN",
    "Ezequiel Tovar (R)": "COL",
    "Freddie Freeman (L)": "LAD",
    "Gabriel Moreno (R)": "ARI",
    "Garrett Mitchell (L)": "MIL",
    "Gavin Sheets (L)": "SD",
    "Heriberto Hernandez (R)": "MIA",
    "Hunter Goodman (R)": "COL",
    "Ildemaro Vargas (S)": "ARI",
    "J.P. Crawford (L)": "SEA",
    "J.T. Realmuto (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "Jackson Chourio (R)": "MIL",
    "Jacob Young (R)": "WSH",
    "Jake McCarthy (L)": "COL",
    "James Wood (L)": "WSH",
    "Jared Young (L)": "NYM",
    "Jarren Duran (L)": "BOS",
    "Jesus Sanchez (L)": "TOR",
    "Jo Adell (R)": "LAA",
    "Jonathan Aranda (L)": "TB",
    "Jordan Walker (R)": "STL",
    "Josh Bell (S)": "MIN",
    "Josh Jung (R)": "TEX",
    "Juan Soto (L)": "NYM",
    "Junior Caminero (R)": "TB",
    "Ketel Marte (S)": "ARI",
    "Kyle Manzardo (L)": "CLE",
    "Kyle Schwarber (L)": "PHI",
    "Luis Garcia Jr. (L)": "WSH",
    "Luke Raley (L)": "SEA",
    "Manny Machado (R)": "SD",
    "Marcus Semien (R)": "NYM",
    "Masataka Yoshida (L)": "BOS",
    "Matt Chapman (R)": "SF",
    "Matt Olson (L)": "ATL",
    "Max Muncy (L)": "LAD",
    "Michael Harris II (L)": "ATL",
    "Michael Massey (L)": "KC",
    "Mickey Gasper (S)": "BOS",
    "Miguel Vargas (R)": "CWS",
    "Mike Trout (R)": "LAA",
    "Mike Yastrzemski (L)": "ATL",
    "Nick Kurtz (L)": "ATH",
    "Nolan Arenado (R)": "ARI",
    "Oneil Cruz (L)": "PIT",
    "Otto Lopez (R)": "MIA",
    "Pete Alonso (R)": "BAL",
    "Pete Crow-Armstrong (L)": "CHC",
    "Randal Grichuk (R)": "CWS",
    "Ronald Acuna Jr. (R)": "ATL",
    "Ryan O'Hearn (L)": "PIT",
    "Ryan Vilade (R)": "TB",
    "Salvador Perez (R)": "KC",
    "Seiya Suzuki (R)": "CHC",
    "Shohei Ohtani (L)": "LAD",
    "Spencer Horwitz (L)": "PIT",
    "Spencer Torkelson (R)": "DET",
    "Travis Bazzana (L)": "CLE",
    "Trea Turner (R)": "PHI",
    "Trent Grisham (L)": "NYY",
    "Tristan Gray (L)": "MIN",
    "Ty France (R)": "SD",
    "Wade Meckler (L)": "LAA",
    "Wenceel Perez (S)": "DET",
    "Will Smith (R)": "LAD",
    "William Contreras (R)": "MIL",
    "Willy Adames (R)": "SF",
    "Xavier Edwards (S)": "MIA",
    "Yandy Diaz (R)": "TB",
    "Yordan Alvarez (L)": "HOU",
    "Zach Neto (R)": "LAA",
}

BUM_PITCHERS = {
    "Bachar",
    "Lauer",
    "Sugano",
    "Taillon",
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
        "title": "ATH @ CHC - Gage Jump (R, ATH) vs Jameson Taillon 🧤 (R, CHC)",
        "description": "Tail key data: Park boost -32% (stadium -1%, weather -31%). Away starter risk unavailable. Jameson Taillon 🧤 (HR risk 1.80, vs LHB +1.80, vs RHB +1.10).",
        "rows": [
            row("Pete Crow-Armstrong", "L", "+675", 80, "💎", ["vs Jump"], """Tail: 1 HR, 1 near-HR, 98.2 mph EV. Matchup: Jump split/risk data unavailable. Fade: limited split/risk sample; park/weather net drag (-32%). Model score 80; odds Listed +675 - Over 0.5 HR.""", blast="good"),
            row("Seiya Suzuki", "R", "+550", 62, "💎", ["vs Jump"], """Tail: 0 HR, 87.0 mph EV. Matchup: Jump split/risk data unavailable. Fade: limited split/risk sample; park/weather net drag (-32%). Model score 62; odds Listed +550 - Over 0.5 HR."""),
            row("Carlos Cortes", "L", "+900", 72, "💎", ["vs Taillon"], """Tail: 1 HR, 2 near-HR, 88.3 mph EV. Matchup: Taillon LHB split +1.80, HR risk 1.80. Fade: park/weather net drag (-32%). Model score 72; odds Listed +900 - Over 0.5 HR.""", blast="good"),
            row("Nick Kurtz", "L", "+360", 64, "💎", ["vs Taillon"], """Tail: 0 HR, 1 near-HR, 84.6 mph EV. Matchup: Taillon LHB split +1.80, HR risk 1.80. Fade: park/weather net drag (-32%); limited recent HR events. Model score 64; odds Listed +360 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "BAL @ BOS - Shane Baz (R, BAL) vs Connelly Early (R, BOS)",
        "description": "Tail key data: Park boost -15% (stadium -8%, weather -8%). Shane Baz (HR risk 0.13, vs LHB -0.23, vs RHB +0.61). Connelly Early (HR risk 0.19, vs LHB +0.72, vs RHB +0.00).",
        "rows": [
            row("Jarren Duran", "L", "+590", 92, "⭐ 🌕 💣", ["vs Baz"], """Worst Pickz Favorite. Tail: 3 HR, 4 near-HR, 94.4 mph EV. Matchup: Baz LHB split -0.23, HR risk 0.13. Fade: slight split headwind (-0.23); park/weather net drag (-15%). Model score 92; odds Listed +590 - Over 0.5 HR.""", blast="high"),
            row("Masataka Yoshida", "L", "+920", 78, "💎", ["vs Baz"], """Tail: 1 HR, 2 near-HR, 94.3 mph EV. Matchup: Baz LHB split -0.23, HR risk 0.13. Fade: slight split headwind (-0.23); park/weather net drag (-15%). Model score 78; odds Listed +920 - Over 0.5 HR.""", blast="good"),
            row("Mickey Gasper", "S", "+980", 73, "💎", ["vs Baz"], """Tail: 0 HR, 2 near-HR, 92.7 mph EV. Matchup: Baz RHB split +0.61, HR risk 0.13. Fade: park/weather net drag (-15%). Model score 73; odds Listed +980 - Over 0.5 HR.""", blast="good"),
            row("Coby Mayo", "R", "+540", 78, "⭐ 💎", ["vs Early"], """Worst Pickz Favorite. Tail: 1 HR, 1 near-HR, 95.8 mph EV. Matchup: Early RHB split +0.00, HR risk 0.19. Fade: park/weather net drag (-15%). Model score 78; odds Listed +540 - Over 0.5 HR.""", blast="good"),
            row("Pete Alonso", "R", "+420", 73, "💎", ["vs Early"], """Tail: 0 HR, 1 near-HR, 95.4 mph EV. Matchup: Early RHB split +0.00, HR risk 0.19. Fade: park/weather net drag (-15%); limited recent HR events. Model score 73; odds Listed +420 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "CLE @ NYY - Joey Cantillo (R, CLE) vs Cam Schlittler (R, NYY)",
        "description": "Tail key data: Park boost -8% (stadium +8%, weather -16%). Joey Cantillo (HR risk -0.42, vs LHB -0.01, vs RHB -0.41). Cam Schlittler (HR risk -0.76, vs LHB -0.64, vs RHB -0.60).",
        "rows": [
            row("Trent Grisham", "L", "+474", 78, "💎", ["vs Cantillo"], """Tail: 1 HR, 1 near-HR, 96.2 mph EV. Matchup: Cantillo LHB split -0.01, HR risk -0.42. Fade: slight split headwind (-0.01); pitcher suppresses HR (-0.42). Model score 78; odds Listed +474 - Over 0.5 HR.""", blast="good"),
            row("Ben Rice", "L", "+370", 74, "💎", ["vs Cantillo"], """Tail: 0 HR, 1 near-HR, 96.4 mph EV. Matchup: Cantillo LHB split -0.01, HR risk -0.42. Fade: slight split headwind (-0.01); pitcher suppresses HR (-0.42). Model score 74; odds Listed +370 - Over 0.5 HR.""", blast="good"),
            row("Anthony Volpe", "R", "+920", 70, "💎", ["vs Cantillo"], """Tail: 1 HR, 1 near-HR, 84.5 mph EV. Matchup: Cantillo RHB split -0.41, HR risk -0.42. Fade: tough split lane (-0.41); pitcher suppresses HR (-0.42). Model score 70; odds Listed +920 - Over 0.5 HR.""", blast="good"),
            row("Travis Bazzana", "L", "+900", 74, "💎", ["vs Schlittler"], """Tail: 1 HR, 1 near-HR, 91.6 mph EV. Matchup: Schlittler LHB split -0.64, HR risk -0.76. Fade: tough split lane (-0.64); pitcher suppresses HR (-0.76). Model score 74; odds Listed +900 - Over 0.5 HR.""", blast="good"),
            row("Kyle Manzardo", "L", "+587", 76, "💎", ["vs Schlittler"], """Tail: 0 HR, 99.8 mph EV. Matchup: Schlittler LHB split -0.64, HR risk -0.76. Fade: tough split lane (-0.64); pitcher suppresses HR (-0.76). Model score 76; odds Listed +587 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "COL @ LAA - Tomoyuki Sugano 🧤 (R, COL) vs Grayson Rodriguez (R, LAA)",
        "description": "Tail key data: Park boost +11% (stadium +8%, weather +2%). Tomoyuki Sugano 🧤 (HR risk 1.19, vs LHB +1.81, vs RHB -0.04). Grayson Rodriguez (HR risk 0.28, vs LHB +1.07, vs RHB -1.03).",
        "rows": [
            row("Zach Neto", "R", "+357", 80, "🌕 💣", ["vs Sugano"], """Tail: 2 HR, 3 near-HR, 87.7 mph EV. Matchup: Sugano RHB split -0.04, HR risk 1.19. Fade: slight split headwind (-0.04); lighter EV form (87.7 mph). Model score 80; odds Listed +357 - Over 0.5 HR.""", blast="high"),
            row("Jo Adell", "R", "+390", 83, "🌕 💣", ["vs Sugano"], """Tail: 2 HR, 3 near-HR, 90.6 mph EV. Matchup: Sugano RHB split -0.04, HR risk 1.19. Fade: slight split headwind (-0.04). Model score 83; odds Listed +390 - Over 0.5 HR.""", blast="high"),
            row("Mike Trout", "R", "+290", 84, "🌕 💣", ["vs Sugano"], """Tail: 2 HR, 4 near-HR, 90.4 mph EV. Matchup: Sugano RHB split -0.04, HR risk 1.19. Fade: slight split headwind (-0.04). Model score 84; odds Listed +290 - Over 0.5 HR.""", blast="high"),
            row("Wade Meckler", "L", "+710", 82, "🌕 💣", ["vs Sugano"], """Tail: 2 HR, 4 near-HR, 87.7 mph EV. Matchup: Sugano LHB split +1.81, HR risk 1.19. Fade: lighter EV form (87.7 mph). Model score 82; odds Listed +710 - Over 0.5 HR.""", blast="high"),
            row("Hunter Goodman", "R", "+390", 80, "⭐ 🌕 💣", ["vs Rodriguez"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 90.3 mph EV. Matchup: Rodriguez RHB split -1.03, HR risk 0.28. Fade: tough split lane (-1.03). Model score 80; odds Listed +390 - Over 0.5 HR.""", blast="high"),
            row("Ezequiel Tovar", "R", "+790", 70, "💎", ["vs Rodriguez"], """Tail: 1 HR, 1 near-HR, 82.0 mph EV. Matchup: Rodriguez RHB split -1.03, HR risk 0.28. Fade: tough split lane (-1.03); lighter EV form (82.0 mph). Model score 70; odds Listed +790 - Over 0.5 HR.""", blast="good"),
            row("Jake McCarthy", "L", "+820", 72, "💎", ["vs Rodriguez"], """Tail: 1 HR, 2 near-HR, 85.6 mph EV. Matchup: Rodriguez LHB split +1.07, HR risk 0.28. Fade: lighter EV form (85.6 mph). Model score 72; odds Listed +820 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "CWS @ MIN - Davis Martin (R, CWS) vs Connor Prielipp (R, MIN)",
        "description": "Tail key data: Park boost data unavailable. Davis Martin (HR risk -0.73, vs LHB -0.59, vs RHB -0.56). Connor Prielipp (HR risk 0.11, vs LHB +0.27, vs RHB +0.13).",
        "rows": [
            row("Byron Buxton", "R", "+335", 75, "💎", ["vs Martin"], """Tail: 1 HR, 1 near-HR, 92.7 mph EV. Matchup: Martin RHB split -0.56, HR risk -0.73. Fade: tough split lane (-0.56); pitcher suppresses HR (-0.73). Model score 75; odds Listed +335 - Over 0.5 HR.""", blast="good"),
            row("Josh Bell", "S", "+650", 71, "💎", ["vs Martin"], """Tail: 0 HR, 1 near-HR, 92.7 mph EV. Matchup: Martin RHB split -0.56, HR risk -0.73. Fade: tough split lane (-0.56); pitcher suppresses HR (-0.73). Model score 71; odds Listed +650 - Over 0.5 HR.""", blast="good"),
            row("Tristan Gray", "L", "+850", 76, "💎", ["vs Martin"], """Tail: 1 HR, 3 near-HR, 90.2 mph EV. Matchup: Martin LHB split -0.59, HR risk -0.73. Fade: tough split lane (-0.59); pitcher suppresses HR (-0.73). Model score 76; odds Listed +850 - Over 0.5 HR.""", blast="good"),
            row("Miguel Vargas", "R", "+500", 86, "⭐ 🌕 💣", ["vs Prielipp"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 96.0 mph EV. Matchup: Prielipp RHB split +0.13, HR risk 0.11. Fade: HR outcomes are still high-variance. Model score 86; odds Listed +500 - Over 0.5 HR.""", blast="high"),
            row("Colson Montgomery", "L", "+390", 69, "💎", ["vs Prielipp"], """Tail: 0 HR, 2 near-HR, 89.2 mph EV. Matchup: Prielipp LHB split +0.27, HR risk 0.11. Fade: HR outcomes are still high-variance. Model score 69; odds Listed +390 - Over 0.5 HR.""", blast="good"),
            row("Randal Grichuk", "R", "+522", 65, "💎", ["vs Prielipp"], """Tail: 0 HR, 91.0 mph EV. Matchup: Prielipp RHB split +0.13, HR risk 0.11. Fade: limited recent HR events. Model score 65; odds Listed +522 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "DET @ TB - Jack Flaherty (R, DET) vs Steven Matz (R, TB)",
        "description": "Tail key data: Park boost -4% (stadium -4%, weather +0%). Jack Flaherty (HR risk 0.13, vs LHB +0.01, vs RHB +0.16). Steven Matz (HR risk 0.29, vs LHB +0.18, vs RHB +0.37).",
        "rows": [
            row("Yandy Diaz", "R", "+540", 78, "💎", ["vs Flaherty"], """Tail: 1 HR, 1 near-HR, 95.7 mph EV. Matchup: Flaherty RHB split +0.16, HR risk 0.13. Fade: HR outcomes are still high-variance. Model score 78; odds Listed +540 - Over 0.5 HR.""", blast="good"),
            row("Jonathan Aranda", "L", "+410", 83, "⭐ 🌕 💣", ["vs Flaherty"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 90.6 mph EV. Matchup: Flaherty LHB split +0.01, HR risk 0.13. Fade: HR outcomes are still high-variance. Model score 83; odds Listed +410 - Over 0.5 HR.""", blast="high"),
            row("Junior Caminero", "R", "+330", 66, "💎", ["vs Flaherty"], """Tail: 0 HR, 91.6 mph EV. Matchup: Flaherty RHB split +0.16, HR risk 0.13. Fade: limited recent HR events. Model score 66; odds Listed +330 - Over 0.5 HR."""),
            row("Ryan Vilade", "R", "N/A", 82, "🌕 💣", ["vs Flaherty"], """Tail: 2 HR, 2 near-HR, 91.7 mph EV. Matchup: Flaherty RHB split +0.16, HR risk 0.13. Fade: HR outcomes are still high-variance. Model score 82; odds Listed prop - Over 0.5 HR.""", blast="high"),
            row("Wenceel Perez", "S", "+700", 70, "💎", ["vs Matz"], """Tail: 1 HR, 1 near-HR, 87.9 mph EV. Matchup: Matz RHB split +0.37, HR risk 0.29. Fade: lighter EV form (87.9 mph). Model score 70; odds Listed +700 - Over 0.5 HR.""", blast="good"),
            row("Spencer Torkelson", "R", "+490", 64, "💎", ["vs Matz"], """Tail: 0 HR, 1 near-HR, 87.9 mph EV. Matchup: Matz RHB split +0.37, HR risk 0.29. Fade: limited recent HR events; lighter EV form (87.9 mph). Model score 64; odds Listed +490 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "KC @ CIN - Noah Cameron (R, KC) vs Andrew Abbott (R, CIN)",
        "description": "Tail key data: Park boost +6% (stadium +14%, weather -9%). Noah Cameron (HR risk -0.70, vs LHB +0.00, vs RHB -0.75). Andrew Abbott (HR risk -0.17, vs LHB -0.22, vs RHB -0.02).",
        "rows": [
            row("JJ Bleday", "L", "+340", 79, "⭐ 🌕 💣", ["vs Cameron"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 89.2 mph EV. Matchup: Cameron LHB split +0.00, HR risk -0.70. Fade: pitcher suppresses HR (-0.70); weather carry headwind (-9%). Model score 79; odds Listed +340 - Over 0.5 HR.""", blast="high"),
            row("Eugenio Suarez", "R", "+357", 76, "💎", ["vs Cameron"], """Tail: 1 HR, 1 near-HR, 94.3 mph EV. Matchup: Cameron RHB split -0.75, HR risk -0.70. Fade: tough split lane (-0.75); pitcher suppresses HR (-0.70). Model score 76; odds Listed +357 - Over 0.5 HR.""", blast="good"),
            row("Michael Massey", "L", "+307", 72, "⭐ 💎", ["vs Abbott"], """Worst Pickz Favorite. Tail: 1 HR, 2 near-HR, 84.1 mph EV. Matchup: Abbott LHB split -0.22, HR risk -0.17. Fade: slight split headwind (-0.22); pitcher risk below avg (-0.17). Model score 72; odds Listed +307 - Over 0.5 HR.""", blast="good"),
            row("Salvador Perez", "R", "+362", 71, "💎", ["vs Abbott"], """Tail: 1 HR, 1 near-HR, 88.9 mph EV. Matchup: Abbott RHB split -0.02, HR risk -0.17. Fade: slight split headwind (-0.02); pitcher risk below avg (-0.17). Model score 71; odds Listed +362 - Over 0.5 HR.""", blast="good"),
            row("Bobby Witt Jr.", "R", "+300", 77, "⭐ 💎", ["vs Abbott"], """Worst Pickz Favorite. Tail: 0 HR, 2 near-HR, 97.0 mph EV. Matchup: Abbott RHB split -0.02, HR risk -0.17. Fade: slight split headwind (-0.02); pitcher risk below avg (-0.17). Model score 77; odds Listed +300 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "LAD @ ARI - Eric Lauer 🧤 (R, LAD) vs Michael Soroka (R, ARI)",
        "description": "Tail key data: Park boost -8% (stadium -7%, weather +0%). Eric Lauer 🧤 (HR risk 1.47, vs LHB +0.69, vs RHB +1.48). Michael Soroka (HR risk -0.85, vs LHB -0.50, vs RHB -1.01).",
        "rows": [
            row("Ketel Marte", "S", "+350", 74, "💎", ["vs Lauer"], """Tail: 0 HR, 2 near-HR, 93.7 mph EV. Matchup: Lauer RHB split +1.48, HR risk 1.47. Fade: park/weather net drag (-8%). Model score 74; odds Listed +350 - Over 0.5 HR.""", blast="good"),
            row("Nolan Arenado", "R", "+550", 80, "💎", ["vs Lauer"], """Tail: 1 HR, 2 near-HR, 96.2 mph EV. Matchup: Lauer RHB split +1.48, HR risk 1.47. Fade: park/weather net drag (-8%). Model score 80; odds Listed +550 - Over 0.5 HR.""", blast="good"),
            row("Gabriel Moreno", "R", "+775", 73, "💎", ["vs Lauer"], """Tail: 1 HR, 2 near-HR, 89.1 mph EV. Matchup: Lauer RHB split +1.48, HR risk 1.47. Fade: park/weather net drag (-8%). Model score 73; odds Listed +775 - Over 0.5 HR.""", blast="good"),
            row("Ildemaro Vargas", "S", "+790", 72, "💎", ["vs Lauer"], """Tail: 1 HR, 1 near-HR, 90.2 mph EV. Matchup: Lauer RHB split +1.48, HR risk 1.47. Fade: park/weather net drag (-8%). Model score 72; odds Listed +790 - Over 0.5 HR.""", blast="good"),
            row("Will Smith", "R", "+675", 88, "⭐ 🌕 💣", ["vs Soroka"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 96.1 mph EV. Matchup: Soroka RHB split -1.01, HR risk -0.85. Fade: tough split lane (-1.01); pitcher suppresses HR (-0.85). Model score 88; odds Listed +675 - Over 0.5 HR.""", blast="high"),
            row("Shohei Ohtani", "L", "+310", 87, "🌕 💣", ["vs Soroka"], """Tail: 2 HR, 2 near-HR, 97.4 mph EV. Matchup: Soroka LHB split -0.50, HR risk -0.85. Fade: tough split lane (-0.50); pitcher suppresses HR (-0.85). Model score 87; odds Listed +310 - Over 0.5 HR.""", blast="high"),
            row("Freddie Freeman", "L", "+600", 73, "💎", ["vs Soroka"], """Tail: 1 HR, 1 near-HR, 91.4 mph EV. Matchup: Soroka LHB split -0.50, HR risk -0.85. Fade: tough split lane (-0.50); pitcher suppresses HR (-0.85). Model score 73; odds Listed +600 - Over 0.5 HR.""", blast="good"),
            row("Max Muncy", "L", "+440", 84, "⭐ 🌕 💣", ["vs Soroka"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 92.5 mph EV. Matchup: Soroka LHB split -0.50, HR risk -0.85. Fade: tough split lane (-0.50); pitcher suppresses HR (-0.85). Model score 84; odds Listed +440 - Over 0.5 HR.""", blast="high"),
        ],
    },
    {
        "title": "MIA @ WSH - Lake Bachar 🧤 (R, MIA) vs Richard Lovelady (R, WSH)",
        "description": "Tail key data: Park boost data unavailable. Lake Bachar 🧤 (HR risk 1.47, vs LHB +0.37, vs RHB +1.30). Richard Lovelady (HR risk 0.20, vs LHB -0.89, vs RHB +1.04).",
        "rows": [
            row("Curtis Mead", "R", "+680", 88, "⭐ 🌕 💣", ["vs Bachar"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 96.4 mph EV. Matchup: Bachar RHB split +1.30, HR risk 1.47. Fade: HR outcomes are still high-variance. Model score 88; odds Listed +680 - Over 0.5 HR.""", blast="high"),
            row("Jacob Young", "R", "+1600", 81, "💎", ["vs Bachar"], """Tail: 1 HR, 2 near-HR, 97.1 mph EV. Matchup: Bachar RHB split +1.30, HR risk 1.47. Fade: HR outcomes are still high-variance. Model score 81; odds Listed +1600 - Over 0.5 HR.""", blast="good"),
            row("CJ Abrams", "L", "+593", 75, "💎", ["vs Bachar"], """Tail: 1 HR, 1 near-HR, 92.7 mph EV. Matchup: Bachar LHB split +0.37, HR risk 1.47. Fade: HR outcomes are still high-variance. Model score 75; odds Listed +593 - Over 0.5 HR.""", blast="good"),
            row("James Wood", "L", "+379", 80, "⭐ 💎", ["vs Bachar"], """Worst Pickz Favorite. Tail: 1 HR, 1 near-HR, 97.7 mph EV. Matchup: Bachar LHB split +0.37, HR risk 1.47. Fade: HR outcomes are still high-variance. Model score 80; odds Listed +379 - Over 0.5 HR.""", blast="good"),
            row("Luis Garcia Jr.", "L", "+570", 76, "💎", ["vs Bachar"], """Tail: 1 HR, 2 near-HR, 92.0 mph EV. Matchup: Bachar LHB split +0.37, HR risk 1.47. Fade: HR outcomes are still high-variance. Model score 76; odds Listed +570 - Over 0.5 HR.""", blast="good"),
            row("Heriberto Hernandez", "R", "N/A", 73, "💎", ["vs Lovelady"], """Tail: 0 HR, 1 near-HR, 95.0 mph EV. Matchup: Lovelady RHB split +1.04, HR risk 0.20. Fade: limited recent HR events. Model score 73; odds Listed prop - Over 0.5 HR.""", blast="good"),
            row("Otto Lopez", "R", "+760", 73, "💎", ["vs Lovelady"], """Tail: 0 HR, 1 near-HR, 95.1 mph EV. Matchup: Lovelady RHB split +1.04, HR risk 0.20. Fade: limited recent HR events. Model score 73; odds Listed +760 - Over 0.5 HR.""", blast="good"),
            row("Xavier Edwards", "S", "+1300", 73, "💎", ["vs Lovelady"], """Tail: 1 HR, 1 near-HR, 90.9 mph EV. Matchup: Lovelady RHB split +1.04, HR risk 0.20. Fade: HR outcomes are still high-variance. Model score 73; odds Listed +1300 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "NYM @ SEA - Jonah Tong (R, NYM) vs Logan Gilbert (R, SEA)",
        "description": "Tail key data: Park boost +4% (stadium +0%, weather +3%). Away starter risk unavailable. Logan Gilbert (HR risk 0.85, vs LHB +0.61, vs RHB +0.77).",
        "rows": [
            row("Dominic Canzone", "L", "+650", 73, "💎", ["vs Tong"], """Tail: 1 HR, 1 near-HR, 90.9 mph EV. Matchup: Tong split/risk data unavailable. Fade: limited split/risk sample. Model score 73; odds Listed +650 - Over 0.5 HR.""", blast="good"),
            row("Luke Raley", "L", "+475", 78, "⭐ 🌕 💣", ["vs Tong"], """Worst Pickz Favorite. Tail: 2 HR, 2 near-HR, 83.9 mph EV. Matchup: Tong split/risk data unavailable. Fade: limited split/risk sample; lighter EV form (83.9 mph). Model score 78; odds Listed +475 - Over 0.5 HR.""", blast="high"),
            row("J.P. Crawford", "L", "+790", 81, "🌕 💣", ["vs Tong"], """Tail: 2 HR, 2 near-HR, 90.8 mph EV. Matchup: Tong split/risk data unavailable. Fade: limited split/risk sample. Model score 81; odds Listed +790 - Over 0.5 HR.""", blast="high"),
            row("Colt Emerson", "L", "+760", 74, "💎", ["vs Tong"], """Tail: 1 HR, 1 near-HR, 92.2 mph EV. Matchup: Tong split/risk data unavailable. Fade: limited split/risk sample. Model score 74; odds Listed +760 - Over 0.5 HR.""", blast="good"),
            row("Juan Soto", "L", "+310", 98, "🌕 💣", ["vs Gilbert"], """Tail: 4 HR, 5 near-HR, 97.6 mph EV. Matchup: Gilbert LHB split +0.61, HR risk 0.85. Fade: HR outcomes are still high-variance. Model score 98; odds Listed +310 - Over 0.5 HR.""", blast="high"),
            row("Jared Young", "L", "+680", 84, "🌕 💣", ["vs Gilbert"], """Tail: 2 HR, 2 near-HR, 93.6 mph EV. Matchup: Gilbert LHB split +0.61, HR risk 0.85. Fade: HR outcomes are still high-variance. Model score 84; odds Listed +680 - Over 0.5 HR.""", blast="high"),
            row("Marcus Semien", "R", "+725", 72, "💎", ["vs Gilbert"], """Tail: 1 HR, 2 near-HR, 88.1 mph EV. Matchup: Gilbert RHB split +0.77, HR risk 0.85. Fade: HR outcomes are still high-variance. Model score 72; odds Listed +725 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "PIT @ HOU - Bubba Chandler (R, PIT) vs Mike Burrows (R, HOU)",
        "description": "Tail key data: Park boost +6% (stadium +7%, weather -1%). Bubba Chandler (HR risk -0.13, vs LHB +0.13, vs RHB -0.46). Mike Burrows (HR risk 0.43, vs LHB +0.56, vs RHB -0.02).",
        "rows": [
            row("Yordan Alvarez", "L", "+270", 79, "⭐ 💎", ["vs Chandler"], """Worst Pickz Favorite. Tail: 1 HR, 2 near-HR, 95.3 mph EV. Matchup: Chandler LHB split +0.13, HR risk -0.13. Fade: pitcher risk below avg (-0.13). Model score 79; odds Listed +270 - Over 0.5 HR.""", blast="good"),
            row("Christian Walker", "R", "+410", 75, "💎", ["vs Chandler"], """Tail: 1 HR, 1 near-HR, 93.3 mph EV. Matchup: Chandler RHB split -0.46, HR risk -0.13. Fade: tough split lane (-0.46); pitcher risk below avg (-0.13). Model score 75; odds Listed +410 - Over 0.5 HR.""", blast="good"),
            row("Spencer Horwitz", "L", "+540", 84, "⭐ 🌕 💣", ["vs Burrows"], """Worst Pickz Favorite. Tail: 3 HR, 3 near-HR, 86.7 mph EV. Matchup: Burrows LHB split +0.56, HR risk 0.43. Fade: lighter EV form (86.7 mph). Model score 84; odds Listed +540 - Over 0.5 HR.""", blast="high"),
            row("Brandon Lowe", "L", "+320", 90, "⭐ 🌕 💣", ["vs Burrows"], """Worst Pickz Favorite. Tail: 2 HR, 5 near-HR, 94.3 mph EV. Matchup: Burrows LHB split +0.56, HR risk 0.43. Fade: HR outcomes are still high-variance. Model score 90; odds Listed +320 - Over 0.5 HR.""", blast="high"),
            row("Oneil Cruz", "L", "+410", 91, "🌕 💣", ["vs Burrows"], """Tail: 2 HR, 3 near-HR, 99.2 mph EV. Matchup: Burrows LHB split +0.56, HR risk 0.43. Fade: HR outcomes are still high-variance. Model score 91; odds Listed +410 - Over 0.5 HR.""", blast="high"),
            row("Bryan Reynolds", "S", "+570", 72, "💎", ["vs Burrows"], """Tail: 1 HR, 1 near-HR, 89.9 mph EV. Matchup: Burrows RHB split -0.02, HR risk 0.43. Fade: slight split headwind (-0.02). Model score 72; odds Listed +570 - Over 0.5 HR.""", blast="good"),
            row("Ryan O'Hearn", "L", "+590", 86, "🌕 💣", ["vs Burrows"], """Tail: 3 HR, 3 near-HR, 90.1 mph EV. Matchup: Burrows LHB split +0.56, HR risk 0.43. Fade: HR outcomes are still high-variance. Model score 86; odds Listed +590 - Over 0.5 HR.""", blast="high"),
        ],
    },
    {
        "title": "SD @ PHI - Randy Vasquez (R, SD) vs Aaron Nola (R, PHI)",
        "description": "Tail key data: Park boost -7% (stadium +14%, weather -21%). Randy Vasquez (HR risk 0.46, vs LHB -0.13, vs RHB +1.03). Aaron Nola (HR risk 0.16, vs LHB +0.09, vs RHB +0.22).",
        "rows": [
            row("Trea Turner", "R", "+630", 86, "⭐ 🌕 💣", ["vs Vasquez"], """Worst Pickz Favorite. Tail: 2 HR, 3 near-HR, 93.5 mph EV. Matchup: Vasquez RHB split +1.03, HR risk 0.46. Fade: park/weather net drag (-7%). Model score 86; odds Listed +630 - Over 0.5 HR.""", blast="high"),
            row("Bryson Stott", "L", "+650", 77, "💎", ["vs Vasquez"], """Tail: 1 HR, 2 near-HR, 92.6 mph EV. Matchup: Vasquez LHB split -0.13, HR risk 0.46. Fade: slight split headwind (-0.13); park/weather net drag (-7%). Model score 77; odds Listed +650 - Over 0.5 HR.""", blast="good"),
            row("J.T. Realmuto", "R", "+820", 73, "💎", ["vs Vasquez"], """Tail: 1 HR, 1 near-HR, 90.6 mph EV. Matchup: Vasquez RHB split +1.03, HR risk 0.46. Fade: park/weather net drag (-7%). Model score 73; odds Listed +820 - Over 0.5 HR.""", blast="good"),
            row("Kyle Schwarber", "L", "+250", 91, "🌕 💣", ["vs Vasquez"], """Tail: 2 HR, 3 near-HR, 99.2 mph EV. Matchup: Vasquez LHB split -0.13, HR risk 0.46. Fade: slight split headwind (-0.13); park/weather net drag (-7%). Model score 91; odds Listed +250 - Over 0.5 HR.""", blast="high"),
            row("Manny Machado", "R", "+543", 90, "🌕 💣", ["vs Nola"], """Tail: 2 HR, 3 near-HR, 97.6 mph EV. Matchup: Nola RHB split +0.22, HR risk 0.16. Fade: park/weather net drag (-7%). Model score 90; odds Listed +543 - Over 0.5 HR.""", blast="high"),
            row("Gavin Sheets", "L", "+490", 62, "💎", ["vs Nola"], """Tail: 0 HR, 87.3 mph EV. Matchup: Nola LHB split +0.09, HR risk 0.16. Fade: park/weather net drag (-7%); limited recent HR events. Model score 62; odds Listed +490 - Over 0.5 HR."""),
            row("Ty France", "R", "+600", 67, "💎", ["vs Nola"], """Tail: 0 HR, 1 near-HR, 90.6 mph EV. Matchup: Nola RHB split +0.22, HR risk 0.16. Fade: park/weather net drag (-7%); limited recent HR events. Model score 67; odds Listed +600 - Over 0.5 HR."""),
        ],
    },
    {
        "title": "SF @ MIL - Trevor McDonald (R, SF) vs Kyle Harrison (R, MIL)",
        "description": "Tail key data: Park boost -10% (stadium +10%, weather -20%). Trevor McDonald (HR risk -0.69, vs LHB -0.10, vs RHB -1.22). Kyle Harrison (HR risk -1.05, vs LHB -1.31, vs RHB -0.56).",
        "rows": [
            row("William Contreras", "R", "+630", 70, "💎", ["vs McDonald"], """Tail: 0 HR, 93.9 mph EV. Matchup: McDonald RHB split -1.22, HR risk -0.69. Fade: tough split lane (-1.22); pitcher suppresses HR (-0.69). Model score 70; odds Listed +630 - Over 0.5 HR.""", blast="good"),
            row("Jackson Chourio", "R", "+590", 72, "⭐ 💎", ["vs McDonald"], """Worst Pickz Favorite. Tail: 0 HR, 1 near-HR, 94.5 mph EV. Matchup: McDonald RHB split -1.22, HR risk -0.69. Fade: tough split lane (-1.22); pitcher suppresses HR (-0.69). Model score 72; odds Listed +590 - Over 0.5 HR.""", blast="good"),
            row("William Contreras", "R", "+630", 70, "💎", ["vs McDonald"], """Tail: 0 HR, 93.9 mph EV. Matchup: McDonald RHB split -1.22, HR risk -0.69. Fade: tough split lane (-1.22); pitcher suppresses HR (-0.69). Model score 70; odds Listed +630 - Over 0.5 HR.""", blast="good"),
            row("Garrett Mitchell", "L", "+760", 72, "💎", ["vs McDonald"], """Tail: 1 HR, 1 near-HR, 90.3 mph EV. Matchup: McDonald LHB split -0.10, HR risk -0.69. Fade: slight split headwind (-0.10); pitcher suppresses HR (-0.69). Model score 72; odds Listed +760 - Over 0.5 HR.""", blast="good"),
            row("Matt Chapman", "R", "+610", 72, "💎", ["vs Harrison"], """Tail: 0 HR, 96.3 mph EV. Matchup: Harrison RHB split -0.56, HR risk -1.05. Fade: tough split lane (-0.56); pitcher suppresses HR (-1.05). Model score 72; odds Listed +610 - Over 0.5 HR.""", blast="good"),
            row("Bryce Eldridge", "L", "+700", 78, "🚀 💎", ["vs Harrison"], """Tail: 0 HR, 1 near-HR, 105.9 mph EV. Matchup: Harrison LHB split -1.31, HR risk -1.05. Fade: tough split lane (-1.31); pitcher suppresses HR (-1.05). Model score 78; odds Listed +700 - Over 0.5 HR.""", blast="good"),
            row("Willy Adames", "R", "+527", 62, "⭐ 💎", ["vs Harrison"], """Worst Pickz Favorite. Tail: 0 HR, 87.0 mph EV. Matchup: Harrison RHB split -0.56, HR risk -1.05. Fade: tough split lane (-0.56); pitcher suppresses HR (-1.05). Model score 62; odds Listed +527 - Over 0.5 HR."""),
            row("Casey Schmitt", "R", "+520", 70, "⭐ 💎", ["vs Harrison"], """Worst Pickz Favorite. Tail: 1 HR, 1 near-HR, 81.7 mph EV. Matchup: Harrison RHB split -0.56, HR risk -1.05. Fade: tough split lane (-0.56); pitcher suppresses HR (-1.05). Model score 70; odds Listed +520 - Over 0.5 HR.""", blast="good"),
        ],
    },
    {
        "title": "TEX @ STL - Nathan Eovaldi (R, TEX) vs Dustin May (R, STL)",
        "description": "Tail key data: Park boost -27% (stadium -9%, weather -18%). Nathan Eovaldi (HR risk -0.04, vs LHB -0.47, vs RHB +0.45). Dustin May (HR risk -0.32, vs LHB -0.29, vs RHB -0.28).",
        "rows": [
            row("Jordan Walker", "R", "+550", 83, "🌕 💣", ["vs Eovaldi"], """Tail: 2 HR, 2 near-HR, 92.8 mph EV. Matchup: Eovaldi RHB split +0.45, HR risk -0.04. Fade: pitcher risk below avg (-0.04); park/weather net drag (-27%). Model score 83; odds Listed +550 - Over 0.5 HR.""", blast="high"),
            row("Brandon Nimmo", "L", "+780", 84, "⭐ 🌕 💣", ["vs May"], """Worst Pickz Favorite. Tail: 1 HR, 4 near-HR, 93.9 mph EV. Matchup: May LHB split -0.29, HR risk -0.32. Fade: slight split headwind (-0.29); pitcher risk below avg (-0.32). Model score 84; odds Listed +780 - Over 0.5 HR.""", blast="high"),
            row("Josh Jung", "R", "+1100", 80, "🌕 💣", ["vs May"], """Tail: 2 HR, 2 near-HR, 89.9 mph EV. Matchup: May RHB split -0.28, HR risk -0.32. Fade: slight split headwind (-0.28); pitcher risk below avg (-0.32). Model score 80; odds Listed +1100 - Over 0.5 HR.""", blast="high"),
        ],
    },
    {
        "title": "TOR @ ATL - Kevin Gausman (R, TOR) vs Bryce Elder (R, ATL)",
        "description": "Tail key data: Park boost -15% (stadium -3%, weather -13%). Kevin Gausman (HR risk -0.76, vs LHB -0.69, vs RHB -0.46). Bryce Elder (HR risk -0.62, vs LHB -0.79, vs RHB +0.27).",
        "rows": [
            row("Michael Harris II", "L", "+520", 75, "💎", ["vs Gausman"], """Tail: 1 HR, 2 near-HR, 91.4 mph EV. Matchup: Gausman LHB split -0.69, HR risk -0.76. Fade: tough split lane (-0.69); pitcher suppresses HR (-0.76). Model score 75; odds Listed +520 - Over 0.5 HR.""", blast="good"),
            row("Mike Yastrzemski", "L", "+790", 68, "💎", ["vs Gausman"], """Tail: 0 HR, 92.3 mph EV. Matchup: Gausman LHB split -0.69, HR risk -0.76. Fade: tough split lane (-0.69); pitcher suppresses HR (-0.76). Model score 68; odds Listed +790 - Over 0.5 HR.""", blast="good"),
            row("Matt Olson", "L", "+410", 76, "💎", ["vs Gausman"], """Tail: 0 HR, 99.7 mph EV. Matchup: Gausman LHB split -0.69, HR risk -0.76. Fade: tough split lane (-0.69); pitcher suppresses HR (-0.76). Model score 76; odds Listed +410 - Over 0.5 HR.""", blast="good"),
            row("Ronald Acuna Jr.", "R", "+425", 72, "💎", ["vs Gausman"], """Tail: 0 HR, 95.7 mph EV. Matchup: Gausman RHB split -0.46, HR risk -0.76. Fade: tough split lane (-0.46); pitcher suppresses HR (-0.76). Model score 72; odds Listed +425 - Over 0.5 HR.""", blast="good"),
            row("Jesus Sanchez", "L", "+625", 79, "⭐ 💎", ["vs Elder"], """Worst Pickz Favorite. Tail: 1 HR, 2 near-HR, 94.7 mph EV. Matchup: Elder LHB split -0.79, HR risk -0.62. Fade: tough split lane (-0.79); pitcher suppresses HR (-0.62). Model score 79; odds Listed +625 - Over 0.5 HR.""", blast="good"),
            row("Daulton Varsho", "L", "+520", 67, "💎", ["vs Elder"], """Tail: 0 HR, 1 near-HR, 91.0 mph EV. Matchup: Elder LHB split -0.79, HR risk -0.62. Fade: tough split lane (-0.79); pitcher suppresses HR (-0.62). Model score 67; odds Listed +520 - Over 0.5 HR."""),
        ],
    },
]

for game in games:
    for entry in game['rows']:
        add_bum_row_emojis(entry)
        apply_inferred_due(entry, game)

if __name__ == '__main__':
    def js_string(value):
        return json.dumps(value, ensure_ascii=False)

    def emit_games_js(games_data):
        out = ['const games = [']
        for game in games_data:
            out.append('    {')
            out.append(f"        title: {js_string(game['title'])},")
            out.append(f"        description: {js_string(game['description'])},")
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

    out = ROOT / '_games-0602.txt'
    out.write_text(emit_games_js(games) + '\n', encoding='utf-8')
    print('wrote', out.name)
