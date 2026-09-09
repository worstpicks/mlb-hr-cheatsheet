#!/usr/bin/env python3
"""Scaffold the 8/16 build / patch / audit / backfill scripts from the 8/15 set.

Run before the slate build. This regenerates patch-0816-preview.py from the 8/15
template, so run it BEFORE locking straights and Goblin legs.

Unlike the 8/15 scaffold this also re-points the deep audit's USER_PROPS /
RESOLVED / EXPECTED_BUMS tables, which previously inherited the prior slate and
had to be fixed by hand afterwards.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RAW_PROPS = """RAW_PROPS = [
    "Yandy Diaz",
    "Ryan Vilade",
    "Jorge Mateo",
    "Pete Alonso⭐",
    "Christian Encarnacion-Strand",
    "Coby Mayo",
    "Gunnar Henderson",
    "Leody Taveras",
    "Bryan Reynolds",
    "Brandon Lowe⭐",
    "Wilyer Abreu⭐",
    "Jarren Duran",
    "Masataka Yoshida",
    "Matt Olson",
    "Ronald Acuna Jr.",
    "Austin Riley💎",
    "Corbin Carroll",
    "Tim Tawa",
    "Lars Nootbaar",
    "Kazuma Okamoto",
    "Trent Grisham",
    "Jazz Chisholm Jr.💎",
    "Spencer Jones",
    "Luis Garcia Jr.",
    "Ben Rice",
    "Brett Baty",
    "Francisco Lindor",
    "Bo Bichette",
    "Abimelec Ortiz",
    "Dylan Crews",
    "Spencer Torkelson",
    "Munetaka Murakami",
    "Randal Grichuk",
    "Rhys Hoskins",
    "Angel Genao",
    "Jackson Merrill",
    "Manny Machado",
    "Fernando Tatis Jr.",
    "Xander Bogaerts",
    "Ty France",
    "Matt McLain",
    "Tyler Stephenson",
    "Agustin Ramirez💎",
    "Griffin Conine",
    "Kody Clemens",
    "Josh Bell",
    "Royce Lewis",
    "Kyle Schwarber",
    "J.T. Realmuto",
    "Bryson Stott",
    "Alex Bregman💎",
    "Miguel Amaya",
    "Pete Crow-Armstrong",
    "Jung Hoo Lee",
    "Bryce Eldridge",
    "Mickey Moniak💎",
    "Willi Castro",
    "Hunter Goodman",
    "Zac Veen",
    "Tyler Soderstrom💎",
    "Zack Gelof",
    "Jonah Heim",
    "Jake Burger",
    "Brandon Nimmo",
    "Jose Siri💎",
    "Mike Trout",
    "Jac Caglianone",
    "Carter Jensen",
    "John Rave",
    "Hunter Feduccia",
    "Teoscar Hernandez",
    "Jake Bauers",
    "Gary Sanchez",
    "Jackson Chourio",
    "Taylor Trammell💎",
    "Yordan Alvarez",
    "Nelson Velazquez",
    "Dominic Canzone",
    "Cal Raleigh",
]"""

ALIASES = """ALIASES = {
    # The request wrote "MAsataka"; PropFinder exports "Masataka".
    "MAsataka Yoshida": "Masataka Yoshida",
    "Masataka Yoshida": "Masataka Yoshida",
    "JT Realmuto": "J.T. Realmuto",
    "J.T. Realmuto": "J.T. Realmuto",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Pete Crow-Armstrong": "Pete Crow-Armstrong",
    "Ronald Acuna Jr.": "Ronald Acuna Jr.",
    "Ronald Acuña Jr.": "Ronald Acuna Jr.",
    "Ronald Acuna": "Ronald Acuna Jr.",
    "Agustin Ramirez": "Agustin Ramirez",
    "Agustín Ramírez": "Agustin Ramirez",
    "Jazz Chisholm Jr.": "Jazz Chisholm Jr.",
    "Luis Garcia Jr.": "Luis Garcia Jr.",
    "Fernando Tatis Jr.": "Fernando Tatis Jr.",
    "Christian Encarnacion-Strand": "Christian Encarnacion-Strand",
    "Kazuma Okamoto": "Kazuma Okamoto",
    "Munetaka Murakami": "Munetaka Murakami",
    "Abimelec Ortiz": "Abimelec Ortiz",
    "Randal Grichuk": "Randal Grichuk",
    "Nelson Velazquez": "Nelson Velazquez",
    "Tyler Soderstrom": "Tyler Soderstrom",
    "Jac Caglianone": "Jac Caglianone",
    "Hunter Goodman": "Hunter Goodman",
    "Bryce Eldridge": "Bryce Eldridge",
    "Jung Hoo Lee": "Jung Hoo Lee",
    "Jose Siri": "Jose Siri",
    "Brandon Lowe": "Brandon Lowe",
    "Gary Sanchez": "Gary Sanchez",
    "Teoscar Hernandez": "Teoscar Hernandez",
    "Yordan Alvarez": "Yordan Alvarez",
    "Leody Taveras": "Leody Taveras",
}"""

BATTER_GAME_OVERRIDES = """BATTER_GAME_OVERRIDES: dict[str, str] = {}"""

PITCHER_HAND = """PITCHER_HAND = {
    # 8/16 LHP
    "Trevor Rogers": "L",
    "Patrick Sandoval": "L",
    "Ryan Weathers": "L",
    "Nick Lodolo": "L",
    "Cody Bradford": "L",
    "Jacob Lopez": "L",
    "Noah Cameron": "L",
    "Tarik Skubal": "L",
    # 8/16 RHP
    "Freddy Peralta": "R",
    "Michael Soroka": "R",
    "Bryce Elder": "R",
    "Lake Bachar": "R",
    "Dylan Cease": "R",
    "Casey Mize": "R",
    "Tanner Bibee": "R",
    "Sean Burke": "R",
    "Drew Anderson": "R",
    "Eury Perez": "R",
    "Jake Irvin": "R",
    "Christian Scott": "R",
    "Andrew Painter": "R",
    "Dean Kremer": "R",
    "Hunter Dobbins": "R",
    "Edward Cabrera": "R",
    "Gabriel Hughes": "R",
    "Blade Tidwell": "R",
    "Ryan Johnson": "R",
    "Logan Henderson": "R",
    "Bryan Woo": "R",
    "Hunter Brown": "R",
}"""

# Surname fragments used to stamp `throws` on backfilled zone rows. Full names
# where a bare surname collides with a batter on this slate (Otto Lopez, Daz
# Cameron, Logan Henderson vs Gunnar Henderson).
LHP_KEYS = [
    "Rogers",
    "Sandoval",
    "Weathers",
    "Lodolo",
    "Bradford",
    "Jacob Lopez",
    "Noah Cameron",
    "Skubal",
]

GAMECOUNT = 15
EXPECTED_BUMS = ["Ryan Johnson", "Edward Cabrera", "Jake Irvin", "Lake Bachar"]
AUDIT_LHP = [
    "Trevor Rogers",
    "Patrick Sandoval",
    "Ryan Weathers",
    "Nick Lodolo",
    "Cody Bradford",
    "Tarik Skubal",
]

# Yesterday's starters must not survive anywhere in today's sheet. Pitchers only:
# several 8/15 bats are in 8/16 lineups without being listed props.
STALE_PITCHERS = [
    "Anthony Kay",
    "Troy Melton",
    "Michael McGreevy",
    "Matthew Boyd",
    "Cam Schlittler",
    "Braydon Fisher",
    "Michael Lorenzen",
    "Logan Webb",
    "Brad Lord",
    "Sean Manaea",
    "Kyle Bradish",
    "Ian Seymour",
    "Ryan Gusto",
    "Brady Singer",
    "Randy Vasquez",
    "Joey Cantillo",
    "Jesus Luzardo",
    "Connor Prielipp",
    "Emerson Hancock",
    "Hayden Wesneski",
    "Eduardo Rodriguez",
    "Grant Holmes",
    "Jacob Misiorowski",
    "Justin Wrobleski",
    "Sonny Gray",
    "Jared Jones",
    "Randy Dobnak",
    "Reid Detmers",
    "MacKenzie Gore",
    "J.T. Ginn",
]

STAR = "\u2b50"
GEM = "\U0001f48e"

_DATE_SWAPS: list[tuple[str, str]] = [
    ("2026-08-15", "2026-08-16"),
    ("2026-08-14", "2026-08-15"),
    ("Saturday, August 15, 2026", "Sunday, August 16, 2026"),
    ("Saturday, August 15", "Sunday, August 16"),
    ("August 15, 2026", "August 16, 2026"),
    ("August 15", "August 16"),
    ("Friday, August 14, 2026", "Saturday, August 15, 2026"),
    ("Friday, August 14", "Saturday, August 15"),
    ("August 14, 2026", "August 15, 2026"),
    ("August 14", "August 15"),
    ("08-15", "08-16"),
    ("08-14", "08-15"),
    ("0815", "0816"),
    ("0814", "0815"),
    ("8/15", "8/16"),
    ("8/14", "8/15"),
]


def swap_dates(text: str) -> str:
    for idx, (needle, _) in enumerate(_DATE_SWAPS):
        text = text.replace(needle, f"\x00{idx}\x00")
    for idx, (_, sub) in enumerate(_DATE_SWAPS):
        text = text.replace(f"\x00{idx}\x00", sub)
    return text


def _ordered_archive_dates(block: str) -> list[str]:
    """Every archive date in the block plus any the swap chain skipped.

    Yesterday's slate becomes today's archive, so the run of dates immediately
    behind the slate date must be contiguous; earlier gaps are real off-days and
    are preserved as-is.
    """
    found = re.findall(r'"(2026-\d\d-\d\d)"', block)
    have = set(found)
    for d in ("2026-08-15", "2026-08-14", "2026-08-13", "2026-08-12"):
        have.add(d)
    return sorted(have, reverse=True)


def parsed_props() -> list[tuple[str, str]]:
    """(resolved name, marker constant name) from RAW_PROPS."""
    out: list[tuple[str, str]] = []
    for m in re.finditer(r'^\s+"([^"]+)",', RAW_PROPS, flags=re.M):
        raw = m.group(1)
        marker = "STAR" if STAR in raw else ("GEM" if GEM in raw else "")
        name = raw.replace(STAR, "").replace(GEM, "").strip()
        out.append((name, marker))
    return out


def main() -> None:
    props = parsed_props()
    propcount = len(props)
    stars = sum(1 for _, m in props if m == "STAR")
    gems = sum(1 for _, m in props if m == "GEM")

    # ---- build script ----
    text = swap_dates((ROOT / "build-0815-from-csv.py").read_text(encoding="utf-8"))
    text = re.sub(r"RAW_PROPS = \[.*?\n\]", RAW_PROPS, text, count=1, flags=re.S)
    text = re.sub(r"ALIASES = \{.*?\n\}", ALIASES, text, count=1, flags=re.S)
    text = re.sub(
        r"BATTER_GAME_OVERRIDES: dict\[str, str\] = \{\}|BATTER_GAME_OVERRIDES: dict\[str, str\] = \{.*?\n\}",
        BATTER_GAME_OVERRIDES,
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"PROBABLE_OVERRIDES = \{.*?\n\}|PROBABLE_OVERRIDES: dict\[str, dict\] = \{\}",
        "PROBABLE_OVERRIDES: dict[str, dict] = {}",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"PITCHER_HAND = \{.*?\n\}", PITCHER_HAND, text, count=1, flags=re.S)
    (ROOT / "build-0816-from-csv.py").write_text(text, encoding="utf-8")
    print("wrote build-0816-from-csv.py")

    # ---- patch script ----
    p = swap_dates((ROOT / "patch-0815-preview.py").read_text(encoding="utf-8"))
    before = len(p)
    p = re.sub(
        r"\n# 8/16 judgment:.*?straight_names = \{straight_o05\[\"name\"\], straight_o15\[\"name\"\]\}\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "straight judgment lock not stripped"
    before = len(p)
    p = re.sub(
        r"\n# 8/16 Goblin judgment:.*?    fav3 = _fav3_lock\n",
        "\n",
        p,
        count=1,
        flags=re.S,
    )
    assert len(p) < before, "goblin judgment lock not stripped"
    # The date swap only slides dates it has rules for, so each scaffold silently
    # drops a day from this hand-maintained list. Rebuild the leading run from the
    # slate date backwards instead of patching a fixed literal, and assert on the
    # dates rather than on any one string being present somewhere in the file.
    p, n = re.subn(
        r'    for date in \[\n(?:        "2026-\d\d-\d\d",\n)+',
        lambda m: '    for date in [\n'
        + "".join(f'        "{d}",\n' for d in _ordered_archive_dates(m.group(0))),
        p,
        count=1,
    )
    assert n == 1, "archive manifest date list not found"
    listed = re.search(r'    for date in \[\n((?:        "2026-\d\d-\d\d",\n)+)', p).group(1)
    for need in ("2026-08-15", "2026-08-14", "2026-08-13", "2026-08-12"):
        assert f'"{need}",' in listed, f"{need} missing from the archive manifest list"
    assert 'ARCHIVE_PREVIOUS = ROOT / "preview" / "archive" / "2026-08-15.html"' in p, (
        "archive target should point at the slate being replaced"
    )
    (ROOT / "patch-0816-preview.py").write_text(p, encoding="utf-8")
    print("wrote patch-0816-preview.py")

    # ---- summary verifier ----
    (ROOT / "verify-summary-0816.py").write_text(
        swap_dates((ROOT / "verify-summary-0815.py").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print("wrote verify-summary-0816.py")

    # ---- final audit ----
    a = swap_dates((ROOT / "_audit_0815_final.py").read_text(encoding="utf-8"))
    # August 16 2026 is a Sunday, so the swapped-forward "wrong" pair now holds it.
    a, n = re.subn(
        r'if "Friday, August 16" in html or "Sunday, August 16" in html:',
        'if "Friday, August 16" in html or "Saturday, August 16" in html:',
        a,
        count=1,
    )
    assert n == 1, "final audit wrong-weekday pair not re-pointed"
    a = a.replace(
        'fail("wrong weekday on August 16 (must be Saturday)")',
        'fail("wrong weekday on August 16 (must be Sunday)")',
        1,
    )
    assert '"Sunday, August 16, 2026" not in html' in a, "hero weekday assertion lost"
    bums = ", ".join(f'"{b}"' for b in EXPECTED_BUMS)
    a = re.sub(r"expected_bum = \{[^}]*\}", f"expected_bum = {{{bums}}}", a, count=1)
    lhp_block = "    for base in (\n" + "".join(f'        "{n}",\n' for n in AUDIT_LHP) + "    ):"
    a = re.sub(r"    for base in \(\n(?:        \"[^\"]+\",\n)+    \):", lhp_block, a, count=1)
    a = re.sub(r"PROPCOUNT = \d+", f"PROPCOUNT = {propcount}", a, count=1)
    a = re.sub(r"GAMECOUNT = \d+", f"GAMECOUNT = {GAMECOUNT}", a, count=1)
    (ROOT / "_audit_0816_final.py").write_text(a, encoding="utf-8")
    print(f"wrote _audit_0816_final.py (PROPCOUNT={propcount}, GAMECOUNT={GAMECOUNT})")

    # ---- deep audit ----
    d = swap_dates((ROOT / "_deep_audit_0815.py").read_text(encoding="utf-8"))
    body = "".join(f'    ("{n}", {m or chr(34) + chr(34)}),\n' for n, m in props)
    d, n = re.subn(
        r"USER_PROPS: list\[tuple\[str, str\]\] = \[.*?\n\]",
        "USER_PROPS: list[tuple[str, str]] = [\n" + body + "]",
        d,
        count=1,
        flags=re.S,
    )
    assert n == 1, "USER_PROPS block not found"
    res = (
        'RESOLVED = {"MAsataka Yoshida": "Masataka Yoshida", "JT Realmuto": "J.T. Realmuto", '
        '"Pete Crow Armstrong": "Pete Crow-Armstrong", "Ronald Acuna": "Ronald Acuna Jr."}'
    )
    d, n = re.subn(r"RESOLVED = \{[^\n]*\}", res, d, count=1)
    assert n == 1, "RESOLVED block not found"
    d, n = re.subn(
        r"EXPECTED_BUMS = \{[^\n]*\}",
        "EXPECTED_BUMS = {" + ", ".join(f'"{b}"' for b in EXPECTED_BUMS) + "}",
        d,
        count=1,
    )
    assert n == 1, "EXPECTED_BUMS block not found"
    stale_block = "STALE_8_15 = [\n" + "".join(f'    "{n}",\n' for n in STALE_PITCHERS) + "]"
    d, n = re.subn(r"STALE_8_1\d = \[.*?\n\]", stale_block, d, count=1, flags=re.S)
    assert n == 1, "stale list block not found"
    d = re.sub(r"for name in STALE_8_1\d:", "for name in STALE_8_15:", d, count=1)
    # Rebuild the whole wrong-weekday tuple from the real weekday instead of
    # swapping one entry: a targeted swap leaves the now-correct day in the list
    # (August 16 2026 is a Sunday), which fails the audit on a correct sheet.
    wrong_days = [
        f'"{day}, August 16"'
        for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
    ]
    d, n = re.subn(
        r'for wrong in \((?:\s*"[A-Za-z]+, August 16",?)+\):',
        "for wrong in (" + ", ".join(wrong_days) + "):",
        d,
        count=1,
    )
    assert n == 1, "deep audit wrong-weekday tuple not re-pointed"
    assert '"Sunday, August 16"' not in d.split("for wrong in (")[1].split("):")[0], (
        "Sunday is the correct weekday for August 16 and must not be flagged wrong"
    )
    d = re.sub(r"GAMECOUNT = \d+", f"GAMECOUNT = {GAMECOUNT}", d, count=1)
    (ROOT / "_deep_audit_0816.py").write_text(d, encoding="utf-8")
    print(f"wrote _deep_audit_0816.py ({propcount} props, {stars} stars, {gems} gems)")

    # ---- zone backfill ----
    z = swap_dates((ROOT / "_backfill_zones_0815.py").read_text(encoding="utf-8"))
    z = re.sub(
        r"LHP = \{.*?\n\}",
        "LHP = {\n" + "".join(f'    "{n}",\n' for n in LHP_KEYS) + "}",
        z,
        count=1,
        flags=re.S,
    )
    (ROOT / "_backfill_zones_0816.py").write_text(z, encoding="utf-8")
    print("wrote _backfill_zones_0816.py")

    # ---- helpers ----
    for src, dst in (
        ("_best_0815.py", "_best_0816.py"),
        ("_pick_review_0815.py", "_pick_review_0816.py"),
        ("_final_check_0815.py", "_final_check_0816.py"),
        ("_show_legs_0815.py", "_show_legs_0816.py"),
    ):
        if (ROOT / src).is_file():
            t = swap_dates((ROOT / src).read_text(encoding="utf-8"))
            if dst == "_final_check_0816.py":
                t = re.sub(r"GAMECOUNT = \d+", f"GAMECOUNT = {GAMECOUNT}", t, count=1)
                t = re.sub(r"BUMCOUNT = \d+", f"BUMCOUNT = {len(EXPECTED_BUMS)}", t, count=1)
            (ROOT / dst).write_text(t, encoding="utf-8")
            print(f"wrote {dst}")


if __name__ == "__main__":
    main()
