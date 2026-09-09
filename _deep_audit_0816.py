#!/usr/bin/env python3
"""Deep content audit for the 2026-08-16 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-16"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "\u2b50"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

GAMECOUNT = 15

# (name, marker) exactly as the user listed them for 8/16
USER_PROPS: list[tuple[str, str]] = [
    ("Yandy Diaz", ""),
    ("Ryan Vilade", ""),
    ("Jorge Mateo", ""),
    ("Pete Alonso", STAR),
    ("Christian Encarnacion-Strand", ""),
    ("Coby Mayo", ""),
    ("Gunnar Henderson", ""),
    ("Leody Taveras", ""),
    ("Bryan Reynolds", ""),
    ("Brandon Lowe", STAR),
    ("Wilyer Abreu", STAR),
    ("Jarren Duran", ""),
    ("Masataka Yoshida", ""),
    ("Matt Olson", ""),
    ("Ronald Acuna Jr.", ""),
    ("Austin Riley", GEM),
    ("Corbin Carroll", ""),
    ("Tim Tawa", ""),
    ("Lars Nootbaar", ""),
    ("Kazuma Okamoto", ""),
    ("Trent Grisham", ""),
    ("Jazz Chisholm Jr.", GEM),
    ("Spencer Jones", ""),
    ("Luis Garcia Jr.", ""),
    ("Ben Rice", ""),
    ("Brett Baty", ""),
    ("Francisco Lindor", ""),
    ("Bo Bichette", ""),
    ("Abimelec Ortiz", ""),
    ("Dylan Crews", ""),
    ("Spencer Torkelson", ""),
    ("Munetaka Murakami", ""),
    ("Randal Grichuk", ""),
    ("Rhys Hoskins", ""),
    ("Angel Genao", ""),
    ("Jackson Merrill", ""),
    ("Manny Machado", ""),
    ("Fernando Tatis Jr.", ""),
    ("Xander Bogaerts", ""),
    ("Ty France", ""),
    ("Matt McLain", ""),
    ("Tyler Stephenson", ""),
    ("Agustin Ramirez", GEM),
    ("Griffin Conine", ""),
    ("Kody Clemens", ""),
    ("Josh Bell", ""),
    ("Royce Lewis", ""),
    ("Kyle Schwarber", ""),
    ("J.T. Realmuto", ""),
    ("Bryson Stott", ""),
    ("Alex Bregman", GEM),
    ("Miguel Amaya", ""),
    ("Pete Crow-Armstrong", ""),
    ("Jung Hoo Lee", ""),
    ("Bryce Eldridge", ""),
    ("Mickey Moniak", GEM),
    ("Willi Castro", ""),
    ("Hunter Goodman", ""),
    ("Zac Veen", ""),
    ("Tyler Soderstrom", GEM),
    ("Zack Gelof", ""),
    ("Jonah Heim", ""),
    ("Jake Burger", ""),
    ("Brandon Nimmo", ""),
    ("Jose Siri", GEM),
    ("Mike Trout", ""),
    ("Jac Caglianone", ""),
    ("Carter Jensen", ""),
    ("John Rave", ""),
    ("Hunter Feduccia", ""),
    ("Teoscar Hernandez", ""),
    ("Jake Bauers", ""),
    ("Gary Sanchez", ""),
    ("Jackson Chourio", ""),
    ("Taylor Trammell", GEM),
    ("Yordan Alvarez", ""),
    ("Nelson Velazquez", ""),
    ("Dominic Canzone", ""),
    ("Cal Raleigh", ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED = {"MAsataka Yoshida": "Masataka Yoshida", "JT Realmuto": "J.T. Realmuto", "Pete Crow Armstrong": "Pete Crow-Armstrong", "Ronald Acuna": "Ronald Acuna Jr."}

# 8/15-only content that must not survive onto the 8/16 sheet. Prior-day starters plus
# batters absent from this slate - shared names like Alonso or Suarez are on 8/16 too,
# so listing them here would fail every correct sheet.
STALE_8_15 = [
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

EXPECTED_BUMS = {"Ryan Johnson", "Edward Cabrera", "Jake Irvin", "Lake Bachar"}

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def fold(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.lower().replace("\u2019", "'")


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")
    folded = fold(html)

    # Row objects: name + emoji string
    rows = re.findall(r'\{ name: "([^"]+)"[^}]*?emojis: "([^"]*)"', html)
    print(f"=== DEEP AUDIT {DATE} ===")
    print(f"rows parsed: {len(rows)}")
    if len(rows) != len(USER_PROPS):
        fail(f"expected {len(USER_PROPS)} rows, parsed {len(rows)}")

    by_name: dict[str, str] = {}
    for raw, em in rows:
        plain = raw.rsplit(" (", 1)[0]
        by_name[fold(plain)] = em

    fav = sum(1 for _, em in rows if STAR in em)
    gem = sum(1 for _, em in rows if GEM in em)
    want_fav = sum(1 for _, m in USER_PROPS if m == STAR)
    want_gem = sum(1 for _, m in USER_PROPS if m == GEM)
    print(f"favorites {fav} (want {want_fav}) · gems {gem} (want {want_gem})")
    if fav != want_fav:
        fail(f"expected {want_fav} favorites, got {fav}")
    if gem != want_gem:
        fail(f"expected {want_gem} gems, got {gem}")

    # Every listed prop present with the right marker
    for name, marker in USER_PROPS:
        lookup = RESOLVED.get(name, name)
        em = by_name.get(fold(lookup))
        if em is None:
            fail(f"prop missing from sheet: {name}")
            continue
        if marker == STAR and STAR not in em:
            fail(f"{name} should be a favorite (star)")
        if marker == GEM and GEM not in em:
            fail(f"{name} should be a hidden gem")
        if marker == "" and (STAR in em or GEM in em):
            fail(f"{name} should have no star/gem, got {em!r}")

    # Games and park/split header coverage
    titles = re.findall(r'title: "([^"]+)"', html)
    # gameMeta embeds escaped quotes around the pitcher-meta spans, so a plain [^"]*
    # capture stops after the park segment and hides the pitcher splits.
    metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', html)
    print(f"games: {len(titles)}")
    if len(titles) != GAMECOUNT:
        fail(f"expected {GAMECOUNT} games, got {len(titles)}")
    for t, meta in zip(titles, metas):
        if "Park " not in meta:
            fail(f"game missing park %: {t}")
        if "LHB" not in meta or "RHB" not in meta:
            fail(f"game missing hand park split: {t}")
        if meta.count("pitcher-meta") < 2:
            fail(f"game missing both pitcher splits: {t}")

    # Bums gloved in titles, and their opponents flagged on rows
    for bum in EXPECTED_BUMS:
        if f"{bum} {GLOVE}" not in html:
            fail(f"bum {bum} missing {GLOVE} in game title")
    gloved_titles = [t for t in titles if GLOVE in t]
    if len(gloved_titles) != len(EXPECTED_BUMS):
        fail(f"expected {len(EXPECTED_BUMS)} gloved titles, got {len(gloved_titles)}")

    # Rows facing a bum should carry the vs-bum emoji trio
    for t in gloved_titles:
        m = re.search(r"\{ title: \"" + re.escape(t) + r"\".*?\n\s*\], \}", html, re.S)
        block = m.group(0) if m else ""
        bum_last = None
        gm = re.search(r"vs ([^(]+?) " + GLOVE, t) or re.search(
            r"- ([^(]+?) " + GLOVE, t
        )
        if gm:
            bum_last = gm.group(1).strip().split()[-1]
        if not bum_last:
            continue
        for rm in re.finditer(
            r'\{ name: "([^"]+)"[^}]*?emojis: "([^"]*)"[^}]*?chips: \["vs ([^"]+)"\]', block
        ):
            name, em, chip = rm.groups()
            if chip.strip().split()[-1] == bum_last and GLOVE not in em:
                fail(f"{name} faces bum {bum_last} but row lacks {GLOVE}")

    # Staleness: ignore the historical straights tracker, which legitimately lists past days
    body = re.sub(
        r'<script[^>]*straights-history-data.*?</script>', "", html, flags=re.S
    )
    body_folded = fold(body)
    for name in STALE_8_15:
        if fold(name) in body_folded:
            fail(f"stale 8/15 content on sheet: {name}")

    # Date correctness
    if "Sunday, August 16, 2026" not in html:
        fail("hero must read Sunday, August 16, 2026")
    for wrong in ("Monday, August 16", "Tuesday, August 16", "Wednesday, August 16",
                  "Thursday, August 16", "Friday, August 16", "Saturday, August 16"):
        if wrong in html:
            fail(f"wrong weekday for August 16: {wrong}")

    # Regression guard for the CWS/WSH park-key aliasing bug: Ballpark Pal ships these
    # as CHW / WAS, and the old pair-by-pair alias map dropped unseen matchups.
    for gkey in ("CWS @ DET", "WSH @ NYM"):
        m = re.search(
            r'title: "' + re.escape(gkey) + r'[^"]*".*?gameMeta: "((?:[^"\\]|\\.)*)"', html, re.S
        )
        if not m:
            fail(f"{gkey} game block not found")
        elif "Park " not in m.group(1):
            fail(f"{gkey} missing park factor (team-code alias regression)")

    print()
    for w in warns:
        print("WARN", w)
    if errs:
        print("FAIL deep audit:")
        for e in errs:
            print("  -", e)
        return 1
    print("OK deep audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
