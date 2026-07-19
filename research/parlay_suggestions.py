#!/usr/bin/env python3
"""Multi-factor Research-tab parlay suggestions (HR pairs + hits slate).

Built only from hitter stats already attached to the research slate — no cheat
sheet scores or odds. Intended to run at the end of ``build_slate`` and be
mirrored client-side when older JSON lacks this block.
"""
from __future__ import annotations

from typing import Any


def _num(x: Any, default: float | None = None) -> float | None:
    try:
        if x is None:
            return default
        return float(x)
    except (TypeError, ValueError):
        return default


def _pct(v: float | None, digits: int = 1) -> str:
    if v is None:
        return "—"
    return f"{v:.{digits}f}"


def _collect_hitters(games: list[dict]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for g in games or []:
        matchup = g.get("matchup") or f"{g.get('away')} @ {g.get('home')}"
        ap = (g.get("awayPitcher") or {}).get("name")
        hp = (g.get("homePitcher") or {}).get("name")
        for side, lu_key, opp_p in (
            ("away", "awayLineup", hp),
            ("home", "homeLineup", ap),
        ):
            team = g.get(side)
            for h in g.get(lu_key) or []:
                st = h.get("stats") or {}
                pa = _num(st.get("pa"), 0) or 0
                if pa < 25:
                    continue
                name = (h.get("name") or "").strip()
                if not name:
                    continue
                bip_pct = _num(st.get("bipPct"))
                bip = _num(st.get("bip"))
                if bip_pct is None and bip is not None and pa:
                    bip_pct = 100.0 * bip / pa
                rows.append(
                    {
                        "id": h.get("id"),
                        "name": name,
                        "team": team,
                        "matchup": matchup,
                        "gamePk": g.get("gamePk"),
                        "order": h.get("order"),
                        "projected": bool(h.get("projected")),
                        "oppPitcher": opp_p,
                        "pa": pa,
                        "barrelPct": _num(st.get("barrelPct")),
                        "hardHitPct": _num(st.get("hardHitPct")),
                        "avgEV": _num(st.get("avgEV")),
                        "fbPct": _num(st.get("fbPct")),
                        "pullAirPct": _num(st.get("pullAirPct")),
                        "pullBarrelPct": _num(st.get("pullBarrelPct")),
                        "iso": _num(st.get("iso")),
                        "xwoba": _num(st.get("xwoba")),
                        "hrFbPct": _num(st.get("hrFbPct")),
                        "whiffPct": _num(st.get("whiffPct")),
                        "kPct": _num(st.get("kPct")),
                        "bipPct": bip_pct,
                        "avg": _num(st.get("avg")),
                        "recentForm": _num(st.get("recentForm")),
                    }
                )
    return rows


def _power_score(r: dict[str, Any]) -> float | None:
    keys = ("barrelPct", "hardHitPct", "iso", "fbPct", "avgEV")
    if sum(1 for k in keys if r.get(k) is not None) < 4:
        return None
    b = r["barrelPct"] or 0.0
    hh = r["hardHitPct"] or 0.0
    iso = r["iso"] or 0.0
    fb = r["fbPct"] or 0.0
    ev = r["avgEV"] or 0.0
    if b < 8 and iso < 0.180:
        return None
    if hh < 35 and b < 10:
        return None
    score = (
        b * 3.2
        + hh * 0.9
        + iso * 120
        + fb * 0.55
        + max(0.0, ev - 88) * 4.5
        + (r["pullAirPct"] or 0.0) * 0.8
        + (r["pullBarrelPct"] or 0.0) * 1.4
        + (r["xwoba"] or 0.0) * 40
        + (r["hrFbPct"] or 0.0) * 0.35
        + max(0.0, r["recentForm"] or 0.0) * 0.15
    )
    if (r["whiffPct"] or 0) > 38:
        score *= 0.92
    return score


def _hits_score(r: dict[str, Any]) -> float | None:
    if r.get("whiffPct") is None:
        return None
    whiff = r["whiffPct"] or 99.0
    if whiff > 30:
        return None
    bip = r["bipPct"]
    if whiff > 28 and (bip or 0) < 65:
        return None
    hh = r["hardHitPct"] or 0.0
    xw = r["xwoba"] or 0.0
    avg = r["avg"] or 0.0
    k = r["kPct"]
    score = max(0.0, 32 - whiff) * 3.2
    if k is not None:
        score += max(0.0, 28 - k) * 1.8
    if bip is not None:
        score += (bip - 60) * 1.5
    score += hh * 0.55 + xw * 55 + avg * 40
    score += max(0.0, r["recentForm"] or 0.0) * 0.1
    if hh < 28 and xw < 0.300:
        score *= 0.85
    return score


def _hr_key_stats(r: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if r.get("barrelPct") is not None:
        out.append(f"Barrel% {_pct(r['barrelPct'])}")
    if r.get("hardHitPct") is not None:
        out.append(f"HardHit% {_pct(r['hardHitPct'])}")
    if r.get("avgEV") is not None:
        out.append(f"Avg EV {_pct(r['avgEV'])} mph")
    if r.get("fbPct") is not None:
        out.append(f"FB% {_pct(r['fbPct'])}")
    if r.get("iso") is not None:
        out.append(f"ISO {_pct(r['iso'], 3)}")
    if r.get("pullAirPct") is not None:
        out.append(f"PullAir% {_pct(r['pullAirPct'])}")
    if r.get("xwoba") is not None:
        out.append(f"xwOBA {_pct(r['xwoba'], 3)}")
    return out[:5]


def _hits_key_stats_line(r: dict[str, Any]) -> str:
    parts = [
        f"Whiff% {_pct(r.get('whiffPct'))}",
        f"K% {_pct(r.get('kPct'))}" if r.get("kPct") is not None else None,
        f"BIP% {_pct(r.get('bipPct'))}" if r.get("bipPct") is not None else None,
        f"HardHit% {_pct(r.get('hardHitPct'))}" if r.get("hardHitPct") is not None else None,
        f"xwOBA {_pct(r.get('xwoba'), 3)}" if r.get("xwoba") is not None else None,
        f"AVG {_pct(r.get('avg'), 3)}" if r.get("avg") is not None else None,
    ]
    return " · ".join(p for p in parts if p)


def _why_hr(r: dict[str, Any]) -> str:
    bits = []
    if (r.get("barrelPct") or 0) >= 18:
        bits.append("elite barrel rate")
    elif (r.get("barrelPct") or 0) >= 14:
        bits.append("strong barrel rate")
    if (r.get("hardHitPct") or 0) >= 50:
        bits.append("50%+ hard-hit")
    elif (r.get("hardHitPct") or 0) >= 45:
        bits.append("elevated hard-hit")
    if (r.get("iso") or 0) >= 0.300:
        bits.append("high ISO")
    if (r.get("avgEV") or 0) >= 93:
        bits.append("high exit velocity")
    if (r.get("fbPct") or 0) >= 32 or (r.get("pullAirPct") or 0) >= 18:
        bits.append("air-ball authority")
    if not bits:
        bits.append("stacked power metrics in the Research window")
    note = "Projected lineup spot — " if r.get("projected") else ""
    return f"{note}{' / '.join(bits[:4])} combine for a multi-factor HR upside profile."


def _why_combo(players: list[dict[str, Any]]) -> str:
    games = {p.get("gamePk") for p in players if p.get("gamePk") is not None}
    matchups = " / ".join(
        dict.fromkeys(p.get("matchup") or "" for p in players if p.get("matchup"))
    )
    if len(games) >= len(players):
        diversify = f"Diversified across {matchups} to reduce single-game dependency."
    elif len(games) > 1:
        diversify = f"Spread across {len(games)} games ({matchups}) for partial diversification."
    else:
        diversify = "Same-game stack justified by exceptional complementary power profiles."
    n = len(players)
    return (
        f"All {n} legs clear multiple power thresholds (barrel, hard-hit, EV/ISO), "
        f"not a single hot metric. {diversify} "
        f"The combination stacks independent higher-upside damage shapes from the Research tab window."
    )


def _player_payload(r: dict[str, Any], *, kind: str) -> dict[str, Any]:
    base = {
        "id": r.get("id"),
        "name": r["name"],
        "team": r.get("team"),
        "matchup": r.get("matchup"),
        "gamePk": r.get("gamePk"),
        "projected": bool(r.get("projected")),
        "oppPitcher": r.get("oppPitcher"),
    }
    if kind == "hr":
        base["keyStats"] = _hr_key_stats(r)
        base["why"] = _why_hr(r)
        base["score"] = round(r.get("powerScore") or 0, 2)
    else:
        base["keyStatsLine"] = _hits_key_stats_line(r)
        base["score"] = round(r.get("hitsScore") or 0, 2)
    return base


def _combo_key(players: list[dict[str, Any]]) -> str:
    return "|".join(sorted(p["name"] for p in players if p.get("name")))


def _pick_hr_combo(
    power: list[dict[str, Any]], *, size: int
) -> tuple[list[dict[str, Any]], bool] | None:
    """Greedy pick of ``size`` power bats, preferring different games/teams."""
    if len(power) < size:
        return None

    def try_build(*, allow_same_game: bool) -> list[dict[str, Any]] | None:
        picked: list[dict[str, Any]] = []
        used_names: set[str] = set()
        used_teams: set[str] = set()
        used_games: set[Any] = set()
        for r in power:
            if r["name"] in used_names:
                continue
            if r.get("team") and r["team"] in used_teams:
                continue
            gk = r.get("gamePk")
            if not allow_same_game and gk is not None and gk in used_games:
                continue
            picked.append(r)
            used_names.add(r["name"])
            if r.get("team"):
                used_teams.add(r["team"])
            if gk is not None:
                used_games.add(gk)
            if len(picked) >= size:
                return picked
        return None

    built = try_build(allow_same_game=False) or try_build(allow_same_game=True)
    if not built:
        return None
    same_game = len({p.get("gamePk") for p in built if p.get("gamePk") is not None}) <= 1
    return built, same_game


def build_parlay_suggestions(games: list[dict], sheet_date: str | None = None) -> dict[str, Any]:
    """Return structured parlay suggestions for a research slate."""
    note = (
        "These suggestions are generated exclusively from MLB Research tab data "
        "using multi-factor statistical analysis."
    )
    empty = {
        "source": "research-multi-factor",
        "sheetDate": sheet_date,
        "note": note,
        "hr2Leg": None,
        "hr3Leg": None,
        "hitsParlay": None,
        "meta": {"hittersScored": 0, "powerPool": 0, "hitsPool": 0},
    }

    rows = _collect_hitters(games)
    power: list[dict[str, Any]] = []
    for r in rows:
        s = _power_score(r)
        if s is None:
            continue
        r2 = dict(r)
        r2["powerScore"] = s
        power.append(r2)
    power.sort(key=lambda x: -x["powerScore"])

    hits: list[dict[str, Any]] = []
    for r in rows:
        s = _hits_score(r)
        if s is None:
            continue
        r2 = dict(r)
        r2["hitsScore"] = s
        hits.append(r2)
    hits.sort(key=lambda x: -x["hitsScore"])

    empty["meta"] = {
        "hittersScored": len(rows),
        "powerPool": len(power),
        "hitsPool": len(hits),
    }
    if len(power) < 2 and len(hits) < 6:
        return empty

    result = dict(empty)
    two = _pick_hr_combo(power, size=2)
    if two:
        players, same = two
        result["hr2Leg"] = {
            "label": "2-Leg HR Parlay",
            "players": [_player_payload(p, kind="hr") for p in players],
            "whyPair": _why_combo(players),
            "sameGame": same,
            "comboKey": _combo_key(players),
        }

    # Prefer 3-leg that doesn't fully reuse the 2-leg set when possible
    used_two = {p["name"] for p in (two[0] if two else [])}
    power_for_three = [r for r in power if r["name"] not in used_two] or power
    three = _pick_hr_combo(power_for_three, size=3) or _pick_hr_combo(power, size=3)
    if three:
        players, same = three
        result["hr3Leg"] = {
            "label": "3-Leg HR Parlay",
            "players": [_player_payload(p, kind="hr") for p in players],
            "whyPair": _why_combo(players),
            "sameGame": same,
            "comboKey": _combo_key(players),
        }

    picked_hits: list[dict[str, Any]] = []
    game_counts: dict[Any, int] = {}
    for r in hits:
        gk = r.get("gamePk")
        if game_counts.get(gk, 0) >= 2 and len(picked_hits) < 6:
            continue
        if r["name"] in {p["name"] for p in picked_hits}:
            continue
        picked_hits.append(r)
        game_counts[gk] = game_counts.get(gk, 0) + 1
        if len(picked_hits) >= 8:
            break

    if len(picked_hits) >= 6:
        result["hitsParlay"] = {
            "label": "Smart Hits Parlay (Contact-Quality Focused)",
            "players": [_player_payload(r, kind="hits") for r in picked_hits],
            "why": (
                "Built from stacked contact traits — low whiff, low K%, high BIP% — "
                "then filtered for hit quality via hard-hit rate and/or xwOBA/AVG so "
                "the slate is not just soft-contact volume. Coverage spans multiple "
                "games for diversification while staying anchored to Research-tab "
                "contact and ball-in-play metrics."
            ),
        }

    return result
