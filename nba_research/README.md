# NBA research

The NBA research tab uses the NFL/NHL research stylesheet and compares player
appearances with opponent-position production. Built from public ESPN final
box scores, current rosters, and schedules; no account or API key is required.

Run from the repository root:

    python -m nba_research.build_slate --date 2026-10-08 --days 4

Then open `/nba-research/index.html` through the local preview server.

## Samples

Auto prioritizes current regular-season appearances, then current preseason,
then previous regular season to fill 10 appearances. Each row labels preseason
and its team. A player with no recent appearances has no invented statistics.
Regular-only, preseason-only and prior-season filters are available. DNPs are
excluded. At 10 regular-season appearances, preseason fully leaves the window.
Position defense includes all players in the guard/forward/center group, not
just starters or a projected individual defender. Per-36 comparisons are in
the matchup popup; rate percentages use summed makes and attempts.

Recent logs are limited to the latest 10 final games per team per season type.
Player games with a previous club can appear and identify that team. This is
not an exhaustive full-season database. No prop odds, official tracking stats,
projected starters, calibrated probabilities, or automatic bet selections are
invented. Estimated usage and possessions are explained in the page.

## With / without

The player dialog's "With / without" tab splits his regular-season games by
whether a teammate is in the box: tonight's ruled-out teammates (the roster's
Out flag) first, then his top teammates by minutes. A teammate "sat" when he
was on the club and not in the box (DNP, injury, rest). Games, minutes, the
stat's average, per-36 and the hit rate against the card's line are printed
with their sample sizes; samples under 5 games are greyed. A card whose
teammate (20+ usual minutes) is out tonight carries a "W/O" chip that opens it.

The data is `preview/data/nba-splits.json`, written by
`python -m nba_research.splits` (and on every Prop Shop build): every 2025-26
game from `season_rates/2025-26.json.gz` plus this season's regular-season
games from the slates, kept as they arrive because a slate only holds each
club's last ten. The scheduled slate build does not touch it.

## Refreshing

Final box scores cache for one year; rosters/schedules cache for one hour.
The build writes the date files and manifest; failed upstream requests are
reported in the UI rather than silently presented as complete coverage.
`Refresh` reloads the built dataset, not a new server-side scrape.
The GitHub workflow builds today plus the next three days when deployed.
Cache is intermediate data and must not be committed.
