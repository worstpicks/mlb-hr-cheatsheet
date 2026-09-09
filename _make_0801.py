#!/usr/bin/env python3
"""Scaffold 2026-08-01 build/patch/verify from 7/31 templates."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Kazuma Okamoto💎",
    "Vladimir Guerrero Jr.",
    "Jimmy Crooks💎",
    "Jordan Walker⭐",
    "Alec Burleson⭐",
    "Lars Nootbaar",
    "Richie Palacios💎",
    "Junior Caminero⭐",
    "Victor Mesa Jr.",
    "Munetaka Murakami⭐",
    "Andrew Benintendi",
    "Miguel Vargas",
    "Colson Montgomery⭐",
    "Dominic Canzone⭐",
    "Cal Raleigh⭐",
    "Julio Rodriguez",
    "Rob Refsnyder",
    "Kody Clemens⭐",
    "Royce Lewis",
    "Francisco Alvarez⭐",
    "A.J. Ewing💎",
    "Francisco Lindor⭐",
    "Heriberto Hernandez",
    "Leo Jimenez💎",
    "Otto Lopez",
    "Eugenio Suarez⭐",
    "Elly De La Cruz",
    "JJ Bleday",
    "Esmerlyn Valdez",
    "Ryan O'Hearn",
    "Coby Mayo⭐",
    "Pete Alonso💎",
    "Bryce Harper⭐",
    "Bryson Stott",
    "Derek Hill",
    "Jeremy Pena",
    "Yainer Diaz💎",
    "Taylor Trammell",
    "Jake Burger",
    "Ezequiel Duran",
    "Corey Seager💎",
    "Chase DeLauter",
    "Patrick Bailey",
    "Rhys Hoskins",
    "Gabriel Moreno",
    "Ildemaro Vargas",
    "Max Kepler",
    "Corbin Carroll",
    "Michael Conforto💎",
    "Carson Kelly",
    "Alex Bregman",
    "Ben Rice",
    "Anthony Volpe",
    "Spencer Jones",
    "Amed Rosario",
    "Mike Yastrzemski💎",
    "Matt Olson",
    "Ronald Acuna Jr.💎",
    "Drake Baldwin",
    "Hunter Goodman",
    "Mickey Moniak",
    "Willi Castro",
    "Salvador Perez💎",
    "Carter Jensen⭐",
    "Lane Thomas",
    "John Rave💎",
    "Ty France💎",
    "Jackson Merrill⭐",
    "Manny Machado⭐",
    "Bryce Eldridge",
    "Rafael Devers",
    "Shohei Ohtani⭐",
    "Enrique Hernandez💎",
    "Freddie Freeman",
    "Kyle Tucker",
    "Willson Contreras",
    "Jorge Soler",
    "Jose Siri",
    "Jo Adell",
    "Cooper Pratt",
    "Jake Bauers⭐",
    "Garrett Mitchell",
    "Andrew Vaughn",
    "Luis Lara",
    "Tyler Soderstrom",
    "Henry Bolte",
    "Lawrence Butler",
    "Riley Greene⭐",
    "Hao-Yu Lee💎",
    "Dillon Dingler",
]"""

ALIASES = """ALIASES = {
    "Andrew Beintendi": "Andrew Benintendi",
    "Andrew Benintendi": "Andrew Benintendi",
    "AJ Ewing": "A.J. Ewing",
    "A.J. Ewing": "A.J. Ewing",
    "Garret Mitchell": "Garrett Mitchell",
    "Garrett Mitchell": "Garrett Mitchell",
    "Hao-Yu-Lee": "Hao-Yu Lee",
    "Hao Yu Lee": "Hao-Yu Lee",
    "Hao-Yu Lee": "Hao-Yu Lee",
    "Hao-Yu  Lee": "Hao-Yu Lee",
    "Julio Rodriguez": "Julio Rodriguez",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Vlad Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Jeremy Pena": "Jeremy Pena",
    "Enrique Hernandez": "Enrique Hernandez",
    "Kike Hernandez": "Enrique Hernandez",
    "Ryan OHearn": "Ryan O'Hearn",
    "Ryan O'Hearn": "Ryan O'Hearn",
    "Richie Palacios": "Richie Palacios",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Kazuma Okamoto": "Kazuma Okamoto",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-07-31", "2026-08-01")
    text = text.replace("2026-07-30", "2026-07-31")
    text = text.replace("07-31", "08-01")
    text = text.replace("07-30", "07-31")
    text = text.replace("0731", "0801")
    text = text.replace("July 31, 2026", "August 1, 2026")
    text = text.replace("Friday, July 31, 2026", "Saturday, August 1, 2026")
    text = text.replace("Friday, July 31", "Saturday, August 1")
    text = text.replace("July 31", "August 1")
    text = text.replace("build0731", "build0801")
    text = text.replace("b0731", "b0801")
    return text


def main() -> None:
    src_build = ROOT / "build-0731-from-csv.py"
    dst_build = ROOT / "build-0801-from-csv.py"
    text = swap_dates(src_build.read_text(encoding="utf-8"))

    text = re.sub(r"RAW_PROPS = \[.*?\]", RAW_PROPS, text, count=1, flags=re.S)
    text = re.sub(r"ALIASES = \{.*?\}", ALIASES, text, count=1, flags=re.S)

    # Clear day-specific locks / probable overrides that may not apply.
    text = re.sub(
        r"PROBABLE_OVERRIDES = \{.*?\}",
        "PROBABLE_OVERRIDES = {}",
        text,
        count=1,
        flags=re.S,
    )
    # Keep PITCHER_HAND if present; rebuild will fill from CSVs mostly.
    text = text.replace("ATL_NYM_DH_SPECS = {}", "ATL_NYM_DH_SPECS = {}")

    # Drop 7/31 Garcia straight lock / fav3 lock if present.
    text = re.sub(
        r"\n# 7/31 judgment:.*?(?=\n# 6/22 judgment:)",
        "\n",
        text,
        count=1,
        flags=re.S,
    )

    dst_build.write_text(text, encoding="utf-8")
    print("wrote", dst_build.name)

    # Patch
    src_patch = ROOT / "patch-0731-preview.py"
    dst_patch = ROOT / "patch-0801-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    # Remove day-specific straight / fav locks from 7/31.
    ptext = re.sub(
        r"\n# 7/31 judgment:.*?(?=\n# 6/22 judgment:)",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 7/31 Fav3:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    # Archive previous = 7/31
    ptext = ptext.replace(
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-01.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-31.html"',
    )
    # Fix botched swaps if any
    ptext = ptext.replace("2026-08-01.html", "2026-07-31.html") if "ARCHIVE" in ptext else ptext
    # Careful: SHEET_DATE should stay 08-01; archive hrefs to 07-31
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-31.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-07-31.html"',
        ptext,
    )
    # Hero line
    ptext = ptext.replace(
        '"<p>Saturday, August 1, 2026 — Worst Pickz HR cheat sheet"',
        '"<p>Saturday, August 1, 2026 — Worst Pickz HR cheat sheet"',
    )
    # Manifest labels
    ptext = ptext.replace("July 31, 2026 — current slate", "August 1, 2026 — current slate")
    ptext = ptext.replace('href": "archive/2026-08-01.html"', 'href": "archive/2026-07-31.html"')
    ptext = ptext.replace("archive/2026-08-01.html", "archive/2026-07-31.html")

    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    # Verify summary
    src_v = ROOT / "verify-summary-0731.py"
    dst_v = ROOT / "verify-summary-0801.py"
    dst_v.write_text(swap_dates(src_v.read_text(encoding="utf-8")), encoding="utf-8")
    print("wrote", dst_v.name)

    # Audit
    src_a = ROOT / "_audit_0731_final.py"
    dst_a = ROOT / "_audit_0801_final.py"
    atext = swap_dates(src_a.read_text(encoding="utf-8"))
    atext = atext.replace("Friday, August 1, 2026", "Saturday, August 1, 2026")
    atext = atext.replace('if "Thursday, July 30, 2026"', 'if "Friday, July 31, 2026"')
    atext = atext.replace(
        'if "Friday, July 31, 2026" in html or "Wednesday, July" in html:',
        'if "Friday, July 31, 2026 — Worst" in html or "Thursday, July" in html:',
    )
    # Fix archive checks
    atext = atext.replace("2026-07-30.html", "2026-07-31.html")
    atext = atext.replace('content="2026-07-30"', 'content="2026-07-31"')
    atext = atext.replace("7/30 archive", "7/31 archive")
    atext = atext.replace("7/30 still labeled current", "7/31 still labeled current")
    atext = atext.replace("July 30, 2026 — current slate", "July 31, 2026 — current slate")
    dst_a.write_text(atext, encoding="utf-8")
    print("wrote", dst_a.name)


if __name__ == "__main__":
    main()
