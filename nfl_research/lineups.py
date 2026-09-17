"""Each offence's research lineup, chosen from its current depth chart.

The research tab used to show every player who ranked in the top two-to-five of
his position by last season's volume -- fourteen cards a side. Ordering by 2025
yardage also put the wrong man on top: a back now fourth on his club's chart
still headlined because he carried it a lot last year.

A lineup is the skill group a team actually lines up with:

    QB1 · RB1 · RB2 · WR1 · WR2 · WR3 · TE1 · TE2

Eight players, in depth order, from the club's most recent depth chart. Each one
is matched to the stats season's numbers by gsis id. A starter with no games in
that season still gets his card, marked `no_history`, because leaving the actual
TE1 off the board is worse than showing him with an empty log. That is usually a
rookie before his debut, but once the stats season is the current one it is just
as often a veteran who missed the opening weeks -- Brock Bowers after week one.
"""
from __future__ import annotations

# TE2 earns a card: two-tight-end sets are common enough that the second one
# sees real targets, and in the red zone he is often the one they throw to.
LINEUP = (("QB", 1), ("RB", 2), ("WR", 3), ("TE", 2))
SKILL = tuple(pos for pos, _ in LINEUP)

ESPN_HEADSHOT = "https://a.espncdn.com/i/headshots/nfl/players/full/{}.png"


def _player_index(players: dict) -> dict[str, dict]:
    """gsis id -> player dict, across every team and position.

    Searched league-wide rather than within the club, so a player the roster
    re-filing missed is still found under whatever team his numbers landed on.
    """
    index: dict[str, dict] = {}
    for positions in players.values():
        for bucket in positions.values():
            for p in bucket:
                pid = p.get("player_id")
                if pid and pid not in index:
                    index[pid] = p
    return index


def _fallback(pool: dict, pos: str, count: int) -> list[dict]:
    """No depth chart for this club: top of last season's volume, but only as
    many as a real lineup holds, so the card count stays honest either way."""
    return [dict(p, rank=i) for i, p in enumerate((pool.get(pos) or [])[:count], start=1)]


def build_lineups(players: dict, depth: dict[str, list[dict]], teams: set[str]) -> tuple[dict, dict]:
    """Return (lineups, report). `lineups` has the same shape as `players`:
    team -> pos -> [player dicts], ranks rewritten to depth order."""
    index = _player_index(players)
    lineups: dict[str, dict] = {}
    report = {"from_depth": 0, "fallback": 0, "no_history": [], "teams_without_chart": []}

    for team in sorted(teams):
        chart = [r for r in depth.get(team, []) if r.get("pos") in SKILL]
        pool = players.get(team, {})
        out: dict[str, list[dict]] = {}

        if not chart:
            report["teams_without_chart"].append(team)
            for pos, count in LINEUP:
                out[pos] = _fallback(pool, pos, count)
                report["fallback"] += len(out[pos])
            lineups[team] = out
            continue

        for pos, count in LINEUP:
            slots = sorted((r for r in chart if r["pos"] == pos), key=lambda r: r["rank"])
            picked: list[dict] = []
            for row in slots:
                if len(picked) == count:
                    break
                found = index.get(row.get("gsis_id") or "")
                if found:
                    # his own numbers, but the chart's name, position and slot
                    card = dict(found, name=row["name"], pos=pos, rank=len(picked) + 1)
                else:
                    card = {
                        "name": row["name"],
                        "player_id": row.get("gsis_id"),
                        "pos": pos,
                        "rank": len(picked) + 1,
                        "gp": 0,
                        "headshot": ESPN_HEADSHOT.format(row["espn_id"]) if row.get("espn_id") else "",
                        "stats": {},
                        "log": [],
                        "no_history": True,
                    }
                    report["no_history"].append(f"{team} {pos}{len(picked) + 1} {row['name']}")
                picked.append(card)
            out[pos] = picked
            report["from_depth"] += len(picked)
        lineups[team] = out

    return lineups, report
