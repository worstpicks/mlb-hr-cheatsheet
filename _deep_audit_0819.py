#!/usr/bin/env python3
"""Deep content audit for the 2026-08-19 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-19"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "⭐"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

GAMECOUNT = 15
WEEKDAY = "Wednesday"
DATE_TEXT = "August 19, 2026"

# (name, game override, marker), generated from build-0818-from-csv.py RAW_PROPS so
# the audit cannot drift from what was actually built. Two Max Muncys today (ATH 3B
# and LAD 3B), so those two carry an explicit game.
ANY = None
USER_PROPS: list[tuple[str, str | None, str]] = [
    ('Oneil Cruz', ANY, STAR),
    ('Brandon Lowe', ANY, ""),
    ('Ben Malgeri', ANY, GEM),
    ('Spencer Torkelson', ANY, STAR),
    ('Brett Callahan', ANY, ""),
    ('Francisco Lindor', ANY, ""),
    ('Brett Baty', ANY, GEM),
    ('Bo Bichette', ANY, STAR),
    ('Jackson Merrill', ANY, ""),
    ('Manny Machado', ANY, ""),
    ('Luis Campusano', ANY, ""),
    ('Josh Bell', ANY, ""),
    ('Kody Clemens', ANY, STAR),
    ('Royce Lewis', ANY, ""),
    ('Ryan Kreidler', ANY, ""),
    ('Matt Olson', ANY, STAR),
    ('Michael Harris II', ANY, ""),
    ('Drake Baldwin', ANY, ""),
    ('Austin Riley', ANY, STAR),
    ('Ronald Acuna jr.', ANY, ""),
    ('Miguel Amaya', ANY, ""),
    ('Michael Conforto', ANY, ""),
    ('Pete Crow Armstrong', ANY, ""),
    ('Colson Montgomery', ANY, ""),
    ('Miguel Vargas', ANY, ""),
    ('Brenton Doyle', ANY, ""),
    ('Wilyer Abreu', ANY, ""),
    ('Adley Rutschman', ANY, ""),
    ('Corbin Carroll', ANY, STAR),
    ('Max Kepler', ANY, ""),
    ('Gabriel Moreno', ANY, ""),
    ('Tim Tawa', ANY, ""),
    ('Bryce Harper', ANY, STAR),
    ('Kyle Schwarber', ANY, ""),
    ('Griffin Conine', ANY, ""),
    ('Owen Caissie', ANY, ""),
    ('Joe Mack', ANY, ""),
    ('Leody Taveras', ANY, ""),
    ('Pete Alonso', ANY, GEM),
    ('Dylan Beavers', ANY, ""),
    ('Coby Mayo', ANY, GEM),
    ('Gunnar Henderson', ANY, ""),
    ('Colton Cowser', ANY, ""),
    ('Spencer Jones', ANY, ""),
    ('Trent Grisham', ANY, ""),
    ('Jazz Chisholm Jr.', ANY, ""),
    ('Heliot Ramos', ANY, ""),
    ('Ryan McMahon', ANY, ""),
    ('Luis Garcia Jr.', ANY, GEM),
    ('Ben Rice', ANY, STAR),
    ('Jonny DeLuca', ANY, ""),
    ('Jorge Mateo', ANY, ""),
    ('Jonathan Aranda', ANY, STAR),
    ('Richie Palacios', ANY, ""),
    ('Jesus Sanchez', ANY, ""),
    ('Jo Adell', ANY, STAR),
    ('Rhys Hoskins', ANY, ""),
    ('Nathaniel Lowe', ANY, ""),
    ('Victor Bericoto', ANY, ""),
    ('Rafael Devers', ANY, ""),
    ('Bryce Eldridge', ANY, ""),
    ('Elly De La Cruz', ANY, ""),
    ('Tyler Stephenson', ANY, STAR),
    ('Dane Myers', ANY, ""),
    ('Ivan Herrera', ANY, ""),
    ('Jimmy Crooks', ANY, GEM),
    ('Alec Burleson', ANY, ""),
    ('JJ Wetherholt', ANY, ""),
    ('Joshua Baez', ANY, ""),
    ('Jackson Chourio', ANY, ""),
    ('William Contreras', ANY, STAR),
    ('Brice Turang', ANY, ""),
    ('Gary Sanchez', ANY, ""),
    ('Christian Yelich', ANY, ""),
    ('Garrett Mitchell', ANY, ""),
    ('Luis Lara', ANY, GEM),
    ('Dominic Canzone', ANY, STAR),
    ('Brock Rodeen', ANY, ""),
    ('Zack Gelof', ANY, ""),
    ('Lawrence Butler', ANY, ""),
    ('Max Muncy', "ATH @ KC", ""),
    ('Jeff McNeil', ANY, ""),
    ('Jac Caglianone', ANY, GEM),
    ('Michael Massey', ANY, STAR),
    ('Maikel Garcia', ANY, ""),
    ('Carter Jensen', ANY, STAR),
    ('Corey Seager', ANY, ""),
    ('Joc Pederson', ANY, ""),
    ('Evan Carter', ANY, ""),
    ('Abimelec Ortiz', ANY, GEM),
    ('Jose Tena', ANY, STAR),
    ('CJ Abrams', ANY, ""),
    ('Dylan Crews', ANY, ""),
    ('Yordan Alvarez', ANY, STAR),
    ('Nelson Velazquez', ANY, GEM),
    ('Taylor Trammell', ANY, STAR),
    ('Josh Lowe', ANY, GEM),
    ("Travis d'Arnaud", ANY, ""),
    ('Willi Castro', ANY, STAR),
    ('Mickey Moniak', ANY, ""),
    ('Zac Veen', ANY, GEM),
    ('Andy Pages', ANY, ""),
    ('Max Muncy', "LAD @ COL", ""),
    ('Teoscar Hernandez', ANY, GEM),
    ('Shohei Ohtani', ANY, STAR),
    ('Mookie Betts', ANY, ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Ronald Acuna": "Ronald Acuna Jr.",
    # PropFinder drops the generational suffix and punctuates initials.
    "Ronald Acuna jr.": "Ronald Acuna Jr.",
    "Brock Rodeen": "Brock Rodden",
}

# 8/18-only content that must not survive onto the 8/18 sheet. Prior-day starters that
# are not on this slate — arms working both days would fail every correct sheet.
STALE_8_18 = [
    "Andrew Abbott",
    "Brady Basso",
    "Braxton Ashcraft",
    "Bryan Hudson",
    "Bryce Miller",
    "Cade Gibson",
    "Cal Quantrill",
    "Carlos Rodon",
    "Carson Whisenhunt",
    "Cristian Javier",
    "Daniel Lynch IV",
    "Eric Lauer",
    "Foster Griffin",
    "George Klassen",
    "Jackson Kent",
    "Jose Soriano",
    "Keider Montero",
    "Kevin Gausman",
    "Kyle Harrison",
    "Kyle Leahy",
    "Merrill Kelly",
    "Nick Martinez",
    "Ranger Suarez",
    "Robbie Ray",
    "Ryan Feltner",
    "Shane Baz",
    "Tyler Mahle",
    "Zach Thornton",
    "Zack Wheeler",
    "Zebby Matthews",
]

# HR risk >= 0.95 on today's hr-targets export.
EXPECTED_BUMS = {"Jackson Jobe", "Aaron Nola", "Max Scherzer"}

# Every game now carries both starters' splits: the 11:42 re-export shipped rows for
# all 22 arms, and the two 0-BF arms (Emanuel, Gamboa) render the honest
# "no MLB HR data yet" lane rather than being dropped from the header.
# Matt Wilkinson and Ethan Pecko have no measured data anywhere, and the sheet now
# OMITS a starter rather than printing a "no HR data" placeholder, so those two
# headers legitimately carry one split.
SINGLE_SPLIT_GAMES: set[str] = {"SF @ CLE", "LAA @ HOU"}

# Probables replaced before first pitch, all confirmed against the MLB Stats API
# (Kansas City and Chicago already show their arm in the boxscore): ATH Perkins ->
# Basso, KC Black -> Lynch IV, CWS Fedde -> Hudson, MIA Phillips -> Gibson. None may
# survive anywhere on the sheet.
SUPERSEDED_PROBABLES = ["Jose Urquidy", "Urquidy", "Adrian Houser"]

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def fold(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.lower().replace("’", "'")


def main() -> int:
    html = PREVIEW.read_text(encoding="utf-8")

    titles = re.findall(r'title: "([^"]+)"', html)
    print(f"=== DEEP AUDIT {DATE} ===")

    # Row objects grouped by the game block they sit in, so doubleheader duplicates
    # can be told apart.
    rows: list[tuple[str, str, str]] = []  # (game_key, plain name, emojis)
    for gm in re.finditer(r'\{\s*title: "([^"]+)".*?rows: \[(.*?)\n\s*\],', html, re.S):
        gkey = gm.group(1).split(" - ")[0]
        for rm in re.finditer(r'\{ name: "([^"]+)"[^}]*?emojis: "([^"]*)"', gm.group(2)):
            rows.append((gkey, rm.group(1).rsplit(" (", 1)[0], rm.group(2)))

    print(f"rows parsed: {len(rows)}")
    if len(rows) != len(USER_PROPS):
        fail(f"expected {len(USER_PROPS)} rows, parsed {len(rows)}")

    by_key: dict[tuple[str, str], str] = {(g, fold(n)): em for g, n, em in rows}
    by_name: dict[str, list[str]] = {}
    for _g, n, em in rows:
        by_name.setdefault(fold(n), []).append(em)

    fav = sum(1 for _g, _n, em in rows if STAR in em)
    gem = sum(1 for _g, _n, em in rows if GEM in em)
    want_fav = sum(1 for _n, _g, m in USER_PROPS if m == STAR)
    want_gem = sum(1 for _n, _g, m in USER_PROPS if m == GEM)
    print(f"favorites {fav} (want {want_fav}) · gems {gem} (want {want_gem})")
    if fav != want_fav:
        fail(f"expected {want_fav} favorites, got {fav}")
    if gem != want_gem:
        fail(f"expected {want_gem} gems, got {gem}")

    # Every listed prop present with the right marker, in the right game.
    for name, game, marker in USER_PROPS:
        lookup = fold(RESOLVED.get(name, name))
        if game is None:
            ems = by_name.get(lookup)
            if not ems:
                fail(f"prop missing from sheet: {name}")
                continue
            em = ems[0]
        else:
            em = by_key.get((game, lookup))
            if em is None:
                fail(f"prop missing from sheet: {name} [{game}]")
                continue
        label = name if game is None else f"{name} [{game}]"
        if marker == STAR and STAR not in em:
            fail(f"{label} should be a favorite (star)")
        if marker == GEM and GEM not in em:
            fail(f"{label} should be a hidden gem")
        if marker == "" and (STAR in em or GEM in em):
            fail(f"{label} should have no star/gem, got {em!r}")

    # Games and park/split header coverage
    # gameMeta embeds escaped quotes around the pitcher-meta spans, so a plain [^"]*
    # capture stops after the park segment and hides the pitcher splits.
    metas = re.findall(r'gameMeta: "((?:[^"\\]|\\.)*)"', html)
    print(f"games: {len(titles)}")
    if len(titles) != GAMECOUNT:
        fail(f"expected {GAMECOUNT} games, got {len(titles)}")
    for t, meta in zip(titles, metas):
        gkey = t.split(" - ")[0]
        if "Park " not in meta:
            fail(f"game missing park %: {t}")
        if "LHB" not in meta or "RHB" not in meta:
            fail(f"game missing hand park split: {t}")
        if meta.count("pitcher-meta") < 2:
            if gkey in SINGLE_SPLIT_GAMES:
                warns.append(f"{gkey}: one SP split only — PropFinder shipped no 8/17 row for that arm")
            else:
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
        gm = re.search(r"vs ([^(]+?) " + GLOVE, t) or re.search(r"- ([^(]+?) " + GLOVE, t)
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
    body = re.sub(r'<script[^>]*straights-history-data.*?</script>', "", html, flags=re.S)
    body_folded = fold(body)
    for name in STALE_8_18:
        if fold(name) in body_folded:
            fail(f"stale 8/18 content on sheet: {name}")
    for name in SUPERSEDED_PROBABLES:
        if fold(name) in body_folded:
            fail(f"superseded probable still on sheet: {name}")

    # The owner asked for no "no HR risk" placeholders anywhere on the board: either
    # a real number or nothing at all.
    for phrase in ("no MLB HR data yet", "no PropFinder HR risk", "split/risk data unavailable"):
        if phrase in html:
            fail(f"missing-HR-risk placeholder on sheet: {phrase!r}")

    # Date correctness
    if f"{WEEKDAY}, {DATE_TEXT}" not in html:
        fail(f"hero must read {WEEKDAY}, {DATE_TEXT}")
    # Derive the wrong-weekday set instead of listing it: hardcoding the list meant
    # the correct weekday stayed in it after a date change and failed a correct sheet.
    all_days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
    for wrong in (d for d in all_days if d != WEEKDAY):
        if f"{wrong}, {DATE_TEXT}" in html:
            fail(f"wrong weekday for {DATE_TEXT}: {wrong}")
    if f'<meta name="sheet-date" content="{DATE}">' not in html:
        fail(f"sheet-date meta must be {DATE}")

    # Regression guard for the CWS/WSH park-key aliasing bug: Ballpark Pal ships these
    # as CHW / WAS, and the old pair-by-pair alias map dropped unseen matchups.
    for gkey in ("CWS @ CHC", "WSH @ TEX"):
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
