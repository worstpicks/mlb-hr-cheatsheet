from pathlib import Path
import re

text = Path("build-sheet-2026-08-05.py").read_text(encoding="utf-8")
props = len(re.findall(r'"batter":', text))
zs = len(re.findall(r'"zone_score":\s*[1-9]', text))
print("props", props, "zone_score>0", zs)
for name in ["Michael Conforto", "Rafael Devers", "Bryce Eldridge"]:
    m = re.search(
        rf'"batter":\s*"{re.escape(name)}".{{0,1200}}?"zone_score":\s*([^,\n]+)',
        text,
        re.S,
    )
    print(name, m.group(1).strip() if m else "NOT FOUND")
