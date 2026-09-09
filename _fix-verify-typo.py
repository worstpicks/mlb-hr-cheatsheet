from pathlib import Path

p = Path("verify-summary-0710.py")
t = p.read_text(encoding="utf-8")
old = 'games_counts = Counter(r.get("game_key") for r in hits)\nover_game = [g for g, c in game_counts.items() if c > 2]'
new = 'per_game = Counter(r.get("game_key") for r in hits)\nover_game = [g for g, c in per_game.items() if c > 2]'
if old not in t:
    raise SystemExit(f"pattern not found: {old!r}")
p.write_text(t.replace(old, new), encoding="utf-8")
print("fixed")
