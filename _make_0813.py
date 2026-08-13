#!/usr/bin/env python3
"""Scaffold 2026-08-13 build/patch/verify from 8/12 templates."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Griffin Conine⭐",
    "Owen Caissie",
    "Brandon Lowe💎",
    "Jacob Gonzalez",
    "Endy Rodriguez⭐",
    "Eduardo Valencia",
    "James Outman",
    "Dillon Dingler",
    "Jo Adell",
    "Rhys Hoskins💎",
    "Nathaniel Lowe💎",
    "Angel Genao",
    "Chase DeLauter",
    "Ben Rice⭐",
    "Trent Grisham",
    "Spencer Jones💎",
    "Heliot Ramos",
    "Munetaka Murakami⭐",
    "Miguel Vargas💎",
    "Tyler Stephenson💎",
    "JJ Bleday",
    "Kazuma Okamoto",
    "Alejandro Kirk",
    "Ernie Clement",
    "Jarren Duran💎",
    "Wilyer Abreu",
    "Brady House",
    "Dylan Crews💎",
    "Abimelec Ortiz",
    "Daylen Lile",
    "Keibert Ruiz",
    "Kody Clemens⭐",
    "Josh Bell",
    "Royce Lewis",
    "Victor Caratini",
    "Bryce Harper⭐",
    "Kyle Schwarber⭐",
    "Derek Hill",
    "Bryson Stott",
    "Bryan De La Cruz",
    "Moises Ballesteros",
    "Alex Bregman",
    "Miguel Amaya",
    "Mike Trout",
    "Travis d'Arnaud",
    "Vaughn Grissom",
    "Ezequiel Duran",
    "Joc Pederson💎",
    "Corey Seager",
    "Teoscar Hernandez",
    "Mookie Betts",
    "Andy Pages",
    "Endy Hernandez",
    "Kyle Tucker",
    "Jackson Chourio⭐",
    "William Contreras💎",
    "Brice Turang⭐",
    "Jake Bauers",
    "Garrett Mitchell",
]"""

ALIASES = """ALIASES = {
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Pete Crow": "Pete Crow-Armstrong",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Eduardo Valencia": "Eduardo Valencia",
    "Edouardo Valencia": "Eduardo Valencia",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Vladimir Guerrero Jr.": "Vladimir Guerrero Jr.",
    "Moises Ballesteros": "Moises Ballesteros",
    "Moisés Ballesteros": "Moises Ballesteros",
    "Munetaka Murakami": "Munetaka Murakami",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "William Contreras": "William Contreras",
    "Willson Contreras": "Willson Contreras",
    # LAD lists "E. Hernandez R" at third; the only Hernandez on that roster is
    # Enrique (Kike). The prop sheet wrote "Endy", which collides with Endy
    # Rodriguez on PIT, so pin it explicitly.
    "Endy Hernandez": "Enrique Hernandez",
    "Enrique Hernandez": "Enrique Hernandez",
    "Kike Hernandez": "Enrique Hernandez",
    "Travis d'Arnaud": "Travis d'Arnaud",
    "Travis dArnaud": "Travis d'Arnaud",
    "JJ Bleday": "JJ Bleday",
    "J.J. Bleday": "JJ Bleday",
    "Jacob Gonzalez": "Jacob Gonzalez",
    "Nathaniel Lowe": "Nathaniel Lowe",
    "Brandon Lowe": "Brandon Lowe",
    "Chase DeLauter": "Chase DeLauter",
    "Abimelec Ortiz": "Abimelec Ortiz",
    "Walbert Urena": "Walbert Urena",
    "Jacob deGrom": "Jacob deGrom",
}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/13 LHP
    "Parker Messick": "L",
    "Max Fried": "L",
    "Andrew Abbott": "L",
    "Payton Tolle": "L",
    "Shane Drohan": "L",
    # 8/13 RHP
    "Keider Montero": "R",
    "Braxton Ashcraft": "R",
    "Tyler Phillips": "R",
    "Logan Gilbert": "R",
    "Davis Martin": "R",
    "Max Scherzer": "R",
    "Kevin Gausman": "R",
    "Cade Cavalli": "R",
    "Aaron Nola": "R",
    "Taj Bradley": "R",
    "Jacob deGrom": "R",
    "Walbert Urena": "R",
    "Roki Sasaki": "R",
}"""


# Longest-match-first so "2026-08-12" is tokenized before the bare "08-12" rule
# can chew into the ISO string it just produced.
_DATE_SWAPS: list[tuple[str, str]] = [
    ("2026-08-12", "2026-08-13"),
    ("2026-08-11", "2026-08-12"),
    ("Wednesday, August 12, 2026", "Thursday, August 13, 2026"),
    ("Wednesday, August 12", "Thursday, August 13"),
    ("August 12, 2026", "August 13, 2026"),
    ("August 12", "August 13"),
    ("Tuesday, August 11, 2026", "Wednesday, August 12, 2026"),
    ("Tuesday, August 11", "Wednesday, August 12"),
    ("August 11, 2026", "August 12, 2026"),
    ("August 11", "August 12"),
    ("08-12", "08-13"),
    ("08-11", "08-12"),
    ("0812", "0813"),
    ("0811", "0812"),
    ("8/12", "8/13"),
    ("8/11", "8/12"),
]


def swap_dates(text: str) -> str:
    for idx, (needle, _) in enumerate(_DATE_SWAPS):
        text = text.replace(needle, f"\x00{idx}\x00")
    for idx, (_, sub) in enumerate(_DATE_SWAPS):
        text = text.replace(f"\x00{idx}\x00", sub)
    return text


def main() -> None:
    # ---- build script ----
    text = swap_dates((ROOT / "build-0812-from-csv.py").read_text(encoding="utf-8"))
    text = re.sub(r"RAW_PROPS = \[.*?\n\]", RAW_PROPS, text, count=1, flags=re.S)
    text = re.sub(r"ALIASES = \{.*?\n\}", ALIASES, text, count=1, flags=re.S)
    text = re.sub(
        r"PROBABLE_OVERRIDES = \{.*?\n\}|PROBABLE_OVERRIDES: dict\[str, dict\] = \{\}",
        "PROBABLE_OVERRIDES: dict[str, dict] = {}",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"PITCHER_HAND = \{.*?\n\}", PITCHER_HAND, text, count=1, flags=re.S)
    (ROOT / "build-0813-from-csv.py").write_text(text, encoding="utf-8")
    print("wrote build-0813-from-csv.py")

    # ---- patch script ----
    p = swap_dates((ROOT / "patch-0812-preview.py").read_text(encoding="utf-8"))
    before = len(p)
    p = re.sub(
        r"\n# 8/13 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "straight judgment lock not stripped"
    before = len(p)
    p = re.sub(
        r"\n# 8/13 Goblin judgment:.*?    fav3 = _fav3_lock\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "goblin judgment lock not stripped"
    # The date swap slides every hand-maintained manifest date forward, dropping the
    # day that just became an archive. Re-add it to the ordered list.
    p = p.replace(
        '    for date in [\n        "2026-08-12",\n        "2026-08-10",',
        '    for date in [\n        "2026-08-12",\n        "2026-08-11",\n        "2026-08-10",',
        1,
    )
    assert 'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-12.html"' in p, (
        "archive target should point at the slate being replaced"
    )
    (ROOT / "patch-0813-preview.py").write_text(p, encoding="utf-8")
    print("wrote patch-0813-preview.py")

    # ---- summary verifier ----
    (ROOT / "verify-summary-0813.py").write_text(
        swap_dates((ROOT / "verify-summary-0812.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0813.py")

    # ---- final audit ----
    a = swap_dates((ROOT / "_audit_0812_final.py").read_text(encoding="utf-8"))
    a = a.replace(
        'if "Tuesday, August 13" in html or "Thursday, August 13" in html:',
        'if "Tuesday, August 13" in html or "Wednesday, August 13" in html:',
        1,
    )
    a = a.replace(
        'fail("wrong weekday on August 13 (must be Wednesday)")',
        'fail("wrong weekday on August 13 (must be Thursday)")',
        1,
    )
    a = re.sub(
        r"expected_bum = \{[^}]*\}",
        'expected_bum = {"Max Scherzer", "Aaron Nola"}',
        a,
        count=1,
    )
    a = re.sub(
        r"    for base in \(\n(?:        \"[^\"]+\",\n)+    \):",
        (
            "    for base in (\n"
            '        "Parker Messick",\n'
            '        "Max Fried",\n'
            '        "Andrew Abbott",\n'
            '        "Payton Tolle",\n'
            '        "Shane Drohan",\n'
            "    ):"
        ),
        a,
        count=1,
    )
    # Derive from RAW_PROPS rather than restating it: a hand-edited count silently
    # stops checking the props that were added after it was last touched.
    propcount = len(re.findall(r'^\s+"', RAW_PROPS, flags=re.M))
    a = re.sub(r"PROPCOUNT = \d+", f"PROPCOUNT = {propcount}", a, count=1)
    # Slate size changes day to day; the old audits hardcoded 15 games inline, which
    # then failed every short slate. Keep it a named constant the scaffold updates.
    if "GAMECOUNT" in a:
        a = re.sub(r"GAMECOUNT = \d+", "GAMECOUNT = 9", a, count=1)
    else:
        a = a.replace(f"PROPCOUNT = {propcount}", f"PROPCOUNT = {propcount}\nGAMECOUNT = 9", 1)
        a = re.sub(
            r"if len\(titles\) != \d+:\n            fail\(f\"expected \d+ games, got \{len\(titles\)\}\"\)",
            'if len(titles) != GAMECOUNT:\n            fail(f"expected {GAMECOUNT} games, got {len(titles)}")',
            a,
            count=1,
        )
        a = re.sub(
            r"if len\(metas\) != \d+:\n            fail\(f\"expected \d+ gameMeta, got \{len\(metas\)\}\"\)",
            'if len(metas) != GAMECOUNT:\n            fail(f"expected {GAMECOUNT} gameMeta, got {len(metas)}")',
            a,
            count=1,
        )
    (ROOT / "_audit_0813_final.py").write_text(a, encoding="utf-8")
    print("wrote _audit_0813_final.py")

    # ---- zone backfill ----
    z = swap_dates((ROOT / "_backfill_zones_0812.py").read_text(encoding="utf-8"))
    z = re.sub(
        r"LHP = \{.*?\n\}",
        (
            "LHP = {\n"
            '    "Messick",\n'
            '    "Fried",\n'
            '    "Abbott",\n'
            '    "Tolle",\n'
            '    "Drohan",\n'
            "}"
        ),
        z,
        count=1,
        flags=re.S,
    )
    (ROOT / "_backfill_zones_0813.py").write_text(z, encoding="utf-8")
    print("wrote _backfill_zones_0813.py")

    # ---- ranking helper ----
    (ROOT / "_best_0813.py").write_text(
        swap_dates((ROOT / "_best_0812.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote _best_0813.py")


if __name__ == "__main__":
    main()
