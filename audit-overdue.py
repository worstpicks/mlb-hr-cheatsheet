#!/usr/bin/env python3
"""Print overdue rule pass/fail for every batter on the slate."""
import json
import runpy
from pathlib import Path

from overdue_eval import evaluate_overdue

ROOT = Path(__file__).resolve().parent
runpy.run_path(str(ROOT / "build-sheet-2026-05-18.py"), run_name="__not_main__")

# games is defined in build module namespace — re-exec to get games
ns = runpy.run_path(
    str(ROOT / "build-sheet-2026-05-18.py"),
    init_globals={"__name__": "audit"},
)
# run_path doesn't return games; import build differently
import importlib.util

spec = importlib.util.spec_from_file_location("build0518", ROOT / "build-sheet-2026-05-18.py")
mod = importlib.util.module_from_spec(spec)
# Prevent double write on import — patch write
spec.loader.exec_module(mod)  # type: ignore
