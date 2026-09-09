import re
from pathlib import Path

t = Path("build-0802-from-csv.py").read_text(encoding="utf-8")
m = re.search(r"RAW_PROPS = \[(.*?)\]", t, re.S)
props = re.findall(r'"([^"]+)"', m.group(1))
print("props", len(props))
print("favs", sum(1 for p in props if "⭐" in p))
print("gems", sum(1 for p in props if "💎" in p))
