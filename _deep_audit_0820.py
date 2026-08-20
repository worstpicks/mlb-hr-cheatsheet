#!/usr/bin/env python3
"""Deep content audit for the 2026-08-20 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-08-20"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "⭐"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

GAMECOUNT = 9
WEEKDAY = "Thursday"
DATE_TEXT = "August 20, 2026"

# (name, game override, marker), generated from build-0818-from-csv.py RAW_PROPS so
# the audit cannot drift from what was actually built. Two Max Muncys today (ATH 3B
# and LAD 3B), so those two carry an explicit game.
ANY = None
USER_PROPS: list[tuple[str, str | None, str]] = [
    ('JJ Bleday', ANY, GEM),
    ('Michael Toglia', ANY, ""),
    ('Tyler Stephenson', ANY, ""),
    ('Elly De La Cruz', ANY, ""),
    ('Matt McLain', ANY, ""),
    ('Eugenio Suarez', ANY, ""),
    ('Alec Burleson', ANY, STAR),
    ('Jimmy Crooks', ANY, GEM),
    ('Ivan Herrera', ANY, ""),
    ('Jonny DeLuca', ANY, GEM),
    ('Jorge Mateo', ANY, ""),
    ('Yandy Diaz', ANY, GEM),
    ('Jonathan Aranda', ANY, ""),
    ('Kazuma Okamoto', ANY, STAR),
    ('Daz Cameron', ANY, ""),
    ('Jo Adell', ANY, ""),
    ('Nathaniel Lowe', ANY, GEM),
    ('Bryce Eldridge', ANY, STAR),
    ('Rafael Devers', ANY, ""),
    ('Jung Hoo Lee', ANY, ""),
    ('Garrett Mitchell', ANY, ""),
    ('Jackson Chourio', ANY, GEM),
    ('William Contreras', ANY, STAR),
    ('Randy Arozarena', ANY, ""),
    ('Julio Rodriguez', ANY, ""),
    ('Cal Raleigh', ANY, ""),
    ('Weston Wilson', ANY, ""),
    ('Jac Caglianone', ANY, STAR),
    ('Salvador Perez', ANY, GEM),
    ('Vinnie Pasquantino', ANY, STAR),
    ('Jeff McNeil', ANY, ""),
    ('Zack Gelof', ANY, ""),
    ('Brian Serven', ANY, ""),
    ('Munetaka Murakami', ANY, STAR),
    ('Miguel Vargas', ANY, STAR),
    ('Andrew Benintendi', ANY, STAR),
    ('Randal Grichuk', ANY, ""),
    ('Lane Thomas', ANY, STAR),
    ('Ronald Acuna Jr.', ANY, GEM),
    ('Matt Olson', ANY, STAR),
    ('Austin Riley', ANY, STAR),
    ('Pete Alonso', ANY, STAR),
    ('Gunnar Henderson', ANY, GEM),
    ('Coby Mayo', ANY, GEM),
    ("Tyler O'Neill", ANY, ""),
    ('Colton Cowser', ANY, ""),
    ('Samuel Basallo', ANY, ""),
    ('Ben Rice', ANY, ""),
    ('Jazz Chisholm Jr.', ANY, GEM),
    ('Trent Grisham', ANY, ""),
    ('Amed Rosario', ANY, ""),
    ('Corey Seager', ANY, STAR),
    ('Jake Burger', ANY, ""),
    ('Jarred Kelenic', ANY, ""),
    ('Abimelec Ortiz', ANY, GEM),
    ('Brady House', ANY, ""),
    ('Taylor Trammell', ANY, STAR),
    ('Cam Smith', ANY, ""),
    ('Yordan Alvarez', ANY, ""),
    ('Daulton Varsho', ANY, ""),
    ('Nelson Velazquez', ANY, ""),
    ("Travis d'Arnaud", ANY, ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED = {
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Ronald Acuna": "Ronald Acuna Jr.",
    # PropFinder drops the generational suffix and punctuates initials.
    "Ronald Acuna": "Ronald Acuna Jr.",
}

# 8/19-only content that must not survive onto the 8/18 sheet. Prior-day starters that
# are not on this slate — arms working both days would fail every correct sheet.
STALE_8_19 = [
    "AJ Smith-Shawver",
    "Aaron Nola",
    "Brandon Pfaadt",
    "Cade Cavalli",
    "Chase Burns",
    "Chris Bassitt",
    "Clay Holmes",
    "Drew Rasmussen",
    "Dustin May",
    "Ethan Pecko",
    "Jackson Jobe",
    "Kumar Rocker",
    "Kyle Freeland",
    "Logan Gilbert",
    "Matt Wilkinson",
    "Matthew Liberatore",
    "Max Scherzer",
    "Michael King",
    "Parker Messick",
    "Paul Skenes",
    "Payton Tolle",
    "Robert Stock",
    "Roki Sasaki",
    "Sandy Alcantara",
    "Sean Newcomb",
    "Seth Lugo",
    "Taj Bradley",
    "Walbert Urena",
    "Will Warren",
]

# HR risk >= 0.95 on today's hr-targets export.
EXPECTED_BUMS = {"Grayson Rodriguez"}

# Every game now carries both starters' splits: the 11:42 re-export shipped rows for
# all 22 arms, and the two 0-BF arms (Emanuel, Gamboa) render the honest
# "no MLB HR data yet" lane rather than being dropped from the header.
# Every arm on this slate has a full HR-risk row, so every header carries two splits.
SINGLE_SPLIT_GAMES: set[str] = set()

# Probables replaced before first pitch, all confirmed against the MLB Stats API
# (Kansas City and Chicago already show their arm in the boxscore): ATH Perkins ->
# Basso, KC Black -> Lynch IV, CWS Fedde -> Hudson, MIA Phillips -> Gibson. None may
# survive anywhere on the sheet.
SUPERSEDED_PROBABLES: list[str] = []  # no probable changed on this slate

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
    for name in STALE_8_19:
        if fold(name) in body_folded:
            fail(f"stale 8/19 content on sheet: {name}")
    for name in SUPERSEDED_PROBABLES:
        if fold(name) in body_folded:
            fail(f"superseded probable still on sheet: {name}")

    # The hits rubric ranks on lineup slot. If the research JSON is missing when the
    # patch computes ranks, every input silently falls back to a league default and the
    # ticket fills with nine-hole and bench bats -- which is exactly what shipped on
    # 8/18-8/20 before the ordering fix. Assert the outcome, not the plumbing.
    import json as _json, unicodedata as _ud
    rjson = ROOT / "preview" / "data" / f"research-{DATE}.json"
    if rjson.is_file():
        def _fold2(n):
            b = _ud.normalize("NFKD", n or "")
            b = "".join(c for c in b if not _ud.combining(c))
            return re.sub(r"[^a-z0-9]", "", b.lower())
        _d = _json.loads(rjson.read_text(encoding="utf-8"))
        _slot = {}
        for _g in _d.get("games", []):
            for _side in ("awayLineup", "homeLineup"):
                for _pl in _g.get(_side) or []:
                    if _pl.get("order"):
                        _slot[_fold2(_pl["name"])] = _pl["order"]
        _m = re.search(r"data-goblin-gambly-lines='([^']*hits[^']*)'", html)
        if _m:
            import html as _htmlmod
            _legs = [l.split(" - ")[0] for l in _json.loads(_htmlmod.unescape(_m.group(1)))]
            _bench = [n for n in _legs if (_slot.get(_fold2(n)) or 0) > 9]
            if _bench:
                fail(f"hits parlay contains bench bats (lineup slot >9): {_bench}")
            _known = [_slot[_fold2(n)] for n in _legs if _fold2(n) in _slot]
            if _known and sum(_known) / len(_known) > 5.0:
                fail(
                    f"hits parlay mean lineup slot {sum(_known)/len(_known):.1f} > 5.0 — "
                    "expected-PA ranking looks inert"
                )
    else:
        fail(f"research JSON missing for {DATE}; hits rubric cannot rank on lineup slot")

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
    for gkey in ("ATL @ CWS", "WSH @ TEX"):
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
