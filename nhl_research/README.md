# NHL Research + Anytime Goal Scorer sheet

The NFL tab's twin, on ice. Same `nrs-` DOM, same stylesheet, same left/right
log-vs-log read — so the two tabs cannot drift apart visually.

## Daily use

```bash
python fetch-nhl-research-slate.py --date 2026-10-10   # or --date today
python -m nhl_research.atgs_sheet --date 2026-10-10
python serve-research.py
```

Then <http://localhost:8080/nhl-research/index.html> and
<http://localhost:8080/nhl-research/atgs.html>.

The first slate of a season pulls and caches the whole year (~90s). Every build
after that reads `nhl_research/cache/` and takes about ten seconds.

## Where the data comes from

All free, no key, all from NHL.com's own public API.

| Source | What it gives |
| --- | --- |
| `api-web.nhle.com/v1/schedule/<date>` | the day's games, logos, venues |
| `api-web.nhle.com/v1/roster/<team>/<season>` | who plays for whom **now** |
| `api.nhle.com/stats/rest/en/skater/summary` | goals, assists, points, shots, TOI, PP |
| `api.nhle.com/stats/rest/en/skater/realtime` | hits, blocks, takeaways, giveaways |
| `api.nhle.com/stats/rest/en/goalie/summary` | saves, shots against, SV% |
| `api-web.nhle.com/v1/gamecenter/<id>/play-by-play` | shot coordinates → iCF/iFF/iSCF |
| The Odds API *(optional)* | prop lines, if `ODDS_API_KEY` is set |

ESPN is not used. It 403s from some networks, and the NHL's own feed is better.

## Three things that will bite you

**The stats API pages unstably.** `skater/summary` caps at 100 rows a page and
refuses to page past 10,000, while a season is ~47,000 rows. Worse, sorting on
`gameDate` alone leaves rows within a night in arbitrary order, so paging
duplicates some and drops others — the first pull came back with 1,108
duplicates *and* McDavid two games short of the 82 he played. Every pull is
therefore chunked by team and sorted on `gameId` + `playerId`, which is unique.
`build_rows` also dedupes on the way in. If you add a report, keep both.

**Stats season ≠ schedule season.** On opening night the new season has no rows,
so `resolve_stats_season` falls back a year, and `current_team_lookup` puts last
season's production on this season's uniform. Skip the second half and every
summer trade goes invisible — Dorofeyev sits under Vegas while playing for the
Rangers.

**Line slots are ranked by ice time.** The NHL publishes no depth chart. C1/D2
and the "allowed to C1" tables are both ordered by TOI within each game, which
is the honest proxy: the coach's top line is whoever he plays the most.

## The rating model

`rating.py`, ported from the hand-built `nhl_cheatsheet_*_revamp.html` sheets:

| Component | Pts | Reads |
| --- | --- | --- |
| Shot Volume | 20 | shots and attempts per game |
| Shot Quality | 20 | iFF, iSCF, iHDCF — dangerous touches, not empty volume |
| Defensive Exploitability | 20 | goals, shots, chances allowed to his line slot |
| Goalie Matchup | 15 | opposing starter's SV%, high-danger rate, GA/G |
| Form and Tendencies | 15 | recent goal pace, ice time, power-play work |

90-100 Elite · 80-89 Strong · 70-79 Playable · 60-69 Thin · <60 Dart

Each input is scored against the **league** distribution, shipped in the slate
as `scales` (101 breakpoints per input). Scoring against the slate instead made
the bands drift with its size — a five-game night is mostly depth forwards, and
grading them against each other pushed nearly the whole board into Dart.

`iSCF` is an approximation. Natural Stat Trick draws its scoring-chance area as
a "home plate" polygon it does not publish as a formula, so `shot_quality.py`
uses the usual distance-and-angle reading of it. Applied identically to every
skater and every defense, so comparisons hold even where the absolute count
drifts from NST's.

## Layout

```
nhl_research/
  nhl_api.py        schedule, rosters, standings
  nhl_stats.py      the bulk pulls, aggregates, league baselines, rating scales
  shot_quality.py   play-by-play crawl → iCF / iFF / iSCF / iHDCF
  rating.py         the five-component 100-point model
  build_slate.py    assembles preview/data/nhl-research-<date>.json
  atgs_sheet.py     builds the cheat sheet page
  templates/        atgs_sheet.html
  cache/            per-season raw pulls (gitignored-sized, ~2.6 MB/season)

preview/nhl-research/
  index.html  nhl-research.css  nhl-research.js    the research tab
  atgs.html   atgs-manifest.json  archive/         the cheat sheet
```

`nhl-research.css` imports the NFL stylesheet and overrides only the palette and
the few hockey-specific pieces. Fix a layout bug on either tab and both get it.
