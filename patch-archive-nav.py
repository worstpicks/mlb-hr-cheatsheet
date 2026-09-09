#!/usr/bin/env python3
"""Use manifest href strings in archive <select> for reliable navigation."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

OLD = """                sheets.forEach((s) => {
                    const opt = document.createElement("option");
                    opt.value = resolveManifestHref(s.href);
                    opt.textContent = s.label;
                    archiveSheetSelect.appendChild(opt);
                });
                if (current) {
                    try {
                        archiveSheetSelect.value = resolveManifestHref(current.href);
                    } catch (e) {
                        archiveSheetSelect.selectedIndex = 0;
                    }
                }"""

NEW = """                sheets.forEach((s) => {
                    const opt = document.createElement("option");
                    opt.value = s.href;
                    opt.textContent = s.label;
                    archiveSheetSelect.appendChild(opt);
                });
                if (current) {
                    const curHref = current.href;
                    if ([...archiveSheetSelect.options].some((o) => o.value === curHref)) {
                        archiveSheetSelect.value = curHref;
                    } else {
                        archiveSheetSelect.selectedIndex = 0;
                    }
                }"""


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if OLD not in text:
        if "opt.value = s.href" in text:
            print("already ok", path.name)
            return
        print("skip (pattern missing)", path.name)
        return
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("patched archive nav", path.name)


def main() -> None:
    for rel in [
        "preview/index.html",
        "index.html",
        "preview/archive/2026-05-14.html",
        "preview/archive/2026-05-15.html",
        "preview/archive/2026-05-16.html",
    ]:
        p = ROOT / rel
        if p.is_file():
            patch(p)


if __name__ == "__main__":
    main()
