#!/usr/bin/env python3
"""MLB Stats API helpers for the research slate (schedule, probables, lineups)."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from csv_slate_meta import name_lookup_key

from game_row_enrich import load_pitcher_hr9_lookup
from research.batter_splits import fetch_batter_hand_split_lookup, write_batter_hand_cache
from research.park_factors import attach_park_factors_to_games, load_park_lookup
from research.pitch_mix import (
    attach_pitcher_arsenal,
    enrich_lineup_pitch_mix,
    fetch_batter_pitch_type_lookup,
    fetch_pitcher_arsenal_lookup,
    league_pitch_averages,
    write_pitch_mix_cache,
)
from research.pitcher_dinger_risk import attach_dinger_risk_to_games
from research.propfinder_stats import load_propfinder_lookup
from research.savant_api import (
    fetch_batter_statcast_lookup,
    merge_into_hitter_stats,
    write_savant_cache,
)
from research.savant_pitcher import (
    fetch_pitcher_hand_split_lookup,
    fetch_pitcher_statcast_lookup,
    write_savant_pitcher_cache,
    write_savant_pitcher_hand_cache,
)
from research.window_savant import (
    fetch_season_statcast_lookup,
    merge_season_savant,
)
from research.rolling_window import (
    HITTER_ROLLING_GAMES,
    PITCHER_ROLLING_STARTS,
    fetch_rolling_batter_lookup,
    fetch_rolling_pitcher_lookup,
    merge_rolling_over_season,
)
from research.window_stats import fetch_window_stats_batch, window_bounds

MLB_API = "https://statsapi.mlb.com/api/v1"

SHEET_ABBR_FROM_API = {"AZ": "ARI", "WAS": "WSH", "WSN": "WSH", "OAK": "ATH", "TB": "TB", "SF": "SF"}


def normalize_abbr(abbr: str) -> str:
    return SHEET_ABBR_FROM_API.get((abbr or "").upper(), (abbr or "").upper())


def game_key(away: str, home: str) -> str:
    return f"{normalize_abbr(away)} @ {normalize_abbr(home)}"


def _get(path_query: str, timeout: int = 30) -> dict:
    url = f"{MLB_API}{path_query}"
    req = urllib.request.Request(url, headers={"User-Agent": "WorstPickz-Research/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def fetch_schedule(sheet_date: str) -> list[dict]:
    """Return normalized game dicts for a calendar date."""
    query = urllib.parse.urlencode(
        {
            "sportId": 1,
            "date": sheet_date,
            "hydrate": "probablePitcher,team,venue,linescore,weather,flags",
        }
    )
    data = _get(f"/schedule?{query}")
    games: list[dict] = []
    for day in data.get("dates") or []:
        for g in day.get("games") or []:
            away_team = (g.get("teams") or {}).get("away", {}).get("team") or {}
            home_team = (g.get("teams") or {}).get("home", {}).get("team") or {}
            away_abbr = normalize_abbr(away_team.get("abbreviation") or "")
            home_abbr = normalize_abbr(home_team.get("abbreviation") or "")
            if not away_abbr or not home_abbr:
                continue
            away_prob = (g.get("teams") or {}).get("away", {}).get("probablePitcher") or {}
            home_prob = (g.get("teams") or {}).get("home", {}).get("probablePitcher") or {}
            venue = g.get("venue") or {}
            status = (g.get("status") or {}).get("detailedState") or ""
            mlb_weather = g.get("weather") or {}
            games.append(
                {
                    "gamePk": g.get("gamePk"),
                    "matchup": game_key(away_abbr, home_abbr),
                    "away": away_abbr,
                    "home": home_abbr,
                    "awayTeamId": away_team.get("id"),
                    "homeTeamId": home_team.get("id"),
                    "startTime": g.get("gameDate") or "",
                    "venue": venue.get("name") or "",
                    "venueId": venue.get("id"),
                    "status": status,
                    "mlbWeather": {
                        "condition": mlb_weather.get("condition") or "",
                        "temp": mlb_weather.get("temp") or "",
                        "wind": mlb_weather.get("wind") or "",
                    }
                    if mlb_weather
                    else None,
                    "awayPitcher": _pitcher_dict(away_prob),
                    "homePitcher": _pitcher_dict(home_prob),
                }
            )
    games.sort(key=lambda x: x.get("startTime") or "")
    return games


def _pitcher_dict(raw: dict) -> dict | None:
    if not raw or not raw.get("id"):
        return None
    return {
        "id": raw.get("id"),
        "name": raw.get("fullName") or "",
        "throws": (raw.get("pitchHand") or {}).get("code") or "",
    }


def _fill_pitcher_throws(games: list[dict]) -> None:
    """Schedule hydration omits pitchHand — backfill via batched people call."""
    missing: dict[int, list[dict]] = {}
    for g in games:
        for key in ("awayPitcher", "homePitcher"):
            p = g.get(key)
            if p and p.get("id") and not (p.get("throws") or "").strip():
                missing.setdefault(int(p["id"]), []).append(p)
    if not missing:
        return
    ids = ",".join(str(i) for i in sorted(missing))
    try:
        data = _get(f"/people?personIds={ids}")
    except Exception:
        return
    for person in data.get("people") or []:
        code = ((person.get("pitchHand") or {}).get("code") or "").strip().upper()
        pid = person.get("id")
        if not code or pid not in missing:
            continue
        for p in missing[pid]:
            p["throws"] = code


def fetch_lineup(game_pk: int) -> tuple[list[dict], list[dict]]:
    """Return (away_lineup, home_lineup) from boxscore batting order."""
    try:
        data = _get(f"/game/{game_pk}/boxscore")
    except Exception:
        return [], []
    out_away: list[dict] = []
    out_home: list[dict] = []
    for side, bucket in (("away", out_away), ("home", out_home)):
        team = (data.get("teams") or {}).get(side) or {}
        order = team.get("battingOrder") or []
        players = team.get("players") or {}
        for slot, pid in enumerate(order, start=1):
            key = f"ID{pid}"
            entry = players.get(key) or {}
            person = entry.get("person") or {}
            if not person.get("fullName"):
                continue
            bat_side = (entry.get("batSide") or {}).get("code") or ""
            pos = (entry.get("position") or {}).get("abbreviation") or ""
            bucket.append(
                {
                    "id": person.get("id"),
                    "name": person.get("fullName"),
                    "order": slot,
                    "position": pos,
                    "hand": bat_side,
                    "projected": False,
                }
            )
    return out_away, out_home


def _roster_season_for_api(sheet_season: int) -> int:
    """MLB roster endpoint may lag for future/simulated seasons — fall back one year."""
    for year in (sheet_season, sheet_season - 1):
        try:
            data = _get(
                f"/teams/147/roster?rosterType=active&season={year}",
                timeout=10,
            )
            entries = data.get("roster") or data.get("rosters") or []
            if entries:
                return year
        except Exception:
            continue
    return sheet_season - 1


def fetch_team_hitters(team_id: int, roster_season: int) -> list[dict]:
    if not team_id:
        return []
    for year in (roster_season, roster_season - 1, None):
        query = f"/teams/{team_id}/roster?rosterType=active"
        if year is not None:
            query += f"&season={year}"
        try:
            data = _get(query)
        except Exception:
            continue
        entries = data.get("roster") or data.get("rosters") or []
        hitters: list[dict] = []
        for entry in entries:
            person = entry.get("person") or {}
            pos = entry.get("position") or {}
            abbr = (pos.get("abbreviation") or "").upper()
            if abbr in ("P",) or (pos.get("type") or "").lower() == "pitcher":
                continue
            hitters.append(
                {
                    "id": person.get("id"),
                    "name": person.get("fullName") or "",
                    "hand": (person.get("batSide") or {}).get("code") or "",
                    "position": abbr,
                    "projected": True,
                }
            )
        if hitters:
            return hitters
    return []


def fetch_batter_hands_batch(
    player_ids: list[int],
    *,
    chunk_size: int = 50,
) -> dict[int, str]:
    """player_id -> L/R/S from MLB /people batSide."""
    lookup: dict[int, str] = {}
    unique = sorted({int(x) for x in player_ids if x})
    for i in range(0, len(unique), chunk_size):
        chunk = unique[i : i + chunk_size]
        ids_str = ",".join(str(x) for x in chunk)
        try:
            data = _get(f"/people?personIds={ids_str}", timeout=45)
        except Exception:
            continue
        for person in data.get("people") or []:
            pid = _int(person.get("id"))
            if not pid:
                continue
            hand = (person.get("batSide") or {}).get("code") or ""
            if hand:
                lookup[pid] = hand
    return lookup


def _attach_hands_to_lineup(lineup: list[dict], hands: dict[int, str]) -> list[dict]:
    out: list[dict] = []
    for row in lineup:
        enriched = dict(row)
        pid = int(enriched.get("id") or 0)
        if pid and not enriched.get("hand"):
            enriched["hand"] = hands.get(pid) or ""
        out.append(enriched)
    return out


def fetch_hitter_season_stats(player_id: int, season: int | None = None) -> dict:
    if not player_id:
        return {}
    season = season or _season_from_date(None)
    for yr in (season, season - 1):
        hydrate = urllib.parse.quote(f"stats(group=[hitting],type=[season],season={yr})")
        try:
            data = _get(f"/people/{player_id}?hydrate={hydrate}")
        except Exception:
            continue
        people = data.get("people") or []
        if not people:
            continue
        for group in people[0].get("stats") or []:
            splits = group.get("splits") or []
            if not splits:
                continue
            stat = splits[0].get("stat") or {}
            return {
                "avg": _float(stat.get("avg")),
                "obp": _float(stat.get("obp")),
                "slg": _float(stat.get("slg")),
                "iso": _iso(stat),
                "hr": _int(stat.get("homeRuns")),
                "pa": _int(stat.get("plateAppearances")),
                "ab": _int(stat.get("atBats")),
                "kPct": _pct(stat.get("strikeOuts"), stat.get("plateAppearances")),
                "bbPct": _pct(stat.get("baseOnBalls"), stat.get("plateAppearances")),
                "source": "mlb",
            }
    return {}


def _build_stats_by_window(
    pid: int,
    savant_lookup: dict[int, dict],
    window_lookups: dict[str, dict[int, dict]],
) -> dict[str, dict]:
    savant = savant_lookup.get(pid) or {}
    win_stats = (window_lookups.get("season") or {}).get(pid) or {}
    return {"season": merge_season_savant(win_stats, savant)}


def _attach_season_stats(
    row: dict,
    savant_lookup: dict[int, dict],
    window_lookups: dict[str, dict[int, dict]],
) -> dict:
    enriched = dict(row)
    pid = int(enriched.get("id") or 0)
    if not pid:
        return enriched
    season_stats = dict(_build_stats_by_window(pid, savant_lookup, window_lookups).get("season") or {})
    preserve_keys = ("mixPlus", "mixEdge", "mixXwoba", "mixBest", "mixWorst", "mixPitches", "nearHr")
    existing = enriched.get("stats") or {}
    for key in preserve_keys:
        if existing.get(key) is not None:
            season_stats[key] = existing[key]
    if existing.get("nearHr") is not None and "propfinder" not in str(season_stats.get("source") or ""):
        src = season_stats.get("source") or "savant"
        season_stats["source"] = f"{src}+propfinder" if src else "propfinder"
    enriched["stats"] = season_stats
    return enriched


def _attach_lineup_season_stats(
    lineup: list[dict],
    savant_lookup: dict[int, dict],
    window_lookups: dict[str, dict[int, dict]],
) -> list[dict]:
    return [
        _attach_season_stats(row, savant_lookup, window_lookups)
        for row in lineup
    ]


def enrich_hitter_row(
    row: dict,
    *,
    window_lookup: dict[int, dict],
    savant_lookup: dict[int, dict],
    propfinder_lookup: dict[str, dict],
    savant_only: bool = True,
) -> dict:
    enriched = dict(row)
    pid = int(enriched.get("id") or 0)
    savant = savant_lookup.get(pid) if pid else None
    window = None if savant_only else (window_lookup.get(pid) if pid else None)
    propfinder = propfinder_lookup.get(name_lookup_key(enriched.get("name") or "")) if propfinder_lookup else None
    enriched["stats"] = merge_into_hitter_stats(
        window, savant, propfinder, savant_only=savant_only
    )
    return enriched


def enrich_lineup(
    lineup: list[dict],
    *,
    window_lookup: dict[int, dict],
    savant_lookup: dict[int, dict],
    propfinder_lookup: dict[str, dict],
    savant_only: bool = True,
) -> list[dict]:
    return [
        enrich_hitter_row(
            row,
            window_lookup=window_lookup,
            savant_lookup=savant_lookup,
            propfinder_lookup=propfinder_lookup,
            savant_only=savant_only,
        )
        for row in lineup
    ]


def build_projected_lineup(
    team_id: int,
    roster_season: int,
    *,
    window_lookup: dict[int, dict],
    savant_lookup: dict[int, dict],
    propfinder_lookup: dict[str, dict],
    savant_only: bool = True,
    limit: int | None = None,
) -> list[dict]:
    hitters = fetch_team_hitters(team_id, roster_season)

    def sort_key(h: dict) -> tuple:
        pid = int(h.get("id") or 0)
        sav = savant_lookup.get(pid) or {}
        win = window_lookup.get(pid) or {}
        return (sav.get("pa") or win.get("pa") or 0, sav.get("hr") or win.get("hr") or 0)

    hitters.sort(key=sort_key, reverse=True)
    chosen = hitters if limit is None else hitters[:limit]
    lineup = [{**h, "order": i} for i, h in enumerate(chosen, start=1)]
    return enrich_lineup(
        lineup,
        window_lookup=window_lookup,
        savant_lookup=savant_lookup,
        propfinder_lookup=propfinder_lookup,
        savant_only=savant_only,
    )


def merge_roster_bench_into_lineup(
    lineup: list[dict],
    team_id: int | None,
    roster_season: int,
    savant_lookup: dict[int, dict],
) -> list[dict]:
    """Keep listed starters in order; append other active-roster hitters for bench depth."""
    if not team_id or not lineup:
        return lineup
    roster = fetch_team_hitters(team_id, roster_season)
    if not roster:
        return lineup
    existing_ids = {int(h["id"]) for h in lineup if h.get("id")}
    existing_names = {name_lookup_key(h.get("name") or "") for h in lineup if h.get("name")}

    def sort_key(h: dict) -> tuple:
        pid = int(h.get("id") or 0)
        sav = savant_lookup.get(pid) or {}
        return (sav.get("pa") or 0, sav.get("hr") or 0)

    bench = [
        h
        for h in roster
        if h.get("id")
        and int(h["id"]) not in existing_ids
        and name_lookup_key(h.get("name") or "") not in existing_names
    ]
    if not bench:
        return lineup
    bench.sort(key=sort_key, reverse=True)
    merged = list(lineup)
    max_order = max((int(h.get("order") or 0) for h in merged), default=0)
    for h in bench:
        max_order += 1
        merged.append({**h, "order": max_order, "projected": True})
    return merged


def resolve_side_lineup(
    box_lineup: list[dict],
    team_id: int | None,
    roster_season: int,
    *,
    window_lookup: dict[int, dict],
    savant_lookup: dict[int, dict],
    propfinder_lookup: dict[str, dict],
    savant_only: bool = True,
) -> list[dict]:
    if box_lineup:
        lineup = enrich_lineup(
            box_lineup,
            window_lookup=window_lookup,
            savant_lookup=savant_lookup,
            propfinder_lookup=propfinder_lookup,
            savant_only=savant_only,
        )
    elif team_id:
        return build_projected_lineup(
            team_id,
            roster_season,
            window_lookup=window_lookup,
            savant_lookup=savant_lookup,
            propfinder_lookup=propfinder_lookup,
            savant_only=savant_only,
        )
    else:
        return []
    if team_id:
        lineup = merge_roster_bench_into_lineup(
            lineup, team_id, roster_season, savant_lookup
        )
        lineup = enrich_lineup(
            lineup,
            window_lookup=window_lookup,
            savant_lookup=savant_lookup,
            propfinder_lookup=propfinder_lookup,
            savant_only=savant_only,
        )
    return lineup


def _collect_player_ids(games: list[dict]) -> list[int]:
    ids: set[int] = set()
    for game in games:
        for side in ("awayLineup", "homeLineup"):
            for row in game.get(side) or []:
                pid = row.get("id")
                if pid:
                    ids.add(int(pid))
    return sorted(ids)


def _collect_pitcher_ids(games: list[dict]) -> list[int]:
    ids: set[int] = set()
    for game in games:
        for key in ("awayPitcher", "homePitcher"):
            pitcher = game.get(key)
            pid = pitcher.get("id") if pitcher else None
            if pid:
                ids.add(int(pid))
    return sorted(ids)


def _apply_rolling_stat_windows(games: list[dict], season: int) -> tuple[int, int]:
    """Merge last-N-game / last-N-start Savant profiles onto lineup + pitcher stats."""
    hitter_ids = _collect_player_ids(games)
    pitcher_ids = _collect_pitcher_ids(games)
    rolling_batter = fetch_rolling_batter_lookup(hitter_ids, season, HITTER_ROLLING_GAMES)
    rolling_pitcher = fetch_rolling_pitcher_lookup(pitcher_ids, season, PITCHER_ROLLING_STARTS)
    for game in games:
        for side in ("awayLineup", "homeLineup"):
            updated: list[dict] = []
            for row in game.get(side) or []:
                pid = int(row.get("id") or 0)
                if not pid:
                    updated.append(row)
                    continue
                stats = dict(row.get("stats") or {})
                merged = merge_rolling_over_season(rolling_batter.get(pid), stats)
                updated.append({**row, "stats": merged or stats})
            game[side] = updated
        for pkey in ("awayPitcher", "homePitcher"):
            pitcher = game.get(pkey)
            if not pitcher:
                continue
            pid = int(pitcher.get("id") or 0)
            if not pid:
                continue
            stats = dict(pitcher.get("stats") or {})
            merged = merge_rolling_over_season(rolling_pitcher.get(pid), stats)
            if merged:
                pitcher["stats"] = merged
    return len(rolling_batter), len(rolling_pitcher)


def _attach_pitcher_savant_stats(games: list[dict], savant_pitcher_lookup: dict[int, dict]) -> None:
    if not savant_pitcher_lookup:
        return
    for game in games:
        for key in ("awayPitcher", "homePitcher"):
            pitcher = game.get(key)
            if not pitcher:
                continue
            pid = pitcher.get("id")
            if not pid:
                continue
            sav = savant_pitcher_lookup.get(int(pid))
            if not sav:
                continue
            stats: dict[str, Any] = dict(pitcher.get("stats") or {})
            for stat_key, val in sav.items():
                if val is not None and stats.get(stat_key) is None:
                    stats[stat_key] = val
            pitcher["stats"] = stats


def _attach_park_to_games(games: list[dict], sheet_date: str) -> None:
    lookup = load_park_lookup(sheet_date)
    if lookup.get("by_game") or lookup.get("by_venue"):
        attach_park_factors_to_games(games, lookup)


def _attach_pitcher_stats_to_games(games: list[dict], sheet_date: str) -> None:
    from sheet_data import hr_targets_csv, load_pitcher_risk, pitcher_risk_pct, resolve_pitcher

    risk_path = hr_targets_csv(sheet_date)
    pitcher_risk = load_pitcher_risk(risk_path) if risk_path and risk_path.is_file() else {}
    hr9_lookup = load_pitcher_hr9_lookup(sheet_date)

    for game in games:
        for key in ("awayPitcher", "homePitcher"):
            pitcher = game.get(key)
            if not pitcher or not pitcher.get("name"):
                continue
            name = pitcher["name"]
            row = resolve_pitcher(pitcher_risk, name)
            stats: dict[str, Any] = dict(pitcher.get("stats") or {})
            if row:
                stats.update(
                    {
                        "hrRisk": row["overall"],
                        "hrRiskPct": pitcher_risk_pct(row["overall"]),
                        "vsLhb": row["vs_lhb"],
                        "vsLhbPct": pitcher_risk_pct(row["vs_lhb"]),
                        "vsRhb": row["vs_rhb"],
                        "vsRhbPct": pitcher_risk_pct(row["vs_rhb"]),
                    }
                )
            last = name.split()[-1].lower()
            hr9 = hr9_lookup.get(name.lower()) or hr9_lookup.get(last)
            if hr9 is not None:
                stats["hr9"] = hr9
            if stats:
                pitcher["stats"] = stats


def _attach_hr_model_to_games(games: list[dict]) -> None:
    try:
        from research.hr_park_model import attach_hr_model_to_games

        attach_hr_model_to_games(games)
    except Exception:
        return


def _attach_open_meteo_to_games(games: list[dict]) -> None:
    try:
        from research.park_weather import fetch_game_hour_weather
    except Exception:
        return
    for game in games:
        venue = game.get("venue") or ""
        start = game.get("startTime") or ""
        if not venue or not start:
            continue
        try:
            wx = fetch_game_hour_weather(
                venue,
                start,
                game_pk=game.get("gamePk"),
                mlb_weather=game.get("mlbWeather"),
            )
            if wx and not wx.get("error"):
                game["parkWeather"] = wx
                if wx.get("roofStatus"):
                    game["roofStatus"] = wx["roofStatus"]
                if wx.get("propPass"):
                    game["propPass"] = True
        except Exception:
            continue


def _serialize_zone_lookup(lookup: dict) -> dict[str, dict]:
    return {f"{batter}|{pitcher}": entry for (batter, pitcher), entry in lookup.items()}


def build_slate(sheet_date: str, *, with_stats: bool = True, savant_only: bool = True) -> dict:
    season = _season_from_date(sheet_date)
    roster_season = _roster_season_for_api(season)
    window_start, window_end = window_bounds(sheet_date, days=30)
    savant_lookup: dict[int, dict] = fetch_batter_statcast_lookup(season) if with_stats else {}
    savant_pitcher_lookup: dict[int, dict] = {}
    pitcher_hand_lookup: dict[int, dict[str, dict]] = {}
    pitcher_arsenal_lookup: dict[int, dict[str, float]] = {}
    pitcher_arsenal_prior_lookup: dict[int, dict[str, float]] = {}
    batter_pitch_lookup: dict[int, dict[str, dict]] = {}
    league_pitch_avgs: dict[str, dict] = {}
    season_statcast: dict[int, dict] = {}
    window_lookups: dict[str, dict[int, dict]] = {}
    if with_stats:
        try:
            hand_splits = fetch_batter_hand_split_lookup(season)
            for pid, splits in hand_splits.items():
                sav = savant_lookup.setdefault(pid, {})
                for key, val in splits.items():
                    if val is not None:
                        sav[key] = val
            write_batter_hand_cache(
                hand_splits,
                Path(__file__).resolve().parent.parent / "preview" / "data",
                season,
            )
        except Exception as exc:
            print(f"  WARN batter hand splits failed (platoon edge will be missing): {exc}")
        if savant_lookup:
            write_savant_cache(
                savant_lookup,
                Path(__file__).resolve().parent.parent / "preview" / "data",
                season,
            )
        try:
            savant_pitcher_lookup = fetch_pitcher_statcast_lookup(season)
            write_savant_pitcher_cache(
                savant_pitcher_lookup,
                Path(__file__).resolve().parent.parent / "preview" / "data",
                season,
            )
        except Exception as exc:
            savant_pitcher_lookup = {}
            print(f"  WARN pitcher Savant stats failed (dinger risk / K stuff degraded): {exc}")
        try:
            pitcher_hand_lookup = fetch_pitcher_hand_split_lookup(season)
            write_savant_pitcher_hand_cache(
                pitcher_hand_lookup,
                Path(__file__).resolve().parent.parent / "preview" / "data",
                season,
            )
        except Exception as exc:
            pitcher_hand_lookup = {}
            print(f"  WARN pitcher hand splits failed (LHB/RHB dinger risk missing): {exc}")
        try:
            pitcher_arsenal_lookup = fetch_pitcher_arsenal_lookup(season)
            batter_pitch_lookup = fetch_batter_pitch_type_lookup(season)
            league_pitch_avgs = league_pitch_averages(batter_pitch_lookup)
            write_pitch_mix_cache(
                pitcher_arsenal_lookup,
                batter_pitch_lookup,
                league_pitch_avgs,
                Path(__file__).resolve().parent.parent / "preview" / "data",
                season,
            )
            if season > 2024:
                pitcher_arsenal_prior_lookup = fetch_pitcher_arsenal_lookup(season - 1)
                prior_path = (
                    Path(__file__).resolve().parent.parent
                    / "preview"
                    / "data"
                    / f"savant-pitcher-arsenal-{season - 1}.json"
                )
                prior_path.write_text(
                    json.dumps(
                        {
                            "season": season - 1,
                            "source": "savant-pitch-arsenal-stats",
                            "pitchers": len(pitcher_arsenal_prior_lookup),
                            "lookup": {str(k): v for k, v in pitcher_arsenal_prior_lookup.items()},
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
        except Exception as exc:
            pitcher_arsenal_lookup = {}
            pitcher_arsenal_prior_lookup = {}
            batter_pitch_lookup = {}
            league_pitch_avgs = {}
            print(f"  WARN pitch mix data failed (Mix% / Edge% will be missing): {exc}")
        try:
            season_statcast = fetch_season_statcast_lookup(season)
            window_lookups["season"] = season_statcast
            for pid, pull_stats in season_statcast.items():
                sav = savant_lookup.setdefault(pid, {})
                for key in ("pullPct", "pullAirPct", "pullBarrelPct"):
                    if sav.get(key) is None and pull_stats.get(key) is not None:
                        sav[key] = pull_stats[key]
        except Exception as exc:
            season_statcast = {}
            window_lookups = {}
            print(f"  WARN season statcast pull data failed: {exc}")
    propfinder_lookup: dict[str, dict] = (
        load_propfinder_lookup(sheet_date) if with_stats else {}
    )

    games: list[dict] = []
    for g in fetch_schedule(sheet_date):
        game = dict(g)
        pk = game.get("gamePk")
        away_lu: list[dict] = []
        home_lu: list[dict] = []
        if pk:
            away_lu, home_lu = fetch_lineup(pk)
        game["awayLineup"] = away_lu
        game["homeLineup"] = home_lu
        games.append(game)

    rotowire_meta: dict[str, Any] = {}
    try:
        from research.rotowire_lineups import apply_rotowire_fallback_to_games

        rotowire_meta = apply_rotowire_fallback_to_games(
            games, sheet_date, roster_season=roster_season
        )
    except Exception as exc:
        rotowire_meta = {"source": "rotowire", "error": str(exc)}

    # RotoWire daily lineups are often login-walled now; fill remaining TBD
    # probables from FantasyPros (+ ESPN) so Savant pitcher stats still attach.
    projected_meta: dict[str, Any] = {}
    try:
        from research.projected_pitchers import apply_projected_pitcher_fallback_to_games

        projected_meta = apply_projected_pitcher_fallback_to_games(games, sheet_date)
    except Exception as exc:
        projected_meta = {"source": "projected-pitchers", "error": str(exc)}

    _fill_pitcher_throws(games)
    _attach_park_to_games(games, sheet_date)
    if with_stats:
        _attach_open_meteo_to_games(games)
        _attach_pitcher_savant_stats(games, savant_pitcher_lookup)
        _attach_pitcher_stats_to_games(games, sheet_date)
        attach_dinger_risk_to_games(games, hand_lookup=pitcher_hand_lookup)

    window_lookup: dict[int, dict] = {}
    if with_stats and not savant_only:
        id_set: set[int] = set(_collect_player_ids(games))
        for game in games:
            for team_id_key in ("awayTeamId", "homeTeamId"):
                tid = game.get(team_id_key)
                if tid:
                    for h in fetch_team_hitters(tid, roster_season):
                        if h.get("id"):
                            id_set.add(int(h["id"]))
        window_lookup = fetch_window_stats_batch(
            sorted(id_set), window_start, window_end, season
        )

    for game in games:
        if with_stats:
            game["awayPitcher"] = attach_pitcher_arsenal(
                game.get("awayPitcher"),
                pitcher_arsenal_lookup,
                prior_lookup=pitcher_arsenal_prior_lookup,
                season=season,
            )
            game["homePitcher"] = attach_pitcher_arsenal(
                game.get("homePitcher"),
                pitcher_arsenal_lookup,
                prior_lookup=pitcher_arsenal_prior_lookup,
                season=season,
            )
            game["awayLineup"] = resolve_side_lineup(
                game.get("awayLineup") or [],
                game.get("awayTeamId"),
                roster_season,
                window_lookup=window_lookup,
                savant_lookup=savant_lookup,
                propfinder_lookup=propfinder_lookup,
                savant_only=savant_only,
            )
            game["homeLineup"] = resolve_side_lineup(
                game.get("homeLineup") or [],
                game.get("homeTeamId"),
                roster_season,
                window_lookup=window_lookup,
                savant_lookup=savant_lookup,
                propfinder_lookup=propfinder_lookup,
                savant_only=savant_only,
            )
            game["awayLineup"] = enrich_lineup_pitch_mix(
                game["awayLineup"],
                game.get("homePitcher"),
                batter_pitch_lookup=batter_pitch_lookup,
                league_avgs=league_pitch_avgs,
                savant_lookup=savant_lookup,
            )
            game["homeLineup"] = enrich_lineup_pitch_mix(
                game["homeLineup"],
                game.get("awayPitcher"),
                batter_pitch_lookup=batter_pitch_lookup,
                league_avgs=league_pitch_avgs,
                savant_lookup=savant_lookup,
            )
            if window_lookups:
                game["awayLineup"] = _attach_lineup_season_stats(
                    game["awayLineup"], savant_lookup, window_lookups
                )
                game["homeLineup"] = _attach_lineup_season_stats(
                    game["homeLineup"], savant_lookup, window_lookups
                )
        game["lineupStatus"] = _lineup_status(
            game.get("awayLineup") or [], game.get("homeLineup") or []
        )

    rolling_batters = 0
    rolling_pitchers = 0
    if with_stats:
        rolling_batters, rolling_pitchers = _apply_rolling_stat_windows(games, season)

    if with_stats:
        hand_ids = _collect_player_ids(games)
        hands = fetch_batter_hands_batch(hand_ids) if hand_ids else {}
        if hands:
            for game in games:
                game["awayLineup"] = _attach_hands_to_lineup(game.get("awayLineup") or [], hands)
                game["homeLineup"] = _attach_hands_to_lineup(game.get("homeLineup") or [], hands)
        _attach_hr_model_to_games(games)

    zone_lookup: dict[str, dict] = {}
    if with_stats:
        try:
            from zone_matchups import load_zone_lookup

            zone_lookup = _serialize_zone_lookup(load_zone_lookup(sheet_date))
        except Exception:
            pass

    return {
        "sheet_date": sheet_date,
        "season": season,
        "roster_season": roster_season,
        "stat_window": "rolling",
        "stat_windows": {
            "hitters": {
                "label": f"Last {HITTER_ROLLING_GAMES} games",
                "games": HITTER_ROLLING_GAMES,
            },
            "pitchers": {
                "label": f"Last {PITCHER_ROLLING_STARTS} starts",
                "starts": PITCHER_ROLLING_STARTS,
            },
            "season": {
                "label": str(season),
                "games": None,
            },
        },
        "rolling_batters": rolling_batters,
        "rolling_pitchers": rolling_pitchers,
        "window_start": window_start if not savant_only else None,
        "window_end": window_end if not savant_only else None,
        "source": (
            "savant+propfinder"
            if propfinder_lookup and savant_only
            else ("mlb+savant+propfinder" if propfinder_lookup else ("savant" if savant_only else "mlb+savant"))
        ),
        "savant_only": savant_only,
        "enriched": bool(propfinder_lookup),
        "propfinder_lookup": propfinder_lookup,
        "savant_batters": len(savant_lookup),
        "savant_pitchers": len(savant_pitcher_lookup),
        "pitch_mix_pitchers": len(pitcher_arsenal_lookup),
        "pitch_mix_batters": len(batter_pitch_lookup),
        "propfinder_batters": len(propfinder_lookup),
        "zone_lookup": zone_lookup,
        "zone_matchups": len(zone_lookup),
        "window_batters": len(window_lookup),
        "savant_lookup": {str(k): v for k, v in savant_lookup.items()},
        "savant_pitcher_lookup": {str(k): v for k, v in savant_pitcher_lookup.items()},
        "pitcher_hand_lookup": {str(k): v for k, v in pitcher_hand_lookup.items()},
        "pitcher_arsenal_lookup": {str(k): v for k, v in pitcher_arsenal_lookup.items()},
        "pitcher_arsenal_prior_lookup": {str(k): v for k, v in pitcher_arsenal_prior_lookup.items()},
        "batter_pitch_lookup": {str(k): v for k, v in batter_pitch_lookup.items()},
        "league_pitch_avgs": league_pitch_avgs,
        "rotowire": rotowire_meta,
        "projected_pitchers": projected_meta,
        "games": games,
    }

def _lineup_status(away: list, home: list) -> str:
    away_confirmed = any(not h.get("projected") for h in away)
    home_confirmed = any(not h.get("projected") for h in home)
    if away_confirmed and home_confirmed:
        return "confirmed"
    if away_confirmed or home_confirmed:
        return "partial"
    if away or home:
        return "projected"
    return "empty"


def _season_from_date(sheet_date: str | None) -> int:
    if sheet_date and re.fullmatch(r"\d{4}-\d{2}-\d{2}", sheet_date):
        return int(sheet_date[:4])
    from datetime import date

    return date.today().year


def _float(val: Any) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _int(val: Any) -> int | None:
    if val is None or val == "":
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _iso(stat: dict) -> float | None:
    slg = _float(stat.get("slg"))
    avg = _float(stat.get("avg"))
    if slg is not None and avg is not None:
        return round(slg - avg, 3)
    return None


def _pct(num: Any, den: Any) -> float | None:
    n, d = _int(num), _int(den)
    if n is None or d is None or d == 0:
        return None
    return round(100.0 * n / d, 1)
