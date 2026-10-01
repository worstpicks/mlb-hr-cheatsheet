# NHL Research + Anytime Goal Scorer sheet

The NFL tab's twin, on ice. Same `nrs-` DOM, same stylesheet, same left/right
log-vs-log read — so the two tabs cannot drift apart visually.

## Daily use

```bash
python fetch-nhl-research-slate.py --date today
python -m nhl_research.atgs_sheet --date 2026-09-29
python serve-research.py
```

Then <http://localhost:8080/nhl-research/index.html> and
<http://localhost:8080/nhl-research/atgs.html>. Use `serve-research.py` on 8080,
not a bare `python -m http.server`: it sends `Cache-Control: no-cache`, without
which the browser keeps serving an old `index.html` pinned to an old `?v=` script.

### It builds itself

`.github/workflows/nhl-research.yml` runs every two hours (at :47 past) and on
demand from the Actions tab. Each run builds **today and the three days ahead**,
so the days ahead are always posted and today's slate picks up last night's
games once they are final. GitHub's scheduler is best-effort -- the first week it
started runs hours late and dropped one outright, leaving today without last
night's games -- so the schedule is deliberately dense: a late run is covered by
the next one. It commits only when a slate actually changed (scores are kept out
of the slate, so a run during the games has nothing to commit), prunes slates
more than a week old, and keeps
`preview/data/nhl-research-manifest.json` -- the list of posted days the page
steers by. If today is somehow not posted, the page opens on the nearest day that
is and says so, rather than showing an empty board.

Built by hand this went blank the first morning nobody ran it.

### The cheat sheet reads a play list

Paste the day's plays, exactly as the research tab's Prop List exports them, into
`nhl_research/atgs_days/<date>.txt` -- the NHL twin of `nfl_research/atd_weeks/`.
Committing that file is enough: the workflow builds the sheet on the push. The
sheet is never built without a list, so the page stays on the last one you made.
With that file the sheet is those plays; without it, every rated forward. The
build prints any listed play it could not find on the slate, so a name that
drifted out of a club's lineup is reported rather than silently dropped.

Next to it, `nhl_research/atgs_days/<date>.lineup.txt` carries what the slate
cannot know: tonight's starting goalies and who is scratched.

    goalie PHI Joseph Woll | expected, back-to-back
    out NJD Connor Brown | lower body, out at least two games

Without it the opponent's goalie is the club's busiest by ice time, which on
10/1 picked an injured-reserve goalie for EDM and VAN and the wrong healthy one
for SEA, CGY and FLA; and the roster feed still lists injured-reserve players.
Read the morning lineups (RotoWire lineups + injury report, DailyFaceoff
starting goalies) and break ties with the NHL box scores (who started last
night decides a back-to-back). A named goalie replaces the guess for every
skater shooting at him; an `out` player comes off the sheet and is reported.

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
| `api-web.nhle.com/v1/gamecenter/<id>/boxscore` | preseason stats — the aggregate API publishes none |
| The Odds API *(optional)* | prop lines, if `ODDS_API_KEY` is set |

ESPN is not used. It 403s from some networks, and the NHL's own feed is better.

## Four things that will bite you

**The stats API pages unstably.** `skater/summary` caps at 100 rows a page and
refuses to page past 10,000, while a season is ~47,000 rows. Worse, sorting on
`gameDate` alone leaves rows within a night in arbitrary order, so paging
duplicates some and drops others — the first pull came back with 1,108
duplicates *and* McDavid two games short of the 82 he played. Every pull is
therefore chunked by team and sorted on `gameId` + `playerId`, which is unique.
`build_rows` also dedupes on the way in. If you add a report, keep both.

**The logs span seasons, and the live one has to refresh.** A log runs last
season, then the preseason, then this season. Picking one season instead -- this
one as soon as it had games -- left five games of data on day two: twenty-two
clubs with no players. And a season's cache is only permanent once the season is
over; `build_rows(..., live=True)` re-pulls from the last cached night onward on
every build, and the play-by-play cache grows game by game. Both were
frozen-on-first-pull before.

**A lineup is the active roster.** `current_roster` gives each player's club and
name. Anyone not on a roster is left off his club's board: that is cut camp
invitees (who otherwise take line slots on preseason ice time) and also players
on injured reserve, who cannot score tonight either. Names come from the roster
too -- the stats feed's name field changed under us from "Jack Roslovic" to
"John (Jack) Roslovic".

**Line slots are ranked by ice time.** The NHL publishes no depth chart. C1/D2
and the "allowed to C1" tables are both ordered by TOI within each game, which
is the honest proxy: the coach's top line is whoever he plays the most.

## The research tab

**Player Logs** -- each skater's game log on the left, what the opponent allows
to that line slot on the right. Dates run oldest at the top, most recent at the
bottom, next to the average they feed.

A **Puck Line & Moneyline** board (P1/P2/P3/F2P splits per club) was built and
then taken out: the NHL publishes no historical odds and no free feed carries
them, so it could show results but not lines. `team_trends.py` and its cached
period splits are still here if a price feed is ever connected.

## Preseason

The NHL's aggregate stats API publishes **nothing** for the preseason -- twenty-two
games in, `skater/summary` with `gameTypeId=1` still answered zero rows. The
per-game boxscores carry all of it, so `preseason.py` walks the preseason
schedule and reads them directly (the same gap `espn_preseason.py` fills on the
football side), and the play-by-play crawl covers those games for iFF/iSCF too.

Preseason is **merged into the same log**, not offered as a separate source:
a handful of games a club is too thin to stand alone, but fine as the newest
entries in a 25-game window. Those rows carry `pre: true` and show a PRE tag.
Two things that came with merging:

- The merge has to run **before** `build_aggregates`. Appended after, the rows
  were never aggregated and the build logged a merge that had not happened.
- Preseason boxscores abbreviate names ("S. Reinhart"), so a player's name is the
  fullest spelling in his window, not the latest row's.

The page opens on **opening night** (`SEASON_OPENER` in `nhl-research.js`) while
the season has not started; after that it follows today.

## Going live: the image host

Every logo and headshot loads from `https://assets.nhle.com`, which has to be in
`img-src` in `preview/_headers`. The local server sends no CSP, so a missing
entry never shows up here -- only on the deployed site, as every image blank.

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
  preseason.py      preseason stats from boxscores (the stats API has none)
  team_trends.py    per-period team splits (unused since the P/L board came out)
  build_slate.py    assembles preview/data/nhl-research-<date>.json
  atgs_sheet.py     builds the cheat sheet page
  atgs_days/        the day's plays, pasted from the Prop List
  templates/        atgs_sheet.html
  cache/            per-season raw pulls (gitignored-sized, ~2.6 MB/season)

preview/nhl-research/
  index.html  nhl-research.css  nhl-research.js    the research tab
  atgs.html   atgs-manifest.json  archive/         the cheat sheet
```

`nhl-research.css` imports the NFL stylesheet and overrides only the palette and
the few hockey-specific pieces. Fix a layout bug on either tab and both get it.
