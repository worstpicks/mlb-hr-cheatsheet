#!/usr/bin/env python3
"""Re-sync 6/1 games + summary columns without re-archiving prior slate."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("patch0601", ROOT / "patch-0601-preview.py")
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)

manifest = json.loads(patch.MANIFEST_PATH.read_text(encoding="utf-8"))
patch.patch_preview(manifest)
patch.sync_root_index()
print("resync complete (no archive step)")
