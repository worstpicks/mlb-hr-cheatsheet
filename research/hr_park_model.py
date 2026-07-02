#!/usr/bin/env python3
"""Unified HR prop model: dimensions + density altitude + wind + park + pitcher."""
from __future__ import annotations

import math
from typing import Any

from research.park_weather import wind_component_toward_cf, _baseline_da_ft
from research.stadium_db import lookup_stadium_spec

REF_ALLEY_FT = 377.0
CARRY_HR_PCT_PER_3FT = 0.11
WEATHER_DA_BLEND = 0.75
WEATHER_CARRY_BLEND = 0.25
CARRY_CHANNEL_SCALE = 0.45
DIM_OVERLAP_SCALE = 0.50
WIND_SOFT_CAP_MPH = 12.0
WIND_SOFT_TAIL = 0.45
HR_ENV_WEIGHTS = {
    "stadium": 0.30,
    "weather": 0.15,
    "wind": 0.25,
    "dim": 0.15,
    "pitcher": 0.15,
}
HR_ENV_FACTOR_CAP = 12.0
HR_ENV_TOTAL_CAP = 18.0
DISPLAY_PCT_CAP = 22.0


def _clamp_display_pct(n: float | None, lo: float = -DISPLAY_PCT_CAP, hi: float = DISPLAY_PCT_CAP) -> float | None:
    if n is None:
        return None
    return max(lo, min(hi, round(float(n))))


def _clamp_hr_env_mult(mult: float | None, lo: float = 0.88, hi: float = 1.12) -> float:
    if mult is None:
        return 1.0
    return max(lo, min(hi, float(mult)))


def _display_fence_pct(wall_ft: float | None, ref_ft: float = 377.0) -> float | None:
    if wall_ft is None:
        return None
    return _clamp_display_pct(((ref_ft - float(wall_ft)) / 3.0) * 3.7)


def _display_wind_pct(wind_mph: float | None) -> float | None:
    if wind_mph is None:
        return None
    return _clamp_display_pct(float(wind_mph))


def _hr_env_factor_pct(mult: float | None) -> float:
    if mult is None:
        return 0.0
    pct = (float(mult) - 1.0) * 100.0
    return max(-HR_ENV_FACTOR_CAP, min(HR_ENV_FACTOR_CAP, pct))


def _combine_hr_env_pct(factors: dict[str, float | None]) -> float:
    total = 0.0
    for key, mult in factors.items():
        weight = HR_ENV_WEIGHTS.get(key, 0.0)
        total += _hr_env_factor_pct(mult) * weight
    clamped = _clamp_display_pct(total, -HR_ENV_TOTAL_CAP, HR_ENV_TOTAL_CAP)
    return 0.0 if clamped is None else float(clamped)


def carry_feet_to_hr_pct(carry_ft: float) -> float:
    return (carry_ft / 3.0) * CARRY_HR_PCT_PER_3FT


def da_compound_multiplier(da_delta_ft: float | None) -> float:
    if da_delta_ft is None:
        return 1.0
    pct = _clamp_display_pct(da_delta_ft / 250.0, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP)
    return 1.0 if pct is None else 1.0 + pct / 100.0


def wind_compound_multiplier(wind_out_mph: float | None) -> float:
    if wind_out_mph is None:
        return 1.0
    mph = float(wind_out_mph)
    sign = 1.0 if mph >= 0 else -1.0
    abs_mph = abs(mph)
    if abs_mph <= WIND_SOFT_CAP_MPH:
        effective = abs_mph
    else:
        effective = WIND_SOFT_CAP_MPH + (abs_mph - WIND_SOFT_CAP_MPH) * WIND_SOFT_TAIL
    pct = _clamp_display_pct(sign * effective, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP)
    return 1.0 if pct is None else 1.0 + pct / 100.0


def weather_compound_multiplier(
    da_delta_ft: float | None,
    carry_boost_ft: float | None = None,
) -> float:
    """Blend DA and carry channels — avoids double-counting the same thin-air signal."""
    da_mult = da_compound_multiplier(da_delta_ft)
    da_pct = (da_mult - 1.0) * 100.0
    carry_boost = float(carry_boost_ft or 0)
    carry_pct_raw = carry_feet_to_hr_pct(carry_boost) if carry_boost else 0.0
    carry_pct = _clamp_display_pct(
        carry_pct_raw * CARRY_CHANNEL_SCALE,
        -HR_ENV_FACTOR_CAP,
        HR_ENV_FACTOR_CAP,
    )
    carry_pct = 0.0 if carry_pct is None else float(carry_pct)
    blended = da_pct * WEATHER_DA_BLEND + carry_pct * WEATHER_CARRY_BLEND
    blended = _clamp_display_pct(blended, -HR_ENV_FACTOR_CAP, HR_ENV_FACTOR_CAP)
    return 1.0 if blended is None else 1.0 + blended / 100.0


def wall_distance_multiplier(wall_ft: float | None, ref: float = REF_ALLEY_FT) -> float:
    pct = _display_fence_pct(wall_ft, ref)
    return 1.0 if pct is None else 1.0 + pct / 100.0


def wall_height_penalty(height_ft: float | None) -> float:
    if height_ft is None:
        return 1.0
    pct = 0.0
    if height_ft >= 20:
        pct = -3.0
    elif height_ft >= 10:
        pct = -1.0
    elif height_ft <= 5:
        pct = 2.0
    return 1.0 + pct / 100.0


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


def stadium_pct_for_hand(game: dict, hand: str) -> int | None:
    """Stadium structure only — live Open-Meteo weather/wind applied separately."""
    h = _hand_code(hand)
    if h == "L" and game.get("parkLhbStadiumPct") is not None:
        return int(game["parkLhbStadiumPct"])
    if h in ("R", "S") and game.get("parkRhbStadiumPct") is not None:
        return int(game["parkRhbStadiumPct"])
    combined = park_pct_for_hand(game, hand)
    wx_pct = game.get("parkWeatherPct")
    if combined is not None and wx_pct is not None:
        return int(combined) - int(wx_pct)
    if game.get("parkStadiumPct") is not None:
        return int(game["parkStadiumPct"])
    return combined


def _has_decomposed_park(game: dict) -> bool:
    return bool(
        game.get("parkLhbStadiumPct") is not None
        or game.get("parkRhbStadiumPct") is not None
        or game.get("parkStadiumPct") is not None
        or game.get("parkStadiumOnly")
    )


def _dim_mult_scaled(dim_mult: float, decomposed: bool) -> float:
    if not decomposed:
        return dim_mult
    return 1.0 + (dim_mult - 1.0) * DIM_OVERLAP_SCALE


def pitcher_split_score(pitcher: dict | None, batter_hand: str) -> float | None:
    if not pitcher:
        return None
    stats = pitcher.get("stats") or {}
    hand = _hand_code(batter_hand)
    if hand == "L":
        return stats.get("vsLhb") or stats.get("vs_lhb")
    return stats.get("vsRhb") or stats.get("vs_rhb")


def pitcher_hr_multiplier(pitcher: dict | None, batter_hand: str) -> float:
    stats = (pitcher or {}).get("stats") or {}
    hand = _hand_code(batter_hand)
    dinger_pct = None
    if hand == "L":
        dinger_pct = stats.get("dingerRiskLhbPct") or stats.get("dingerRiskPct") or stats.get("dingerRisk")
    else:
        dinger_pct = stats.get("dingerRiskRhbPct") or stats.get("dingerRiskPct") or stats.get("dingerRisk")
    if dinger_pct is not None:
        dev = (float(dinger_pct) - 50.0) / 400.0
        return _clamp_hr_env_mult(1.0 + dev)
    score = pitcher_split_score(pitcher, batter_hand)
    if score is None:
        score = stats.get("hrRisk") or stats.get("overall")
    if score is None:
        return 1.0
    return _clamp_hr_env_mult(1.0 + float(score) * 0.12)


def compute_game_weather_model(park_weather: dict | None, stadium: dict) -> dict[str, Any]:
    wx = park_weather or {}
    baseline = wx.get("baselineDaFt") or _baseline_da_ft()
    da = wx.get("densityAltFt")
    da_delta = None if da is None else da - baseline
    carry_boost = wx.get("distanceBoostFt") or 0
    da_mult = da_compound_multiplier(da_delta)
    carry_pct = _clamp_display_pct(
        carry_feet_to_hr_pct(float(carry_boost)) * CARRY_CHANNEL_SCALE,
        -HR_ENV_FACTOR_CAP,
        HR_ENV_FACTOR_CAP,
    )
    carry_mult = 1.0 if carry_pct is None else 1.0 + carry_pct / 100.0
    weather_mult = _clamp_hr_env_mult(weather_compound_multiplier(da_delta, carry_boost))

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

    decomposed = _has_decomposed_park(game)
    park_pct = stadium_pct_for_hand(game, hand)
    stadium_mult = 1.0 if park_pct is None else _clamp_hr_env_mult(1.0 + (float(park_pct) / 100.0) * 0.45)

    if hand == "L":
        wind_mult = _clamp_hr_env_mult(hr_model.get("windMultLhb") or 1.0)
        dim_mult = _clamp_hr_env_mult(
            _dim_mult_scaled(hr_model.get("dimMultLhb") or 1.0, decomposed)
        )
        wind_out = hr_model.get("windOutLhbMph")
    else:
        wind_mult = _clamp_hr_env_mult(hr_model.get("windMultRhb") or 1.0)
        dim_mult = _clamp_hr_env_mult(
            _dim_mult_scaled(hr_model.get("dimMultRhb") or 1.0, decomposed)
        )
        wind_out = hr_model.get("windOutRhbMph")

    weather_mult = _clamp_hr_env_mult(hr_model.get("weatherMult") or 1.0)
    pitcher_mult = pitcher_hr_multiplier(opposing_pitcher, hand)

    combined_pct = _combine_hr_env_pct(
        {
            "stadium": stadium_mult,
            "weather": weather_mult,
            "wind": wind_mult,
            "dim": dim_mult,
            "pitcher": pitcher_mult,
        }
    )
    combined = round(1.0 + combined_pct / 100.0, 3)

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
