from pathlib import Path
import re

html = Path("preview/index.html").read_text(encoding="utf-8")
m = re.search(
    r'\{ name: "Munetaka Murakami[^"]*".*?emojis: "([^"]*)".*?chips: (\[[^\]]+\])',
    html,
)
print("found", bool(m))
if m:
    print("emojis", m.group(1))
    print("chips", m.group(2))
    print("has star", "⭐" in m.group(1))
    print("has rocket", "🚀" in m.group(1))
intro = re.search(r"(\d+) listed HR props.*?<strong>(\d+) Worst Pickz Favorite", html)
print("intro", intro.group(0)[:120] if intro else "n/a")
# fav3
if "Munetaka Murakami" in html.split("Favorite 3 Leg")[1][:800]:
    print("in fav3 block")
else:
    print("fav3 snippet:", html.split("Favorite 3 Leg")[1][:400])
