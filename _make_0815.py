#!/usr/bin/env python3
"""Scaffold the 8/15 build / patch / audit / backfill scripts from the 8/14 set.

Run before the slate build. This regenerates patch-0815-preview.py from the 8/14
template, so run it BEFORE locking straights and Goblin legs — re-running it
afterwards overwrites those locks.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Eduardo Valencia💎",
    "Gleyber Torres",
    "Munetaka Murakami⭐",
    "Colson Montgomery💎",
    "Andrew Benintendi",
    "Braden Montgomery",
    "Ian Happ",
    "Miguel Amaya💎",
    "Pete Crow-Armstrong💎",
    "Michael Conforto",
    "Jordan Walker⭐",
    "Ivan Herrera",
    "Jimmy Crooks",
    "Jose Fermin",
    "Jesus Sanchez⭐",
    "Vladimir Guerrero Jr.",
    "Ernie Clement",
    "Trent Grisham",
    "Jazz Chisholm Jr.",
    "Luis Garcia Jr.",
    "Spencer Jones",
    "Ben Rice⭐",
    "Heliot Ramos",
    "Jung Hoo Lee",
    "Bryce Eldridge💎",
    "Rafael Devers",
    "Zac Veen💎",
    "Willi Castro",
    "Hunter Goodman",
    "Mickey Moniak",
    "Brett Baty💎",
    "Francisco Lindor",
    "Jorge Polanco",
    "Daylen Lile",
    "Brady House",
    "Andrew Pinckney",
    "Dylan Crews",
    "Jonathan Aranda",
    "Victor Mesa Jr.",
    "Junior Caminero",
    "Gunnar Henderson💎",
    "Christian Encarnacion-Strand",
    "Coby Mayo💎",
    "Pete Alonso⭐",
    "Jeremiah Jackson",
    "Tyler Stephenson💎",
    "Eugenio Suarez",
    "Sal Stewart",
    "Griffin Conine⭐",
    "Heriberto Hernandez",
    "Owen Caissie",
    "Joe Mack",
    "Royce Lewis⭐",
    "Byron Buxton",
    "Austin Martin",
    "Victor Caratini",
    "Bryson Stott",
    "Kyle Schwarber",
    "Trea Turner",
    "J.T. Realmuto💎",
    "Bryce Harper",
    "Yordan Alvarez⭐",
    "Taylor Trammell💎",
    "Daulton Varsho",
    "Nelson Velazquez",
    "Dominic Canzone⭐",
    "Cal Raleigh",
    "Josh Naylor",
    "Julio Rodriguez",
    "Randy Arozarena",
    "Nathaniel Lowe",
    "Chase DeLauter💎",
    "Jo Adell",
    "Rhys Hoskins",
    "Jase Bowen",
    "Fernando Tatis Jr.💎",
    "Jackson Merrill⭐",
    "Manny Machado💎",
    "Jacob Gonzalez",
    "Brandon Lowe💎",
    "Jake Mangum",
    "Connor Wong",
    "Jarren Duran💎",
    "Wilyer Abreu",
    "Shohei Ohtani",
    "Hunter Feduccia",
    "Teoscar Hernandez",
    "Max Muncy",
    "Andrew Vaughn💎",
    "Jake Bauers",
    "Jackson Chourio⭐",
    "Gary Sanchez",
    "Ozzie Albies",
    "Matt Olson",
    "Lane Thomas",
    "Austin Riley⭐",
    "Jim Jarvis",
    "Corbin Carroll⭐",
    "Lars Nootbaar💎",
    "Travis d'Arnaud",
    "Moises Ballesteros",
    "Josh Lowe",
    "Jac Caglianone⭐",
    "Carter Jensen💎",
    "Salvador Perez",
    "Tyler Soderstrom💎",
    "Jonah Heim",
    "Henry Bolte",
    "Zack Gelof",
    "Joc Pederson💎",
    "Corey Seager⭐",
    "Wyatt Langford",
]"""

ALIASES = """ALIASES = {
    # The request wrote "Btaden"; PropFinder and the CWS lineup have Braden.
    "Btaden Montgomery": "Braden Montgomery",
    "Braden Montgomery": "Braden Montgomery",
    "Colson Montgomery": "Colson Montgomery",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "JT Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Josh lowe": "Josh Lowe",
    "Josh Lowe": "Josh Lowe",
    "Brandon Lowe": "Brandon Lowe",
    "Nathaniel Lowe": "Nathaniel Lowe",
    "Travis d'Arnaud": "Travis d'Arnaud",
    "Travis dArnaud": "Travis d'Arnaud",
    "Randy Arozarena": "Randy Arozarena",
    "Munetaka Murakami": "Munetaka Murakami",
    "Moises Ballesteros": "Moises Ballesteros",
    "Moisés Ballesteros": "Moises Ballesteros",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Victor Mesa": "Victor Mesa Jr.",
    "Christian Encarnacion-Strand": "Christian Encarnacion-Strand",
    "Chase DeLauter": "Chase DeLauter",
    "Jonathan Aranda": "Jonathan Aranda",
    "Yordan Alvarez": "Yordan Alvarez",
    "Teoscar Hernandez": "Teoscar Hernandez",
    "Heriberto Hernandez": "Heriberto Hernandez",
    "Shohei Ohtani": "Shohei Ohtani",
    "Tyler Soderstrom": "Tyler Soderstrom",
    "Jac Caglianone": "Jac Caglianone",
    "Hunter Goodman": "Hunter Goodman",
    "Bryce Eldridge": "Bryce Eldridge",
    "Nelson Velazquez": "Nelson Velazquez",
    "Jorge Polanco": "Jorge Polanco",
    "Gary Sanchez": "Gary Sanchez",
    "Jesus Sanchez": "Jesus Sanchez",
    "Jung Hoo Lee": "Jung Hoo Lee",
}"""

# Two different Max Muncys are on this slate — PropFinder splits them by hand
# ("Max Muncy LHB" for LAD, "Max Muncy RHB" for ATH). The request means the
# Dodgers third baseman from the LAD lineup, so pin the game.
BATTER_GAME_OVERRIDES = """BATTER_GAME_OVERRIDES: dict[str, str] = {
    "Max Muncy": "MIL @ LAD",
}"""

# Braydon Fisher is PropFinder's listed TOR starter. The lineup card names
# Simeon Woods Richardson as the primary arm behind him, but he has no data in
# any 8/15 export, so the board is built on Fisher (user decision).
PITCHER_HAND = """PITCHER_HAND = {
    # 8/15 LHP
    "Anthony Kay": "L",
    "Matthew Boyd": "L",
    "Sean Manaea": "L",
    "Ian Seymour": "L",
    "Joey Cantillo": "L",
    "Jesus Luzardo": "L",
    "Connor Prielipp": "L",
    "Eduardo Rodriguez": "L",
    "Justin Wrobleski": "L",
    "Reid Detmers": "L",
    "MacKenzie Gore": "L",
    # 8/15 RHP
    "Troy Melton": "R",
    "Michael McGreevy": "R",
    "Cam Schlittler": "R",
    "Braydon Fisher": "R",
    "Michael Lorenzen": "R",
    "Logan Webb": "R",
    "Brad Lord": "R",
    "Kyle Bradish": "R",
    "Ryan Gusto": "R",
    "Brady Singer": "R",
    "Randy Vasquez": "R",
    "Emerson Hancock": "R",
    "Hayden Wesneski": "R",
    "Grant Holmes": "R",
    "Jacob Misiorowski": "R",
    "Sonny Gray": "R",
    "Jared Jones": "R",
    "Randy Dobnak": "R",
    "J.T. Ginn": "R",
}"""

# Surname fragments used to stamp `throws` on backfilled zone rows.
LHP_KEYS = [
    "Kay",
    "Boyd",
    "Manaea",
    "Seymour",
    "Cantillo",
    "Luzardo",
    "Prielipp",
    "Eduardo Rodriguez",
    "Wrobleski",
    "Detmers",
    "Gore",
]

GAMECOUNT = 15
EXPECTED_BUMS = ["Justin Wrobleski", "Michael Lorenzen", "Jared Jones"]
# LHP the audit spot-checks for a correct "(L" hand in the game titles.
AUDIT_LHP = [
    "Anthony Kay",
    "Matthew Boyd",
    "Sean Manaea",
    "Ian Seymour",
    "Jesus Luzardo",
    "MacKenzie Gore",
]

# Yesterday's starters must not survive anywhere in today's sheet. Pitchers only:
# several 8/14 bats are in 8/15 lineups without being listed props, so grepping
# their names would false-positive.
STALE_PITCHERS = [
    "Sandy Alcantara",
    "Chase Burns",
    "Jake Bennett",
    "Bubba Chandler",
    "Sean Newcomb",
    "Jackson Jobe",
    "Chris Bassitt",
    "Steven Matz",
    "Michael King",
    "Gavin Williams",
    "Andrew Alvarez",
    "Robert Stock",
    "Brandon Pfaadt",
    "Chris Sale",
    "Gerrit Cole",
    "Shane Bieber",
    "George Kirby",
    "Peter Lambert",
    "Seth Lugo",
    "Grayson Rodriguez",
    "Kumar Rocker",
    "Gage Jump",
    "Robert Gasser",
    "Yoshinobu Yamamoto",
    "Kyle Freeland",
    "Landen Roupp",
]


# Longest-match-first so "2026-08-14" is tokenized before the bare "08-14" rule
# can chew into the ISO string it just produced.
_DATE_SWAPS: list[tuple[str, str]] = [
    ("2026-08-14", "2026-08-15"),
    ("2026-08-13", "2026-08-14"),
    ("Friday, August 14, 2026", "Saturday, August 15, 2026"),
    ("Friday, August 14", "Saturday, August 15"),
    ("August 14, 2026", "August 15, 2026"),
    ("August 14", "August 15"),
    ("Thursday, August 13, 2026", "Friday, August 14, 2026"),
    ("Thursday, August 13", "Friday, August 14"),
    ("August 13, 2026", "August 14, 2026"),
    ("August 13", "August 14"),
    ("08-14", "08-15"),
    ("08-13", "08-14"),
    ("0814", "0815"),
    ("0813", "0814"),
    ("8/14", "8/15"),
    ("8/13", "8/14"),
]


def swap_dates(text: str) -> str:
    for idx, (needle, _) in enumerate(_DATE_SWAPS):
        text = text.replace(needle, f"\x00{idx}\x00")
    for idx, (_, sub) in enumerate(_DATE_SWAPS):
        text = text.replace(f"\x00{idx}\x00", sub)
    return text


def main() -> None:
    # ---- build script ----
    text = swap_dates((ROOT / "build-0814-from-csv.py").read_text(encoding="utf-8"))
    text = re.sub(r"RAW_PROPS = \[.*?\n\]", RAW_PROPS, text, count=1, flags=re.S)
    text = re.sub(r"ALIASES = \{.*?\n\}", ALIASES, text, count=1, flags=re.S)
    text = re.sub(
        r"BATTER_GAME_OVERRIDES: dict\[str, str\] = \{\}|BATTER_GAME_OVERRIDES: dict\[str, str\] = \{.*?\n\}",
        BATTER_GAME_OVERRIDES,
        text,
        count=1,
        flags=re.S,
    )
    assert '"Max Muncy": "MIL @ LAD"' in text, "Max Muncy game pin not injected"
    text = re.sub(
        r"PROBABLE_OVERRIDES = \{.*?\n\}|PROBABLE_OVERRIDES: dict\[str, dict\] = \{\}",
        "PROBABLE_OVERRIDES: dict[str, dict] = {}",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"PITCHER_HAND = \{.*?\n\}", PITCHER_HAND, text, count=1, flags=re.S)
    (ROOT / "build-0815-from-csv.py").write_text(text, encoding="utf-8")
    print("wrote build-0815-from-csv.py")

    # ---- patch script ----
    p = swap_dates((ROOT / "patch-0814-preview.py").read_text(encoding="utf-8"))
    before = len(p)
    p = re.sub(
        r"\n# 8/15 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "straight judgment lock not stripped"
    before = len(p)
    p = re.sub(
        r"\n# 8/15 Goblin judgment:.*?    fav3 = _fav3_lock\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "goblin judgment lock not stripped"
    # The date swap slides every hand-maintained manifest date forward, dropping
    # the day that just became an archive. Re-add it to the ordered list.
    p = p.replace(
        '    for date in [\n        "2026-08-14",\n        "2026-08-13",\n        "2026-08-11",',
        '    for date in [\n        "2026-08-14",\n        "2026-08-13",\n        "2026-08-12",\n        "2026-08-11",',
        1,
    )
    assert '"2026-08-12",' in p, "2026-08-12 dropped from the archive manifest list"
    assert 'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-14.html"' in p, (
        "archive target should point at the slate being replaced"
    )
    (ROOT / "patch-0815-preview.py").write_text(p, encoding="utf-8")
    print("wrote patch-0815-preview.py")

    # ---- summary verifier ----
    (ROOT / "verify-summary-0815.py").write_text(
        swap_dates((ROOT / "verify-summary-0814.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0815.py")

    # ---- final audit ----
    a = swap_dates((ROOT / "_audit_0814_final.py").read_text(encoding="utf-8"))
    # August 15 2026 is a Saturday, so the swapped-forward pair of "wrong"
    # weekdays now contains the correct one. Re-point it.
    a = a.replace(
        'if "Thursday, August 15" in html or "Saturday, August 15" in html:',
        'if "Friday, August 15" in html or "Sunday, August 15" in html:',
        1,
    )
    a = a.replace(
        'fail("wrong weekday on August 15 (must be Friday)")',
        'fail("wrong weekday on August 15 (must be Saturday)")',
        1,
    )
    bums = ", ".join(f'"{b}"' for b in EXPECTED_BUMS)
    a = re.sub(r"expected_bum = \{[^}]*\}", f"expected_bum = {{{bums}}}", a, count=1)
    lhp_block = "    for base in (\n" + "".join(f'        "{n}",\n' for n in AUDIT_LHP) + "    ):"
    a = re.sub(r"    for base in \(\n(?:        \"[^\"]+\",\n)+    \):", lhp_block, a, count=1)
    propcount = len(re.findall(r'^\s+"', RAW_PROPS, flags=re.M))
    a = re.sub(r"PROPCOUNT = \d+", f"PROPCOUNT = {propcount}", a, count=1)
    a = re.sub(r"GAMECOUNT = \d+", f"GAMECOUNT = {GAMECOUNT}", a, count=1)
    (ROOT / "_audit_0815_final.py").write_text(a, encoding="utf-8")
    print(f"wrote _audit_0815_final.py (PROPCOUNT={propcount}, GAMECOUNT={GAMECOUNT})")

    # ---- deep audit ----
    d = swap_dates((ROOT / "_deep_audit_0814.py").read_text(encoding="utf-8"))
    # The variable name carries underscores (STALE_8_13), which the date swaps
    # deliberately do not touch — rename it and its use site explicitly.
    stale_block = "STALE_8_14 = [\n" + "".join(f'    "{n}",\n' for n in STALE_PITCHERS) + "]"
    d, n_sub = re.subn(r"STALE_8_1\d = \[.*?\n\]", stale_block, d, count=1, flags=re.S)
    assert n_sub == 1, "stale list block not found"
    d = re.sub(r"for name in STALE_8_1\d:", "for name in STALE_8_14:", d, count=1)
    assert '"Sandy Alcantara"' in d and "STALE_8_13" not in d, "stale list not replaced"
    # The swapped-forward "wrong weekday" tuple now contains Saturday, which is
    # the correct weekday for August 15 — swap that entry for Friday. Matched by
    # regex because the literal spans two lines at an indentation the template owns.
    d, n_wd = re.subn(
        r'("Thursday, August 15", )"Saturday, August 15"',
        r'\1"Friday, August 15"',
        d,
        count=1,
    )
    assert n_wd == 1, "deep audit wrong-weekday tuple not re-pointed"
    assert '"Saturday, August 15, 2026" not in html' in d, (
        "deep audit lost the hero weekday assertion"
    )
    d = re.sub(r"PROPCOUNT = \d+", f"PROPCOUNT = {propcount}", d, count=1)
    d = re.sub(r"GAMECOUNT = \d+", f"GAMECOUNT = {GAMECOUNT}", d, count=1)
    (ROOT / "_deep_audit_0815.py").write_text(d, encoding="utf-8")
    print("wrote _deep_audit_0815.py")

    # ---- zone backfill ----
    z = swap_dates((ROOT / "_backfill_zones_0814.py").read_text(encoding="utf-8"))
    z = re.sub(
        r"LHP = \{.*?\n\}",
        "LHP = {\n" + "".join(f'    "{n}",\n' for n in LHP_KEYS) + "}",
        z,
        count=1,
        flags=re.S,
    )
    (ROOT / "_backfill_zones_0815.py").write_text(z, encoding="utf-8")
    print("wrote _backfill_zones_0815.py")

    # ---- ranking helpers ----
    for src, dst in (
        ("_best_0814.py", "_best_0815.py"),
        ("_pick_review_0814.py", "_pick_review_0815.py"),
    ):
        if (ROOT / src).is_file():
            (ROOT / dst).write_text(
                swap_dates((ROOT / src).read_text(encoding="utf-8")), encoding="utf-8"
            )
            print(f"wrote {dst}")


if __name__ == "__main__":
    main()
