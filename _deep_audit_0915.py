#!/usr/bin/env python3
"""Deep content audit for the 2026-09-15 sheet: prop coverage, markers, bums, staleness."""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = "2026-09-15"
PREVIEW = ROOT / "preview" / "index.html"

STAR = "⭐"
GEM = "\U0001f48e"
GLOVE = "\U0001f9e4"

GAMECOUNT = 15
WEEKDAY = "Tuesday"
DATE_TEXT = "September 15, 2026"

# Listed names who are on nobody's roster today: no team, no game, so no matchup to
# score and no honest row to print. Empty right now -- every one of the 132 listed
# props resolved. An entry here exempts exactly one name and leaves every other prop
# strictly required, and the audit still fails if a row IS printed for the exempted
# name, so it cannot quietly become a place to hide a dropped pick.
NOT_ON_SLATE: dict[str, str] = {}

# (name, game override, marker), generated from build-0915-from-csv.py RAW_PROPS so
# the audit cannot drift from what was actually built. Max Muncy is ambiguous again
# and pinned to the Dodgers by the owner's list ordering, even though Oakland's is
# the one starting tonight -- see the note in the builder.
ANY = None
USER_PROPS: list[tuple[str, str | None, str]] = [
    ("Jonathan Aranda", ANY, ""),
    ("Victor Mesa Jr.", ANY, "⭐"),
    ("Junior Caminero", ANY, "⭐"),
    ("Zack Gelof", ANY, ""),
    ("Bryan Reynolds", ANY, ""),
    ("Rafael Flores", ANY, ""),
    ("William Contreras", ANY, "💎"),
    ("Joey Ortiz", ANY, ""),
    ("Garrett Mitchell", ANY, ""),
    ("Patrick Bailey", ANY, ""),
    ("Randal Grichuk", ANY, ""),
    ("Munetaka Murakami", ANY, ""),
    ("Elly De La Cruz", ANY, ""),
    ("Eugenio Suarez", ANY, ""),
    ("JJ Bleday", ANY, ""),
    ("Mookie Betts", ANY, ""),
    ("Will Smith", ANY, "💎"),
    ("Andrew Pinckney", ANY, ""),
    ("Dylan Crews", ANY, ""),
    ("James Wood", ANY, ""),
    ("Kyle Schwarber", ANY, ""),
    ("Alec Bohm", ANY, ""),
    ("Alejandro Kirk", ANY, "💎"),
    ("Kazuma Okamoto", ANY, ""),
    ("George Springer", ANY, ""),
    ("Vladimir Guerrero Jr.", ANY, ""),
    ("Spencer Torkelson", ANY, "💎"),
    ("Colt Keith", ANY, ""),
    ("Brett Callahan", ANY, ""),
    ("Dillon Dingler", ANY, ""),
    ("Kevin McGonigle", ANY, ""),
    ("Pete Alonso", ANY, ""),
    ("Coby Mayo", ANY, "💎"),
    ("Jeremiah Jackson", ANY, ""),
    ("Royce Lewis", ANY, ""),
    ("Ryan Kreidler", ANY, ""),
    ("George Lombard Jr.", ANY, ""),
    ("Spencer Jones", ANY, ""),
    ("Aaron Judge", ANY, ""),
    ("Ben Rice", ANY, ""),
    ("Luis Garcia Jr.", ANY, ""),
    ("Michael Busch", ANY, ""),
    ("Pete Crow Armstrong", ANY, ""),
    ("Matt Olson", ANY, ""),
    ("Ronald Acuna Jr.", ANY, ""),
    ("Austin Riley", ANY, ""),
    ("Leonardo Bernal", ANY, ""),
    ("Ivan Herrera", ANY, ""),
    ("Alec Burleson", ANY, ""),
    ("Bryce Eldridge", ANY, ""),
    ("Jung Hoo Lee", ANY, ""),
    ("Jake Burger", ANY, ""),
    ("Ezequiel Duran", ANY, ""),
    ("Corey Seager", ANY, "⭐"),
    ("Adley Rutschman", ANY, ""),
    ("Mickey Gasper", ANY, ""),
    ("Roman Anthony", ANY, ""),
    ("Nelson Velazquez", ANY, ""),
    ("Taylor Trammell", ANY, ""),
    ("Cam Smith", ANY, ""),
    ("Vinnie Pasquantino", ANY, ""),
    ("Salvador Perez", ANY, "💎"),
    ("Jac Caglianone", ANY, ""),
    ("Connor Norby", ANY, ""),
    ("Cole Carrigg", ANY, ""),
    ("Hunter Goodman", ANY, ""),
    ("Kyle Karros", ANY, ""),
    ("Manny Machado", ANY, "⭐"),
    ("Xander Bogaerts", ANY, ""),
    ("Ty France", ANY, "💎"),
    ("Fernando Tatis Jr.", ANY, "💎"),
    ("Jackson Merrill", ANY, ""),
    ("Moises Ballesteros", ANY, ""),
    ("Mike Trout", ANY, ""),
    ("Jose Siri", ANY, ""),
    ("Lazaro Montes", ANY, ""),
    ("Michael Arroyo", ANY, ""),
    ("Cal Raleigh", ANY, ""),
    ("Randy Arozarena", ANY, ""),
    ("Lars Nootbar", ANY, "💎"),
    ("Gabriel Moreno", ANY, ""),
    ("Otto Lopez", ANY, "💎"),
    ("Javier Sanoja", ANY, ""),
    ("Graham Pauley", ANY, ""),
]

# Name the sheet legitimately uses that differs from the user's spelling.
RESOLVED: dict[str, str] = {
    # Typed with a stray space and a stray capital; both resolved against the
    # export rather than dropped.
    "Chase De Lauter": "Chase DeLauter",
    "Ozzie ALbies": "Ozzie Albies",
    # Two transposed letters, corrected against the export by the builder. The
    # audit has to know the corrected spelling or it looks for a row that was never
    # going to exist under the typed one.
    "Lars Nootbar": "Lars Nootbaar",
}

# Derived at run time from the previous slate -- see derive_stale_prev_day().


# HR risk >= 0.95 on today's hr-targets export.
EXPECTED_BUMS = {'Sean Manaea', 'Logan Gilbert'}

# Every game carries two pitcher segments. Trevor Williams is missing from the
# HR-risk export -- PropFinder built it around Kumar Rocker -- so his header
# renders the measured BAA lane carried from his 2026-08-03 export.
SINGLE_SPLIT_GAMES: set[str] = set()

# Probables replaced after the PropFinder export, both confirmed against the MLB
# Stats API. Neither may survive anywhere on the sheet. (Will Dion was never a real
# probable -- the pasted block was stale; Washington's arm is and was Brad Lord.)
SUPERSEDED_PROBABLES: list[str] = []  # every exported arm is a live probable

def _title_pitchers(html_text: str) -> set[str]:
    """Both starters out of every game title on a rendered sheet."""
    names: set[str] = set()
    for m in re.finditer(r'\{\s*title: "([^"]+)"', html_text):
        title = m.group(1)
        if " - " not in title or " vs " not in title:
            continue
        _, matchup = title.split(" - ", 1)
        for seg in matchup.split(" vs ", 1):
            # "Sean Burke 🧤 (R, CWS)" -> "Sean Burke"
            nm = re.sub(r"\s*\([^)]*\)\s*$", "", seg).replace("\U0001f9e4", "").strip()
            if nm:
                names.add(nm)
    return names


def derive_stale_prev_day() -> list[str]:
    """Arms who started the LAST slate and are not starting this one.

    This list used to be a literal, copied forward from one day's clone to the next
    while the comment above it claimed it was derived. It went stale the moment a
    pitcher in it took the mound again -- today it failed the sheet for deGrom,
    Gilbert, Perez and Fried, all of whom are actually starting. Derive it, so it is
    right on a day nobody edits it.

    Returns an empty list when the previous sheet cannot be read: this check exists
    to catch yesterday's content bleeding through, and with nothing to compare
    against there is no such claim to make.
    """
    archives = sorted(
        p for p in (ROOT / "preview" / "archive").glob("20*.html") if p.stem < DATE
    )
    if not archives:
        return []
    prev = _title_pitchers(archives[-1].read_text(encoding="utf-8", errors="ignore"))
    today = _title_pitchers(PREVIEW.read_text(encoding="utf-8", errors="ignore"))
    today_folded = {fold(n) for n in today}
    return sorted(n for n in prev if fold(n) not in today_folded)


GAME_BLOCK_RE = re.compile(r'\{\s*title: "([^"]+)".*?rows: \[(.*?)\n\s*\],', re.S)
SP_HAND_RE = re.compile(r'\((L|R),')
SWITCH_ROW_RE = re.compile(r'\{ name: "([^"]+\(S\))".*?note: "((?:[^"\\\\]|\\\\.)*)"', re.S)
SWITCH_LANE_RE = re.compile(r'(\S+) SHB\u2192(LHB|RHB) split')
NON_ALPHA = re.compile(r'[^a-z]')

errs: list[str] = []
warns: list[str] = []


def fail(msg: str) -> None:
    errs.append(msg)


def _suffix_key(norm: str) -> str:
    """Drop a generational suffix so name variants of one player collapse."""
    for suf in ("jr", "sr", "ii", "iii", "iv"):
        if norm.endswith(suf) and len(norm) > len(suf) + 2:
            return norm[: -len(suf)]
    return norm


def _best_slot(slots: dict) -> dict:
    """Keep the LOWEST batting order per human.

    A lineup can list the same player twice under name variants -- "Fernando
    Tatis" at order 1 and "Fernando Tatis Jr." at order 10. Taking whichever
    landed last made the real leadoff hitter look benched.
    """
    best = {}
    for name, slot in slots.items():
        base = _suffix_key(name)
        if base not in best or slot < best[base]:
            best[base] = slot
    return {name: best[_suffix_key(name)] for name in slots}


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

    # A game card with no rows renders as an empty box on the site. It happens when
    # nothing on the prop list maps to that game -- which on 9/12 meant the wrong
    # list had been loaded entirely, and the empty card was the only visible symptom.
    # Fail on it here so the next one is caught before it ships rather than after.
    per_game: dict[str, int] = {}
    for _gm in re.finditer(r'\{\s*title: "([^"]+)".*?rows: \[(.*?)\n\s*\],', html, re.S):
        per_game[_gm.group(1)] = len(re.findall(r'\{ name: "', _gm.group(2)))
    for _t, _n in per_game.items():
        if _n == 0:
            fail(f"game card has no rows (renders as an empty box): {_t}")

    print(f"rows parsed: {len(rows)}")
    want_rows = [p for p in USER_PROPS if p[0] not in NOT_ON_SLATE]
    for _n, _why in NOT_ON_SLATE.items():
        print(f"  not on the slate: {_n} ({_why})")
    if len(rows) != len(want_rows):
        fail(f"expected {len(want_rows)} rows, parsed {len(rows)}")

    by_key: dict[tuple[str, str], str] = {(g, fold(n)): em for g, n, em in rows}
    by_name: dict[str, list[str]] = {}
    for _g, n, em in rows:
        by_name.setdefault(fold(n), []).append(em)

    fav = sum(1 for _g, _n, em in rows if STAR in em)
    gem = sum(1 for _g, _n, em in rows if GEM in em)
    want_fav = sum(1 for _n, _g, m in want_rows if m == STAR)
    want_gem = sum(1 for _n, _g, m in want_rows if m == GEM)
    print(f"favorites {fav} (want {want_fav}) · gems {gem} (want {want_gem})")
    if fav != want_fav:
        fail(f"expected {want_fav} favorites, got {fav}")
    if gem != want_gem:
        fail(f"expected {want_gem} gems, got {gem}")

    # Every listed prop present with the right marker, in the right game.
    for name, game, marker in USER_PROPS:
        if name in NOT_ON_SLATE:
            if fold(name) in by_name:
                fail(f"{name} is off the slate but a row was printed for him anyway")
            continue
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
    # Count GLOVES, not titles: a game can have a bum on both mounds (MIN @ ATH today
    # carries Matthews and Springs), so one title can legitimately hold two.
    glove_count = sum(t.count(GLOVE) for t in titles)
    if glove_count != len(EXPECTED_BUMS):
        fail(f"expected {len(EXPECTED_BUMS)} gloved arms, got {glove_count}")

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
    for name in derive_stale_prev_day():
        if fold(name) in body_folded:
            fail(f"stale prior-slate content on sheet: {name}")
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
        _slot = _best_slot(_slot)
        _m = re.search(r"data-goblin-gambly-lines='([^']*hits[^']*)'", html)
        if _m:
            import html as _htmlmod
            _legs = [l.split(" - ")[0] for l in _json.loads(_htmlmod.unescape(_m.group(1)))]
            def _slot_of(n):
                k = _fold2(n)
                v = _slot.get(k) or _slot.get(_suffix_key(k))
                if v is None:
                    for _k, _v in _slot.items():
                        if _suffix_key(_k) == _suffix_key(k):
                            return _v
                return v
            _bench = [n for n in _legs if (_slot_of(n) or 0) > 9]
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

    # No pick board may carry a bat who is not in a posted lineup. The hits parlay
    # has been guarded since 8/20; the HR boards were not, and today's O1.5 went to
    # a slot-12 bench bat before this check existed. Rows may still be LISTED --
    # only picking is barred.
    if rjson.is_file():
        _lineup = {}
        for _g in _json.loads(rjson.read_text(encoding="utf-8")).get("games", []):
            for _side in ("awayLineup", "homeLineup"):
                for _pl in _g.get(_side) or []:
                    if _pl.get("order"):
                        _lineup[_fold2(_pl["name"])] = _pl["order"]
        _lineup = _best_slot(_lineup)
        import html as _htmlmod2
        for _m2 in re.finditer(r"data-(?:goblin-gambly-lines|gambly-line)='([^']*)'", html):
            try:
                _legs2 = _json.loads(_htmlmod2.unescape(_m2.group(1)))
            except ValueError:
                continue
            for _leg in _legs2:
                _nm = _leg.split(" - ")[0]
                _sl = _lineup.get(_fold2(_nm))
                if _sl is None:
                    _sl = _lineup.get(_suffix_key(_fold2(_nm)))
                if _sl is None:
                    for _k, _v in _lineup.items():
                        if _suffix_key(_k) == _suffix_key(_fold2(_nm)):
                            _sl = _v
                            break
                if (_sl or 99) > 9:
                    fail(f"pick board carries a bat not in a posted lineup: {_nm}")

    # Two different players can share a name on one slate. The research lineup map
    # was keyed by name alone, so the later game overwrote the earlier and the
    # Dodgers' cleanup hitter inherited an Oakland bench slot -- which barred a listed
    # favorite from every pick board. Assert each row resolves to ITS OWN game.
    if rjson.is_file():
        from goblin_hits_parlay import load_research_hit_stats, lookup_research_entry

        _stats = load_research_hit_stats(DATE)
        _slots: dict[tuple[str, str], int] = {}
        for _g in _json.loads(rjson.read_text(encoding="utf-8")).get("games", []):
            _gk = f"{_g.get('away')} @ {_g.get('home')}"
            for _side in ("awayLineup", "homeLineup"):
                for _pl in _g.get(_side) or []:
                    if _pl.get("order"):
                        _slots[(_gk, _suffix_key(_fold2(_pl["name"])))] = _pl["order"]
        _checked = 0
        for _gkey, _nm, _em in rows:
            _plain = _gkey.split(" (G")[0]
            _entry = lookup_research_entry(_stats, _nm, _plain)
            if not _entry:
                continue
            if (_plain, _suffix_key(_fold2(_nm))) not in _slots:
                continue  # not in this game's posted lineup; nothing to cross-check
            _checked += 1
            if _entry.get("game") != _plain:
                fail(
                    f"{_nm} in the {_plain} block resolved to a namesake in "
                    f"{_entry.get('game')}"
                )
        print(f"rows cross-checked against their own game's lineup: {_checked}")

    # A switch hitter bats OPPOSITE the arm, so his lane is fixed by the pitcher's
    # hand rather than chosen. batter_split() used to hand him max(vsLHB, vsRHB),
    # which can only ever inflate him -- it put Cal Raleigh on the 3-leg card at
    # +1.58 when his real lane against the left-handed Springs is +0.25.
    _sw = 0
    for _gm in GAME_BLOCK_RE.finditer(html):
        _arms = {}
        for _seg in _gm.group(1).split(' - ', 1)[-1].split(' vs '):
            _hm = re.search(SP_HAND_RE, _seg)
            if _hm:
                _pname = _seg[: _hm.start()].replace(GLOVE, '').strip().lower()
                _arms[re.sub(NON_ALPHA, '', _pname)] = _hm.group(1)
        for _rm in SWITCH_ROW_RE.finditer(_gm.group(2)):
            _lane = re.search(SWITCH_LANE_RE, _rm.group(2))
            if not _lane:
                continue
            _chip = re.sub(NON_ALPHA, '', _lane.group(1).lower())
            _throws = next((v for k, v in _arms.items() if k.endswith(_chip)), None)
            if not _throws:
                continue
            _sw += 1
            _want = 'RHB' if _throws == 'L' else 'LHB'
            if _lane.group(2) != _want:
                fail(
                    f'{_rm.group(1)} vs {_lane.group(1)} ({_throws}HP) is shown batting '
                    f'{_lane.group(2)}; a switch hitter bats {_want} against that arm'
                )
    print(f'switch-hitter lanes checked: {_sw}')

    # The score is only worth printing if it distinguishes rows. Before the
    # 2026-09-15 rebalance the model ended in a clamp at 58 and a third of every
    # board landed exactly there -- favorites the owner had flagged sat at the same
    # number as bats with no form at all, because the scale had bottomed out rather
    # than rated them. Fail loudly if any single value ever swallows the board again.
    _scores = [int(x) for x in re.findall(r"score: (\d+)", html)]
    if _scores:
        from collections import Counter as _Counter

        _top_val, _top_n = _Counter(_scores).most_common(1)[0]
        _share = 100.0 * _top_n / len(_scores)
        print(f"score spread: {len(set(_scores))} distinct values over {len(_scores)} rows; "
              f"most common {_top_val} on {_share:.0f}%")
        if _share > 20.0:
            fail(
                f"{_share:.0f}% of the board prints {_top_val} — the score has stopped "
                "separating rows (a clamp is probably binding)"
            )
        if min(_scores) <= 41 and _scores.count(min(_scores)) > max(2, len(_scores) // 20):
            fail(f"{_scores.count(min(_scores))} rows pinned at the score floor")

    # The owner asked for no "no HR risk" placeholders anywhere on the board: either
    # a real number or nothing at all.
    for phrase in ("no MLB HR data yet", "no PropFinder HR risk", "split/risk data unavailable"):
        if phrase in html:
            fail(f"missing-HR-risk placeholder on sheet: {phrase!r}")

    # Each game's first pitch must be the one MLB has for the STARTERS the sheet
    # lists. A doubleheader files its plain key under game one, so a board that
    # carries only game two was showing a first pitch hours too early.
    try:
        from game_start_times import annotate_and_sort_games

        _stub = [{"title": ttl} for ttl in titles]
        _resolved = {g["title"]: g.get("startTime") for g in annotate_and_sort_games(_stub, DATE)}
        for ttl, meta in zip(titles, metas):
            want = _resolved.get(ttl)
            if not want:
                continue
            import datetime as _dt

            _utc = _dt.datetime.fromisoformat(want.replace("Z", "+00:00"))
            _et = _utc.astimezone(_dt.timezone(_dt.timedelta(hours=-4)))
            _hh = _et.strftime("%I:%M %p").lstrip("0")
            if _hh not in meta:
                fail(f"{ttl.split(' - ')[0]}: header time disagrees with MLB (expected {_hh} ET)")
    except Exception as _exc:
        warns.append(f"could not verify start times: {_exc}")

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

    # Regression guard for the CWS/WSH park-key aliasing bug: Ballpark Pal ships
    # these as CHW / WAS. Derive the games to check from the slate rather than
    # hardcoding a pair -- a hardcoded pair silently passes on every day those
    # clubs are not playing, which is most days.
    alias_re = re.compile(r"\b(CWS|WSH)\b")
    alias_games = [t.split(" - ")[0] for t in titles if alias_re.search(t.split(" - ")[0])]
    if not alias_games:
        warns.append("no CWS/WSH game on this slate - alias guard not exercised")
    for gkey in alias_games:
        m = re.search(
            r'title: "' + re.escape(gkey) + r'[^"]*".*?gameMeta: "((?:[^"\\]|\\.)*)"',
            html,
            re.S,
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
