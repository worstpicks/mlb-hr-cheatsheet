#!/usr/bin/env python3
"""Scaffold 2026-08-11 build/patch/verify from 8/10 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Owen Caissie⭐",
    "Jakob Marsee",
    "Brandon Lowe",
    "Endy Rodriguez",
    "Dillon Dingler⭐",
    "Spencer Torkelson⭐",
    "Rhys Hoskins",
    "Jo Adell⭐",
    "Nathaniel Lowe",
    "Andres Chaparro💎",
    "Brady House💎",
    "Dylan Crews⭐",
    "Ian Happ⭐",
    "Miguel Amaya💎",
    "Pete Crow-Armstrong",
    "Michael Busch",
    "Ben Rice💎",
    "Jazz Chisholm Jr.",
    "Luis Garcia Jr.",
    "Cal Raleigh⭐",
    "Dominic Canzone💎",
    "Vladimir Guerrero Jr.",
    "Jarren Duran",
    "Willson Contreras",
    "Jake Rogers",
    "Matt Olson⭐",
    "Ronald Acuna Jr.💎",
    "Drake Baldwin",
    "Michael Harris II",
    "Francisco Lindor💎",
    "Marcus Semien",
    "A.J. Ewing",
    "Kody Clemens",
    "Josh Bell",
    "Royce Lewis💎",
    "Leody Taveras",
    "Pete Alonso⭐",
    "Jackson Holliday",
    "Coby Mayo💎",
    "Munetaka Murakami⭐",
    "Randal Grichuk",
    "Eugenio Suarez",
    "JJ Bleday⭐",
    "Tyler Stephenson",
    "Jordan Walker⭐",
    "Alec Burleson",
    "Ivan Herrera💎",
    "Bryce Harper⭐",
    "J.T. Realmuto",
    "Kyle Schwarber",
    "Zach Neto",
    "Moises Ballesteros",
    "Nolan Schanuel",
    "Jose Siri⭐",
    "Joc Pederson⭐",
    "Jake Burger",
    "Jase Bowen💎",
    "Gavin Sheets",
    "Jake Bauers⭐",
    "Gary Sanchez",
    "Brice Turang",
    "Tyler Soderstrom",
    "Lawrence Butler💎",
    "Junior Caminero",
    "Victor Mesa Jr.",
    "Yandy Diaz",
    "Lars Nootbaar⭐",
    "Ketel Marte💎",
    "Ezequiel Tovar",
    "Cole Carrigg",
    "Connor Norby",
    "Jung Hoo Lee💎",
    "Rafael Devers",
    "Cam Smith",
    "Christian Walker",
    "Yordan Alvarez",
    "Shohei Ohtani",
    "Teoscar Hernandez",
    "John Rave",
    "Salvador Perez",
    "Carter Jensen💎",
    "Jac Caglianone💎",
]"""

ALIASES = """ALIASES = {
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Jake Burgers": "Jake Burger",
    "Jake Burger": "Jake Burger",
    "Jose Bowen": "Jase Bowen",
    "Jase Bowen": "Jase Bowen",
    "Cole Craigg": "Cole Carrigg",
    "Cole Carrigg": "Cole Carrigg",
    "AJ Ewing": "A.J. Ewing",
    "A.J. Ewing": "A.J. Ewing",
    "JT Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Michael Harris II": "Michael Harris II",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Victor Mesa": "Victor Mesa Jr.",
    "Jung Hoo Lee": "Jung Hoo Lee",
    "Jac Caglianone": "Jac Caglianone",
    "Munetaka Murakami": "Munetaka Murakami",
    "Willson Contreras": "Willson Contreras",
    "William Contreras": "William Contreras",
    "C. Sanchez": "Cristopher Sanchez",
    "Cristopher Sanchez": "Cristopher Sanchez",
    "C. Whisenhunt": "Carson Whisenhunt",
    "Carson Whisenhunt": "Carson Whisenhunt",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/11 LHP
    "Shota Imanaga": "L",
    "Ryan Weathers": "L",
    "Patrick Sandoval": "L",
    "Martin Perez": "L",
    "Nick Lodolo": "L",
    "Cristopher Sanchez": "L",
    "Cody Bradford": "L",
    "Kyle Harrison": "L",
    "Mitch Bratt": "L",
    "Carson Whisenhunt": "L",
    "Blake Snell": "L",
    # 8/11 RHP
    "Tanner Bibee": "R",
    "Drew Anderson": "R",
    "Paul Skenes": "R",
    "Eury Perez": "R",
    "Jake Irvin": "R",
    "Bryan Woo": "R",
    "Dylan Cease": "R",
    "Nolan McLean": "R",
    "Sean Burke": "R",
    "Brandon Young": "R",
    "Bailey Ober": "R",
    "Andre Pallante": "R",
    "Ryan Johnson": "R",
    "Nick Martinez": "R",
    "Mason Barnett": "R",
    "Walker Buehler": "R",
    "Tomoyuki Sugano": "R",
    "Hunter Brown": "R",
    "Michael Wacha": "R",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-10", "TEMP_CUR")
    text = text.replace("2026-08-09", "TEMP_PREV")
    text = text.replace("TEMP_CUR", "2026-08-11")
    text = text.replace("TEMP_PREV", "2026-08-10")
    text = text.replace("08-10", "TEMP_MMDD")
    text = text.replace("08-09", "TEMP_PREV_MMDD")
    text = text.replace("TEMP_MMDD", "08-11")
    text = text.replace("TEMP_PREV_MMDD", "08-10")
    text = text.replace("0810", "TEMP_CODE")
    text = text.replace("0809", "TEMP_PREV_CODE")
    text = text.replace("TEMP_CODE", "0811")
    text = text.replace("TEMP_PREV_CODE", "0810")
    text = text.replace("Monday, August 10, 2026", "Tuesday, August 11, 2026")
    text = text.replace("Monday, August 10", "Tuesday, August 11")
    text = text.replace("August 10, 2026", "August 11, 2026")
    text = text.replace("August 10", "August 11")
    # fix accidental weekday leftovers from naive swaps
    text = text.replace("Monday, August 11", "Tuesday, August 11")
    text = text.replace("Sunday, August 11", "Tuesday, August 11")
    text = text.replace("Wednesday, August 11", "Tuesday, August 11")
    return text


def main() -> None:
    src_build = ROOT / "build-0810-from-csv.py"
    dst_build = ROOT / "build-0811-from-csv.py"
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

    src_patch = ROOT / "patch-0810-preview.py"
    dst_patch = ROOT / "patch-0811-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    # Strip prior-day judgment locks (re-insert after ranking).
    ptext = re.sub(
        r"\n# 8/10 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/10 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-10.html"',
        ptext,
        count=1,
    )
    # Manifest archive block: promote 8/10, keep 8/9.
    ptext = re.sub(
        r'if "2026-08-1[01]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-1[01]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-10" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-10"] = {\n'
            '            "date": "2026-08-10",\n'
            '            "label": "August 10, 2026",\n'
            '            "href": "archive/2026-08-10.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"for date in \[\n(?:        \"2026-08-\d{2}\",\n){1,8}",
        (
            "for date in [\n"
            '        "2026-08-10",\n'
            '        "2026-08-09",\n'
            '        "2026-08-08",\n'
            '        "2026-08-07",\n'
            '        "2026-08-06",\n'
            '        "2026-08-05",\n'
        ),
        ptext,
        count=1,
    )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    (ROOT / "verify-summary-0811.py").write_text(
        swap_dates((ROOT / "verify-summary-0810.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0811.py")

    atext = swap_dates((ROOT / "_audit_0810_final.py").read_text(encoding="utf-8"))
    atext = atext.replace(
        'if "Monday, August 10, 2026 — Worst" in html:',
        'if "Monday, August 10, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Tuesday, August 11, 2026 — Worst" in html:\n        fail("stale 8/10 hero still on current sheet")',
        'if "Monday, August 10, 2026 — Worst" in html:\n        fail("stale 8/10 hero still on current sheet")',
    )
    # After swap, stale-hero check may already be Monday → force correct.
    if 'if "Monday, August 10, 2026 — Worst" in html:' not in atext:
        atext = atext.replace(
            'if "Sunday, August 9, 2026 — Worst" in html:',
            'if "Monday, August 10, 2026 — Worst" in html:',
        )
    atext = atext.replace(
        'fail("stale 8/9 hero still on current sheet")',
        'fail("stale 8/10 hero still on current sheet")',
    )
    atext = atext.replace(
        'if "Sunday, August 11" in html or "Saturday, August 11" in html:',
        'if "Monday, August 11" in html or "Wednesday, August 11" in html:',
    )
    atext = atext.replace(
        'fail("wrong weekday on August 11 (must be Monday)")',
        'fail("wrong weekday on August 11 (must be Tuesday)")',
    )
    atext = atext.replace(
        'if "August 10, 2026 — current slate" in html:\n        fail("8/10 still labeled current")',
        'if "August 10, 2026 — current slate" in html:\n        fail("8/10 still labeled current")',
    )
    atext = atext.replace(
        'expected_bum = {"Jameson Taillon", "Reid Detmers"}',
        'expected_bum = {"Tomoyuki Sugano", "Ryan Johnson", "Mason Barnett"}',
    )
    atext = atext.replace(
        """    for base in (
        "Trevor Rogers",
        "MacKenzie Gore",
        "Reid Detmers",
        "Jacob Lopez",
        "Noah Cameron",
        "Tarik Skubal",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")""",
        """    for base in (
        "Shota Imanaga",
        "Ryan Weathers",
        "Patrick Sandoval",
        "Martin Perez",
        "Nick Lodolo",
        "Cristopher Sanchez",
        "Cody Bradford",
        "Kyle Harrison",
        "Mitch Bratt",
        "Carson Whisenhunt",
        "Blake Snell",
    ):
        if not re.search(rf"{re.escape(base)}(?: 🧤)? \\(L", html):
            fail(f"LHP hand missing/wrong: {base} (L")""",
    )
    atext = atext.replace(
        'arch = ROOT / "preview" / "archive" / "2026-08-10.html"',
        'arch = ROOT / "preview" / "archive" / "2026-08-10.html"',
    )
    atext = atext.replace("8/9 archive missing", "8/10 archive missing")
    atext = atext.replace("8/9 archive wrong sheet-date", "8/10 archive wrong sheet-date")
    # 15 games today
    atext = atext.replace("!= 10", "!= 15")
    atext = atext.replace("expected 10 games", "expected 15 games")
    atext = atext.replace("expected 10 gameMeta", "expected 15 gameMeta")
    # PROPCOUNT placeholder — set after build
    if "PROPCOUNT =" not in atext:
        atext = atext.replace(
            'DATE = "2026-08-11"\nPREVIEW',
            'DATE = "2026-08-11"\nPROPCOUNT = 82\nPREVIEW',
        )
    else:
        atext = re.sub(r"PROPCOUNT = \d+", "PROPCOUNT = 82", atext, count=1)
    (ROOT / "_audit_0811_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0811_final.py")

    ztext = swap_dates((ROOT / "_backfill_zones_0810.py").read_text(encoding="utf-8"))
    ztext = re.sub(
        r"LHP = \{.*?\}",
        """LHP = {
    "Imanaga",
    "Weathers",
    "Sandoval",
    "Perez",
    "Lodolo",
    "Sanchez",
    "Bradford",
    "Harrison",
    "Bratt",
    "Whisenhunt",
    "Snell",
}""",
        ztext,
        count=1,
        flags=re.S,
    )
    (ROOT / "_backfill_zones_0811.py").write_text(ztext, encoding="utf-8")
    print("wrote _backfill_zones_0811.py")

    (ROOT / "_best_0811.py").write_text(
        swap_dates((ROOT / "_best_0810.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote _best_0811.py")


if __name__ == "__main__":
    main()
