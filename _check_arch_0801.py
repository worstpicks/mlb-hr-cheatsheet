from pathlib import Path
import re

t = Path("preview/archive/2026-08-01.html").read_text(encoding="utf-8")
print(re.search(r'sheet-date" content="([^"]+)"', t).group(1))
print(re.search(r"<p>((?:Sunday|Saturday|Friday), [^—]+)", t).group(1))
print("has Seager", "Corey Seager" in t)
print("has Mayo", "Coby Mayo" in t)
