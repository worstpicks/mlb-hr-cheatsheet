from pathlib import Path
import re

t = Path("preview/index.html").read_text(encoding="utf-8")
# Match game objects with title + description fields used in sheet
games = re.findall(
    r'title:\s*"([^"]+)".{0,400}?description:\s*"([^"]*)"',
    t,
    re.S,
)
if not games:
    games = re.findall(
        r'title:\s*"([^"]+)".{0,800}?desc:\s*"([^"]*)"',
        t,
        re.S,
    )
print("games found", len(games))
miss = []
for title, desc in games:
    has_park = ("%" in desc) or ("Park" in desc) or ("park" in desc)
    has_split = ("LHB" in desc) or ("RHB" in desc) or ("vs L" in desc) or ("split" in desc.lower())
    if not has_park or not has_split:
        miss.append((title[:70], has_park, has_split, desc[:160]))
print("missing park/split", len(miss))
for m in miss:
    print(m)
if games:
    print("SAMPLE:", games[0][0])
    print(games[0][1][:280])
