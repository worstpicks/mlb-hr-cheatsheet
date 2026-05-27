#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
text = (ROOT / "preview/index.html").read_text(encoding="utf-8")
block = (ROOT / "_games-0527.txt").read_text(encoding="utf-8").strip()

start = text.find("const games = [")
end_marker = "];\n\n            const grid"
end = text.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit(f"markers not found start={start} end={end}")

new_text = text[:start] + block + "\n\n            const grid" + text[end + len(end_marker) :]
new_text = new_text.replace("+900 with 2 HR versus Abbott", "+900 with 2 HR versus Tong")
(ROOT / "preview/index.html").write_text(new_text, encoding="utf-8")

m = re.search(r'Coby Mayo \(R\).*?emojis: "([^"]*)"', new_text)
g = re.search(r'Paul Goldschmidt \(R\).*?emojis: "([^"]*)"', new_text)
print("Mayo emojis:", m.group(1) if m else "missing")
print("Goldschmidt emojis:", g.group(1) if g else "missing")
