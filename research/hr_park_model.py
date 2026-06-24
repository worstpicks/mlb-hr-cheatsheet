#!/usr/bin/env python3
"""Unified HR prop model: dimensions + density altitude + wind + park + pitcher."""
from __future__ import annotations

import math
from typing import Any

from research.park_weather import wind_component_toward_cf, _baseline_da_ft
from research.stadium_db import lookup_stadium_spec

REF_ALLEY_FT = 380.0
CARRY_HR_PCT_PER_3FT = 0.11  # +3 ft at 380 ft ≈ +10–12% HR prob
DA_MULT_PER_1000FT = 0.10  # +10% compounding per 1,000 ft DA above baseline
WIND_MULT_AT_15MPH = 0.25  # +25% at 15 mph dead-out tailwind


def carry_feet_to_hr_pct(carry_ft: float) -> float:
    return (carry_ft / 3.0) * CARRY_HR_PCT_PER_3FT


def da_compound_multiplier(da_delta_ft: float | None) -> float:
    if da_delta_ft is None:
        return 1.0
    if da_delta_ft <= 0:
        return max(0.82, 1.0 + (da_delta_ft / 1000.0) * 0.04)
    return (1.0 + DA_MULT_PER_1000FT) ** (da_delta_ft / 1000.0)


def wind_compound_multiplier(wind_out_mph: float | None) -> float:
    if wind_out_mph is None:
        return 1.0
    return max(0.72, 1.0 + (wind_out_mph / 15.0) * WIND_MULT_AT_15MPH)


def wall_distance_multiplier(wall_ft: float | None, ref: float = REF_ALLEY_FT) -> float:
    """Shorter fence vs 380 ft reference → higher HR multiplier."""
    if wall_ft is None:
        return 1.0
    extra_carry = ref - wall_ft
    return max(0.88, 1.0 + carry_feet_to_hr_pct(extra_carry))


def wall_height_penalty(height_ft: float | None) -> float:
    if height_ft is None:
        return 1.0
    if height_ft >= 20:
        return 0.94
    if height_ft >= 10:
        return 0.97
    if height_ft <= 5:
        return 1.03
    return 1.0


def _hand_code(hand: str | None) -> str:
    h = (hand or "R").strip().upper()
    return h if h in ("L", "R", "S") else "R"


def _effective_hand(batter_hand: str | None, pitcher_throws: str | None) -> str:
    hand = _hand_code(batter_hand)
    if hand != "S":
        return hand
    throws = (pitcher_throws or "R").strip().upper()
    return "R" if throws == "L" else "L"


def pull_alley(stadium: dict, hand: str) -> tuple[float | None, float | None, float | None]:
    """Return (wall distance, compass bearing, wall height) for hitter pull side."""
    walls = stadium.get("walls") or {}
    heights = stadium.get("heights") or {}
    cf_bearing = stadium.get("bearing")
    if hand == "L":
        override = stadium.get("pullL") or {}
        dist = override.get("dist") or walls.get("rcf")
        bearing = override.get("bearing")
        if bearing is None and cf_bearing is not None:
            bearing = (cf_bearing + 22) % 360
        height = heights.get("rf") or heights.get("cf")
        return dist, bearing, height
    override = stadium.get("pullR") or {}
    dist = override.get("dist") or walls.get("lcf")
    bearing = override.get("bearing")
    if bearing is None and cf_bearing is not None:
        bearing = (cf_bearing - 22) % 360
    height = heights.get("lf") or heights.get("cf")
    return dist, bearing, height


def park_pct_for_hand(game: dict, hand: str) -> int | None:
    h = _hand_code(hand)
    if h == "L" and game.get("parkLhbPct") is not None:
        return int(game["parkLhbPct"])
    if h in ("R", "S") and game.get("parkRhbPct") is not None:
        return int(game["parkRhbPct"])
    if game.get("parkHrPct") is not None:
        return int(game["parkHrPct"])
    return None


def pitcher_split_score(pitcher: dict | None, batter_hand: str) -> float | None:
    if not pitcher:
        return None
    stats = pitcher.get("stats") or {}
    hand = _hand_code(batter_hand)
    if hand == "L":
        return stats.get("vsLhb") or stats.get("vs_lhb")
    return stats.get("vsRhb") or stats.get("vs_rhb")


def pitcher_hr_multiplier(pitcher: dict | None, batter_hand: str) -> float:
    score = pitcher_split_score(pitcher, batter_hand)
    if score is None:
        stats = (pitcher or {}).get("stats") or {}
        score = stats.get("hrRisk") or stats.get("overall")
    if score is None:
        return 1.0
    return max(0.65, 1.0 + float(score) * 0.5)


def compute_game_weather_model(park_weather: dict | None, stadium: dict) -> dict[str, Any]:
    wx = park_weather or {}
    baseline = wx.get("baselineDaFt") or _baseline_da_ft()
    da = wx.get("densityAltFt")
    da_delta = None if da is None else da - baseline
    da_mult = da_compound_multiplier(da_delta)
    carry_boost = wx.get("distanceBoostFt") or 0
    carry_mult = max(0.85, 1.0 + carry_feet_to_hr_pct(float(carry_boost)))

    wind_from = wx.get("windDirDeg")
    wind_mph = wx.get("windMph")
    wind_l = wind_r = None
    if wind_from is not None and wind_mph is not None:
        _, bearing_l, _ = pull_alley(stadium, "L")
        _, bearing_r, _ = pull_alley(stadium, "R")
        wind_l = wind_component_toward_cf(wind_from, wind_mph, bearing_l)
        wind_r = wind_component_toward_cf(wind_from, wind_mph, bearing_r)
    else:
        wind_r = wx.get("windComponentMph")

    wind_mult_l = wind_compound_multiplier(wind_l)
    wind_mult_r = wind_compound_multiplier(wind_r if wind_from is not None else wx.get("windComponentMph"))

    walls = stadium.get("walls") or {}
    dim_mult_l = wall_distance_multiplier(pull_alley(stadium, "L")[0]) * wall_height_penalty(pull_alley(stadium, "L")[2])
    dim_mult_r = wall_distance_multiplier(pull_alley(stadium, "R")[0]) * wall_height_penalty(pull_alley(stadium, "R")[2])

    weather_mult = da_mult * carry_mult
    return {
        "refAlleyFt": REF_ALLEY_FT,
        "daDeltaFt": da_delta,
        "daMult": round(da_mult, 3),
        "carryMult": round(carry_mult, 3),
        "weatherMult": round(weather_mult, 3),
        "windOutLhbMph": wind_l,
        "windOutRhbMph": wind_r if wind_from is not None else wx.get("windComponentMph"),
        "windMultLhb": round(wind_mult_l, 3),
        "windMultRhb": round(wind_mult_r, 3),
        "dimMultLhb": round(dim_mult_l, 3),
        "dimMultRhb": round(dim_mult_r, 3),
        "wallLfFt": walls.get("lf"),
        "wallCfFt": walls.get("cf"),
        "wallRfFt": walls.get("rf"),
    }


def compute_hitter_hr_prop(
    hitter: dict,
    game: dict,
    opposing_pitcher: dict | None,
) -> dict[str, Any]:
    venue = game.get("venue") or ""
    stadium = lookup_stadium_spec(venue) or {}
    hand = _effective_hand(hitter.get("hand"), opposing_pitcher.get("throws") if opposing_pitcher else None)
    hr_model = game.get("hrModel") or compute_game_weather_model(game.get("parkWeather"), stadium)

    park_pct = park_pct_for_hand(game, hand)
    stadium_mult = 1.0 if park_pct is None else max(0.7, 1.0 + park_pct / 100.0)

    if hand == "L":
        wind_mult = hr_model.get("windMultLhb") or 1.0
        dim_mult = hr_model.get("dimMultLhb") or 1.0
        wind_out = hr_model.get("windOutLhbMph")
    else:
        wind_mult = hr_model.get("windMultRhb") or 1.0
        dim_mult = hr_model.get("dimMultRhb") or 1.0
        wind_out = hr_model.get("windOutRhbMph")

    weather_mult = hr_model.get("weatherMult") or 1.0
    pitcher_mult = pitcher_hr_multiplier(opposing_pitcher, hand)

    combined = stadium_mult * weather_mult * wind_mult * dim_mult * pitcher_mult
    combined_pct = round((combined - 1.0) * 100.0, 1)

    prop_pass = bool(game.get("propPass") or game.get("parkWeather", {}).get("propPass"))
    if prop_pass:
        combined_pct = None
        combined = None

    pull_dist, pull_bearing, _ = pull_alley(stadium, hand)
    return {
        "hand": hand,
        "combinedMult": None if combined is None else round(combined, 3),
        "combinedPct": combined_pct,
        "propPass": prop_pass,
        "stadiumMult": round(stadium_mult, 3),
        "weatherMult": round(weather_mult, 3),
        "windMult": round(wind_mult, 3),
        "dimMult": round(dim_mult, 3),
        "pitcherMult": round(pitcher_mult, 3),
        "parkPct": park_pct,
        "windOutMph": wind_out,
        "pullWallFt": pull_dist,
        "pullBearing": pull_bearing,
    }


def attach_hr_model_to_game(game: dict) -> None:
    stadium = lookup_stadium_spec(game.get("venue") or "")
    if not stadium:
        return
    game["hrModel"] = compute_game_weather_model(game.get("parkWeather"), stadium)
    for side, opp_key in (("awayLineup", "homePitcher"), ("homeLineup", "awayPitcher")):
        pitcher = game.get(opp_key)
        for row in game.get(side) or []:
            row["hrProp"] = compute_hitter_hr_prop(row, game, pitcher)


def attach_hr_model_to_games(games: list[dict]) -> None:
    for game in games:
        attach_hr_model_to_game(game)
