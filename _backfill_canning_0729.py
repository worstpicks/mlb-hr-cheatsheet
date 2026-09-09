#!/usr/bin/env python3
from pathlib import Path

path = Path("data/hr-targets-overall-2026-07-29.csv")
text = path.read_text(encoding="utf-8-sig")
if "Griffin Canning" in text:
    print("already present")
else:
    rows = text.rstrip("\n").split("\n")
    nums = [int(r.split(",")[0]) for r in rows[5:] if r and r[0].isdigit()]
    n = max(nums) + 1
    row = (
        f"{n},4:10 PM,Griffin Canning,vs,0.58,0.95,-0.15,1.74,"
        f"10.5%,20.0%,46.4%,24.9%,6.5%,278"
    )
    rows.append(row)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("backfilled", row)
