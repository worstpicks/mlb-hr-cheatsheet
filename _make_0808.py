#!/usr/bin/env python3
"""Scaffold 2026-08-08 build/patch/verify from 8/7 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Spencer Jones",
    "Heliot Ramos",
    "Ronald Acuna Jr.💎",
    "Matt Olson",
    "Mike Yastrzemski💎",
    "Dominic Smith",
    "Owen Caissie",
    "Zach Neto",
    "Mike Trout💎",
    "Willson Contreras",
    "Andruw Monasterio",
    "Jonah Heim",
    "Tyler Soderstrom",
    "Brian Serven",
    "Derek Hill",
    "Bryson Stott",
    "Jesus Sanchez💎",
    "George Springer",
    "Brandon Lowe⭐",
    "Endy Rodriguez💎",
    "Brett Baty",
    "Francisco Alvarez",
    "Marcus Semien",
    "Francisco Lindor💎",
    "Abimelec Ortiz💎",
    "Dylan Crews",
    "Elly De La Cruz💎",
    "Sal Stewart",
    "Noelvi Marte💎",
    "Jackson Chourio💎",
    "Andrew Vaughn",
    "Brice Turang💎",
    "Jake Bauers",
    "Garrett Mitchell",
    "Josh Bell",
    "Ryan Kreidler",
    "Alex Jackson",
    "John Rave",
    "Starling Marte",
    "Jac Caglianone",
    "Pete Crow-Armstrong⭐",
    "Miguel Amaya",
    "Tyrone Taylor",
    "Wyatt Langford⭐",
    "Leody Taveras",
    "Pete Alonso⭐",
    "Christian Encarnacion-Strand💎",
    "Gunnar Henderson",
    "Jordan Walker",
    "Alec Burleson💎",
    "Jimmy Crooks⭐",
    "Nelson Velazquez",
    "Willi Castro",
    "Ezequiel Tovar",
    "Bryce Eldridge",
    "Rafael Devers",
    "Osleivis Basabe",
    "Gleyber Torres💎",
    "Dillon Dingler💎",
    "Hao-Yu Lee💎",
    "Manny Machado",
    "Jackson Merrill",
    "Gage Workman",
    "Yordan Alvarez⭐",
    "Taylor Trammell💎",
    "Randal Grichuk💎",
    "Munetaka Murakami⭐",
    "Colson Montgomery⭐",
    "Andrew Benintendi",
    "Jo Adell",
    "Rhys Hoskins",
    "Tim Tawa💎",
    "Lars Nootbaar",
    "Max Muncy",
    "Mookie Betts",
    "Cal Raleigh⭐",
    "Julio Rodriguez⭐",
    "Randy Arozarena",
    "Junior Caminero⭐",
    "Victor Mesa Jr.",
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
    "Willson Contreras": "Willson Contreras",
    "William Contreras": "William Contreras",
    "Andruw Monasterio": "Andruw Monasterio",
    "Andrew Monasterio": "Andruw Monasterio",
    "Endy Rodriguez": "Endy Rodriguez",
    "Abimelec Ortiz": "Abimelec Ortiz",
    "Noelvi Marte": "Noelvi Marte",
    "Osleivis Basabe": "Osleivis Basabe",
    "Randal Grichuk": "Randal Grichuk",
    "Taylor Trammell": "Taylor Trammell",
    "Spencer Jones": "Spencer Jones",
    "Heliot Ramos": "Heliot Ramos",
    "Mike Yastrzemski": "Mike Yastrzemski",
    "Mike Trout": "Mike Trout",
    "Jesus Sanchez": "Jesus Sanchez",
    "Brandon Lowe": "Brandon Lowe",
    "Francisco Lindor": "Francisco Lindor",
    "Jackson Chourio": "Jackson Chourio",
    "Brice Turang": "Brice Turang",
    "Alec Burleson": "Alec Burleson",
    "Jimmy Crooks": "Jimmy Crooks",
    "Gleyber Torres": "Gleyber Torres",
    "Dillon Dingler": "Dillon Dingler",
    "Yordan Alvarez": "Yordan Alvarez",
    "Munetaka Murakami": "Munetaka Murakami",
    "Colson Montgomery": "Colson Montgomery",
    "Pete Alonso": "Pete Alonso",
    "Wyatt Langford": "Wyatt Langford",
    "Cal Raleigh": "Cal Raleigh",
    "Julio Rodriguez": "Julio Rodriguez",
    "Junior Caminero": "Junior Caminero",
    "Tim Tawa": "Tim Tawa",
    "Gage Workman": "Gage Workman",
    "Starling Marte": "Starling Marte",
    "Miguel Amaya": "Miguel Amaya",
    "Alex Jackson": "Alex Jackson",
    "John Rave": "John Rave",
    "Ryan Kreidler": "Ryan Kreidler",
    "Dominic Smith": "Dominic Smith",
    "Brian Serven": "Brian Serven",
    "Nelson Velazquez": "Nelson Velazquez",
    "Ezequiel Tovar": "Ezequiel Tovar",
    "Bryce Eldridge": "Bryce Eldridge",
    "Lars Nootbaar": "Lars Nootbaar",
    "Matthew Liberatore": "Matthew Liberatore",
    "M. Liberatore": "Matthew Liberatore",
    "Yoshinobu Yamamoto": "Yoshinobu Yamamoto",
    "Y. Yamamoto": "Yoshinobu Yamamoto",
    "Jacob deGrom": "Jacob deGrom",
    "Jacob Degrom": "Jacob deGrom",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/8 LHP
    "Chris Sale": "L",
    "Gage Jump": "L",
    "Jake Bennett": "L",
    "Andrew Alvarez": "L",
    "Robert Gasser": "L",
    "Anthony Kay": "L",
    "Kyle Freeland": "L",
    "Matthew Liberatore": "L",
    # 8/8 RHP
    "Gerrit Cole": "R",
    "Walbert Urena": "R",
    "Sandy Alcantara": "R",
    "Max Scherzer": "R",
    "Aaron Nola": "R",
    "Robert Stock": "R",
    "Bubba Chandler": "R",
    "Chase Burns": "R",
    "Clay Holmes": "R",
    "Seth Lugo": "R",
    "Taj Bradley": "R",
    "Gavin Williams": "R",
    "Kyle Bradish": "R",
    "Jacob deGrom": "R",
    "Peter Lambert": "R",
    "Michael King": "R",
    "Jackson Jobe": "R",
    "Landen Roupp": "R",
    "Yoshinobu Yamamoto": "R",
    "Brandon Pfaadt": "R",
    "Griffin Jax": "R",
    "George Kirby": "R",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-07", "TEMP_CUR")
    text = text.replace("2026-08-06", "TEMP_PREV")
    text = text.replace("TEMP_CUR", "2026-08-08")
    text = text.replace("TEMP_PREV", "2026-08-07")
    text = text.replace("08-07", "TEMP_MMDD")
    text = text.replace("08-06", "TEMP_PREV_MMDD")
    text = text.replace("TEMP_MMDD", "08-08")
    text = text.replace("TEMP_PREV_MMDD", "08-07")
    text = text.replace("0807", "TEMP_CODE")
    text = text.replace("0806", "TEMP_PREV_CODE")
    text = text.replace("TEMP_CODE", "0808")
    text = text.replace("TEMP_PREV_CODE", "0807")
    text = text.replace("Friday, August 7, 2026", "Saturday, August 8, 2026")
    text = text.replace("Friday, August 7", "Saturday, August 8")
    text = text.replace("August 7, 2026", "August 8, 2026")
    text = text.replace("August 7", "August 8")
    # fix accidental weekday leftovers
    text = text.replace("Thursday, August 8", "Saturday, August 8")
    text = text.replace("Friday, August 8", "Saturday, August 8")
    text = text.replace("Wednesday, August 8", "Saturday, August 8")
    return text


def main() -> None:
    src_build = ROOT / "build-0807-from-csv.py"
    dst_build = ROOT / "build-0808-from-csv.py"
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

    src_patch = ROOT / "patch-0807-preview.py"
    dst_patch = ROOT / "patch-0808-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    ptext = re.sub(
        r"\n# 8/7 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/7 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-07.html"',
        ptext,
        count=1,
    )
    # Manifest prior-day block
    ptext = re.sub(
        r'if "2026-08-0[78]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[78]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-07" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-07"] = {\n'
            '            "date": "2026-08-07",\n'
            '            "label": "August 7, 2026",\n'
            '            "href": "archive/2026-08-07.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    # Ordered archive list must start with prior day, not current
    ptext = re.sub(
        r'for date in \[\n(?:        "2026-08-08",\n)?        "2026-08-07",\n        "2026-08-0[56]",\n        "2026-08-0[45]",',
        'for date in [\n        "2026-08-07",\n        "2026-08-06",\n        "2026-08-05",\n        "2026-08-04",',
        ptext,
        count=1,
    )
    if '"2026-08-07",\n        "2026-08-06",\n        "2026-08-05",\n        "2026-08-04"' not in ptext:
        # fallback: force the head of the list
        ptext = re.sub(
            r"for date in \[\n(?:        \"2026-08-\d{2}\",\n){1,4}",
            'for date in [\n        "2026-08-07",\n        "2026-08-06",\n        "2026-08-05",\n        "2026-08-04",\n',
            ptext,
            count=1,
        )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    (ROOT / "verify-summary-0808.py").write_text(
        swap_dates((ROOT / "verify-summary-0807.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0808.py")

    atext = swap_dates((ROOT / "_audit_0807_final.py").read_text(encoding="utf-8"))
    atext = atext.replace("Friday, August 8, 2026", "Saturday, August 8, 2026")
    atext = atext.replace(
        'if "Thursday, August 6, 2026 — Worst" in html:',
        'if "Friday, August 7, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Thursday, August 8" in html or "Wednesday, August 8" in html:',
        'if "Friday, August 8" in html or "Thursday, August 8" in html:',
    )
    atext = atext.replace(
        'fail("wrong weekday on August 8 (must be Friday)")',
        'fail("wrong weekday on August 8 (must be Saturday)")',
    )
    atext = atext.replace(
        'if "August 6, 2026 — current slate" in html:\n        fail("8/6 still labeled current")',
        'if "August 7, 2026 — current slate" in html:\n        fail("8/7 still labeled current")',
    )
    atext = atext.replace("!= 67", "!= 80")
    atext = atext.replace("expected 67 props", "expected 80 props")
    atext = atext.replace(
        'expected_bum = {"Ronel Blanco", "George Klassen", "Ryan Feltner", "Jack Perkins"}',
        'expected_bum = {"PLACEHOLDER"}',
    )
    atext = atext.replace(
        """    for base in (
        "Zach Thornton",
        "Max Fried",
        "Payton Tolle",
        "Parker Messick",
        "Noah Schultz",
        "Shane Drohan",
        "Robbie Ray",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")""",
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
    )
    atext = atext.replace(
        'arch = ROOT / "preview" / "archive" / "2026-08-07.html"',
        'arch = ROOT / "preview" / "archive" / "2026-08-07.html"',
    )
    atext = atext.replace("8/6 archive missing", "8/7 archive missing")
    atext = atext.replace("8/6 archive wrong sheet-date", "8/7 archive wrong sheet-date")
    # ensure archive content check is 08-07
    atext = atext.replace(
        'elif \'content="2026-08-08"\' not in arch.read_text(encoding="utf-8"):',
        'elif \'content="2026-08-07"\' not in arch.read_text(encoding="utf-8"):',
    )
    (ROOT / "_audit_0808_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0808_final.py")

    ztext = swap_dates((ROOT / "_backfill_zones_0807.py").read_text(encoding="utf-8"))
    ztext = ztext.replace(
        """LHP = {
    "Thornton",
    "Fried",
    "Tolle",
    "Messick",
    "Schultz",
    "Drohan",
    "Ray",
}""",
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
    )
    (ROOT / "_backfill_zones_0808.py").write_text(ztext, encoding="utf-8")
    print("wrote _backfill_zones_0808.py")

    (ROOT / "_best_0808.py").write_text(
        swap_dates((ROOT / "_best_0807.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote _best_0808.py")


if __name__ == "__main__":
    main()
