#!/usr/bin/env python3
"""Scaffold 2026-08-02 build/patch/verify from 8/1 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Pete Alonso⭐",
    "Coby Mayo",
    "Christian Encarnacion-Strand",
    "Bryce Harper",
    "Bryson Stott",
    "J.T. Realmuto",
    "Derek Hill",
    "James Wood",
    "CJ Abrams",
    "Luis Garcia Jr.",
    "Jacob Young",
    "Ronald Acuna Jr.⭐",
    "Matt Olson⭐",
    "Austin Riley",
    "Drake Baldwin",
    "Kazuma Okamoto",
    "Vladimir Guerrero Jr.",
    "Jimmy Crooks💎",
    "Alec Burleson⭐",
    "Ryan Vilade💎",
    "Jonathan Aranda",
    "Munetaka Murakami⭐",
    "Randal Grichuk💎",
    "Miguel Vargas⭐",
    "Sam Antonacci",
    "Griffin Conine⭐",
    "Kyle Stowers",
    "Owen Caissie",
    "Otto Lopez",
    "Francisco Alvarez⭐",
    "Tyrone Taylor💎",
    "Brett Baty💎",
    "Patrick Bailey💎",
    "Rhys Hoskins",
    "Chase DeLauter",
    "Kyle Manzardo⭐",
    "Max Kepler",
    "Corbin Carroll⭐",
    "Ildemaro Vargas",
    "Elly De La Cruz",
    "JJ Bleday⭐",
    "Sal Stewart",
    "Eugenio Suarez",
    "Esmerlyn Valdez⭐",
    "Bryan Reynolds💎",
    "Endy Rodriguez",
    "Brandon Lowe⭐",
    "Taylor Trammell⭐",
    "Jeremy Pena",
    "Yordan Alvarez⭐",
    "Corey Seager⭐",
    "Wyatt Langford",
    "Jake Burger",
    "Pete Crow-Armstrong⭐",
    "Miguel Amaya",
    "Ryan McMahon💎",
    "Spencer Jones💎",
    "Trent Grisham⭐",
    "Willi Castro",
    "Brenton Doyle",
    "Lane Thomas",
    "Salvador Perez⭐",
    "John Rave",
    "Vaughn Grissom💎",
    "Jorge Soler",
    "Zach Neto",
    "Garrett Mitchell",
    "Andrew Vaughn💎",
    "Jake Bauers⭐",
    "Bo Naylor",
    "Nick Kurtz",
    "Lawrence Butler",
    "James Outman",
    "Hao-Yu Lee",
    "Mitch Garver⭐",
    "Randy Arozarena⭐",
    "Dominic Canzone",
    "Cole Young",
    "Luke Keaschall",
    "Kody Clemens",
    "Manny Machado⭐",
    "Ty France💎",
    "Bryce Eldridge",
    "Enrique Hernandez",
    "Freddie Freeman⭐",
    "Dalton Rushing⭐",
    "Shohei Ohtani",
    "Andy Pages",
    "Wilyer Abreu",
    "Willson Contreras",
]"""

ALIASES = """ALIASES = {
    "J.T Realmuto": "J.T. Realmuto",
    "JT Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "PCA": "Pete Crow-Armstrong",
    "Hao Yu Lee": "Hao-Yu Lee",
    "Hao-Yu Lee": "Hao-Yu Lee",
    "Hao-Yu-Lee": "Hao-Yu Lee",
    "Christian Encarnacion Strand": "Christian Encarnacion-Strand",
    "Christian Encarnacion-Strand": "Christian Encarnacion-Strand",
    "CES": "Christian Encarnacion-Strand",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Luis García Jr.": "Luis Garcia Jr.",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Vlad Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Jeremy Pena": "Jeremy Pena",
    "Enrique Hernandez": "Enrique Hernandez",
    "Kike Hernandez": "Enrique Hernandez",
    "Garret Mitchell": "Garrett Mitchell",
    "Garrett Mitchell": "Garrett Mitchell",
    "Randal Grichuk": "Randal Grichuk",
    "Esmerlyn Valdez": "Esmerlyn Valdez",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Munetaka Murakami": "Munetaka Murakami",
    "Griffin Conine": "Griffin Conine",
    "Sam Antonacci": "Sam Antonacci",
    "Ryan Vilade": "Ryan Vilade",
    "Vaughn Grissom": "Vaughn Grissom",
    "Mitch Garver": "Mitch Garver",
    "Dalton Rushing": "Dalton Rushing",
    "Wilyer Abreu": "Wilyer Abreu",
    "Willson Contreras": "Willson Contreras",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-01", "2026-08-02")
    text = text.replace("2026-07-31", "2026-08-01")
    text = text.replace("08-01", "08-02")
    text = text.replace("07-31", "08-01")
    text = text.replace("0801", "0802")
    text = text.replace("0731", "0801")
    text = text.replace("August 1, 2026", "August 2, 2026")
    text = text.replace("Saturday, August 1, 2026", "Sunday, August 2, 2026")
    text = text.replace("Saturday, August 1", "Sunday, August 2")
    text = text.replace("August 1", "August 2")
    text = text.replace("build0801", "build0802")
    text = text.replace("b0801", "b0802")
    return text


def main() -> None:
    src_build = ROOT / "build-0801-from-csv.py"
    dst_build = ROOT / "build-0802-from-csv.py"
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
    text = text.replace("ATL_NYM_DH_SPECS = {}", "ATL_NYM_DH_SPECS = {}")

    # Drop prior-day judgment locks.
    text = re.sub(
        r"\n# 8/1 judgment:.*?(?=\n# 6/22 judgment:)",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\n# 7/31 judgment:.*?(?=\n# 6/22 judgment:)",
        "\n",
        text,
        count=1,
        flags=re.S,
    )

    dst_build.write_text(text, encoding="utf-8")
    print("wrote", dst_build.name)

    src_patch = ROOT / "patch-0801-preview.py"
    dst_patch = ROOT / "patch-0802-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    ptext = re.sub(
        r"\n# 8/1 judgment:.*?(?=\n# 6/22 judgment:)",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/1 Fav3:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
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

    # Archive previous slate = 8/1
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-01.html"',
        ptext,
        count=1,
    )
    ptext = ptext.replace("August 1, 2026 — current slate", "August 2, 2026 — current slate")
    ptext = ptext.replace("July 31, 2026 — current slate", "August 1, 2026 — current slate")
    ptext = ptext.replace("archive/2026-08-02.html", "archive/2026-08-01.html")
    # undo over-swap of sheet date in archive path checks if needed
    ptext = ptext.replace(
        'content="2026-08-02"',
        'content="2026-08-02"',
    )

    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    src_v = ROOT / "verify-summary-0801.py"
    dst_v = ROOT / "verify-summary-0802.py"
    dst_v.write_text(swap_dates(src_v.read_text(encoding="utf-8")), encoding="utf-8")
    print("wrote", dst_v.name)

    src_a = ROOT / "_audit_0801_final.py"
    dst_a = ROOT / "_audit_0802_final.py"
    atext = swap_dates(src_a.read_text(encoding="utf-8"))
    atext = atext.replace("Saturday, August 2, 2026", "Sunday, August 2, 2026")
    atext = atext.replace(
        'if "Friday, July 31, 2026 — Worst" in html or "Thursday, July" in html:',
        'if "Saturday, August 1, 2026 — Worst" in html or "Friday, July" in html:',
    )
    atext = atext.replace(
        'if "Saturday, August 1, 2026 — Worst" in html',
        'if "Saturday, August 1, 2026 — Worst" in html',
    )
    # Prior archive checks should point at 8/1
    atext = atext.replace("2026-07-31.html", "2026-08-01.html")
    atext = atext.replace('content="2026-07-31"', 'content="2026-08-01"')
    atext = atext.replace("7/31 archive", "8/1 archive")
    atext = atext.replace("7/31 still labeled current", "8/1 still labeled current")
    atext = atext.replace("July 31, 2026 — current slate", "August 1, 2026 — current slate")
    atext = atext.replace("August 1, 2026 — current slate", "August 1, 2026 — current slate")
    dst_a.write_text(atext, encoding="utf-8")
    print("wrote", dst_a.name)


if __name__ == "__main__":
    main()
