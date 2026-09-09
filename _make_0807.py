#!/usr/bin/env python3
"""Scaffold 2026-08-07 build/patch/verify from 8/6 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Esmerlyn Valdez⭐",
    "Brett Baty💎",
    "Francisco Lindor",
    "Bryce Harper⭐",
    "Derek Hill",
    "Luis Arraez",
    "Jesus Sanchez💎",
    "Brandon Valenzuela",
    "Brady House",
    "JJ Bleday",
    "Eugenio Suarez",
    "Tyler Stephenson💎",
    "Elly De La Cruz",
    "Sal Stewart",
    "Austin Wells",
    "Jose Caballero",
    "George Lombard Jr.",
    "Jazz Chisholm Jr.",
    "Michael Harris II",
    "Austin Riley",
    "Ozzie Albies",
    "Owen Caissie⭐",
    "Jakob Marsee",
    "Griffin Conine💎",
    "Kyle Stowers",
    "Josh Lowe",
    "Wilyer Abreu",
    "Willson Contreras",
    "Brian Serven",
    "Tyler Soderstrom",
    "Jonah Heim",
    "Jake Bauers",
    "Jackson Chourio",
    "Ryan Kreidler",
    "Miguel Vargas",
    "Rhys Hoskins⭐",
    "Jo Adell",
    "Bobby Witt Jr.💎",
    "Tyrone Taylor",
    "Pete Crow-Armstrong⭐",
    "Corey Seager",
    "Alejandro Osuna",
    "Wyatt Langford",
    "Pete Alonso💎",
    "Christian Encarnacion-Strand",
    "Alec Burleson⭐",
    "Jimmy Crooks💎",
    "Nelson Velazquez",
    "Ivan Herrera",
    "Mickey Moniak💎",
    "Willi Castro",
    "Gage Workman",
    "Yordan Alvarez⭐",
    "Nick Allen",
    "Corbin Carroll",
    "Tim Tawa",
    "Max Muncy",
    "Shohei Ohtani",
    "Freddie Freeman",
    "Cal Raleigh",
    "Junior Caminero",
    "Victor Mesa Jr.",
    "Rafael Devers",
    "Dillon Dingler",
    "Spencer Torkelson",
    "Gleyber Torres",
    "Riley Greene",
]"""

ALIASES = """ALIASES = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Bobby Witt Jr.": "Bobby Witt Jr.",
    "Bobby Witt jr.": "Bobby Witt Jr.",
    "Bobby Witt": "Bobby Witt Jr.",
    "Christian Encarnacion Strand": "Christian Encarnacion-Strand",
    "Christian Encarnacion-Strand": "Christian Encarnacion-Strand",
    "C. Encarnacion-Strand": "Christian Encarnacion-Strand",
    "George Lombard Jr.": "George Lombard Jr.",
    "George Lombard": "George Lombard Jr.",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Jazz Chisholm": "Jazz Chisholm Jr.",
    "Michael Harris II": "Michael Harris II",
    "Michael Harris": "Michael Harris II",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Victor Mesa": "Victor Mesa Jr.",
    "Elly De La Cruz": "Elly De La Cruz",
    "Willson Contreras": "Willson Contreras",
    "William Contreras": "William Contreras",
    "Eugenio Suarez": "Eugenio Suarez",
    "Eugenio Suárez": "Eugenio Suarez",
    "Jesus Sanchez": "Jesus Sanchez",
    "Brett Baty": "Brett Baty",
    "Esmerlyn Valdez": "Esmerlyn Valdez",
    "Tyler Stephenson": "Tyler Stephenson",
    "Griffin Conine": "Griffin Conine",
    "Pete Alonso": "Pete Alonso",
    "Jimmy Crooks": "Jimmy Crooks",
    "Mickey Moniak": "Mickey Moniak",
    "Owen Caissie": "Owen Caissie",
    "Rhys Hoskins": "Rhys Hoskins",
    "Alec Burleson": "Alec Burleson",
    "Yordan Alvarez": "Yordan Alvarez",
    "Bryce Harper": "Bryce Harper",
    "Alejandro Osuna": "Alejandro Osuna",
    "Gage Workman": "Gage Workman",
    "Nick Allen": "Nick Allen",
    "Ryan Kreidler": "Ryan Kreidler",
    "Brian Serven": "Brian Serven",
    "Jose Caballero": "Jose Caballero",
    "Brandon Valenzuela": "Brandon Valenzuela",
    "Brady House": "Brady House",
    "Jakob Marsee": "Jakob Marsee",
    "Ivan Herrera": "Ivan Herrera",
    "Nelson Velazquez": "Nelson Velazquez",
    "Willi Castro": "Willi Castro",
    "Tyrone Taylor": "Tyrone Taylor",
    "Tim Tawa": "Tim Tawa",
    "Dillon Dingler": "Dillon Dingler",
    "Zach Thornton": "Zach Thornton",
    "Zac Thornton": "Zach Thornton",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/7 LHP
    "Zach Thornton": "L",
    "Zac Thornton": "L",
    "Max Fried": "L",
    "Payton Tolle": "L",
    "Parker Messick": "L",
    "Noah Schultz": "L",
    "Shane Drohan": "L",
    "Robbie Ray": "L",
    # 8/7 RHP
    "Jose Soriano": "R",
    "Zack Wheeler": "R",
    "Carmen Mlodzinski": "R",
    "Chase Petty": "R",
    "Cade Cavalli": "R",
    "Tyler Mahle": "R",
    "Jack Perkins": "R",
    "George Klassen": "R",
    "Tyler Phillips": "R",
    "Zebby Matthews": "R",
    "Kevin Gausman": "R",
    "Easton McGee": "R",
    "Shane Baz": "R",
    "Nathan Eovaldi": "R",
    "Ryan Feltner": "R",
    "Kyle Leahy": "R",
    "Ronel Blanco": "R",
    "Roki Sasaki": "R",
    "Merrill Kelly": "R",
    "Drew Rasmussen": "R",
    "Logan Gilbert": "R",
    "Keider Montero": "R",
    "Adrian Houser": "R",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-06", "2026-08-07")
    text = text.replace("2026-08-05", "2026-08-06")
    text = text.replace("08-06", "08-07")
    text = text.replace("08-05", "08-06")
    text = text.replace("0806", "0807")
    text = text.replace("0805", "0806")
    text = text.replace("Thursday, August 6, 2026", "Friday, August 7, 2026")
    text = text.replace("Thursday, August 6", "Friday, August 7")
    text = text.replace("August 6, 2026", "August 7, 2026")
    text = text.replace("August 6", "August 7")
    # undo bad weekday swaps from generic August replace
    text = text.replace("Wednesday, August 7", "Friday, August 7")
    text = text.replace("Thursday, August 7", "Friday, August 7")
    return text


def main() -> None:
    src_build = ROOT / "build-0806-from-csv.py"
    dst_build = ROOT / "build-0807-from-csv.py"
    text = swap_dates(src_build.read_text(encoding="utf-8"))
    text = re.sub(r"RAW_PROPS = \[.*?\]", RAW_PROPS, text, count=1, flags=re.S)
    text = re.sub(r"ALIASES = \{.*?\}", ALIASES, text, count=1, flags=re.S)
    text = re.sub(
        r"PROBABLE_OVERRIDES = \{.*?\}",
        "PROBABLE_OVERRIDES = {}",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"PITCHER_HAND = \{.*?\}", PITCHER_HAND, text, count=1, flags=re.S)
    dst_build.write_text(text, encoding="utf-8")
    print("wrote", dst_build.name)

    src_patch = ROOT / "patch-0806-preview.py"
    dst_patch = ROOT / "patch-0807-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    # Drop 8/6 judgment locks
    ptext = re.sub(
        r"\n# 8/6 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/6 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-06.html"',
        ptext,
        count=1,
    )
    ptext = ptext.replace(
        "<p>Friday, August 7, 2026 — Worst Pickz HR cheat sheet",
        "<p>Friday, August 7, 2026 — Worst Pickz HR cheat sheet",
    )
    ptext = re.sub(
        r'if "2026-08-0[67]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[67]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-06" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-06"] = {\n'
            '            "date": "2026-08-06",\n'
            '            "label": "August 6, 2026",\n'
            '            "href": "archive/2026-08-06.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    # Fix ordered archive dates (current is separate; list starts at prior day)
    ptext = re.sub(
        r'for date in \[\n        "2026-08-07",\n        "2026-08-06",\n        "2026-08-04",',
        'for date in [\n        "2026-08-06",\n        "2026-08-05",\n        "2026-08-04",',
        ptext,
        count=1,
    )
    if '"2026-08-06",\n        "2026-08-05",\n        "2026-08-04"' not in ptext:
        ptext = ptext.replace(
            '    for date in [\n        "2026-08-06",\n        "2026-08-04",',
            '    for date in [\n        "2026-08-06",\n        "2026-08-05",\n        "2026-08-04",',
            1,
        )
        ptext = ptext.replace(
            '    for date in [\n        "2026-08-07",\n        "2026-08-06",\n        "2026-08-05",',
            '    for date in [\n        "2026-08-06",\n        "2026-08-05",\n        "2026-08-04",',
            1,
        )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    (ROOT / "verify-summary-0807.py").write_text(
        swap_dates((ROOT / "verify-summary-0806.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0807.py")

    atext = swap_dates((ROOT / "_audit_0806_final.py").read_text(encoding="utf-8"))
    atext = atext.replace("Thursday, August 7, 2026", "Friday, August 7, 2026")
    atext = atext.replace(
        'if "Wednesday, August 5, 2026 — Worst" in html:',
        'if "Thursday, August 6, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Tuesday, August 7" in html or "Wednesday, August 7" in html:',
        'if "Thursday, August 7" in html or "Wednesday, August 7" in html:',
    )
    atext = atext.replace(
        'fail("wrong weekday on August 7 (must be Thursday)")',
        'fail("wrong weekday on August 7 (must be Friday)")',
    )
    atext = atext.replace(
        'if "August 5, 2026 — current slate" in html:\n        fail("8/5 still labeled current")',
        'if "August 6, 2026 — current slate" in html:\n        fail("8/6 still labeled current")',
    )
    atext = atext.replace("!= 69", "!= 67")
    atext = atext.replace("expected 69 props", "expected 67 props")
    atext = atext.replace("!= 11", "!= 15")
    atext = atext.replace("expected 11 games", "expected 15 games")
    atext = atext.replace("expected 11 gameMeta", "expected 15 gameMeta")
    atext = atext.replace(
        'expected_bum = {"Kohl Drake", "Miles Mikolas", "Ryan Johnson"}',
        'expected_bum = {"PLACEHOLDER"}',
    )
    atext = atext.replace(
        """    for must_l in (
        "Andrew Abbott (L",
        "Foster Griffin (L",
        "David Peterson (L",
        "Framber Valdez (L",
        "Cristopher Sanchez (L",
        "Ranger Suarez (L",
        "Martin Perez (L",
        "Kohl Drake",
    ):
        if must_l == "Kohl Drake":
            if not re.search(r"Kohl Drake(?: 🧤)? \\(L", html):
                fail("LHP hand missing/wrong: Kohl Drake (L")
            continue
        if must_l not in html:
            fail(f"LHP hand missing/wrong: {must_l}")""",
        """    for must_l in (
        "Zach Thornton (L",
        "Max Fried (L",
        "Payton Tolle (L",
        "Parker Messick (L",
        "Noah Schultz (L",
        "Shane Drohan (L",
        "Robbie Ray (L",
    ):
        if not re.search(re.escape(must_l).replace(r"\\ \\(L", r"(?: 🧤)? \\(L"), html) and must_l not in html:
            # allow glove between name and hand
            base = must_l.replace(" (L", "")
            if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
                fail(f"LHP hand missing/wrong: {must_l}")""",
    )
    atext = atext.replace(
        'arch = ROOT / "preview" / "archive" / "2026-08-06.html"',
        'arch = ROOT / "preview" / "archive" / "2026-08-06.html"',
    )
    atext = atext.replace("8/5 archive missing", "8/6 archive missing")
    atext = atext.replace('content="2026-08-06"', 'content="2026-08-06"')
    atext = atext.replace("8/5 archive wrong sheet-date", "8/6 archive wrong sheet-date")
    (ROOT / "_audit_0807_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0807_final.py")

    ztext = swap_dates((ROOT / "_backfill_zones_0806.py").read_text(encoding="utf-8"))
    ztext = ztext.replace(
        """LHP = {
    "Abbott",
    "Griffin",
    "Peterson",
    "Valdez",
    "Sanchez",
    "Suarez",
    "Perez",
    "Drake",
}""",
        """LHP = {
    "Thornton",
    "Fried",
    "Tolle",
    "Messick",
    "Schultz",
    "Drohan",
    "Ray",
}""",
    )
    (ROOT / "_backfill_zones_0807.py").write_text(ztext, encoding="utf-8")
    print("wrote _backfill_zones_0807.py")

    (ROOT / "_best_0807.py").write_text(
        swap_dates((ROOT / "_best_0806.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote _best_0807.py")


if __name__ == "__main__":
    main()
