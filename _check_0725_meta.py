from pathlib import Path
import re

html = Path("preview/index.html").read_text(encoding="utf-8")
print("sheet-date", re.search(r'name="sheet-date" content="([^"]+)"', html).group(1))
print("star char count", html.count("⭐"))
print("gem char count", html.count("💎"))
print("glove char count", html.count("🧤"))
for name in [
    "Brian Keller",
    "Connor Prielipp",
    "Brandon Young",
    "Mason Barnett",
    "Tim Mayza",
    "Mike Paredes",
]:
    print(name, "present" if name in html else "ABSENT")

src = Path("build-0725-from-csv.py").read_text(encoding="utf-8")
m = re.search(r"RAW_PROPS = \[(.*?)\]", src, re.S)
props = re.findall(r'"([^"]+)"', m.group(1))
print("RAW_PROPS", len(props))
stars = sum(1 for p in props if "⭐" in p)
gems = sum(1 for p in props if "💎" in p)
print("star props", stars, "gem props", gems)
for p in props:
    print(" -", p)
