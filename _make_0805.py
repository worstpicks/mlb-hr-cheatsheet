#!/usr/bin/env python3
"""Scaffold 2026-08-05 build/patch/verify from 8/4 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Yordan Alvarez",
    "Taylor Trammell",
    "Zach Dezenzo",
    "Brandon Valenzuela",
    "George Springer",
    "Tyrone Taylor💎",
    "Seiya Suzuki",
    "Dansby Swanson",
    "Pete Crow-Armstrong",
    "Michael Conforto⭐",
    "Enrique Hernandez",
    "Kyle Tucker",
    "Hunter Feduccia",
    "Tommy Edman",
    "Teoscar Hernandez💎",
    "Shohei Ohtani",
    "Jake Burger💎",
    "Brandon Nimmo",
    "Wyatt Langford",
    "Corey Seager",
    "Rafael Devers",
    "Bryce Eldridge",
    "Willi Castro💎",
    "Jake McCarthy",
    "Kyle Karros",
    "Hunter Goodman",
    "Junior Caminero",
    "Victor Mesa Jr.⭐",
    "Cedric Mullins",
    "Liam Hicks",
    "Coby Mayo⭐",
    "Pete Alonso💎",
    "Tyler O'Neill",
    "Jose Siri",
    "Zach Neto",
    "Travis d'Arnaud",
    "Bryce Harper⭐",
    "Derek Hill",
    "Bryson Stott",
    "Kyle Schwarber",
    "Bryan De La Cruz",
    "J.T. Realmuto",
    "Daylen Lile⭐",
    "Brady House💎",
    "Abimelec Ortiz",
    "Patrick Bailey⭐",
    "Chase DeLauter💎",
    "Rhys Hoskins",
    "Travis Bazzana",
    "Carson Benge",
    "Francisco Alvarez⭐",
    "Francisco Lindor",
    "Elly De La Cruz⭐",
    "JJ Bleday",
    "Lawrence Butler",
    "Henry Bolte💎",
    "Tyler Soderstrom",
    "Jazz Chisholm Jr.💎",
    "Luis Garcia Jr.⭐",
    "Austin Wells",
    "Ben Rice",
    "Ryan McMahon",
    "Jimmy Crooks💎",
    "Alec Burleson⭐",
    "Nelson Velazquez",
    "Willson Contreras⭐",
    "Wilyer Abreu",
    "Adley Rutschman",
    "Munetaka Murakami⭐",
    "Andrew Benintendi💎",
    "Colson Montgomery",
    "Miguel Vargas",
    "Matt Olson💎",
    "Dominic Smith",
    "Ronald Acuna Jr.",
    "Austin Riley",
    "Griffin Conine💎",
    "Kyle Stowers",
    "Owen Caissie",
    "Jackson Chourio",
    "Andrew Vaughn",
    "Jake Bauers",
    "William Contreras",
    "Bryan Reynolds",
    "Brandon Lowe",
    "Jacob Gonzalez",
    "Esmerlyn Valdez",
    "Jac Caglianone",
    "Bobby Witt Jr.",
    "Kody Clemens",
    "Alan Roden",
    "Julio Rodriguez",
    "Cal Raleigh",
    "Randy Arozarena",
    "Riley Greene⭐",
    "Gleyber Torres",
    "Dillon Dingler",
    "Corbin Carroll",
    "Tim Tawa",
    "Jase Bowen💎",
    "Jackson Merrill",
    "Manny Machado",
]"""

ALIASES = """ALIASES = {
    "JT Realmuto": "J.T. Realmuto",
    "J.T Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Jazz Chisholm": "Jazz Chisholm Jr.",
    "Bobby Witt Jr.": "Bobby Witt Jr.",
    "Bobby Witt": "Bobby Witt Jr.",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Elly De La Cruz": "Elly De La Cruz",
    "Bryan De La Cruz": "Bryan De La Cruz",
    "Travis d'Arnaud": "Travis d'Arnaud",
    "Travis dArnaud": "Travis d'Arnaud",
    "Tyler O'Neill": "Tyler O'Neill",
    "Tyler ONeill": "Tyler O'Neill",
    "Enrique Hernandez": "Enrique Hernandez",
    "Kike Hernandez": "Enrique Hernandez",
    "Willson Contreras": "Willson Contreras",
    "William Contreras": "William Contreras",
    "Will Contreras": "William Contreras",
    "Tim Tawa": "Tim Tawa",
    "Tim tawa": "Tim Tawa",
    "Chase DeLauter": "Chase DeLauter",
    "Abimelec Ortiz": "Abimelec Ortiz",
    "Brandon Valenzuela": "Brandon Valenzuela",
    "Zach Dezenzo": "Zach Dezenzo",
    "Dominic Smith": "Dominic Smith",
    "Jacob Gonzalez": "Jacob Gonzalez",
    "Dillon Dingler": "Dillon Dingler",
    "Jase Bowen": "Jase Bowen",
    "Henry Bolte": "Henry Bolte",
    "Jimmy Crooks": "Jimmy Crooks",
    "Griffin Conine": "Griffin Conine",
    "Tyrone Taylor": "Tyrone Taylor",
    "Teoscar Hernandez": "Teoscar Hernandez",
    "Jake Burger": "Jake Burger",
    "Willi Castro": "Willi Castro",
    "Brady House": "Brady House",
    "Andrew Benintendi": "Andrew Benintendi",
    "Matt Olson": "Matt Olson",
    "Pete Alonso": "Pete Alonso",
    "Michael Conforto": "Michael Conforto",
    "Daylen Lile": "Daylen Lile",
    "Patrick Bailey": "Patrick Bailey",
    "Francisco Alvarez": "Francisco Alvarez",
    "Alec Burleson": "Alec Burleson",
    "Munetaka Murakami": "Munetaka Murakami",
    "Coby Mayo": "Coby Mayo",
    "Riley Greene": "Riley Greene",
    "Victor Mesa Jr": "Victor Mesa Jr.",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/5 LHP
    "Eric Lauer": "L",
    "Shota Imanaga": "L",
    "Carson Whisenhunt": "L",
    "Cody Bradford": "L",
    "Reid Detmers": "L",
    "Trevor Rogers": "L",
    "Jacob Lopez": "L",
    "Noah Cameron": "L",
    "Kyle Harrison": "L",
    "Mitch Bratt": "L",
    # 8/5 RHP
    "Jameson Taillon": "R",
    "Hunter Brown": "R",
    "Nick Martinez": "R",
    "Tomoyuki Sugano": "R",
    "Christian Scott": "R",
    "Tanner Bibee": "R",
    "Rhett Lowder": "R",
    "Jake Irvin": "R",
    "Andrew Painter": "R",
    "Andre Pallante": "R",
    "Will Warren": "R",
    "Sean Burke": "R",
    "Sonny Gray": "R",
    "Eury Perez": "R",
    "Bryce Elder": "R",
    "Dean Kremer": "R",
    "Paul Skenes": "R",
    "Drew Anderson": "R",
    "Bryan Woo": "R",
    "Casey Mize": "R",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-04", "2026-08-05")
    text = text.replace("2026-08-03", "2026-08-04")
    text = text.replace("08-04", "08-05")
    text = text.replace("08-03", "08-04")
    text = text.replace("0804", "0805")
    text = text.replace("0803", "0804")
    text = text.replace("August 4, 2026", "August 5, 2026")
    text = text.replace("Tuesday, August 4, 2026", "Wednesday, August 5, 2026")
    text = text.replace("Tuesday, August 4", "Wednesday, August 5")
    text = text.replace("August 4", "August 5")
    text = text.replace("build0804", "build0805")
    text = text.replace("b0804", "b0805")
    return text


def main() -> None:
    src_build = ROOT / "build-0804-from-csv.py"
    dst_build = ROOT / "build-0805-from-csv.py"
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
    text = re.sub(
        r"\n# 8/4 judgment:.*?(?=\n# 6/22 judgment:|\n# Goblin|\ndef )",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"PITCHER_HAND = \{.*?\}", PITCHER_HAND, text, count=1, flags=re.S)
    dst_build.write_text(text, encoding="utf-8")
    print("wrote", dst_build.name)

    src_patch = ROOT / "patch-0804-preview.py"
    dst_patch = ROOT / "patch-0805-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    # Drop 8/4 judgment locks
    ptext = re.sub(
        r"\n# 8/4 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/4 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-04.html"',
        ptext,
        count=1,
    )
    ptext = ptext.replace(
        "<p>Wednesday, August 5, 2026 — Worst Pickz HR cheat sheet",
        "<p>Wednesday, August 5, 2026 — Worst Pickz HR cheat sheet",
    )
    ptext = ptext.replace(
        "<p>Tuesday, August 5, 2026 — Worst Pickz HR cheat sheet",
        "<p>Wednesday, August 5, 2026 — Worst Pickz HR cheat sheet",
    )
    ptext = re.sub(
        r'if "2026-08-0[45]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[45]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-04" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-04"] = {\n'
            '            "date": "2026-08-04",\n'
            '            "label": "August 4, 2026",\n'
            '            "href": "archive/2026-08-04.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    # Manifest archive order starts with prior day
    ptext = ptext.replace(
        '        "2026-08-04",\n        "2026-08-03",\n        "2026-08-02",',
        '        "2026-08-04",\n        "2026-08-03",\n        "2026-08-02",',
    )
    # Ensure ordered list after current includes 08-04
    if '"2026-08-05",\n        "2026-08-04"' not in ptext and 'for date in [' in ptext:
        ptext = ptext.replace(
            '    for date in [\n        "2026-08-04",',
            '    for date in [\n        "2026-08-04",',
            1,
        )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    src_v = ROOT / "verify-summary-0804.py"
    (ROOT / "verify-summary-0805.py").write_text(
        swap_dates(src_v.read_text(encoding="utf-8")), encoding="utf-8"
    )
    print("wrote verify-summary-0805.py")

    src_a = ROOT / "_audit_0804_final.py"
    atext = swap_dates(src_a.read_text(encoding="utf-8"))
    atext = atext.replace("Tuesday, August 5, 2026", "Wednesday, August 5, 2026")
    atext = atext.replace("Wednesday, August 5, 2026", "Wednesday, August 5, 2026")
    atext = atext.replace(
        'if "Monday, August 4, 2026 — Worst" in html:',
        'if "Tuesday, August 4, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Monday, August 5" in html or "Wednesday, August 5" in html:',
        'if "Tuesday, August 5" in html or "Thursday, August 5" in html:',
    )
    # Fix wrong weekday check leftover: must fail Mon/Thu, allow Wednesday
    atext = atext.replace(
        'if "Tuesday, August 5" in html or "Thursday, August 5" in html:\n'
        '        fail("wrong weekday on August 5 (must be Tuesday)")',
        'if "Tuesday, August 5" in html or "Thursday, August 5" in html:\n'
        '        fail("wrong weekday on August 5 (must be Wednesday)")',
    )
    atext = atext.replace("2026-08-03.html", "2026-08-04.html")
    atext = atext.replace('content="2026-08-03"', 'content="2026-08-04"')
    atext = atext.replace("8/3 archive", "8/4 archive")
    atext = atext.replace("8/3 still labeled current", "8/4 still labeled current")
    atext = atext.replace("August 3, 2026 — current slate", "August 4, 2026 — current slate")
    atext = atext.replace("!= 55", "!= 102")
    atext = atext.replace("expected 55 props", "expected 102 props")
    # Bums from official targets
    atext = atext.replace(
        'expected_bum = {"Joe Ryan", "Grayson Rodriguez", "Zack Littell"}',
        'expected_bum = {"Jameson Taillon", "Andrew Painter", "Bryce Elder", "Jake Irvin", "Dean Kremer", "Tomoyuki Sugano"}',
    )
    atext = atext.replace(
        """    for must_l in (
        "Cade Povich (L",
        "Sean Manaea (L",
        "Joey Cantillo (L",
        "Jesus Luzardo (L",
        "Ryan Weathers (L",
        "Patrick Sandoval (L",
        "MacKenzie Gore (L",
        "Tarik Skubal (L",
        "Eduardo Rodriguez (L",
    ):""",
        """    for must_l in (
        "Eric Lauer (L",
        "Shota Imanaga (L",
        "Carson Whisenhunt (L",
        "Cody Bradford (L",
        "Reid Detmers (L",
        "Trevor Rogers (L",
        "Jacob Lopez (L",
        "Noah Cameron (L",
        "Kyle Harrison (L",
        "Mitch Bratt (L",
    ):""",
    )
    (ROOT / "_audit_0805_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0805_final.py")

    # Zone backfill
    zsrc = ROOT / "_backfill_zones_0804.py"
    ztext = swap_dates(zsrc.read_text(encoding="utf-8"))
    ztext = ztext.replace(
        """LHP = {
    "Povich",
    "Manaea",
    "Cantillo",
    "Luzardo",
    "Weathers",
    "Sandoval",
    "Gore",
    "Skubal",
    "Rodriguez",  # Eduardo Rodriguez (Randy Vasquez is R — hand resolved via build sheet)
}""",
        """LHP = {
    "Lauer",
    "Imanaga",
    "Whisenhunt",
    "Bradford",
    "Detmers",
    "Rogers",
    "Lopez",
    "Cameron",
    "Harrison",
    "Bratt",
}""",
    )
    (ROOT / "_backfill_zones_0805.py").write_text(ztext, encoding="utf-8")
    print("wrote _backfill_zones_0805.py")


if __name__ == "__main__":
    main()
