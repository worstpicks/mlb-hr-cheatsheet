#!/usr/bin/env python3
"""Hits parlay leg selection — contact + zone fit across the full slate.

Canonical rubric for all future MLB cheat sheet slates. Patch scripts should
import from here (see .cursor/rules/mlb-hr-slate-workflow.mdc — Hits parlay rubric).
Do not duplicate this logic inline in patch-YYYY-MM-DD-preview.py.

Design goals (revised Aug 2026 after a 76-slate backtest):
- Rank on a CALIBRATED P(1+ hit), not an arbitrary score, so leg count is a
  conscious decision instead of an accident.
- Expected plate appearances is the dominant term. Across 76 slates of
  boxscores the implied hit rate PER PA is nearly flat by lineup slot
  (.200-.223), while E[PA] runs 4.54 leadoff down to 3.45 in the nine hole.
  That PA gap alone is the whole 68% -> 55% spread in P(1+ hit) by slot, and
  the pre-Aug rubric did not model batting order at all.
- Judge the opposing starter on BAA in the hitter's hand lane, not on the HR
  platoon split. HR risk answers "will this leave the yard", which is the
  wrong question for a hits ticket.
- Use the park's 1B factor, not its HR factor, for the same reason.
- Cover the whole cheat sheet; spread legs across games.

Measured on 47 dates with both an archived ticket and a research JSON:
  old rubric legs   .609 per leg,  0/76 tickets ever cashed
  this model top-11 .654 per leg,  0/47
  this model top- 8 .657 per leg,  1/47
  this model top- 5 .681 per leg,  7/47  (predicted 14.6%, actual 14.9%)
The card intentionally ships all 11 as a "Hits Lotto" -- a long shot by design.
The rubric change roughly doubles that lotto's odds (.609 -> .654 per leg, ~0.6%
-> ~1.5% for the full ticket) rather than shortening it. See TICKET_LEGS.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path
from typing import Callable

# Hits still happen on tough platoon lanes — only extreme headwinds are hard-cut.
# Ranking applies a soft split penalty so deep negatives need elite contact to climb.
SPLIT_HARD_FLOOR = -0.85
SPLIT_SOFT_FLOOR = -0.15

# Empirical expected plate appearances by lineup slot, from 76 slates of MLB
# boxscores (starters only, ~1950 samples per slot). This is the single largest
# driver of P(1+ hit) and the reason a nine-hole bat is a bad hits leg however
# well he is swinging.
SLOT_EXPECTED_PA = {1: 4.54, 2: 4.44, 3: 4.34, 4: 4.22, 5: 4.09,
                    6: 3.92, 7: 3.78, 8: 3.61, 9: 3.45}
DEFAULT_EXPECTED_PA = 3.95

# The research JSON lists a team's whole available group, not just the nine who
# start: slots 1-9 are the batting order and anything above is bench/depth. On
# 2026-08-17 that is how Ohtani, Freeman, Betts, Goodman, McCarthy and Moniak all
# appear -- each genuinely out of the lineup, confirmed against the MLB boxscore.
# A bench bat is a pinch-hit appearance at best and must never be a hits leg.
LAST_STARTING_SLOT = 9
BENCH_EXPECTED_PA = 1.1

LEAGUE_P_HIT_PER_PA = 0.208   # same sample
LEAGUE_BAA = 0.245
LEAGUE_K_PCT = 0.222
AB_PER_PA = 0.88              # AVG is per AB; convert to a per-PA rate
BAT_SHRINK_PA = 150

# Measured calibration, re-fit 2026-08-17 against the full implemented rubric.
# The research window is last-20-games, so hitters rank top partly because their
# recent form is running hot -- classic selection bias, and it does not wash out.
# Uncalibrated, the model predicted .728 per leg where the shipped top-11 actually
# hit .6615 across 47 slates. This factor lines predicted up with realized. It is
# the only reason the displayed parlay probability means anything, so re-fit it
# with _hits_final_backtest.py whenever the formula changes.
SELECTION_CALIBRATION = 0.74

# The card ships ELEVEN legs. This is a deliberate product decision -- the Hits
# Lotto is meant to be a long shot with a big payout, not a high-probability
# ticket. Do not "fix" it down to 5: that trade has already been considered and
# rejected by the sheet's owner.
#
# What the rubric change bought the lotto is a better long shot, not a short one.
# On the same 47 backtested slates the old rubric's top 11 hit .609 per leg
# (P(all 11) ~ 0.6%) where this model's top 11 hit .654 (~1.5%) -- roughly double
# the chance of the lotto ever landing.
TICKET_LEGS = 11

# Informational only: the highest-probability subset, for anyone who wants to see
# where the safe ticket would have stopped. Not what the card renders.
CORE_LEGS = 5

# Spread, but far less than before. Capping at 2 per game was portfolio thinking,
# and an all-must-hit ticket is not a portfolio: there is no diversification benefit,
# and same-game legs are positively correlated (one good offensive night lifts
# several), which HELPS the ticket. The old cap simply forced worse legs on.
# Backtest, top-11 realized: cap 2 .6480 | cap 3 .6576 | uncapped .6615.
# Cap 4 keeps almost all of that and still spreads the card across the slate.
MAX_PER_GAME = 4
MAX_PER_TEAM = 3

# Soft floor on season sample. Thin-sample bats rank on noise; requiring a real
# sample lifted top-11 from .6615 to .6673. Relaxed automatically if too few qualify.
MIN_SEASON_PA = 150

_ROOT = Path(__file__).resolve().parent


def _norm_name(name: str) -> str:
    """Accent-insensitive join key: 'J. Peña (R)' -> 'jpena'."""
    base = unicodedata.normalize("NFKD", name or "")
    base = "".join(c for c in base if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", base.lower())


_NAME_SUFFIXES = ("jr", "sr", "ii", "iii", "iv")


def _suffix_key(norm: str) -> str:
    """Normalised name with a generational suffix removed, for merging variants."""
    for suf in _NAME_SUFFIXES:
        if norm.endswith(suf) and len(norm) > len(suf) + 2:
            return norm[: -len(suf)]
    return norm


def load_research_hit_stats(sheet_date: str, root: Path | None = None) -> dict[str, dict]:
    """Per-batter contact stats from the Research tab JSON (Savant-backed).

    Returns norm-name -> {lineup_slot, bip_pct, avg_bat, xwoba_bat, ld_pct,
    sweet_spot_pct, pa_bat}.
    Missing file returns {} so slates without research data still build.
    """
    path = (root or _ROOT) / "preview" / "data" / f"research-{sheet_date}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    savant = data.get("savant_lookup") or {}
    out: dict[str, dict] = {}
    for game in data.get("games") or []:
        for side, opp_key in (("awayLineup", "homePitcher"), ("homeLineup", "awayPitcher")):
            throws = ((game.get(opp_key) or {}).get("throws") or "R").upper()
            for player in game.get(side) or []:
                stats = player.get("stats") or {}
                sv = savant.get(str(player.get("id"))) or {}
                # The hitter's own line against this arm's hand.
                if throws == "L":
                    plat, plat_pa = stats.get("xwobaVsLhp"), stats.get("paVsLhp")
                else:
                    plat, plat_pa = stats.get("xwobaVsRhp"), stats.get("paVsRhp")
                entry = {
                    # Batting order drives expected PA, which drives P(1+ hit).
                    "lineup_slot": player.get("order"),
                    "bip_pct": stats.get("bipPct", sv.get("bipPct")),
                    "avg_bat": stats.get("avg", sv.get("avg")),
                    "xwoba_bat": stats.get("xwoba", sv.get("xwoba")),
                    "ld_pct": stats.get("ldPct", sv.get("ldPct")),
                    "sweet_spot_pct": sv.get("sweetSpotPct", stats.get("sweetSpotPct")),
                    "pa_bat": stats.get("pa", sv.get("pa")),
                    # Season sample, kept separate so the model can weight it above
                    # the noisy last-20-game window instead of silently falling back.
                    "avg_season": sv.get("avg"),
                    "pa_season": sv.get("pa"),
                    "k_pct_season": sv.get("kPct"),
                    "k_pct_recent": stats.get("kPct"),
                    "platoon_xwoba": plat,
                    "platoon_pa": plat_pa,
                }
                entry["game"] = f"{game.get('away')} @ {game.get('home')}"
                entry["player_id"] = player.get("id")
                entry["name_research"] = player.get("name")
                key = _norm_name(player.get("name") or "")
                if not key or not any(v is not None for v in entry.values()):
                    continue
                prior = out.get(key)
                if prior is None:
                    out[key] = entry
                elif prior.get("player_id") != entry.get("player_id"):
                    # Two DIFFERENT humans share this name on the same slate --
                    # Oakland's right-handed Max Muncy and the Dodgers' left-handed
                    # one, both listed on 2026-09-05. Keying by name alone made the
                    # later game overwrite the earlier, so the Dodgers' cleanup
                    # hitter inherited the Athletic's bench slot and was barred from
                    # every pick board. Keep both and let the caller pick by game.
                    prior.setdefault("_alts", []).append(entry)
                    entry["_alts"] = prior["_alts"]

    # A lineup can list the same human twice under name variants -- San Diego on
    # 2026-09-01 carried "Fernando Tatis" at order 1 and "Fernando Tatis Jr." at
    # order 10. Keyed separately, the suffixed form looked like a bench bat and
    # got the real leadoff hitter barred from every pick board. Collapse the
    # variants and give every spelling the best (lowest) batting order.
    # Scope the merge to one game: the two spellings of a name inside a single
    # lineup are one player, but the same name in two different games is not, and
    # a slate-wide minimum would hand a bench bat his namesake's batting order.
    best: dict[tuple[str, str], int] = {}
    for entry in _all_entries(out):
        slot = entry.get("lineup_slot")
        if slot is None:
            continue
        ident = (entry.get("game") or "", _suffix_key(_norm_name(entry.get("name_research") or "")))
        if ident not in best or slot < best[ident]:
            best[ident] = slot
    for entry in _all_entries(out):
        ident = (entry.get("game") or "", _suffix_key(_norm_name(entry.get("name_research") or "")))
        if ident in best:
            entry["lineup_slot"] = best[ident]
    return out


def _all_entries(stats: dict) -> list[dict]:
    """Every research row, including same-name alternates parked under _alts."""
    seen, out = set(), []
    for entry in stats.values():
        for cand in [entry, *(entry.get("_alts") or [])]:
            if id(cand) not in seen:
                seen.add(id(cand))
                out.append(cand)
    return out


def _pick_candidate(entry: dict, game: str | None) -> dict:
    """Choose between hitters who share a name: by game if known, else by slot.

    Falling back to the lowest starting slot is deliberate. A prop is written for
    the hitter a book priced, and books price the man who is playing -- so when the
    board cannot say which game it means, the starter is the better guess than a
    bench bat who happens to sort later.
    """
    cands = [entry, *(entry.get("_alts") or [])]
    if len(cands) == 1:
        return entry
    if game:
        plain = game.split(" (G")[0]
        for cand in cands:
            if cand.get("game") == plain:
                return cand
    return min(cands, key=lambda c: (c.get("lineup_slot") is None, c.get("lineup_slot") or 99))


def _nickname_match(stats: dict, key: str) -> dict | None:
    """Last resort: same surname, one first name a prefix of the other.

    MLB's lineup feed calls St. Louis's catcher "Leo Bernal" while both the prop
    list and the PropFinder export say "Leonardo Bernal". An exact key misses, and
    downstream that reads as "not in a posted lineup" -- it barred a starting
    catcher on 2026-09-05. Only an unambiguous single match is accepted.
    """
    hits = []
    for k, v in stats.items():
        if k == key or len(k) < 5 or len(key) < 5:
            continue
        # names normalise to one run of letters, so compare from both ends
        if k.endswith(key[-6:]) or key.endswith(k[-6:]):
            short, long = sorted((k, key), key=len)
            if long.startswith(short[:3]) and long.endswith(short[-4:]):
                hits.append(v)
    uniq = {id(h): h for h in hits}
    return next(iter(uniq.values())) if len(uniq) == 1 else None


def lookup_research_entry(stats: dict, name: str, game: str | None = None) -> dict | None:
    """Find a batter's research row, tolerating a generational suffix either way.

    The prop list and the lineup feed disagree about "Jr." in both directions --
    "LaMonte Wade Jr." on the board against "LaMonte Wade" in the lineup, and
    "Fernando Tatis Jr." against "Fernando Tatis". An exact-key lookup silently
    returns nothing, which reads downstream as "not in the lineup".

    Pass `game` ("AWY @ HOM") whenever the caller knows it: two different players
    can share a name on one slate, and only the game tells them apart.
    """
    if not stats:
        return None
    key = _norm_name(name)
    hit = stats.get(key)
    if hit is not None:
        return _pick_candidate(hit, game)
    base = _suffix_key(key)
    if base != key and base in stats:
        return _pick_candidate(stats[base], game)
    # the stored name may be the suffixed one instead
    for k, v in stats.items():
        if _suffix_key(k) == base:
            return _pick_candidate(v, game)
    nick = _nickname_match(stats, key)
    return _pick_candidate(nick, game) if nick else None


def attach_research_hit_stats(
    rows: list[dict], sheet_date: str, root: Path | None = None
) -> int:
    """Merge research-tab contact stats onto ranked rows by batter name."""
    lookup = load_research_hit_stats(sheet_date, root=root)
    if not lookup:
        return 0
    matched = 0
    for row in rows:
        entry = lookup_research_entry(
            lookup,
            row.get("name_plain") or row.get("name") or "",
            row.get("game"),
        )
        if entry:
            row.update(entry)
            matched += 1
    return matched


def load_sp_lane_baa(sheet_date: str, root: Path | None = None) -> dict[str, dict]:
    """Opposing starter BAA and K% split by batter hand, from this slate's exports.

    A hits ticket lives or dies on whether the arm allows base hits. The HR
    platoon split the board already carries answers a different question.
    """
    data_dir = (root or _ROOT) / "data"
    out: dict[str, dict] = {}
    for path in data_dir.glob(f"hr-matchups-*-{sheet_date}.csv"):
        try:
            lines = path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
        except OSError:
            continue
        pitcher = next((l.split(",", 1)[1].strip() for l in lines if l.startswith("Pitcher,")), None)
        idx = next((i for i, l in enumerate(lines) if l.split(",")[0].strip() == "SPLIT"), None)
        if not pitcher or idx is None:
            continue
        header = [c.strip() for c in next(csv.reader([lines[idx]]))]
        lane: dict[str, dict] = {}
        for line in lines[idx + 1 : idx + 4]:
            row = next(csv.reader([line]), None)
            if not row or row[0] not in ("vsLHB", "vsRHB"):
                continue
            rec = dict(zip(header, row))

            def num(key: str) -> float | None:
                try:
                    return float((rec.get(key) or "").strip().replace("%", "")) or None
                except ValueError:
                    return None

            lane["L" if row[0] == "vsLHB" else "R"] = {"baa": num("BAA"), "k_pct": num("K%")}
        if lane:
            out[_norm_name(pitcher)] = lane
            # Chips carry the short name, so index the last token too.
            out.setdefault(_norm_name(pitcher.split()[-1]), lane)
    return out


def load_park_hit_pct(sheet_date: str, root: Path | None = None) -> dict[str, int]:
    """Ballpark Pal 1B % per game key — the hits analogue of the HR park factor."""
    data_dir = (root or _ROOT) / "data"
    matches = sorted(data_dir.glob(f"ParkFactors_{sheet_date}*.csv"))
    if not matches:
        return {}
    by_game: dict[str, list[tuple[str, int]]] = {}
    with matches[0].open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            key = " ".join((row.get("Game") or "").split()).upper()
            m = re.search(r"([+-]?\d+)", (row.get("1B %") or "").replace("%", ""))
            if key and m:
                by_game.setdefault(key, []).append(((row.get("Time") or "").strip(), int(m.group(1))))

    def tkey(t: str) -> int:
        mm = re.match(r"^(\d{1,2}):(\d{2})", t or "")
        if not mm:
            return 9999
        h, mi = int(mm.group(1)), int(mm.group(2))
        return ((h + 12) if 1 <= h <= 11 else h) * 60 + mi

    out: dict[str, int] = {}
    for key, entries in by_game.items():
        entries.sort(key=lambda e: tkey(e[0]))
        out[key] = entries[0][1]
        for i, (_t, v) in enumerate(entries, 1):
            out[f"{key} (G{i})"] = v
    return out


def is_starting(row: dict) -> bool:
    """False only when we positively know the hitter is not in the batting order."""
    slot = row.get("lineup_slot")
    if slot is None:
        return True  # no lineup data yet — do not punish the hitter
    try:
        return int(slot) <= LAST_STARTING_SLOT
    except (TypeError, ValueError):
        return True


def expected_pa(row: dict) -> float:
    slot = row.get("lineup_slot")
    if slot is None:
        return DEFAULT_EXPECTED_PA
    try:
        slot = int(slot)
    except (TypeError, ValueError):
        return DEFAULT_EXPECTED_PA
    if slot > LAST_STARTING_SLOT:
        return BENCH_EXPECTED_PA
    return SLOT_EXPECTED_PA.get(slot, DEFAULT_EXPECTED_PA)


def _contact_quality_mult(row: dict) -> float:
    """Bounded nudge from the signals the old rubric ranked on directly."""
    mult = 1.0
    weight = _research_sample_weight(row)
    bip = row.get("bip_pct")
    if bip is not None:
        mult += max(-0.06, min(0.06, (bip - 66.0) / 200.0)) * weight
    xwoba = row.get("xwoba_bat")
    if xwoba is not None:
        mult += max(-0.05, min(0.05, (xwoba - 0.310) / 2.0)) * weight
    ld = row.get("ld_pct")
    if ld is not None:
        mult += max(-0.03, min(0.04, (ld - 20.0) / 250.0)) * weight
    zc = row.get("zone_contact")
    if zc is not None:
        mult += max(-0.04, min(0.05, (zc - 26.0) / 300.0))
    for pct in (row.get("whiff_pct"), row.get("k_pct")):
        if pct is not None and pct >= 24.0:
            mult -= min(0.10, (pct - 24.0) / 120.0)
    return max(0.78, min(1.20, mult))


def _blend_recent_season(recent, season, w_season: float = 0.65):
    """Season carries most of the weight — the last-20-game window is noisy."""
    if recent is None:
        return season
    if season is None:
        return recent
    return recent * (1 - w_season) + season * w_season


def hit_probability(row: dict) -> float:
    """Calibrated P(1+ hit) = 1 - (1 - p_PA) ** E[PA].

    p_PA is built as (1 - strikeout rate) x hit-rate-on-contact rather than by
    penalising strikeouts vaguely: a PA that ends in a K cannot become a hit, so
    the structure belongs in the model. Contact rate blends the season sample with
    the recent window, weighted to season.
    """
    avg = _blend_recent_season(row.get("avg_bat"), row.get("avg_season"))
    pa_sample = max(row.get("pa_bat") or 0, row.get("pa_season") or 0)
    if avg is None:
        base = LEAGUE_P_HIT_PER_PA
    else:
        weight = min(pa_sample, BAT_SHRINK_PA) / BAT_SHRINK_PA
        base = (avg * AB_PER_PA) * weight + LEAGUE_P_HIT_PER_PA * (1 - weight)

    # Strikeout structure: batter's own K rate, pulled toward the arm he faces.
    bat_k = _blend_recent_season(row.get("k_pct"), row.get("k_pct_season"))
    bat_k = LEAGUE_K_PCT * 100 if bat_k is None else bat_k
    bat_k = max(0.08, min(0.42, bat_k / 100.0))
    sp_k = row.get("sp_lane_k_pct")
    sp_k = LEAGUE_K_PCT if not sp_k else max(0.10, min(0.38, sp_k / 100.0))
    combined_k = max(0.08, min(0.45, (bat_k + sp_k) / 2 + (bat_k - LEAGUE_K_PCT) * 0.35))
    p = (1 - combined_k) * (base / (1 - LEAGUE_K_PCT))

    baa = row.get("sp_lane_baa")
    if baa:
        p *= max(0.82, min(1.20, baa / LEAGUE_BAA))
    park_1b = row.get("park_1b_pct")
    if park_1b:
        p *= 1 + park_1b / 300.0

    # The hitter's own xwOBA against this arm's hand, when the sample is real.
    xw, xw_pa = row.get("platoon_xwoba"), row.get("platoon_pa") or 0
    if xw is not None and xw_pa >= 40:
        p *= max(0.88, min(1.14, 1 + (xw - 0.320) * 0.55))

    p *= _contact_quality_mult(row)
    p *= SELECTION_CALIBRATION
    p = max(0.08, min(0.32, p))
    return 1 - (1 - p) ** expected_pa(row)


def zone_hits_fit(row: dict) -> float:
    """Pitch-zone fit for O0.5 hits — contact first, overall zone second."""
    zone_score = row.get("zone_score") or 0.0
    zone_contact = row.get("zone_contact")
    zone_hard_hit = row.get("zone_hard_hit")
    zone_barrel = row.get("zone_barrel")

    # Contact in the zone is the primary hits signal.
    fit = 0.0
    if zone_contact is not None:
        fit += zone_contact * 1.15
        fit += max(zone_contact - 28.0, 0.0) * 0.55
    else:
        # Missing zone-contact: fall back to overall zone score at a discount.
        fit += zone_score * 0.85

    # Overall zone still matters, but less than for HR boards.
    fit += zone_score * 0.55

    if zone_hard_hit is not None:
        fit += max(zone_hard_hit - 20.0, 0.0) * 0.35
    if zone_barrel is not None:
        # Light barrel bump — barrels help, but this is a hits ticket.
        fit += max(zone_barrel - 14.0, 0.0) * 0.12
    return fit


def contact_hit_form(row: dict) -> float:
    """Recent contact profile — EV / hard contact over HR counting stats."""
    ev = row.get("ev") or 0.0
    hh = row.get("hh_pct")
    barrel = row.get("barrel") or 0.0
    gb = row.get("gb_pct")

    form = 0.0
    # Solid contact EV band for singles/doubles (not just moonshots).
    if ev >= 86.0:
        form += min(ev - 86.0, 12.0) * 0.55
    if hh is not None:
        form += max(hh - 35.0, 0.0) * 0.12
    # Light recent-event signal (presence of contact events, not HR chase).
    form += min(row.get("hr") or 0, 2) * 0.6
    form += min(row.get("near") or 0, 3) * 0.45
    form += min(barrel, 20.0) / 12.0

    # Ground-ball heavy profiles still get hits; don't punish them.
    if gb is not None and 35.0 <= gb <= 55.0:
        form += 1.2

    whiff = row.get("whiff_pct")
    k_pct = row.get("k_pct")
    for pct in (whiff, k_pct):
        if pct is not None and pct <= 22.0:
            form += (22.0 - pct) * 0.22
        elif pct is not None and pct <= 26.0:
            form += (26.0 - pct) * 0.08
    return form


def _research_sample_weight(row: dict) -> float:
    """Discount research terms on thin season samples (<60 PA)."""
    pa = row.get("pa_bat")
    if pa is None:
        return 1.0
    if pa >= 60:
        return 1.0
    return max(pa, 0) / 60.0


def bip_opportunity(row: dict) -> float:
    """Ball-in-play % (Research tab) — the core hits-opportunity signal.

    Slate median sits near 68%; reward high-BIP bats (more chances at a hit),
    drag low-BIP swing-and-miss profiles. Capped so it complements zone fit
    rather than dominating it.
    """
    bip = row.get("bip_pct")
    if bip is None:
        return 0.0
    edge = bip - 66.0
    if edge >= 0.0:
        term = min(edge, 18.0) * 0.65
    else:
        term = max(edge, -20.0) * 0.50
    return term * _research_sample_weight(row)


def research_contact_form(row: dict) -> float:
    """Season hit quality from the Research tab — AVG, xwOBA, LD%, sweet spot."""
    form = 0.0
    avg = row.get("avg_bat")
    if avg is not None:
        form += (avg - 0.240) * 40.0
    xwoba = row.get("xwoba_bat")
    if xwoba is not None:
        form += (xwoba - 0.310) * 25.0
    ld = row.get("ld_pct")
    if ld is not None:
        form += max(ld - 20.0, 0.0) * 0.15
    sweet = row.get("sweet_spot_pct")
    if sweet is not None:
        form += max(sweet - 32.0, 0.0) * 0.10
    return form * _research_sample_weight(row)


def whiff_penalty(row: dict, *, row_high_whiff: Callable[..., bool]) -> float:
    penalty = 0.0
    for pct in (row.get("whiff_pct"), row.get("k_pct")):
        if pct is not None and pct >= 20.0:
            penalty = max(penalty, (pct - 19.0) * 2.4)
    if row_high_whiff(row, for_hits=True):
        penalty += 45.0
    return penalty


def split_adjustment(row: dict) -> float:
    """Soft platoon edge — reward +split, light penalty for mild headwinds."""
    split = row.get("split") or 0.0
    if split >= 0.0:
        return split * 5.5
    if split >= SPLIT_SOFT_FLOOR:
        return split * 3.0  # mild headwind: small drag
    if split >= SPLIT_HARD_FLOOR:
        return split * 5.0  # deeper headwind: stronger drag, still eligible
    return split * 8.0


def compute_hits_rank(row: dict, *, row_high_whiff: Callable[..., bool]) -> float:
    """Rank = calibrated P(1+ hit), with the legacy terms as a small tiebreak.

    The probability carries the decision (expected PA, opposing-arm BAA lane,
    park 1B, contact quality). The old zone/contact score is kept at low weight
    to separate hitters the probability model rates identically -- it must not
    be able to reorder them, which is what produced nine-hole legs before.
    """
    prob = hit_probability(row)
    row["hit_prob"] = prob

    tiebreak = (
        zone_hits_fit(row) * 0.010
        + contact_hit_form(row) * 0.008
        + bip_opportunity(row) * 0.006
        + research_contact_form(row) * 0.006
        + split_adjustment(row) * 0.004
        - whiff_penalty(row, row_high_whiff=row_high_whiff) * 0.010
    )
    return prob * 100.0 + max(-3.0, min(3.0, tiebreak))


def attach_matchup_hit_context(rows: list[dict], sheet_date: str, root: Path | None = None) -> int:
    """Merge opposing-arm BAA/K% lane and park 1B factor onto ranked rows."""
    lanes = load_sp_lane_baa(sheet_date, root=root)
    parks = load_park_hit_pct(sheet_date, root=root)
    matched = 0
    for row in rows:
        chip = (row.get("chip") or "").strip()
        lane = lanes.get(_norm_name(chip)) or lanes.get(_norm_name(chip.split()[-1] if chip else ""))
        if lane:
            side = lane.get("L" if (row.get("hand") or "R") == "L" else "R") or {}
            if side.get("baa"):
                row["sp_lane_baa"] = side["baa"]
            if side.get("k_pct"):
                row["sp_lane_k_pct"] = side["k_pct"]
            matched += 1
        gkey = (row.get("game_key") or "").upper()
        if gkey in parks:
            row["park_1b_pct"] = parks[gkey]
    return matched


def annotate_hits_ranks(
    rows: list[dict],
    *,
    row_high_whiff: Callable[..., bool],
    sheet_date: str | None = None,
) -> None:
    if sheet_date:
        attach_research_hit_stats(rows, sheet_date)
        attach_matchup_hit_context(rows, sheet_date)
    for row in rows:
        row["hits_rank"] = compute_hits_rank(row, row_high_whiff=row_high_whiff)
        row["hits_zone_fit"] = zone_hits_fit(row)
        row["expected_pa"] = expected_pa(row)


def parlay_probability(legs: list[dict]) -> float:
    """Naive independent P(all legs hit) — the number that makes leg count honest."""
    p = 1.0
    for leg in legs:
        p *= leg.get("hit_prob") or hit_probability(leg)
    return p


def _has_hit_form(row: dict) -> bool:
    return (
        (row.get("hr") or 0) >= 1
        or (row.get("near") or 0) >= 1
        or (row.get("ev") or 0) >= 88
        or (row.get("hh_pct") or 0) >= 40
        # Research tab: high ball-in-play rate or strong hit tool counts as form.
        or (row.get("bip_pct") or 0) >= 72
        or (row.get("avg_bat") or 0) >= 0.280
    )


def hits_base_pool(candidates: list[dict]) -> list[dict]:
    """Contact/zone pool across the slate; relax only if we cannot fill 11 legs."""

    def qualifies(r: dict, *, min_zone: float, min_contact: float, split_floor: float) -> bool:
        if (r.get("split") or 0.0) < split_floor:
            return False
        if not is_starting(r):
            return False
        # A bat the probability model likes is in regardless of zone thresholds.
        # The old gates were zone-first, so a top-of-order hitter with a thin zone
        # sample could be filtered out while a nine-hole bat with a loud zone score
        # walked onto the ticket -- exactly the trade the backtest showed losing.
        if (r.get("hit_prob") or 0.0) >= 0.58:
            return True
        zone = r.get("zone_score") or 0.0
        z_contact = r.get("zone_contact") or 0.0
        # Strong zone-contact alone is enough for hits.
        if z_contact >= min_contact:
            return True
        if zone >= min_zone and z_contact >= min_contact - 6:
            return True
        if zone >= min_zone + 4:
            return True
        if z_contact >= min_contact - 4 and _has_hit_form(r):
            return True
        if zone >= min_zone - 2 and _has_hit_form(r):
            return True
        return False

    def sampled(rows: list[dict]) -> list[dict]:
        """Drop thin-sample bats when the slate can still fill the ticket without them."""
        deep = [r for r in rows if (r.get("pa_season") or r.get("pa_bat") or 0) >= MIN_SEASON_PA]
        return deep if len(deep) >= TICKET_LEGS else rows

    strict = [
        r
        for r in candidates
        if qualifies(r, min_zone=16.0, min_contact=26.0, split_floor=SPLIT_HARD_FLOOR)
    ]
    if len(strict) >= 11:
        return sampled(strict)

    relaxed = [
        r
        for r in candidates
        if qualifies(r, min_zone=12.0, min_contact=22.0, split_floor=SPLIT_HARD_FLOOR)
    ]
    if len(relaxed) >= 11:
        return sampled(relaxed)

    fallback = [
        r
        for r in candidates
        if (r.get("split") or 0.0) >= SPLIT_HARD_FLOOR
        and (
            (r.get("zone_score") or 0) >= 10
            or (r.get("zone_contact") or 0) >= 20
            or _has_hit_form(r)
        )
    ]
    if fallback:
        return fallback
    return [r for r in candidates if (r.get("split") or 0.0) >= -0.55]


def _pick_diverse(pool: list[dict], n: int) -> list[dict]:
    """Take top ranks with per-game / per-team caps so the ticket spans the slate."""
    legs: list[dict] = []
    seen: set[str] = set()
    game_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}

    for row in pool:
        if row["name"] in seen:
            continue
        game = row.get("game_key") or ""
        team = row.get("team") or ""
        if game and game_counts.get(game, 0) >= MAX_PER_GAME:
            continue
        if team and team_counts.get(team, 0) >= MAX_PER_TEAM:
            continue
        seen.add(row["name"])
        legs.append(row)
        if game:
            game_counts[game] = game_counts.get(game, 0) + 1
        if team:
            team_counts[team] = team_counts.get(team, 0) + 1
        if len(legs) == n:
            break

    # If diversity caps left us short, fill remaining by rank without caps.
    if len(legs) < n:
        for row in pool:
            if row["name"] in seen:
                continue
            seen.add(row["name"])
            legs.append(row)
            if len(legs) == n:
                break
    return legs


def select_hits_parlay(
    candidates: list[dict],
    *,
    row_high_whiff: Callable[..., bool],
    avoid_whiff: bool = True,
    n: int = TICKET_LEGS,
    sheet_date: str | None = None,
) -> list[dict]:
    annotate_hits_ranks(candidates, row_high_whiff=row_high_whiff, sheet_date=sheet_date)
    pool = hits_base_pool(candidates)
    if avoid_whiff:
        pool = [r for r in pool if not row_high_whiff(r, for_hits=True)]
    pool = sorted(pool, key=lambda x: (x["hits_rank"], x.get("hits_zone_fit") or 0), reverse=True)
    return _pick_diverse(pool, n)


def fill_hits_parlay(
    candidates: list[dict],
    legs: list[dict],
    *,
    row_high_whiff: Callable[..., bool],
    n: int = TICKET_LEGS,
) -> list[dict]:
    if len(legs) >= n:
        return legs[:n]
    have = {r["name"] for r in legs}
    game_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}
    for row in legs:
        game = row.get("game_key") or ""
        team = row.get("team") or ""
        if game:
            game_counts[game] = game_counts.get(game, 0) + 1
        if team:
            team_counts[team] = team_counts.get(team, 0) + 1

    def can_backfill(row: dict, *, respect_caps: bool) -> bool:
        if row["name"] in have:
            return False
        if row_high_whiff(row, for_hits=True):
            return False
        if (row.get("split") or 0.0) < SPLIT_HARD_FLOOR:
            return False
        if not is_starting(row):
            return False
        if respect_caps:
            game = row.get("game_key") or ""
            team = row.get("team") or ""
            if game and game_counts.get(game, 0) >= MAX_PER_GAME:
                return False
            if team and team_counts.get(team, 0) >= MAX_PER_TEAM:
                return False
        if (row.get("hit_prob") or 0.0) >= 0.56:
            return True
        zone = row.get("zone_score") or 0.0
        z_contact = row.get("zone_contact") or 0.0
        if zone >= 11.0 or z_contact >= 22.0:
            return True
        return _has_hit_form(row)

    ranked = sorted(
        candidates,
        key=lambda x: (x.get("hits_rank") or 0, x.get("hits_zone_fit") or 0),
        reverse=True,
    )
    for respect_caps in (True, False):
        for row in ranked:
            if not can_backfill(row, respect_caps=respect_caps):
                continue
            have.add(row["name"])
            legs.append(row)
            game = row.get("game_key") or ""
            team = row.get("team") or ""
            if game:
                game_counts[game] = game_counts.get(game, 0) + 1
            if team:
                team_counts[team] = team_counts.get(team, 0) + 1
            if len(legs) == n:
                return legs
    return legs
