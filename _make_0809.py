#!/usr/bin/env python3
"""Scaffold 2026-08-09 build/patch/verify from 8/8 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Daylen Lile⭐",
    "CJ Abrams",
    "Jose Tena",
    "Elly De La Cruz⭐",
    "Eugenio Suarez",
    "Sal Stewart",
    "Tyler Stephenson💎",
    "Esmerlyn Valdez⭐",
    "Henry Davis",
    "Bryan Reynolds💎",
    "Brett Baty💎",
    "Francisco Alvarez",
    "Bryce Harper⭐",
    "JT Realmuto",
    "Bryson Stott💎",
    "Kyle Schwarber⭐",
    "Kazuma Okamoto💎",
    "Vladimir Guerrero Jr.",
    "Jazz Chisholm Jr.💎",
    "Ben Rice⭐",
    "Austin Wells💎",
    "Luis Garcia Jr.",
    "Drake Baldwin⭐",
    "Mike Yastrzemski💎",
    "Matt Olson⭐",
    "Austin Riley",
    "Ronald Acuna Jr.",
    "Wilyer Abreu⭐",
    "Jarren Duran",
    "Willson Contreras",
    "Lawrence Butler💎",
    "Tyler Soderstrom💎",
    "Owen Caissie",
    "Griffin Conine",
    "Kyle Stowers⭐",
    "Mike Trout",
    "Zach Neto",
    "Moises Ballesteros⭐",
    "Andrew Vaughn⭐",
    "Jackson Chourio",
    "Luis Lara",
    "Jake Bauers",
    "Josh Bell⭐",
    "Royce Lewis💎",
    "Kody Clemens",
    "Ryan Kreidler💎",
    "Salvador Perez⭐",
    "John Rave",
    "Bobby Witt Jr.💎",
    "Jac Caglianone",
    "Carter Jensen",
    "Pete Crow-Armstrong",
    "Munetaka Murakami",
    "Randal Grichuk",
    "Miguel Vargas",
    "Patrick Bailey💎",
    "Travis Bazzana",
    "Nathaniel Lowe💎",
    "Jimmy Crooks⭐",
    "Ivan Herrera",
    "Alec Burleson",
    "Everson Pereira",
    "Willi Castro",
    "Mickey Moniak",
    "Jake McCarthy",
    "Corey Seager⭐",
    "Brandon Nimmo⭐",
    "Jake Burger💎",
    "Jackson Holliday",
    "Dylan Beavers",
    "Colton Cowser💎",
    "Gunnar Henderson⭐",
    "Leody Taveras",
    "Christian Encarnacion-Strand",
    "Jung Hoo Lee",
    "Rafael Devers",
    "Hao-Yu Lee",
    "Colt Keith",
    "Spencer Torkelson",
    "Dominic Canzone⭐",
    "Cal Raleigh⭐",
    "Colt Emerson",
    "Junior Caminero",
    "Victor Mesa Jr.",
    "Ryan Waldschmidt",
    "Gabriel Moreno",
    "Max Kepler",
    "Andy Pages",
    "Shohei Ohtani⭐",
    "Kyle Tucker",
    "Max Muncy",
    "Fernando Tatis Jr.",
    "Manny Machado",
    "Jackson Merrill",
    "Ty France💎",
    "Taylor Trammell⭐",
    "Yordan Alvarez⭐",
]"""

ALIASES = """ALIASES = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Hao Yu Lee": "Hao-Yu Lee",
    "Hao-Yu Lee": "Hao-Yu Lee",
    "Christian Encarnacion Strand": "Christian Encarnacion-Strand",
    "Christian Encarnacion-Strand": "Christian Encarnacion-Strand",
    "Elly De La Cruz": "Elly De La Cruz",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Victor Mesa": "Victor Mesa Jr.",
    "Moises Ballasteros": "Moises Ballesteros",
    "Moises Ballesteros": "Moises Ballesteros",
    "M. Ballesteros": "Moises Ballesteros",
    "Ryan Waldschmdit": "Ryan Waldschmidt",
    "Ryan Waldschmidt": "Ryan Waldschmidt",
    "JT Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Bobby Witt Jr.": "Bobby Witt Jr.",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Jung Hoo Lee": "Jung Hoo Lee",
    "J.T. Ginn": "J.T. Ginn",
    "JT Ginn": "J.T. Ginn",
    "J T Ginn": "J.T. Ginn",
    "Eduardo Rodriguez": "Eduardo Rodriguez",
    "E. Rodriguez": "Eduardo Rodriguez",
    "Jacob Misiorowski": "Jacob Misiorowski",
    "J. Misiorowski": "Jacob Misiorowski",
    "Grayson Rodriguez": "Grayson Rodriguez",
    "G. Rodriguez": "Grayson Rodriguez",
    "Willson Contreras": "Willson Contreras",
    "William Contreras": "William Contreras",
    "Bryan Reynolds": "Bryan Reynolds",
    "Esmerlyn Valdez": "Esmerlyn Valdez",
    "Daylen Lile": "Daylen Lile",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Lawrence Butler": "Lawrence Butler",
    "Nathaniel Lowe": "Nathaniel Lowe",
    "Patrick Bailey": "Patrick Bailey",
    "Colton Cowser": "Colton Cowser",
    "Dominic Canzone": "Dominic Canzone",
    "Everson Pereira": "Everson Pereira",
    "Luis Lara": "Luis Lara",
    "Griffin Conine": "Griffin Conine",
    "Carter Jensen": "Carter Jensen",
    "Travis Bazzana": "Travis Bazzana",
    "Mickey Moniak": "Mickey Moniak",
    "Dylan Beavers": "Dylan Beavers",
    "Colt Emerson": "Colt Emerson",
    "Andy Pages": "Andy Pages",
    "Max Kepler": "Max Kepler",
    "Gabriel Moreno": "Gabriel Moreno",
    "Ty France": "Ty France",
    "Taylor Trammell": "Taylor Trammell",
    "Yordan Alvarez": "Yordan Alvarez",
    "Shohei Ohtani": "Shohei Ohtani",
    "Kyle Tucker": "Kyle Tucker",
    "Corey Seager": "Corey Seager",
    "Brandon Nimmo": "Brandon Nimmo",
    "Gunnar Henderson": "Gunnar Henderson",
    "Cal Raleigh": "Cal Raleigh",
    "Jimmy Crooks": "Jimmy Crooks",
    "Salvador Perez": "Salvador Perez",
    "Josh Bell": "Josh Bell",
    "Andrew Vaughn": "Andrew Vaughn",
    "Kyle Stowers": "Kyle Stowers",
    "Wilyer Abreu": "Wilyer Abreu",
    "Matt Olson": "Matt Olson",
    "Drake Baldwin": "Drake Baldwin",
    "Ben Rice": "Ben Rice",
    "Kyle Schwarber": "Kyle Schwarber",
    "Bryce Harper": "Bryce Harper",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/9 LHP
    "Jesus Luzardo": "L",
    "Sean Manaea": "L",
    "Joey Cantillo": "L",
    "Matthew Boyd": "L",
    "Connor Prielipp": "L",
    "Cade Povich": "L",
    "Ian Seymour": "L",
    "Justin Wrobleski": "L",
    "Eduardo Rodriguez": "L",
    # 8/9 RHP
    "Brady Singer": "R",
    "Brad Lord": "R",
    "J.T. Ginn": "R",
    "Brayan Bello": "R",
    "Grant Holmes": "R",
    "Cam Schlittler": "R",
    "Shane Bieber": "R",
    "Jared Jones": "R",
    "Grayson Rodriguez": "R",
    "Ryan Gusto": "R",
    "Davis Martin": "R",
    "Randy Dobnak": "R",
    "Jacob Misiorowski": "R",
    "Michael Lorenzen": "R",
    "Michael McGreevy": "R",
    "Kumar Rocker": "R",
    "Troy Melton": "R",
    "Logan Webb": "R",
    "Emerson Hancock": "R",
    "Cristian Javier": "R",
    "Randy Vasquez": "R",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-08", "TEMP_CUR")
    text = text.replace("2026-08-07", "TEMP_PREV")
    text = text.replace("TEMP_CUR", "2026-08-09")
    text = text.replace("TEMP_PREV", "2026-08-08")
    text = text.replace("08-08", "TEMP_MMDD")
    text = text.replace("08-07", "TEMP_PREV_MMDD")
    text = text.replace("TEMP_MMDD", "08-09")
    text = text.replace("TEMP_PREV_MMDD", "08-08")
    text = text.replace("0808", "TEMP_CODE")
    text = text.replace("0807", "TEMP_PREV_CODE")
    text = text.replace("TEMP_CODE", "0809")
    text = text.replace("TEMP_PREV_CODE", "0808")
    text = text.replace("Saturday, August 8, 2026", "Sunday, August 9, 2026")
    text = text.replace("Saturday, August 8", "Sunday, August 9")
    text = text.replace("August 8, 2026", "August 9, 2026")
    text = text.replace("August 8", "August 9")
    # fix accidental weekday leftovers
    text = text.replace("Saturday, August 9", "Sunday, August 9")
    text = text.replace("Friday, August 9", "Sunday, August 9")
    text = text.replace("Monday, August 9", "Sunday, August 9")
    return text


def main() -> None:
    src_build = ROOT / "build-0808-from-csv.py"
    dst_build = ROOT / "build-0809-from-csv.py"
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

    src_patch = ROOT / "patch-0808-preview.py"
    dst_patch = ROOT / "patch-0809-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    ptext = re.sub(
        r"\n# 8/8 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/8 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-08.html"',
        ptext,
        count=1,
    )
    ptext = re.sub(
        r'if "2026-08-0[89]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[89]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-08" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-08"] = {\n'
            '            "date": "2026-08-08",\n'
            '            "label": "August 8, 2026",\n'
            '            "href": "archive/2026-08-08.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"for date in \[\n(?:        \"2026-08-\d{2}\",\n){1,5}",
        'for date in [\n        "2026-08-08",\n        "2026-08-07",\n        "2026-08-06",\n        "2026-08-05",\n',
        ptext,
        count=1,
    )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    (ROOT / "verify-summary-0809.py").write_text(
        swap_dates((ROOT / "verify-summary-0808.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0809.py")

    atext = swap_dates((ROOT / "_audit_0808_final.py").read_text(encoding="utf-8"))
    atext = atext.replace("Sunday, August 9, 2026", "Sunday, August 9, 2026")
    atext = atext.replace(
        'if "Saturday, August 8, 2026 — Worst" in html:',
        'if "Saturday, August 8, 2026 — Worst" in html:',
    )
    # After swap_dates, stale-hero check may say Saturday August 9 — fix
    atext = atext.replace(
        'if "Saturday, August 9, 2026 — Worst" in html:',
        'if "Saturday, August 8, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Friday, August 9" in html or "Thursday, August 9" in html:',
        'if "Saturday, August 9" in html or "Monday, August 9" in html:',
    )
    atext = atext.replace(
        'fail("wrong weekday on August 9 (must be Saturday)")',
        'fail("wrong weekday on August 9 (must be Sunday)")',
    )
    atext = atext.replace(
        'if "August 8, 2026 — current slate" in html:\n        fail("8/8 still labeled current")',
        'if "August 8, 2026 — current slate" in html:\n        fail("8/8 still labeled current")',
    )
    atext = atext.replace("!= 80", "!= PROPCOUNT")
    atext = atext.replace("expected 80 props", "expected PROPCOUNT props")
    atext = atext.replace(
        'expected_bum = {"Aaron Nola", "Robert Stock", "Max Scherzer"}',
        'expected_bum = {"Brad Lord", "Grayson Rodriguez", "Justin Wrobleski", "Sean Manaea"}',
    )
    atext = atext.replace(
        """    for base in (
        "Chris Sale",
        "Gage Jump",
        "Jake Bennett",
        "Andrew Alvarez",
        "Robert Gasser",
        "Anthony Kay",
        "Kyle Freeland",
        "Matthew Liberatore",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")""",
        """    for base in (
        "Jesus Luzardo",
        "Sean Manaea",
        "Joey Cantillo",
        "Matthew Boyd",
        "Connor Prielipp",
        "Cade Povich",
        "Ian Seymour",
        "Justin Wrobleski",
        "Eduardo Rodriguez",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")""",
    )
    atext = atext.replace(
        'arch = ROOT / "preview" / "archive" / "2026-08-08.html"',
        'arch = ROOT / "preview" / "archive" / "2026-08-08.html"',
    )
    atext = atext.replace("8/7 archive missing", "8/8 archive missing")
    atext = atext.replace("8/7 archive wrong sheet-date", "8/8 archive wrong sheet-date")
    atext = atext.replace(
        'elif \'content="2026-08-08"\' not in arch.read_text(encoding="utf-8"):',
        'elif \'content="2026-08-08"\' not in arch.read_text(encoding="utf-8"):',
    )
    (ROOT / "_audit_0809_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0809_final.py")

    ztext = swap_dates((ROOT / "_backfill_zones_0808.py").read_text(encoding="utf-8"))
    ztext = ztext.replace(
        """LHP = {
    "Sale",
    "Jump",
    "Bennett",
    "Alvarez",
    "Gasser",
    "Kay",
    "Freeland",
    "Liberatore",
}""",
        """LHP = {
    "Luzardo",
    "Manaea",
    "Cantillo",
    "Boyd",
    "Prielipp",
    "Povich",
    "Seymour",
    "Wrobleski",
    "Rodriguez",
}""",
    )
    (ROOT / "_backfill_zones_0809.py").write_text(ztext, encoding="utf-8")
    print("wrote _backfill_zones_0809.py")

    (ROOT / "_best_0809.py").write_text(
        swap_dates((ROOT / "_best_0808.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote _best_0809.py")


if __name__ == "__main__":
    main()
