#!/usr/bin/env python3
"""Scaffold 2026-08-04 build/patch/verify from 8/3 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Pete Alonso⭐",
    "Bryce Harper⭐",
    "J.T. Realmuto💎",
    "Dylan Crews",
    "Rhys Hoskins",
    "Tyler Stephenson",
    "Eugenio Suarez",
    "JJ Bleday",
    "Sal Stewart",
    "Carlos Cortes",
    "Tyler Soderstrom",
    "Lawrence Butler",
    "Luis Garcia Jr.",
    "Ben Rice",
    "Heliot Ramos",
    "Ryan McMahon",
    "Austin Wells",
    "Nelson Velazquez💎",
    "Willson Contreras",
    "Miguel Vargas⭐",
    "Colson Montgomery",
    "Ronald Acuna Jr.",
    "Mike Yastrzemski",
    "Matt Olson",
    "Owen Caissie⭐",
    "Griffin Conine⭐",
    "Joe Mack",
    "Jake Bauers⭐",
    "Brandon Lowe⭐",
    "John Rave💎",
    "Salvador Perez",
    "Carter Jensen",
    "Royce Lewis",
    "Corey Seager",
    "Joc Pederson",
    "Willy Adames",
    "Daniel Susac",
    "Michael Conforto",
    "Shohei Ohtani",
    "Freddie Freeman",
    "Daulton Varsho",
    "Taylor Trammell",
    "George Springer",
    "Kazuma Okamoto",
    "Hunter Goodman",
    "Junior Caminero⭐",
    "Victor Mesa Jr.",
    "Cole Young",
    "Hao-Yu Lee",
    "Gleyber Torres",
    "Kevin McGonigle",
    "Tim Tawa",
    "Manny Machado",
    "Jackson Merrill",
    "Ty France",
]"""

ALIASES = """ALIASES = {
    "JT Realmuto": "J.T. Realmuto",
    "J.T Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Hao Yu Lee": "Hao-Yu Lee",
    "Hao-Yu Lee": "Hao-Yu Lee",
    "Tim tawa": "Tim Tawa",
    "Tim Tawa": "Tim Tawa",
    "Nelson Velazquez": "Nelson Velazquez",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Mike Yastrzemski": "Mike Yastrzemski",
    "Daulton Varsho": "Daulton Varsho",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Victor Mesa Jr.": "Victor Mesa Jr.",
    "Kevin McGonigle": "Kevin McGonigle",
    "Carlos Cortes": "Carlos Cortes",
    "Griffin Conine": "Griffin Conine",
    "Owen Caissie": "Owen Caissie",
    "Colson Montgomery": "Colson Montgomery",
    "Daniel Susac": "Daniel Susac",
    "Junior Caminero": "Junior Caminero",
    "Willson Contreras": "Willson Contreras",
    "Eugenio Suarez": "Eugenio Suarez",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-03", "2026-08-04")
    text = text.replace("2026-08-02", "2026-08-03")
    text = text.replace("08-03", "08-04")
    text = text.replace("08-02", "08-03")
    text = text.replace("0803", "0804")
    text = text.replace("0802", "0803")
    text = text.replace("August 3, 2026", "August 4, 2026")
    text = text.replace("Monday, August 3, 2026", "Tuesday, August 4, 2026")
    text = text.replace("Monday, August 3", "Tuesday, August 4")
    text = text.replace("August 3", "August 4")
    text = text.replace("build0803", "build0804")
    text = text.replace("b0803", "b0804")
    return text


def main() -> None:
    src_build = ROOT / "build-0803-from-csv.py"
    dst_build = ROOT / "build-0804-from-csv.py"
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
        r"\n# 8/3 judgment:.*?(?=\n# 6/22 judgment:|\n# Goblin|\ndef )",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"PITCHER_HAND = \{.*?\}",
        "PITCHER_HAND = {}",
        text,
        count=1,
        flags=re.S,
    )
    dst_build.write_text(text, encoding="utf-8")
    print("wrote", dst_build.name)

    src_patch = ROOT / "patch-0803-preview.py"
    dst_patch = ROOT / "patch-0804-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    ptext = re.sub(
        r"\n# 8/3 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/3 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-03.html"',
        ptext,
        count=1,
    )
    ptext = ptext.replace(
        "<p>Tuesday, August 4, 2026 — Worst Pickz HR cheat sheet",
        "<p>Tuesday, August 4, 2026 — Worst Pickz HR cheat sheet",
    )
    ptext = ptext.replace(
        "<p>Monday, August 4, 2026 — Worst Pickz HR cheat sheet",
        "<p>Tuesday, August 4, 2026 — Worst Pickz HR cheat sheet",
    )
    # Manifest: promote 8/3
    ptext = re.sub(
        r'if "2026-08-0[34]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[34]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-03" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-03"] = {\n'
            '            "date": "2026-08-03",\n'
            '            "label": "August 3, 2026",\n'
            '            "href": "archive/2026-08-03.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    src_v = ROOT / "verify-summary-0803.py"
    (ROOT / "verify-summary-0804.py").write_text(
        swap_dates(src_v.read_text(encoding="utf-8")), encoding="utf-8"
    )
    print("wrote verify-summary-0804.py")

    src_a = ROOT / "_audit_0803_final.py"
    atext = swap_dates(src_a.read_text(encoding="utf-8"))
    atext = atext.replace("Tuesday, August 4, 2026", "Tuesday, August 4, 2026")
    atext = atext.replace("Monday, August 4, 2026", "Tuesday, August 4, 2026")
    atext = atext.replace(
        'if "Sunday, August 2, 2026 — Worst" in html:',
        'if "Monday, August 3, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Sunday, August 3" in html or "Tuesday, August 3" in html:',
        'if "Monday, August 4" in html or "Wednesday, August 4" in html:',
    )
    atext = atext.replace("2026-08-02.html", "2026-08-03.html")
    atext = atext.replace('content="2026-08-02"', 'content="2026-08-03"')
    atext = atext.replace("8/2 archive", "8/3 archive")
    atext = atext.replace("8/2 still labeled current", "8/3 still labeled current")
    atext = atext.replace("August 2, 2026 — current slate", "August 3, 2026 — current slate")
    atext = atext.replace("Aaron Nola", "bum_placeholder")
    atext = atext.replace("!= 56", "!= 55")
    atext = atext.replace("expected 56 props", "expected 55 props")
    atext = atext.replace("!= 8", "!= 15")
    atext = atext.replace("expected 8 games", "expected 15 games")
    atext = atext.replace("expected 8 gameMeta", "expected 15 gameMeta")
    (ROOT / "_audit_0804_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0804_final.py")


if __name__ == "__main__":
    main()
