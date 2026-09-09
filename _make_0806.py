#!/usr/bin/env python3
"""Scaffold 2026-08-06 build/patch/verify from 8/5 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Coby Mayo💎",
    "Gunnar Henderson⭐",
    "Pete Alonso",
    "Travis d'Arnaud💎",
    "Josh Lowe",
    "Mike Trout",
    "Eugenio Suarez⭐",
    "Sal Stewart💎",
    "Elly De La Cruz",
    "Tyler Stephenson",
    "Tyler Soderstrom",
    "Jonah Heim",
    "Lawrence Butler",
    "Rhys Hoskins⭐",
    "Patrick Bailey",
    "Jo Adell💎",
    "Luis Torrens",
    "Bo Bichette",
    "Marcus Semien",
    "Jake Bauers⭐",
    "Jackson Chourio",
    "Brice Turang",
    "William Contreras",
    "Andrew Vaughn",
    "Brandon Lowe💎",
    "Esmerlyn Valdez💎",
    "Jacob Gonzalez",
    "Endy Rodriguez",
    "Pete Crow-Armstrong⭐",
    "Seiya Suzuki",
    "Tyrone Taylor",
    "Ernie Clement",
    "Kazuma Okamoto",
    "Vladimir Guerrero Jr.",
    "Randy Arozarena",
    "Cal Raleigh",
    "Julio Rodriguez",
    "Spencer Torkelson⭐",
    "Dillon Dingler💎",
    "Hao-Yu Lee💎",
    "Derek Hill💎",
    "J.T. Realmuto⭐",
    "Bryce Harper",
    "Bryson Stott",
    "Kyle Schwarber",
    "Luis Arraez",
    "Daylen Lile",
    "Dylan Crews",
    "Wilyer Abreu⭐",
    "Willson Contreras⭐",
    "Munetaka Murakami💎",
    "Miguel Vargas",
    "Mike Yastrzemski💎",
    "Matt Olson",
    "Drake Baldwin💎",
    "Ronald Acuna Jr.💎",
    "Heriberto Hernandez",
    "Javier Sanoja",
    "Salvador Perez",
    "Bobby Witt Jr.",
    "Jac Caglianone",
    "Tyler Tolbert",
    "Josh Bell💎",
    "Royce Lewis",
    "Corbin Carroll",
    "Geraldo Perdomo",
    "Manny Machado",
    "Freddy Fermin",
    "Sung Mun Song",
]"""

ALIASES = """ALIASES = {
    "JT Realmuto": "J.T. Realmuto",
    "J.T Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Bobby Witt Jr.": "Bobby Witt Jr.",
    "Bobby Witt": "Bobby Witt Jr.",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Vlad Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Elly De La Cruz": "Elly De La Cruz",
    "Travis d'Arnaud": "Travis d'Arnaud",
    "Travis dArnaud": "Travis d'Arnaud",
    "Willson Contreras": "Willson Contreras",
    "William Contreras": "William Contreras",
    "Will Contreras": "William Contreras",
    "Eugenio Suarez": "Eugenio Suarez",
    "Eugenio Suárez": "Eugenio Suarez",
    "Gunnar Henderson": "Gunnar Henderson",
    "Sal Stewart": "Sal Stewart",
    "Jo Adell": "Jo Adell",
    "Brandon Lowe": "Brandon Lowe",
    "Esmerlyn Valdez": "Esmerlyn Valdez",
    "Dillon Dingler": "Dillon Dingler",
    "Hao-Yu Lee": "Hao-Yu Lee",
    "Hao Yu Lee": "Hao-Yu Lee",
    "Derek Hill": "Derek Hill",
    "Munetaka Murakami": "Munetaka Murakami",
    "Mike Yastrzemski": "Mike Yastrzemski",
    "Drake Baldwin": "Drake Baldwin",
    "Josh Bell": "Josh Bell",
    "Coby Mayo": "Coby Mayo",
    "Jake Bauers": "Jake Bauers",
    "Rhys Hoskins": "Rhys Hoskins",
    "Spencer Torkelson": "Spencer Torkelson",
    "Wilyer Abreu": "Wilyer Abreu",
    "Luis Torrens": "Luis Torrens",
    "Endy Rodriguez": "Endy Rodriguez",
    "Tyler Tolbert": "Tyler Tolbert",
    "Sung Mun Song": "Sung Mun Song",
    "Jacob Gonzalez": "Jacob Gonzalez",
    "Javier Sanoja": "Javier Sanoja",
    "Heriberto Hernandez": "Heriberto Hernandez",
    "Freddy Fermin": "Freddy Fermin",
    "Geraldo Perdomo": "Geraldo Perdomo",
    "Tyrone Taylor": "Tyrone Taylor",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Ernie Clement": "Ernie Clement",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/6 LHP
    "Andrew Abbott": "L",
    "Foster Griffin": "L",
    "David Peterson": "L",
    "Framber Valdez": "L",
    "Cristopher Sanchez": "L",
    "Ranger Suarez": "L",
    "Martin Perez": "L",
    "Kohl Drake": "L",
    # 8/6 RHP
    "Ryan Johnson": "R",
    "Brandon Young": "R",
    "Mason Barnett": "R",
    "Nolan McLean": "R",
    "Braxton Ashcraft": "R",
    "Dustin May": "R",
    "Dylan Cease": "R",
    "Bryce Miller": "R",
    "Miles Mikolas": "R",
    "Luis Castillo": "R",
    "Janson Junk": "R",
    "Bailey Ober": "R",
    "Michael Wacha": "R",
    "Walker Buehler": "R",
}"""


def swap_dates(text: str) -> str:
    text = text.replace("2026-08-05", "2026-08-06")
    text = text.replace("2026-08-04", "2026-08-05")
    text = text.replace("08-05", "08-06")
    text = text.replace("08-04", "08-05")
    text = text.replace("0805", "0806")
    text = text.replace("0804", "0805")
    text = text.replace("Wednesday, August 5, 2026", "Thursday, August 6, 2026")
    text = text.replace("Wednesday, August 5", "Thursday, August 6")
    text = text.replace("August 5, 2026", "August 6, 2026")
    text = text.replace("August 5", "August 6")
    text = text.replace("Tuesday, August 6", "Thursday, August 6")  # fix bad weekday swaps
    return text


def main() -> None:
    src_build = ROOT / "build-0805-from-csv.py"
    dst_build = ROOT / "build-0806-from-csv.py"
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

    src_patch = ROOT / "patch-0805-preview.py"
    dst_patch = ROOT / "patch-0806-preview.py"
    ptext = swap_dates(src_patch.read_text(encoding="utf-8"))
    # Drop 8/5 judgment locks (auto-rank first; re-lock after _best_0806)
    ptext = re.sub(
        r"\n# 8/5 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r"\n# 8/5 Goblin judgment:.*?fav3 = _fav3_lock\n",
        "\n",
        ptext,
        count=1,
        flags=re.S,
    )
    ptext = re.sub(
        r'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "20\d{2}-\d{2}-\d{2}\.html"',
        'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-05.html"',
        ptext,
        count=1,
    )
    ptext = ptext.replace(
        "<p>Thursday, August 6, 2026 — Worst Pickz HR cheat sheet",
        "<p>Thursday, August 6, 2026 — Worst Pickz HR cheat sheet",
    )
    ptext = ptext.replace(
        "<p>Wednesday, August 6, 2026 — Worst Pickz HR cheat sheet",
        "<p>Thursday, August 6, 2026 — Worst Pickz HR cheat sheet",
    )
    # Manifest: archive prior day as 08-05
    ptext = re.sub(
        r'if "2026-08-0[56]" in old or ARCHIVE_PREVIOUS\.is_file\(\):\s*'
        r'old\["2026-08-0[56]"\] = \{[^}]+\}\s*',
        (
            'if "2026-08-05" in old or ARCHIVE_PREVIOUS.is_file():\n'
            '        old["2026-08-05"] = {\n'
            '            "date": "2026-08-05",\n'
            '            "label": "August 5, 2026",\n'
            '            "href": "archive/2026-08-05.html",\n'
            "        }\n    "
        ),
        ptext,
        count=1,
        flags=re.S,
    )
    if '"2026-08-06",\n        "2026-08-05"' not in ptext:
        ptext = ptext.replace(
            '    for date in [\n        "2026-08-05",',
            '    for date in [\n        "2026-08-06",\n        "2026-08-05",',
            1,
        )
    dst_patch.write_text(ptext, encoding="utf-8")
    print("wrote", dst_patch.name)

    src_v = ROOT / "verify-summary-0805.py"
    (ROOT / "verify-summary-0806.py").write_text(
        swap_dates(src_v.read_text(encoding="utf-8")), encoding="utf-8"
    )
    print("wrote verify-summary-0806.py")

    src_a = ROOT / "_audit_0805_final.py"
    atext = swap_dates(src_a.read_text(encoding="utf-8"))
    atext = atext.replace("Wednesday, August 6, 2026", "Thursday, August 6, 2026")
    atext = atext.replace(
        'if "Tuesday, August 5, 2026 — Worst" in html:',
        'if "Wednesday, August 5, 2026 — Worst" in html:',
    )
    atext = atext.replace(
        'if "Tuesday, August 6" in html or "Thursday, August 6" in html:',
        'if "Tuesday, August 6" in html or "Wednesday, August 6" in html:',
    )
    atext = atext.replace(
        'fail("wrong weekday on August 6 (must be Wednesday)")',
        'fail("wrong weekday on August 6 (must be Thursday)")',
    )
    # If swap left "must be Thursday" check that fails on Thursday presence — fix:
    atext = atext.replace(
        'if "Tuesday, August 6" in html or "Wednesday, August 6" in html:\n'
        '        fail("wrong weekday on August 6 (must be Thursday)")',
        'if "Tuesday, August 6" in html or "Wednesday, August 6" in html:\n'
        '        fail("wrong weekday on August 6 (must be Thursday)")',
    )
    atext = atext.replace("!= 102", "!= 69")
    atext = atext.replace("expected 102 props", "expected 69 props")
    # games: 11 not 15
    atext = atext.replace("!= 15", "!= 11")
    atext = atext.replace("expected 15 games", "expected 11 games")
    atext = atext.replace("expected 15 gameMeta", "expected 11 gameMeta")
    atext = atext.replace(
        'expected_bum = {"Jameson Taillon", "Andrew Painter", "Bryce Elder", "Jake Irvin", "Dean Kremer", "Tomoyuki Sugano"}',
        'expected_bum = {"Kohl Drake", "Miles Mikolas", "Ryan Johnson"}',
    )
    atext = atext.replace(
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
        """    for must_l in (
        "Andrew Abbott (L",
        "Foster Griffin (L",
        "David Peterson (L",
        "Framber Valdez (L",
        "Cristopher Sanchez (L",
        "Ranger Suarez (L",
        "Martin Perez (L",
        "Kohl Drake (L",
    ):""",
    )
    (ROOT / "_audit_0806_final.py").write_text(atext, encoding="utf-8")
    print("wrote _audit_0806_final.py")

    zsrc = ROOT / "_backfill_zones_0805.py"
    ztext = swap_dates(zsrc.read_text(encoding="utf-8"))
    ztext = ztext.replace(
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
    )
    (ROOT / "_backfill_zones_0806.py").write_text(ztext, encoding="utf-8")
    print("wrote _backfill_zones_0806.py")

    best = (ROOT / "_best_0805.py").read_text(encoding="utf-8")
    (ROOT / "_best_0806.py").write_text(swap_dates(best), encoding="utf-8")
    print("wrote _best_0806.py")


if __name__ == "__main__":
    main()
