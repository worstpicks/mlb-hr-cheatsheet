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

## Refreshing

Final box scores cache for one year; rosters/schedules cache for one hour.
The build writes the date files and manifest; failed upstream requests are
reported in the UI rather than silently presented as complete coverage.
`Refresh` reloads the built dataset, not a new server-side scrape.
The GitHub workflow builds today plus the next three days when deployed.
Cache is intermediate data and must not be committed.
