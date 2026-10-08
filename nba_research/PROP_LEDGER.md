# WorstPickz Prop Shop / Goblin's Ledger

Local shell: `/nba-research/prop-shop.html`. It uses the existing NHL/NFL
sheet layout and shared visual rules. No generated picks or minimum count.

Curated entries are stored in `preview/data/nba-prop-ledger.json`.
Set `date` to the slate's YYYY-MM-DD and `updated` to its ISO timestamp.
Each item in `picks` uses these fields:

- `player`: chosen player name
- `player_id`: NBA research player ID, as a string
- `game_id`: slate game ID, as a string
- `market`: pts, reb, ast, threem, pra, pr, pa, ra, stl, blk, stocks, tov, dd, td
- `side`: over or under
- `line`: a number
- `matchup`: matchup text
- `kickoff`: optional ISO time
- `odds`, `book`: optional supplied price and sportsbook
- `note`: your reasoning
- `result`: pending, hit, miss, or void; settlement is supplied, not inferred

The shell deliberately starts empty. Publishing still requires the user's
explicit authorization, consistent with the local-first workflow.
