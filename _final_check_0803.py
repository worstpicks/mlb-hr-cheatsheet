#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path

html = Path("preview/index.html").read_text(encoding="utf-8")
print("date", re.search(r'sheet-date" content="([^"]+)"', html).group(1))
print("hero", re.search(r"<p>((?:Monday|Sunday), [^—]+)", html).group(1))
print("straights", re.findall(r'class="straight-pick-name">([^<]+)', html))
print("Nola glove", "Aaron Nola 🧤" in html)
print("WSH park", "WSH @ PHI" in html and "Park +26%" in html or "Park +26" in html)

# Check WSH gameMeta for Park
block = re.search(r"const games = \[(.*?)\n\];", html, re.S).group(1)
metas = re.findall(r'title:\s*"([^"]+)".*?gameMeta:\s*"((?:\\.|[^"\\])*)"', block, re.S)
for title, meta in metas:
    if "WSH @ PHI" in title:
        s = meta.encode().decode("unicode_escape")
        print("WSH meta has Park?", "Park" in s, s[:120])

m = re.search(r"Goblin's Insight(.*?)Top 5 HR Tickets", html, re.S)
chunk = m.group(1)
for h4, body in re.findall(r"<h4>(.*?)</h4>\s*<o[lu]>(.*?)</o[lu]>", chunk, re.S):
    names = re.findall(r"<strong>(.*?)</strong>", body)
    print(h4, "->", [re.sub(r"\s*HR.*", "", n) for n in names][:6])

for script in [
    "validate-index-matchups.py",
    "goblin_parlay_rules.py",
    "verify-summary-0803.py",
    "_audit_0803_final.py",
    "verify-deploy.py",
]:
    print("\n>>>", script)
    r = subprocess.run([sys.executable, script], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(r.returncode)
print("ALL OK")
