#!/usr/bin/env python3
"""Fix batter chips/notes: face opposing SP only (never own team's pitcher)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Batter -> team abbrev for 2026-05-18 slate props
PLAYER_TEAMS = {
    "Junior Caminero (R)": "TB",
    "Coby Mayo (R)": "BAL",
    "Pete Alonso (R)": "TB",
    "Samuel Basallo (L)": "BAL",
    "Yandy Diaz (R)": "TB",
    "Kyle Schwarber (L)": "PHI",
    "Adolis Garcia (R)": "PHI",
    "Alec Bohm (R)": "PHI",
    "JJ Bleday (L)": "CIN",
    "Elly De La Cruz (S)": "CIN",
    "Tyler Stephenson (R)": "CIN",
    "Matt McLain (R)": "CIN",
    "J.T. Realmuto (R)": "PHI",
    "Will Benson (L)": "CIN",
    "Austin Riley (R)": "ATL",
    "Matt Olson (L)": "ATL",
    "Mike Yastrzemski (L)": "ATL",
    "Jakob Marsee (L)": "MIA",
    "Otto Lopez (R)": "MIA",
    "Xavier Edwards (S)": "MIA",
    "Dillon Dingler (R)": "DET",
    "Rhys Hoskins (R)": "DET",
    "Travis Bazzana (L)": "CLE",
    "James Wood (L)": "WSH",
    "Mark Vientos (R)": "NYM",
    "Jose Tena (L)": "WSH",
    "Juan Soto (L)": "NYM",
    "MJ Melendez (L)": "NYM",
    "Paul Goldschmidt (R)": "TOR",
    "Trent Grisham (L)": "NYY",
    "George Springer (R)": "TOR",
    "Kazuma Okamoto (R)": "TOR",
    "Jazz Chisholm Jr. (L)": "NYY",
    "Amed Rosario (R)": "TOR",
    "Ernie Clement (R)": "TOR",
    "Byron Buxton (R)": "MIN",
    "Yordan Alvarez (L)": "HOU",
    "Ryan Jeffers (R)": "MIN",
    "Brice Matthews (R)": "HOU",
    "Zach Dezenzo (R)": "HOU",
    "Tristan Gray (L)": "HOU",
    "Bobby Witt Jr. (R)": "KC",
    "Michael Massey (L)": "KC",
    "Salvador Perez (R)": "KC",
    "Jac Caglianone (L)": "KC",
    "Ceddanne Rafaela (R)": "BOS",
    "Wilyer Abreu (L)": "BOS",
    "Mickey Gasper (S)": "BOS",
    "Seiya Suzuki (R)": "CHC",
    "Michael Busch (L)": "CHC",
    "Michael Conforto (L)": "CHC",
    "Ian Happ (S)": "CHC",
    "Pete Crow-Armstrong (L)": "CHC",
    "Andrew Vaughn (R)": "MIL",
    "Jake Bauers (L)": "CHC",
    "Hunter Goodman (R)": "COL",
    "Jordan Beck (R)": "COL",
    "Kyle Karros (R)": "COL",
    "Mickey Moniak (L)": "COL",
    "Jake Burger (R)": "TEX",
    "Kyle Higashioka (R)": "TEX",
    "Shea Langeliers (R)": "ATH",
    "Brent Rooker (R)": "ATH",
    "Zack Gelof (R)": "ATH",
    "Jorge Soler (R)": "LAA",
    "Mike Trout (R)": "LAA",
    "Yoan Moncada (S)": "LAA",
    "Munetaka Murakami (L)": "SEA",
    "Colson Montgomery (L)": "CHW",
    "Miguel Vargas (R)": "CHW",
    "Andrew Benintendi (L)": "CHW",
    "Jarred Kelenic (L)": "CHW",
    "Julio Rodriguez (R)": "SEA",
    "Randy Arozarena (R)": "SEA",
    "Rob Refsnyder (R)": "SEA",
    "Shohei Ohtani (L)": "LAD",
    "Mookie Betts (R)": "LAD",
    "Will Smith (R)": "LAD",
    "Andy Pages (R)": "LAD",
    "Jackson Merrill (L)": "SD",
    "Manny Machado (R)": "SD",
    "Gavin Sheets (L)": "SD",
    "Corbin Carroll (L)": "ARI",
    "Nolan Arenado (R)": "ARI",
    "Rafael Devers (L)": "ARI",
    "Willy Adames (R)": "ARI",
    "Gabriel Moreno (R)": "ARI",
    "Casey Schmitt (R)": "ARI",
    "Harrison Bader (R)": "ARI",
    "Eric Haase (R)": "ARI",
    "Luis Arraez (L)": "ARI",
}

TITLE_RE = re.compile(
    r"^([A-Z]{2,4}) @ ([A-Z]{2,4}) - (.+?) \([^)]+,\s*([A-Z]{2,4})\)\s+vs\s+(.+?) \([^)]+,\s*([A-Z]{2,4})\)\s*$"
)


def pitcher_last(full: str) -> str:
    """Last name only; strip emoji (e.g. 🧤) so parse_game never treats glove as the SP."""
    s = re.sub(r"[\U0001f300-\U0001ffff]", "", full).strip()
    parts = [p for p in s.split() if p]
    return parts[-1] if parts else s


def normalize_title(title: str) -> str:
    """Decode JS \\uXXXX escapes in titles read from index.html (surrogate pairs → emoji)."""
    if "\\u" not in title:
        return title
    try:
        return title.encode("utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return title


def parse_game(title: str) -> dict:
    title = normalize_title(title)
    m = TITLE_RE.match(title.strip())
    if not m:
        raise ValueError(f"Cannot parse game title: {title}")
    away, home, p1_raw, t1, p2_raw, t2 = m.groups()
    p1_name, p2_name = pitcher_last(p1_raw), pitcher_last(p2_raw)
    if t1 == home:
        home_p, away_p = (p1_name, t1), (p2_name, t2)
    elif t1 == away:
        away_p, home_p = (p1_name, t1), (p2_name, t2)
    elif t2 == home:
        home_p, away_p = (p2_name, t2), (p1_name, t1)
    elif t2 == away:
        away_p, home_p = (p1_name, t1), (p2_name, t2)
    else:
        raise ValueError(f"Pitcher teams not in matchup: {title}")
    return {
        "away": away,
        "home": home,
        "away_pitcher": away_p[0],
        "home_pitcher": home_p[0],
        "pitcher_teams": {away: away_p[0], home: home_p[0]},
    }


def opponent_pitcher(batter: str, game: dict) -> str | None:
    team = PLAYER_TEAMS.get(batter)
    if not team:
        return None
    away, home = game["away"], game["home"]
    if team == away:
        return game["home_pitcher"]
    if team == home:
        return game["away_pitcher"]
    return None


def fix_chips(chips: list[str], opp: str) -> list[str]:
    out = []
    for c in chips:
        if c.startswith("vs "):
            out.append(f"vs {opp}")
        elif c.startswith("📜") and " vs " in c:
            out.append(re.sub(r"vs\s+[\w.\s]+", f"vs {opp}", c))
        else:
            out.append(c)
    if not any(x.startswith("vs ") for x in out):
        out.insert(0, f"vs {opp}")
    return out


def fix_note(note: str, game: dict, opp: str, batter_team: str) -> str:
    own_pitchers = {game["pitcher_teams"].get(batter_team, "")}
    # Also replace the other pitcher's name when it was wrongly cited as the matchup SP
    for pname in game["pitcher_teams"].values():
        if pname and pname != opp:
            # possessive and plain mentions of wrong (own-team) pitcher
            if pname == game["pitcher_teams"].get(batter_team):
                note = re.sub(rf"\b{re.escape(pname)}'s\b", f"{opp}'s", note, flags=re.I)
                note = re.sub(rf"\b{re.escape(pname)}\b", opp, note, flags=re.I)
    return note


def fix_games(games: list[dict]) -> tuple[list[dict], list[str]]:
    fixes = []
    for g in games:
        info = parse_game(g["title"])
        for r in g["rows"]:
            batter = r["name"]
            team = PLAYER_TEAMS.get(batter)
            opp = opponent_pitcher(batter, info)
            if not team:
                fixes.append(f"NO TEAM: {batter} in {g['title'][:40]}")
                continue
            if team not in (info["away"], info["home"]):
                fixes.append(f"WRONG GAME: {batter} ({team}) in {info['away']} @ {info['home']}")
                continue
            if not opp:
                continue
            old_chip = next((c for c in r["chips"] if c.startswith("vs ")), "")
            new_chips = fix_chips(r["chips"], opp)
            new_chip = next((c for c in new_chips if c.startswith("vs ")), "")
            note_before = r["note"]
            r["chips"] = new_chips
            r["note"] = fix_note(r["note"], info, opp, team)
            if old_chip != new_chip:
                fixes.append(f"CHIP {batter}: {old_chip} -> {new_chip}")
            if r["note"] != note_before:
                fixes.append(f"NOTE {batter}: own-team pitcher wording corrected")
    return games, fixes


def emit_games_js(games: list[dict]) -> str:
    lines = ["            const games = ["]
    for g in games:
        j = lambda v: json.dumps(v, ensure_ascii=False)
        lines.append(
            f'                {{ title: {j(g["title"])}, description: {j(g["description"])}, rows: ['
        )
        for r in g["rows"]:
            blast = f', blast: {j(r["blast"])}' if r.get("blast") else ""
            overdue = ", overdue: true" if r.get("overdue") else ""
            chips = ", ".join(j(c) for c in r["chips"])
            lines.append(
                f'                    {{ name: {j(r["name"])}, odds: {j(r["odds"])}, score: {r["score"]}, emojis: {j(r["emojis"])}{blast}{overdue}, note: {j(r["note"])}, chips: [{chips}] }},'
            )
        lines.append("                ]},")
    lines.append("            ];")
    return "\n".join(lines)


def patch_html(path: Path, games_js: str) -> bool:
    t = path.read_text(encoding="utf-8")
    pat = re.compile(r"            const games = \[[\s\S]*?            \];")
    m = pat.search(t)
    if not m:
        return False
    t2 = t[: m.start()] + games_js + t[m.end() :]
    if t2 != t:
        path.write_text(t2, encoding="utf-8")
        return True
    return False


def main() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location("build0518", ROOT / "build-sheet-2026-05-18.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    games = mod.games
    games, fixes = fix_games(games)
    games_js = emit_games_js(games)
    (ROOT / "_games-0518.txt").write_text(games_js + "\n", encoding="utf-8")
    print(f"Fixed {len(fixes)} chip/note issues:")
    for f in fixes:
        print(" ", f)
    targets = [
        ROOT / "preview" / "index.html",
        ROOT / "index.html",
    ]
    for p in targets:
        if p.is_file() and patch_html(p, games_js):
            print("patched", p.relative_to(ROOT))
        if p.is_file():
            patch_top5_coby(p)


def patch_top5_coby(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    old = "Coby Mayo <small>Rogers RHB lane at Tropicana</small>"
    new = "Coby Mayo <small>McClanahan RHB lane at Tropicana</small>"
    if old in t:
        path.write_text(t.replace(old, new), encoding="utf-8")
        print("patched TOP5 Coby Mayo in", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
