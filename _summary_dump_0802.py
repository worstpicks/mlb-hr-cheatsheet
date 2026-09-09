import re
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
m = re.search(r"Goblin's Insight(.*?)Top 5 HR Tickets", html, re.S)
chunk = m.group(1)
print("=== GOBLIN ===")
for h4, body in re.findall(r"<h4>(.*?)</h4>\s*<o[lu]>(.*?)</o[lu]>", chunk, re.S):
    names = re.findall(r"<strong>(.*?)</strong>", body)
    print(h4, "->", [re.sub(r"\s*HR$", "", n) for n in names])

print("\n=== TOP5 / WEATHER / LONG ===")
for title in ("Top 5 HR Tickets", "Top 5 Weather Heavy", "Longshot"):
    idx = html.find(title)
    print(title, re.findall(r"<td>([A-Za-z][^<]{2,40})</td>", html[idx : idx + 2500])[:8])
