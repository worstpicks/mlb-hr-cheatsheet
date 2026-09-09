#!/usr/bin/env python3
"""Scaffold 2026-08-12 build/patch/verify from 8/11 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Kody Clemens⭐",
    "Pete Alonso⭐",
    "Gunnar Henderson⭐",
    "Colton Cowser",
    "Jimmy Crooks",
    "Jordan Walker💎",
    "Ivan Herrera",
    "Kyle Schwarber⭐",
    "Bryce Harper",
    "Lawrence Butler💎",
    "Tyler Soderstrom",
    "Zack Gelof",
    "Yandy Diaz",
    "Jonny DeLuca💎",
    "Junior Caminero",
    "Victor Mesa Jr.💎",
    "Corbin Carroll",
    "Lars Nootbaar",
    "Hunter Goodman",
    "Willi Castro",
    "Mickey Moniak⭐",
    "Willy Adames⭐",
    "Rafael Devers",
    "Yordan Alvarez⭐",
    "Nelson Velazquez💎",
    "Taylor Trammell",
    "Jackson Merrill⭐",
    "Ty France💎",
    "Manny Machado💎",
    "Jake Bauers",
    "Jackson Chourio",
    "William Contreras",
    "Andrew Vaughn",
    "Griffin Conine⭐",
    "Owen Caissie⭐",
    "Brandon Lowe⭐",
    "Esmerlyn Valdez",
    "James Outman💎",
    "Eduardo Valencia",
    "Jo Adell⭐",
    "Pete Crow-Armstrong",
    "Ian Happ",
    "Dylan Crews",
    "Daylen Lile",
    "Luis Garcia Jr.⭐",
    "Spencer Jones",
    "Ben Rice",
    "Josh Naylor",
    "Cal Raleigh⭐",
    "Julio Rodriguez",
    "Randy Arozarena💎",
    "Kazuma Okamoto⭐",
    "Vladimir Guerrero Jr.",
    "Jarren Duran⭐",
    "Wilyer Abreu",
    "Ceddanne Rafaela",
    "Matt Olson⭐",
    "Austin Riley⭐",
    "Ronald Acuna Jr.",
    "Francisco Alvarez",
    "Francisco Lindor",
    "Brett Baty💎",
    "Munetaka Murakami⭐",
    "Miguel Vargas",
    "Elly De La Cruz💎",
    "Tyler Stephenson",
    "Eugenio Suarez💎",
    "Teoscar Hernandez⭐",
    "Freddie Freeman",
    "Carter Jensen⭐",
    "John Rave",
    "Michael Massey",
    "Jac Caglianone⭐",
    "Moises Ballesteros⭐",
    "Mike Trout",
    "Nolan Schanuel",
    "Jarred Kelenic⭐",
    "Corey Seager",
    "Elias Diaz",
]"""

ALIASES = """ALIASES = {
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Pete Crow": "Pete Crow-Armstrong",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Johnny DeLuca": "Jonny DeLuca",
    "Jonny DeLuca": "Jonny DeLuca",
    "Edouardo Valencia": "Eduardo Valencia",
    "Eduardo Valencia": "Eduardo Valencia",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Victor Mesa": "Victor Mesa Jr.",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Elly De La Cruz": "Elly De La Cruz",
    "Moises Ballesteros": "Moises Ballesteros",
    "Munetaka Murakami": "Munetaka Murakami",
    "Jac Caglianone": "Jac Caglianone",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "William Contreras": "William Contreras",
    "Willson Contreras": "Willson Contreras",
    "Zac Thornton": "Zach Thornton",
    "Zach Thornton": "Zach Thornton",
    "C. Mlodzinski": "Carmen Mlodzinski",
    "Carmen Mlodzinski": "Carmen Mlodzinski",
    "Daniel Lynch IV": "Daniel Lynch IV",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/12 LHP
    "Foster Griffin": "L",
    "Framber Valdez": "L",
    "David Peterson": "L",
    "Jackson Kent": "L",
    "Ranger Suarez": "L",
    "Zach Thornton": "L",
    "Robbie Ray": "L",
    "Eric Lauer": "L",
    "Daniel Lynch IV": "L",
    "Bryan King": "L",
    # 8/12 RHP
    "Shane Baz": "R",
    "Zebby Matthews": "R",
    "Jose Soriano": "R",
    "Luis Castillo": "R",
    "Rhett Lowder": "R",
    "Merrill Kelly": "R",
    "Ryan Feltner": "R",
    "Adrian Houser": "R",
    "Dustin May": "R",
    "Tyler Mahle": "R",
    "Kyle Leahy": "R",
    "Zack Wheeler": "R",
    "Carmen Mlodzinski": "R",
    "Janson Junk": "R",
    "Bryce Miller": "R",
    "Will Warren": "R",
    "Drew Rasmussen": "R",
    "Jack Perkins": "R",
    "Cal Quantrill": "R",
    "George Klassen": "R",
}"""


# Longest-match-first so "2026-08-11" is tokenized before the bare "08-11" rule
# can chew into the ISO string it just produced.
_DATE_SWAPS: list[tuple[str, str]] = [
    ("2026-08-11", "2026-08-12"),
    ("2026-08-10", "2026-08-11"),
    ("Tuesday, August 11, 2026", "Wednesday, August 12, 2026"),
    ("Tuesday, August 11", "Wednesday, August 12"),
    ("August 11, 2026", "August 12, 2026"),
    ("August 11", "August 12"),
    ("Monday, August 10, 2026", "Tuesday, August 11, 2026"),
    ("Monday, August 10", "Tuesday, August 11"),
    ("August 10, 2026", "August 11, 2026"),
    ("August 10", "August 11"),
    ("08-11", "08-12"),
    ("08-10", "08-11"),
    ("0811", "0812"),
    ("0810", "0811"),
    ("8/11", "8/12"),
    ("8/10", "8/11"),
]


def swap_dates(text: str) -> str:
    for idx, (needle, _) in enumerate(_DATE_SWAPS):
        text = text.replace(needle, f"\x00{idx}\x00")
    for idx, (_, sub) in enumerate(_DATE_SWAPS):
        text = text.replace(f"\x00{idx}\x00", sub)
    return text


def main() -> None:
    # ---- build script ----
    text = swap_dates((ROOT / "build-0811-from-csv.py").read_text(encoding="utf-8"))
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
    (ROOT / "build-0812-from-csv.py").write_text(text, encoding="utf-8")
    print("wrote build-0812-from-csv.py")

    # ---- patch script ----
    p = swap_dates((ROOT / "patch-0811-preview.py").read_text(encoding="utf-8"))
    before = len(p)
    p = re.sub(
        r"\n# 8/12 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "straight judgment lock not stripped"
    before = len(p)
    p = re.sub(
        r"\n# 8/12 Goblin judgment:.*?    fav3 = _fav3_lock\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "goblin judgment lock not stripped"
    # Manifest ordered list lost 2026-08-10 to the date swap; reinsert it.
    p = p.replace(
        '    for date in [\n        "2026-08-11",\n        "2026-08-09",',
        '    for date in [\n        "2026-08-11",\n        "2026-08-10",\n        "2026-08-09",',
        1,
    )
    # Stale fallback label from an older slate.
    p = p.replace(
        '        elif date == "2026-08-12":\n'
        "            ordered.append(\n"
        "                {\n"
        '                    "date": "2026-08-12",\n'
        '                    "label": "August 2, 2026",\n'
        '                    "href": "archive/2026-08-12.html",\n'
        "                }\n"
        "            )\n",
        '        elif date == "2026-08-11":\n'
        "            ordered.append(\n"
        "                {\n"
        '                    "date": "2026-08-11",\n'
        '                    "label": "August 11, 2026",\n'
        '                    "href": "archive/2026-08-11.html",\n'
        "                }\n"
        "            )\n",
        1,
    )
    (ROOT / "patch-0812-preview.py").write_text(p, encoding="utf-8")
    print("wrote patch-0812-preview.py")

    # ---- summary verifier ----
    (ROOT / "verify-summary-0812.py").write_text(
        swap_dates((ROOT / "verify-summary-0811.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0812.py")

    # ---- final audit ----
    a = swap_dates((ROOT / "_audit_0811_final.py").read_text(encoding="utf-8"))
    a = a.replace(
        'if "Monday, August 12" in html or "Wednesday, August 12" in html:',
        'if "Tuesday, August 12" in html or "Thursday, August 12" in html:',
        1,
    )
    a = a.replace(
        'fail("wrong weekday on August 12 (must be Tuesday)")',
        'fail("wrong weekday on August 12 (must be Wednesday)")',
        1,
    )
    a = re.sub(
        r"expected_bum = \{[^}]*\}",
        'expected_bum = {"Ryan Feltner", "Jack Perkins", "Luis Castillo"}',
        a,
        count=1,
    )
    a = re.sub(
        r"    for base in \(\n(?:        \"[^\"]+\",\n)+    \):",
        (
            "    for base in (\n"
            '        "Foster Griffin",\n'
            '        "Framber Valdez",\n'
            '        "David Peterson",\n'
            '        "Ranger Suarez",\n'
            '        "Zach Thornton",\n'
            '        "Robbie Ray",\n'
            '        "Eric Lauer",\n'
            '        "Daniel Lynch IV",\n'
            '        "Bryan King",\n'
            "    ):"
        ),
        a,
        count=1,
    )
    a = re.sub(r"PROPCOUNT = \d+", "PROPCOUNT = 79", a, count=1)
    (ROOT / "_audit_0812_final.py").write_text(a, encoding="utf-8")
    print("wrote _audit_0812_final.py")

    # ---- zone backfill ----
    z = swap_dates((ROOT / "_backfill_zones_0811.py").read_text(encoding="utf-8"))
    z = re.sub(
        r"LHP = \{.*?\n\}",
        (
            "LHP = {\n"
            '    "Griffin",\n'
            '    "Valdez",\n'
            '    "Peterson",\n'
            '    "Kent",\n'
            '    "Suarez",\n'
            '    "Thornton",\n'
            '    "Ray",\n'
            '    "Lauer",\n'
            '    "Lynch",\n'
            '    "King",\n'
            "}"
        ),
        z,
        count=1,
        flags=re.S,
    )
    (ROOT / "_backfill_zones_0812.py").write_text(z, encoding="utf-8")
    print("wrote _backfill_zones_0812.py")

    # ---- ranking helper ----
    (ROOT / "_best_0812.py").write_text(
        swap_dates((ROOT / "_best_0811.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote _best_0812.py")


if __name__ == "__main__":
    main()
