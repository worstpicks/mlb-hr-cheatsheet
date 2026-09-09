#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
text = (ROOT / "preview" / "index.html").read_text(encoding="utf-8")
block = (ROOT / "_games-0527.txt").read_text(encoding="utf-8").strip()

if "PHI @ SD - Cristopher Sanchez" in text:
    print("games block already present")
    raise SystemExit(0)

pat = r"\(\(\) => \{\s*\n\s*const grid = document\.getElementById\(\"gamesGrid\"\);"
repl = "(() => {\n" + block + "\n\n            const grid = document.getElementById(\"gamesGrid\");"
text, n = re.subn(pat, repl, text, count=1)
if n != 1:
    raise SystemExit("insert failed")

(ROOT / "preview" / "index.html").write_text(text, encoding="utf-8")
print("inserted games block")
