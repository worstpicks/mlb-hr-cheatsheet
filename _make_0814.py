#!/usr/bin/env python3
"""Scaffold the 8/14 build / patch / audit / backfill scripts from the 8/13 set.

Run before the slate build. Note that this regenerates patch-0814-preview.py from
the 8/13 template, so run it BEFORE locking straights and Goblin legs — re-running
it afterwards overwrites those locks.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Gage Jump is deliberately absent from the prop list: he is the ATH starting
# pitcher, not a bat. He appeared in the request between the other ATH hitters.
RAW_PROPS = """RAW_PROPS = [
    "Tyler Stephenson💎",
    "Matt McLain",
    "Eugenio Suarez",
    "Sal Stewart",
    "Griffin Conine⭐",
    "Joe Mack",
    "Owen Caissie",
    "Ronny Simon",
    "Bryan Reynolds💎",
    "Esmerlyn Valdez",
    "Jarren Duran",
    "Wilyer Abreu",
    "Eduardo Valencia",
    "Gleyber Torres",
    "Spencer Torkelson",
    "Munetaka Murakami⭐",
    "Drew Romo",
    "Randal Grichuk",
    "Victor Mesa Jr.💎",
    "Yandy Diaz",
    "Jonathan Aranda💎",
    "Junior Caminero",
    "Pete Alonso⭐",
    "Coby Mayo⭐",
    "Francisco Alvarez💎",
    "Carson Benge",
    "A.J. Ewing",
    "Luis Robert⭐",
    "Daylen Lile⭐",
    "Abimelec Ortiz⭐",
    "Jose Tena",
    "Angel Genao💎",
    "Nathaniel Lowe",
    "Patrick Bailey",
    "Chase DeLauter",
    "Jackson Merrill⭐",
    "Manny Machado",
    "Xander Bogaerts",
    "Fernando Tatis Jr.",
    "Jesus Sanchez",
    "Kazuma Okamoto",
    "George Springer",
    "Ben Rice",
    "Spencer Jones",
    "Jazz Chisholm Jr.",
    "Luis Garcia Jr.",
    "Matt Olson",
    "Drake Baldwin💎",
    "Ronald Acuna Jr.",
    "Michael Harris II",
    "Daulton Varsho💎",
    "Taylor Trammell",
    "Yordan Alvarez⭐",
    "Nelson Velazquez",
    "Cam Smith",
    "Julio Rodriguez",
    "Dominic Canzone💎",
    "Josh Naylor💎",
    "Mike Trout⭐",
    "Moises Ballesteros",
    "Jac Caglianone⭐",
    "Salvador Perez",
    "Bobby Witt Jr.",
    "Isaac Collins",
    "Lawrence Butler⭐",
    "Tyler Soderstrom💎",
    "Henry Bolte",
    "Zack Gelof",
    "Justin Foscue",
    "Elias Diaz",
    "Teoscar Hernandez💎",
    "Mookie Betts",
    "Shohei Ohtani💎",
    "Andy Pages",
    "Jake Bauers💎",
    "Brice Turang",
    "William Contreras💎",
    "Joey Ortiz",
    "Rafael Devers",
    "Bryce Eldridge",
    "Victor Bericoto",
    "Willy Adames",
    "Zac Veen",
    "Willi Castro",
    "Hunter Goodman⭐",
]"""

ALIASES = """ALIASES = {
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Ronald Acuna": "Ronald Acuna Jr.",
    # The request wrote "Torkleson"; PropFinder exports "Torkelson".
    "Spencer Torkleson": "Spencer Torkelson",
    "Spencer Torkelson": "Spencer Torkelson",
    "Mookie Betts": "Mookie Betts",
    "A.J. Ewing": "A.J. Ewing",
    "AJ Ewing": "A.J. Ewing",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Victor Mesa": "Victor Mesa Jr.",
    "Moises Ballesteros": "Moises Ballesteros",
    "Moisés Ballesteros": "Moises Ballesteros",
    "Munetaka Murakami": "Munetaka Murakami",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "William Contreras": "William Contreras",
    "Willson Contreras": "Willson Contreras",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Bobby Witt Jr.": "Bobby Witt Jr.",
    "Michael Harris II": "Michael Harris II",
    "Nathaniel Lowe": "Nathaniel Lowe",
    "Brandon Lowe": "Brandon Lowe",
    "Chase DeLauter": "Chase DeLauter",
    "Abimelec Ortiz": "Abimelec Ortiz",
    "Jonathan Aranda": "Jonathan Aranda",
    "Francisco Alvarez": "Francisco Alvarez",
    "Yordan Alvarez": "Yordan Alvarez",
    "Teoscar Hernandez": "Teoscar Hernandez",
    "Shohei Ohtani": "Shohei Ohtani",
    "Tyler Soderstrom": "Tyler Soderstrom",
    "Jac Caglianone": "Jac Caglianone",
    "Hunter Goodman": "Hunter Goodman",
    "Esmerlyn Valdez": "Esmerlyn Valdez",
    "Victor Bericoto": "Victor Bericoto",
    "Bryce Eldridge": "Bryce Eldridge",
    "Randal Grichuk": "Randal Grichuk",
    "Nelson Velazquez": "Nelson Velazquez",
}"""

# Sean Newcomb and Steven Matz are PropFinder's listed starters for CWS and TB.
# The confirmed lineups name Jose Urquidy (R) and Jesse Scholtens (R) instead;
# both are carried here so the hand is right whichever export we end up building.
PITCHER_HAND = """PITCHER_HAND = {
    # 8/14 LHP
    "Jake Bennett": "L",
    "Andrew Alvarez": "L",
    "Chris Sale": "L",
    "Gage Jump": "L",
    "Robert Gasser": "L",
    "Kyle Freeland": "L",
    "Sean Newcomb": "L",
    "Steven Matz": "L",
    # 8/14 RHP
    "Sandy Alcantara": "R",
    "Chase Burns": "R",
    "Jackson Jobe": "R",
    "Jose Urquidy": "R",
    "Bubba Chandler": "R",
    "Michael King": "R",
    "Gavin Williams": "R",
    "Robert Stock": "R",
    "Chris Bassitt": "R",
    "Jesse Scholtens": "R",
    "Gerrit Cole": "R",
    "Shane Bieber": "R",
    "Brandon Pfaadt": "R",
    "George Kirby": "R",
    "Peter Lambert": "R",
    "Seth Lugo": "R",
    "Grayson Rodriguez": "R",
    "Kumar Rocker": "R",
    "Yoshinobu Yamamoto": "R",
    "Landen Roupp": "R",
}"""

# Surname fragments used to stamp `throws` on backfilled zone rows.
LHP_KEYS = ["Bennett", "Alvarez", "Sale", "Jump", "Gasser", "Freeland", "Newcomb", "Matz"]

GAMECOUNT = 13
EXPECTED_BUMS = ["Grayson Rodriguez", "Gavin Williams", "Kumar Rocker"]
# LHP the audit spot-checks for a correct "(L" hand in the game titles.
AUDIT_LHP = ["Jake Bennett", "Andrew Alvarez", "Chris Sale", "Robert Gasser", "Kyle Freeland"]


# Longest-match-first so "2026-08-13" is tokenized before the bare "08-13" rule
# can chew into the ISO string it just produced.
_DATE_SWAPS: list[tuple[str, str]] = [
    ("2026-08-13", "2026-08-14"),
    ("2026-08-12", "2026-08-13"),
    ("Thursday, August 13, 2026", "Friday, August 14, 2026"),
    ("Thursday, August 13", "Friday, August 14"),
    ("August 13, 2026", "August 14, 2026"),
    ("August 13", "August 14"),
    ("Wednesday, August 12, 2026", "Thursday, August 13, 2026"),
    ("Wednesday, August 12", "Thursday, August 13"),
    ("August 12, 2026", "August 13, 2026"),
    ("August 12", "August 13"),
    ("08-13", "08-14"),
    ("08-12", "08-13"),
    ("0813", "0814"),
    ("0812", "0813"),
    ("8/13", "8/14"),
    ("8/12", "8/13"),
]


def swap_dates(text: str) -> str:
    for idx, (needle, _) in enumerate(_DATE_SWAPS):
        text = text.replace(needle, f"\x00{idx}\x00")
    for idx, (_, sub) in enumerate(_DATE_SWAPS):
        text = text.replace(f"\x00{idx}\x00", sub)
    return text


def main() -> None:
    # ---- build script ----
    text = swap_dates((ROOT / "build-0813-from-csv.py").read_text(encoding="utf-8"))
    text = re.sub(r"RAW_PROPS = \[.*?\n\]", RAW_PROPS, text, count=1, flags=re.S)
    text = re.sub(r"ALIASES = \{.*?\n\}", ALIASES, text, count=1, flags=re.S)
    text = re.sub(
        r"PROBABLE_OVERRIDES = \{.*?\n\}|PROBABLE_OVERRIDES: dict\[str, dict\] = \{\}",
        "PROBABLE_OVERRIDES: dict[str, dict] = {}",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"PITCHER_HAND = \{.*?\n\}", PITCHER_HAND, text, count=1, flags=re.S)
    (ROOT / "build-0814-from-csv.py").write_text(text, encoding="utf-8")
    print("wrote build-0814-from-csv.py")

    # ---- patch script ----
    p = swap_dates((ROOT / "patch-0813-preview.py").read_text(encoding="utf-8"))
    before = len(p)
    p = re.sub(
        r"\n# 8/14 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "straight judgment lock not stripped"
    before = len(p)
    p = re.sub(
        r"\n# 8/14 Goblin judgment:.*?    fav3 = _fav3_lock\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "goblin judgment lock not stripped"
    # The date swap slides every hand-maintained manifest date forward, dropping the
    # day that just became an archive. Re-add it to the ordered list.
    p = p.replace(
        '    for date in [\n        "2026-08-13",\n        "2026-08-11",',
        '    for date in [\n        "2026-08-13",\n        "2026-08-12",\n        "2026-08-11",',
        1,
    )
    assert 'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-13.html"' in p, (
        "archive target should point at the slate being replaced"
    )
    (ROOT / "patch-0814-preview.py").write_text(p, encoding="utf-8")
    print("wrote patch-0814-preview.py")

    # ---- summary verifier ----
    (ROOT / "verify-summary-0814.py").write_text(
        swap_dates((ROOT / "verify-summary-0813.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0814.py")

    # ---- final audit ----
    a = swap_dates((ROOT / "_audit_0813_final.py").read_text(encoding="utf-8"))
    a = a.replace(
        'if "Tuesday, August 14" in html or "Wednesday, August 14" in html:',
        'if "Thursday, August 14" in html or "Saturday, August 14" in html:',
        1,
    )
    a = a.replace(
        'fail("wrong weekday on August 14 (must be Thursday)")',
        'fail("wrong weekday on August 14 (must be Friday)")',
        1,
    )
    bums = ", ".join(f'"{b}"' for b in EXPECTED_BUMS)
    a = re.sub(r"expected_bum = \{[^}]*\}", f"expected_bum = {{{bums}}}", a, count=1)
    lhp_block = "    for base in (\n" + "".join(f'        "{n}",\n' for n in AUDIT_LHP) + "    ):"
    a = re.sub(
        r"    for base in \(\n(?:        \"[^\"]+\",\n)+    \):",
        lhp_block,
        a,
        count=1,
    )
    # Derive from RAW_PROPS rather than restating it: a hand-edited count silently
    # stops checking the props that were added after it was last touched.
    propcount = len(re.findall(r'^\s+"', RAW_PROPS, flags=re.M))
    a = re.sub(r"PROPCOUNT = \d+", f"PROPCOUNT = {propcount}", a, count=1)
    a = re.sub(r"GAMECOUNT = \d+", f"GAMECOUNT = {GAMECOUNT}", a, count=1)
    (ROOT / "_audit_0814_final.py").write_text(a, encoding="utf-8")
    print(f"wrote _audit_0814_final.py (PROPCOUNT={propcount}, GAMECOUNT={GAMECOUNT})")

    # ---- zone backfill ----
    z = swap_dates((ROOT / "_backfill_zones_0813.py").read_text(encoding="utf-8"))
    z = re.sub(
        r"LHP = \{.*?\n\}",
        "LHP = {\n" + "".join(f'    "{n}",\n' for n in LHP_KEYS) + "}",
        z,
        count=1,
        flags=re.S,
    )
    (ROOT / "_backfill_zones_0814.py").write_text(z, encoding="utf-8")
    print("wrote _backfill_zones_0814.py")

    # ---- ranking helpers ----
    for src, dst in (("_best_0813.py", "_best_0814.py"), ("_pick_review_0813.py", "_pick_review_0814.py")):
        if (ROOT / src).is_file():
            (ROOT / dst).write_text(
                swap_dates((ROOT / src).read_text(encoding="utf-8")), encoding="utf-8"
            )
            print(f"wrote {dst}")


if __name__ == "__main__":
    main()
