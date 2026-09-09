#!/usr/bin/env python3
"""Scaffold 2026-08-03 build/patch/verify from 8/2 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Bryce Harper",
    "Kyle Schwarber",
    "Brandon Marsh",
    "Derek Hill",
    "J.T. Realmuto",
    "CJ Abrams",
    "Andres Chaparro💎",
    "Harry Ford",
    "Dylan Crews",
    "Jazz Chisholm Jr.",
    "Luis Garcia Jr.💎",
    "Ryan McMahon",
    "Spencer Jones⭐",
    "Ben Rice",
    "Alec Burleson",
    "Jordan Walker💎",
    "Jake Bauers⭐",
    "Andrew Vaughn",
    "Joey Ortiz",
    "Brandon Lowe",
    "Bryan Reynolds",
    "Spencer Horwitz⭐",
    "Esmerlyn Valdez",
    "Corey Seager",
    "Wyatt Langford",
    "Osleivis Basabe",
    "Bryce Eldridge💎",
    "Grant McCray💎",
    "Rafael Devers",
    "Drew Gilbert",
    "Michael Conforto",
    "Dansby Swanson",
    "Pedro Ramirez",
    "Alex Bregman",
    "Nico Hoerner",
    "Enrique Hernandez⭐",
    "Shohei Ohtani",
    "Kyle Tucker💎",
    "Max Muncy",
    "Dalton Rushing",
    "Jeremy Pena⭐",
    "Taylor Trammell",
    "George Springer⭐",
    "Kazuma Okamoto💎",
    "Vladimir Guerrero Jr.⭐",
    "Willi Castro",
    "Cole Carrigg",
    "Hunter Goodman",
    "Junior Caminero💎",
    "Nick Fortes",
    "Victor Mesa Jr.",
    "Corbin Carroll",
    "Geraldo Perdomo💎",
    "Ty France💎",
    "Jackson Merrill",
    "Manny Machado💎",
]"""

ALIASES = """ALIASES = {
    "J.T Realmuto": "J.T. Realmuto",
    "JT Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Andres Chapparo": "Andres Chaparro",
    "Andres Chaparro": "Andres Chaparro",
    "A. Chaparro": "Andres Chaparro",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Jazz Chisholm": "Jazz Chisholm Jr.",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Luis García Jr.": "Luis Garcia Jr.",
    "Osleivis Basabe": "Osleivis Basabe",
    "Grant McCray": "Grant McCray",
    "Pedro Ramirez": "Pedro Ramirez",
    "Enrique Hernandez": "Enrique Hernandez",
    "Kike Hernandez": "Enrique Hernandez",
    "Jeremy Pena": "Jeremy Pena",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Vlad Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Geraldo Perdomo": "Geraldo Perdomo",
    "Cole Carrigg": "Cole Carrigg",
    "Bryce Eldridge": "Bryce Eldridge",
    "Kyle Tucker": "Kyle Tucker",
    "Junior Caminero": "Junior Caminero",
    "Spencer Horwitz": "Spencer Horwitz",
    "Spencer Jones": "Spencer Jones",
    "Jordan Walker": "Jordan Walker",
    "Jake Bauers": "Jake Bauers",
    "George Springer": "George Springer",
    "Ty France": "Ty France",
    "Manny Machado": "Manny Machado",
    "Michael Conforto": "Michael Conforto",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-02", "2026-08-03")
    text = text.replace("2026-08-01", "2026-08-02")
    text = text.replace("08-02", "08-03")
    text = text.replace("08-01", "08-02")
    text = text.replace("0802", "0803")
    text = text.replace("0801", "0802")
    text = text.replace("August 2, 2026", "August 3, 2026")
    text = text.replace("Sunday, August 2, 2026", "Monday, August 3, 2026")
    text = text.replace("Sunday, August 2", "Monday, August 3")
    text = text.replace("August 2", "August 3")
    text = text.replace("build0802", "build0803")
    text = text.replace("b0802", "b0803")
    return text


def main() -> None:
    src_build = ROOT / "build-0802-from-csv.py"
    dst_build = ROOT / "build-0803-from-csv.py"
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
    # Clear prior-day judgment locks.
    text = re.sub(
        r"\n# 8/2 judgment:.*?(?=\n# 6/22 judgment:|\n# Goblin|\ndef )",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    # Fresh pitcher hands for 8/3 — filled after inspect.
    text = re.sub(
        r"PITCHER_HAND = \{.*?\}",
        "PITCHER_HAND = {}",
        text,
        count=1,
        flags=re.S,
    )
    dst_build.write_text(text, encoding="utf-8")
    print("wrote", dst_build.name)

    src_patch = ROOT / "patch-0802-preview.py"
    dst_patch = ROOT / "patch-0803-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    # Remove 8/2 judgment locks.
    ptext = re.sub(
        r"\n# 8/2 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/2 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-02.html"',
        ptext,
        count=1,
    )
    ptext = ptext.replace(
        "<p>Sunday, August 3, 2026 — Worst Pickz HR cheat sheet",
        "<p>Monday, August 3, 2026 — Worst Pickz HR cheat sheet",
    )
    ptext = ptext.replace(
        "<p>Saturday, August 3, 2026 — Worst Pickz HR cheat sheet",
        "<p>Monday, August 3, 2026 — Worst Pickz HR cheat sheet",
    )
    # Fix manifest promote block for prior day 8/2.
    ptext = re.sub(
        r'if "2026-08-0[23]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[23]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-02" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-02"] = {\n'
            '            "date": "2026-08-02",\n'
            '            "label": "August 2, 2026",\n'
            '            "href": "archive/2026-08-02.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    src_v = ROOT / "verify-summary-0802.py"
    dst_v = ROOT / "verify-summary-0803.py"
    dst_v.write_text(swap_dates(src_v.read_text(encoding="utf-8")), encoding="utf-8")
    print("wrote", dst_v.name)

    src_a = ROOT / "_audit_0802_final.py"
    dst_a = ROOT / "_audit_0803_final.py"
    atext = swap_dates(src_a.read_text(encoding="utf-8"))
    atext = atext.replace("Sunday, August 3, 2026", "Monday, August 3, 2026")
    atext = atext.replace(
        'if "Saturday, August 1, 2026 — Worst" in html or "Friday, July" in html:',
        'if "Sunday, August 2, 2026 — Worst" in html or "Saturday, August" in html:',
    )
    atext = atext.replace("2026-08-01.html", "2026-08-02.html")
    atext = atext.replace('content="2026-08-01"', 'content="2026-08-02"')
    atext = atext.replace("8/1 archive", "8/2 archive")
    atext = atext.replace("8/1 still labeled current", "8/2 still labeled current")
    atext = atext.replace("August 1, 2026 — current slate", "August 2, 2026 — current slate")
    # Prop count will be ~56 — update after build.
    atext = atext.replace("!= 90", "!= 56")
    atext = atext.replace("expected 90 props", "expected 56 props")
    # Games: 8 tonight
    atext = atext.replace("!= 15", "!= 8")
    atext = atext.replace("expected 15 games", "expected 8 games")
    atext = atext.replace("expected 15 gameMeta", "expected 8 gameMeta")
    # Bum check — keep flexible
    atext = atext.replace("Max Scherzer", "bum_placeholder")
    dst_a.write_text(atext, encoding="utf-8")
    print("wrote", dst_a.name)


if __name__ == "__main__":
    main()
