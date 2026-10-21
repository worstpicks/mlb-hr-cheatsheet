# WorstPickz Prop Shop / Goblin's Ledger

`/nba-research/prop-shop.html`: the night's handpicked NBA props, each rated out
of 100 and ranked, built the same way as the NHL goal sheet. The owner picks the
props; the shop rates them. It never adds picks of its own. Publishing still
needs the owner's go, one deploy per night.

## A night's build

1. Save the research tab's Prop List export (`nba-prop-research.txt`) as
   `nba_research/prop_days/<date>.txt`: `2026-10-20 | Jayson Tatum | over 1.5 STL | auto, last 5, all`.
   Markets: PTS REB AST 3PM STL BLK PRA PR PA RA SB.
2. First-basket picks go in `prop_days/<date>.first_basket.txt`, one `Name | TEAM` per line
   (ESPN codes: NY, SA, GS, NO...).
3. Check the lineups and write `prop_days/<date>.lineup.txt`:
   `out TEAM Name | note` (pulled to "Off the Shelf"), `doubt TEAM Name | note` (red chip, -5 role),
   `starters TEAM: five names` (RotoWire's expected lineup; drives minutes and first-basket warnings).
   Sources: ESPN's injury JSON and rotowire.com/basketball/nba-lineups.php.
4. `python -m nba_research.dk_props --date <date>`: DraftKings prices from ESPN's public odds API
   (no key) into `data/nba-dk-props-<date>.json`.
5. `python -m nba_research.prop_shop --date <date>`: writes `prop-shop.html`, `prop-shop-archive/<date>.html`,
   the manifest and `preview/data/nba-prop-ledger.json` (the old shell's file, kept in step), and refreshes
   the research tab's with / without file `preview/data/nba-splits.json` (below). Commit it with the sheet.
   The build log prints every prop's score, chance, price and edge, the props pulled and why,
   and the first-basket math.
   A template change on a night already published: `python -m nba_research.prop_shop --date <date> --rerender`
   re-renders the page from the SHEET it carries and refuses the write if any field would change, so a new
   look never moves a pick, a rating or a price (safe on a graded night too).
6. The next morning, `python -m nba_research.prop_grade` grades the night into `prop_shop_record.csv`
   (below) and prints the record. Commit the CSV with that night's sheet so it rides the same deploy.

## The model (prop_model.py)

projection = minutes x per-minute rate x matchup x pace. Rates read every game of last season
(`season_rates/2025-26.json.gz`) plus the preseason at 0.4 weight, fading old games and shrinking
toward the position. The chance of clearing a line is a negative binomial whose level, spread and
scatter were fitted on 2025-26 (`prop_fit.py`). It was checked on Feb–Apr games the fit never saw
and beat the base rate in every market (`prop_shop_fit.json` → `check`).
Preseason minutes are scaled to a regular-season role: 1.5x for starters, 1.2x for bench players,
measured on the opening-week rosters.

A player on a new club counts his preseason there in full (it is the only look at his new role), not at
the usual 0.4; a player with no regular season behind him (rookies, Lillard's missed year) is capped at
34 projected minutes. Both from 10/21: Morant read 8 assists from his Memphis year against 4.8 in
Portland's exhibitions, and Caleb Wilson read 39.9 minutes.

Rating: Model chance 40 · Track record 20 · Matchup 15 · Role & minutes 15 · Price check 10.
Bands: 90 Elite, 80 Strong, 70 Playable, 60 Thin, else Dart. Bargain Bin (value) = plus money,
4+ points over DraftKings' implied chance, matchup 50/100+, no doubt, no thin sample, and no
"book gap" (DraftKings' ladder centered >35% off our projection, usually a role it already moved;
checked once the book centers on 1.5 or more, and a ladder that opens below even money is extended one
rung down to find its center). A book-gap prop also sits out the Top Shelf.

First basket (first_basket.py): ESPN play-by-play of each player's last 15 games gives the jumpers'
tip records, his side's first basket and his share of it as a starter. Chance = side scores first
(57% with the tip) x his share, shrunk toward a fifth; a projected bench player gets a tenth of it.

DraftKings' feed files first-quarter ladders under the full-game market name; `dk_props.ladders()`
splits them and keeps the one that matches the main over/under.

Refit after a season: `python -m nba_research.backtest --season <YYYY>` (box scores), then
`python -m nba_research.prop_fit --season <YYYY>`.

## A teammate out tonight (splits.py)

From the 10/22 build on; every earlier archive is untouched. When a listed player's
teammate who carries some of the offense is out tonight, his projected minutes lean toward his games
without that teammate. The research tab shows the same split for any teammate (player dialog → "With /
without"; `nba_research/README.md`).

- **Out tonight**: an `out` line in `<date>.lineup.txt` or the slate's Out flag, on his club.
- **Carries the offense**: 10+ points a game over the teammate's last 30 regular-season games.
- **The split**: the player's regular-season games on a club the teammate was on, split by whether the
  teammate is in the box. "Sat" = on the club and not in the box (DNP, injury, rest). On a club = from the
  day after his last game for another club to the day before his first game for the next; a player on a
  roster today is on it all season so far. Every 2025-26 game (`season_rates/2025-26.json.gz`) plus this
  season's games from the slates. Needs 5+ games with him and 1+ without.
- **The move**: minutes + (without minus with, in minutes a game) x n/(n+8) x (1 - the share of his minutes
  projection that already came from games without him), n = games without. Several teammates out add up,
  capped at 8 minutes either way. Per-minute rates are not moved: the replay below found the rate splits
  were noise at every shrink it tried.
- **On the card**: a 🪑 "Without X" chip; the why line says "Without X: 4.3 rebounds on 29 minutes in 18
  games he sat, 3.5 on 23 with him. Projected minutes up 2.0 for it." (da Silva, 10/21 dry run); the Role
  reason repeats the minutes. The build log prints each one.

**The check** (`python -m nba_research.splits --backtest`, needs the backtest cache; writes `splits_fit.json`):
2025-26 replayed exactly as `prop_fit.py` does, each morning's teammates out read from who was missing from
that night's box, every split built only from games before that morning. The knobs (points gate 10/14/18,
minutes shrink 4/8/16/off, rate shrink 3/9/off x the model's own, pooled or paired minutes gap) were picked
on Oct-Jan (13,195 player-games); Feb-Apr (10,522, 7,165 of them moved) only checks them. Picked: 10 points,
shrink 8, rates off, pooled gap. Held-out log loss, the six stats summed per player-game:

| | off | on |
|---|---|---|
| all Feb-Apr player-games | 10.3614 | 10.3245 |
| the 7,165 it moves | 10.5984 | 10.5487 |

Every market improved held out (pts 3.0821 -> 3.0708, reb 2.1825 -> 2.1753, ast 1.8037 -> 1.7947,
3pm 1.3324 -> 1.3272, stl 1.1478 -> 1.1449, blk 0.8129 -> 0.8117, pra 3.4241 -> 3.4091), and so did every
"N+" check line on the moved rows (pts 15+ 0.4692 -> 0.4606, ast 5+ 0.3449 -> 0.3394, pra 25+ 0.4224 -> 0.4103).
All 18 minutes-only settings in the grid improved held out (+0.015 to +0.038 log-likelihood per player-game);
every setting that also moved per-minute rates did worse on Oct-Jan than minutes alone (best +0.0078 vs +0.0108).
So `enabled` is true. The rule: on only if the knobs picked on Oct-Jan lower the Feb-Apr log loss, both
overall and on the rows it moves. Rerunning the replay can turn it back off, nothing else does.

Known soft spots: a teammate's "without" games can come from a different role era (Clifford 10/21: his four
games without Raynaud were all early November, before Clifford's minutes grew, so it reads -4.3), and a
three-game split with an injury exit in it (Franz Wagner without Anthony Black) still moves a couple of
minutes. A paired gap (each without-game against his nearest with-games) was meant to fix the first; it
scored a hair worse than the pooled gap on Oct-Jan, so the pooled gap runs. Review big moves before pushing.

## Grading and the record (prop_grade.py)

The morning after a night, once its games are final:

    python -m nba_research.prop_grade                     # every archived night, then the report
    python -m nba_research.prop_grade --date 2026-10-20   # one night
    python -m nba_research.prop_grade --report            # the report only, no ESPN calls

It reads each night's `var SHEET` from `preview/nba-research/prop-shop-archive/<date>.html` (the sheet as
published, prices and all) and grades every prop on the shelf plus the first-basket cards against
ESPN's final box scores (`build_slate.fetch` + `parse_summary`; first basket from `first_basket.opening`).
Props "off the shelf" (scratched before the build) were never rated and are not graded.

- **hit / miss**: an Over N.5 needs floor(N)+1, an Under N.5 floor(N) or fewer. A whole-number line that
  lands exactly is a **push**.
- **void**: he never checked in (a DNP or not in the box at all), or the game was postponed or canceled.
  Seconds on the floor count as playing. First basket is void the same way, else a hit only if he made
  the game's first field goal (free throws never settle it).
- A game that isn't final yet stays ungraded and is picked up on the next run. Its in-progress summary is
  deleted from `nba_research/cache` so the research build never reads a half-played box score as a final.

Rows are appended to `nba_research/prop_shop_record.csv` (committed with the sheet): `date, pid, market,
line, side, chance, price, implied, score, band, tags, result, actual`, then `name, team, opp, game,
prop_id, edge, mean, minutes, actual_min`, the five rating parts (`pts_chance` ... `pts_price`) and a note.
`chance`, `implied` and `edge` are percent; `price` is American and only set for overs DraftKings posted;
`tags` holds `fav` (Top Shelf) and `val` (Bargain Bin). First-basket rows use market `first_basket`, side
`yes`, `actual` 1/0 and name the scorer in the note.

Rerunning is safe: a (date, prop_id) already in the record is never graded or written again. The grader
never writes an archive, and once a night has a row `prop_shop.py` refuses to rebuild it, so the record
always matches the page it was graded from. To rebuild a graded night on purpose, delete its rows first.

The report prints hit rate by score band and by market, hit rate by model-chance bucket, Brier score and
log loss for the model next to DraftKings' implied chance on the same priced props (DraftKings' number
still has the vig in, which flatters the model a little), and flat 1-unit ROI at the listed price for all
priced props, Top Shelf, Bargain Bin and first baskets.

**Changing the model waits for the record.** Below 150 graded props it says so and stops. From 150 it says
whether the record argues for a change: a higher band hitting less than a lower one, DraftKings beating
the model on Brier, or a chance bucket (25+ props) more than 8 points off. That is a proposal for the owner.
Nothing refits or reweights automatically; the rating weights stay 40/20/15/15/10 until the owner says.
