import re
from pathlib import Path

text = Path("preview/index.html").read_text(encoding="utf-8")
pat_start = r'\s*<div class="summary-card full-width straight-of-day-card">'
pat_end = r'<div class="summary-card emoji-key-card">'
starts = [m.start() for m in re.finditer(pat_start, text)]
ends = [m.start() for m in re.finditer(pat_end, text)]
print("starts", starts)
print("ends", ends)
if starts and ends:
    s, e = starts[0], ends[0]
    print("start snippet:", repr(text[s : s + 100]))
    print("between end-80:", repr(text[max(s, e - 80) : e + 60]))
