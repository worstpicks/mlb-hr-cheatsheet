#!/usr/bin/env python3
"""Build 2026-05-31 sheet from imported CSVs and user prop list."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

from csv_slate_meta import derive_games_from_csv
from sheet_data import load_pitcher_risk, resolve_pitcher

ROOT = Path(__file__).resolve().parent
DATE = "2026-05-31"
OUT = ROOT / "build-sheet-2026-05-31.py"

TEAM_ALIAS = {
    "CHW": "CWS",
    "WAS": "WSH",
}

RAW_PROPS = [
    "Coby Mayo",
    "Pete Alonso",
    "Colton Cowser",
    "Kazuma Okamoto⭐",
    "CJ Abrams⭐",
    "James Wood",
    "Gavin Sheets",
    "Ty France",
    "Brandon Lowe⭐",
    "Oneil Cruz⭐",
    "Spencer Horwitz",
    "Konnor Griffin",
    "Byron Buxton",
    "Trevor Larnach",
    "Jonathan Aranda⭐",
    "Yandy Diaz",
    "Mike Trout⭐",
    "Oswald Peraza",
    "Jo Adell",
    "Juan Soto⭐",
    "Jared Young",
    "Mj Melendez",
    "Heriberto Hernandez⭐",
    "Otto Lopez",
    "Owen Caissie",
    "Rhys Hoskins⭐",
    "Kyle Manzardo",
    "Jarren Durran⭐",
    "Wilson Contreras",
    "Mickey Gasper",
    "JJ Bleday",
    "Elly De La Cruz⭐",
    "Matt McLain",
    "Matt Olson",
    "Yordan Alvarez⭐",
    "Christian Walker",
    "Cam Smith",
    "Zach Dezenzo",
    "Garrett Mitchell⭐",
    "Christian Yelich",
    "Jackson Chourio",
    "Colson Montgomery",
    "Colt Keith",
    "Spencer Torkelson",
    "Brandon Nimmo⭐",
    "Josh Jung",
    "Bobby Witt Jr⭐",
    "Jac Caglianone",
    "Salvador Perez",
    "Hunter Goodman",
    "Willi Castro",
    "Willy Adames⭐",
    "Rafael Devers⭐",
    "Casey Schmitt",
    "Carlos Cortes",
    "Tyler Soderstrom",
    "Ben Rice",
    "Cody Bellinger",
    "Paul Goldschmidt",
    "Julio Rodriguez",
    "Luke Raley⭐",
    "Mitch Garver",
    "Patrick Wisdom",
    "Ketel Marte⭐",
    "Corbin Carroll",
    "Freddie Freeman",
    "Shohei Ohtani⭐",
    "Will Smith⭐",
    "Max Muncy",
    "Trea Turner",
    "Brandon Marsh",
    "Kyle Schwarber",
    "Nolan Gorman",
    "JJ Wetherholt",
    "Pete Crow Armstrong",
    "Michael Busch",
]

ALIASES = {
    "Mj Melendez": "MJ Melendez",
    "Jarren Durran": "Jarren Duran",
    "Wilson Contreras": "Willson Contreras",
    "Pete Crow Armstrong": "Pete Crow-Armstrong",
    "Jo Adell": "Jo Adell",
}


def canon_team(team: str) -> str:
    return TEAM_ALIAS.get(team.strip().upper(), team.strip().upper())


def canon_game_key(raw: str) -> str:
    m = re.search(r"([A-Z]{2,3})\s*@\s*([A-Z]{2,3})", raw.upper())
    if not m:
        return " ".join(raw.upper().split())
    away = canon_team(m.group(1))
    home = canon_team(m.group(2))
    return f"{away} @ {home}"


def load_park_factors() -> dict[str, dict]:
    path = ROOT / "data" / f"ParkFactors_{DATE}.csv"
    if not path.exists():
        return {}
    import csv

    out: dict[str, dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = canon_game_key(row.get("Game", "").strip())
            if not key:
                continue
            out[key] = {
                "venue": row.get("Venue", "").strip(),
                "hr_pct": row.get("HR %", "").strip(),
                "hr_stadium": row.get("HR % Stadium", "").strip(),
                "hr_weather": row.get("HR % Weather", "").strip(),
            }
    return out


def fmt_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}"


def score_from_stats(hr, near, ev, barrel, blast):
    s = 62 + hr * 4 + near * 2
    if ev:
        s += min(max(ev - 88, 0), 12)
    if barrel:
        s += min(barrel / 3, 10)
    if blast == "high":
        s += 4
    elif blast == "good":
        s += 2
    return min(98, max(58, int(round(s))))


def blast_from_stats(hr: int, near: int, ev: float | None, barrel: float | None) -> str | None:
    ev = ev or 0.0
    barrel = barrel or 0.0
    if hr >= 2 or (hr + near >= 5) or (ev >= 97 and barrel >= 20):
        return "high"
    if hr >= 1 or near >= 2 or ev >= 92 or barrel >= 15:
        return "good"
    return None


def risk_note(label: str, risk_row: dict | None) -> str:
    if not risk_row:
        return f"{label}: no reliable HR-risk sample in today's export"
    overall = risk_row["overall"]
    lhb = risk_row["vs_lhb"]
    rhb = risk_row["vs_rhb"]
    split_lane = "RHB" if rhb >= lhb else "LHB"
    split_val = rhb if rhb >= lhb else lhb
    return (
        f"{label}: {overall:.2f} HR risk "
        f"(vs LHB {fmt_pct(lhb)}, vs RHB {fmt_pct(rhb)}; strongest {split_lane} lane {fmt_pct(split_val)})"
    )


def display(name: str, hand: str) -> str:
    return f"{name} ({hand})"


def odds_text(odds: str) -> str:
    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"


def emoji_string(is_fav: bool, ev: float | None, score: int, blast: str | None, has_bvp: bool) -> str:
    em: list[str] = []
    if ev is not None and ev >= 100:
        em.append("🚀")
    if is_fav:
        em.append("⭐")
    if score >= 88 or blast == "high":
        em.extend(["🌕", "💣"])
    else:
        em.append("💎")
    if has_bvp:
        em.append("📜")
    # preserve order while deduping
    seen = set()
    dedup = []
    for x in em:
        if x not in seen:
            seen.add(x)
            dedup.append(x)
    return " ".join(dedup) if dedup else "💎"


def main() -> int:
    games_csv = {g["key"]: g for g in derive_games_from_csv(DATE)}
    park = load_park_factors()
    pitcher_risk = load_pitcher_risk(ROOT / "data" / f"hr-targets-overall-{DATE}.csv")

    # map each batter to game/team/opposing SP using row["vs"] from source file
    batter_ctx: dict[str, dict] = {}
    for g in games_csv.values():
        for row in g["batters"].values():
            vs = row["vs"]
            if vs == g["away_sp"]:
                team = g["home"]
            elif vs == g["home_sp"]:
                team = g["away"]
            else:
                continue
            batter_ctx[row["name"].lower()] = {
                "game": g["key"],
                "team": team,
                "opp_sp": vs,
                "row": row,
            }

    fav_names: set[str] = set()
    selected: list[str] = []
    for raw in RAW_PROPS:
        fav = raw.endswith("⭐")
        clean = raw[:-1].strip() if fav else raw.strip()
        clean = ALIASES.get(clean, clean)
        selected.append(clean)
        if fav:
            fav_names.add(clean)

    missing: list[str] = []
    props: list[tuple] = []
    team_map: dict[str, str] = {}
    for name in selected:
        ctx = batter_ctx.get(name.lower())
        if not ctx:
            missing.append(name)
            continue
        row = ctx["row"]
        hand = row["hand"]
        odds = row["odds"]
        hr = int(row["hr"] or 0)
        near = int(row["near"] or 0)
        ev = float(row["ev"]) if row["ev"] is not None else 0.0
        barrel = float(row["barrel"]) if row["barrel"] is not None else 0.0
        blast = blast_from_stats(hr, near, ev, barrel)
        score = score_from_stats(hr, near, ev, barrel, blast)
        team_map[name] = ctx["team"]
        props.append((name, hand, odds, score, ctx["opp_sp"], hr, near, ev, barrel, blast, ctx["game"]))

    # favorites with hand display
    favs_display = sorted(
        [display(name, next(p[1] for p in props if p[0] == name)) for name in fav_names if any(p[0] == name for p in props)]
    )

    # game meta + bums
    game_meta: list[dict] = []
    bum_pitchers: set[str] = set()
    for g in sorted(games_csv.values(), key=lambda x: x["key"]):
        away_full = g["away_sp_full"]
        home_full = g["home_sp_full"]
        away_r = resolve_pitcher(pitcher_risk, away_full) or resolve_pitcher(pitcher_risk, g["away_sp"])
        home_r = resolve_pitcher(pitcher_risk, home_full) or resolve_pitcher(pitcher_risk, g["home_sp"])
        if away_r and away_r["overall"] >= 1.0:
            bum_pitchers.add(g["away_sp"])
        if home_r and home_r["overall"] >= 1.0:
            bum_pitchers.add(g["home_sp"])

        pf = park.get(g["key"], {})
        venue = pf.get("venue") or g["key"]
        hr_pct = pf.get("hr_pct") or "N/A"
        hr_stadium = pf.get("hr_stadium") or "N/A"
        hr_weather = pf.get("hr_weather") or "N/A"
        desc = (
            f"{venue} — HR environment {hr_pct} (stadium {hr_stadium}, weather {hr_weather}). "
            f"{risk_note(away_full, away_r)}. {risk_note(home_full, home_r)}."
        )
        title = g["title"]
        game_meta.append(
            {
                "key": g["key"],
                "title": title,
                "desc": desc,
                "away": g["away"],
                "home": g["home"],
                "away_sp": g["away_sp"],
                "home_sp": g["home_sp"],
            }
        )

    prop_by_game: dict[str, list] = {g["key"]: [] for g in game_meta}
    for p in props:
        prop_by_game[p[10]].append(p)

    # basic BvP kept disabled for freshness unless exact same SP match is added later
    bvp: dict[str, str] = {}

    lines = [
        "#!/usr/bin/env python3",
        '"""Generate games[] block for 2026-05-31 MLB HR cheat sheet."""',
        "import json",
        "from pathlib import Path",
        "",
        "from overdue_eval import apply_inferred_due",
        "",
        "ROOT = Path(__file__).resolve().parent",
        "",
        "FAVS = {",
    ]
    for f in favs_display:
        lines.append(f'    "{f}",')
    lines.extend(["}", "", "PLAYER_TEAMS = {"])
    for name, team in sorted(team_map.items()):
        hand = next(p[1] for p in props if p[0] == name)
        lines.append(f'    "{display(name, hand)}": "{team}",')
    lines.extend(["}", "", "BUM_PITCHERS = {"])
    for b in sorted(bum_pitchers):
        lines.append(f'    "{b}",')
    lines.extend(
        [
            "}",
            "",
            "def odds_text(odds):",
            '    return "Listed prop - Over 0.5 HR" if odds == "N/A" else f"Listed {odds} - Over 0.5 HR"',
            "",
            "def row(name, hand, odds, score, emojis, chips, note, blast=None):",
            "    item = {",
            '        "name": f"{name} ({hand})",',
            '        "odds": odds_text(odds),',
            '        "score": score,',
            '        "emojis": emojis,',
            '        "note": note,',
            '        "chips": chips,',
            "    }",
            "    if blast:",
            '        item["blast"] = blast',
            "    return item",
            "",
            "def add_bum_row_emojis(entry):",
            '    chip = entry["chips"][0].replace("vs ", "").strip()',
            "    if chip not in BUM_PITCHERS:",
            "        return",
            '    em = entry["emojis"]',
            '    if "⚾" not in em:',
            '        em = f"{em} ⚾".strip()',
            '    if "🕊️" not in em:',
            '        em = f"{em} 🕊️".strip()',
            '    if "🧤" not in em:',
            '        em = f"{em} 🧤".strip()',
            '    entry["emojis"] = em',
            "",
            "games = [",
        ]
    )

    for gm in game_meta:
        lines.append("    {")
        lines.append(f'        "title": {json.dumps(gm["title"], ensure_ascii=False)},')
        lines.append(f'        "description": {json.dumps(gm["desc"], ensure_ascii=False)},')
        lines.append('        "rows": [')
        for p in prop_by_game[gm["key"]]:
            name, hand, odds, score, chip, hr, near, ev, barrel, blast, _game = p
            is_fav = display(name, hand) in favs_display
            em = emoji_string(is_fav, ev, score, blast, name in bvp)
            stat = f"{hr} HR"
            if near:
                stat += f", {near} near-HR"
            stat += f", {ev:.1f} mph EV"
            if barrel:
                stat += f" and {barrel:.1f}% barrels"
            if is_fav:
                stat = f"Worst Pickz favorite with {stat}"
            note = f"{stat}. Draws opposing starter {chip}; {gm['key']}."
            if blast:
                lines.append(
                    f'            row("{name}", "{hand}", "{odds}", {score}, "{em}", ["vs {chip}"], '
                    f'"""{note}""", blast="{blast}"),'
                )
            else:
                lines.append(
                    f'            row("{name}", "{hand}", "{odds}", {score}, "{em}", ["vs {chip}"], '
                    f'"""{note}"""),'
                )
        lines.extend(["        ],", "    },"])

    lines.extend(
        [
            "]",
            "",
            "for game in games:",
            "    for entry in game['rows']:",
            "        add_bum_row_emojis(entry)",
            "        apply_inferred_due(entry, game)",
            "",
            "if __name__ == '__main__':",
            "    def js_string(value):",
            "        return json.dumps(value, ensure_ascii=False)",
            "",
            "    def emit_games_js(games_data):",
            "        out = ['const games = [']",
            "        for game in games_data:",
            "            out.append('    {')",
            "            out.append(f\"        title: {js_string(game['title'])},\")",
            "            out.append(f\"        description: {js_string(game['description'])},\")",
            "            out.append('        rows: [')",
            "            for entry in game['rows']:",
            "                parts = [",
            "                    f\"name: {js_string(entry['name'])}\",",
            "                    f\"odds: {js_string(entry['odds'])}\",",
            "                    f\"score: {entry['score']}\",",
            "                    f\"emojis: {js_string(entry['emojis'])}\",",
            "                    f\"note: {js_string(entry['note'])}\",",
            "                    f\"chips: {js_string(entry['chips'])}\",",
            "                ]",
            "                if entry.get('blast'):",
            "                    parts.append(f\"blast: {js_string(entry['blast'])}\")",
            "                out.append('            { ' + ', '.join(parts) + ' },')",
            "            out.append('        ],')",
            "            out.append('    },')",
            "        out.append('];')",
            "        return '\\n'.join(out)",
            "",
            "    out = ROOT / '_games-0531.txt'",
            "    out.write_text(emit_games_js(games) + '\\n', encoding='utf-8')",
            "    print('wrote', out.name)",
        ]
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.name} with {len(props)} props, {len(game_meta)} games, {len(favs_display)} favorites")
    if missing:
        print(f"WARN missing {len(missing)} props from CSV:")
        for n in missing:
            print(" ", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
