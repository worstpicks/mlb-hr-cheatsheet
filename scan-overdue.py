#!/usr/bin/env python3
import importlib.util
from pathlib import Path

from overdue_eval import evaluate_overdue

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("b0518", ROOT / "build-sheet-2026-05-18.py")
mod = importlib.util.module_from_spec(spec)
# Stop build from writing when imported — patch write_text
_orig_write = Path.write_text


def _noop_write(self, *a, **k):
    return None


Path.write_text = _noop_write  # type: ignore[method-assign]
spec.loader.exec_module(mod)  # type: ignore[union-attr]
Path.write_text = _orig_write  # type: ignore[method-assign]

from overdue_eval import apply_inferred_due

games = mod.games
for g in games:
    for r in g["rows"]:
        r.pop("due", None)
        r.pop("overdue", None)
        apply_inferred_due(r, g)

rows_out = []
for g in games:
    for r in g["rows"]:
        ok, checks = evaluate_overdue(r, g)
        n = sum(checks.values())
        if n >= 4:
            rows_out.append((n, ok, r["name"], [k for k, v in checks.items() if not v]))

rows_out.sort(reverse=True)
print("Inferred due, 4+ rules:")
for item in rows_out[:30]:
    print(item)
