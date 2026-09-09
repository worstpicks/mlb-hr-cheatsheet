#!/usr/bin/env python3
"""Ensure Current slate button shows on archived cheat sheets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TARGETS = [
    ROOT / "preview" / "index.html",
    ROOT / "index.html",
    ROOT / "preview" / "archive" / "2026-05-14.html",
    ROOT / "preview" / "archive" / "2026-05-15.html",
    ROOT / "preview" / "archive" / "2026-05-16.html",
]

OLD_BLOCK = """                const currentSlate = findCurrentSlateEntry(sheets);
                if (currentSlateBtn && currentSlate) {
                    const currentHref = resolveManifestHref(currentSlate.href);
                    const onCurrentSlate =
                        normalizeSheetPageUrl(currentHref) === currentSheetPageUrl();
                    currentSlateBtn.href = currentHref;
                    currentSlateBtn.hidden = onCurrentSlate;
                }"""

NEW_BLOCK = """                const currentSlate = findCurrentSlateEntry(sheets);
                if (currentSlateBtn) {
                    if (currentSlate) {
                        const currentHref = resolveManifestHref(currentSlate.href);
                        const onCurrentSlate =
                            normalizeSheetPageUrl(currentHref) === currentSheetPageUrl();
                        currentSlateBtn.href = currentHref;
                        currentSlateBtn.hidden = onCurrentSlate;
                    }
                    if (isArchivedSheetPage()) {
                        currentSlateBtn.hidden = false;
                    }
                }"""

OLD_CATCH = """                } catch (e) {
                    sheetDatePicker.disabled = true;
                    archiveSheetSelect.disabled = true;
                    setArchiveStatus("Sheet list unavailable (offline or missing sheets-manifest.json).", false);
                    return;
                }"""

NEW_CATCH = """                } catch (e) {
                    sheetDatePicker.disabled = true;
                    archiveSheetSelect.disabled = true;
                    setArchiveStatus("Sheet list unavailable (offline or missing sheets-manifest.json).", false);
                    if (currentSlateBtn && isArchivedSheetPage()) {
                        try {
                            currentSlateBtn.href = resolveManifestHref("index.html");
                        } catch (err) {
                            currentSlateBtn.href = "index.html";
                        }
                        currentSlateBtn.hidden = false;
                    }
                    return;
                }"""

IS_ARCHIVED_FN = """            function isArchivedSheetPage() {
                return /\\/archive\\//i.test(window.location.pathname || "");
            }
"""


def patch(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    is_archive = "/archive/" in str(path).replace("\\", "/")

    t = t.replace('href="/index.html" id="currentSlateBtn"', 'href="index.html" id="currentSlateBtn"')

    if is_archive:
        t = t.replace(
            'id="currentSlateBtn" class="current-slate-btn" hidden>Current slate</a>',
            'id="currentSlateBtn" class="current-slate-btn">Current slate</a>',
        )

    if "function isArchivedSheetPage()" not in t:
        anchor = "            function getSheetSiteRoot()"
        if anchor in t:
            t = t.replace(anchor, IS_ARCHIVED_FN + "\n" + anchor, 1)
        else:
            anchor = "            function resolveManifestHref(href)"
            t = t.replace(anchor, IS_ARCHIVED_FN + "\n" + anchor, 1)

    if OLD_BLOCK in t:
        t = t.replace(OLD_BLOCK, NEW_BLOCK, 1)

    if OLD_CATCH in t:
        t = t.replace(OLD_CATCH, NEW_CATCH, 1)

    t = t.replace('resolveManifestHref("/index.html")', 'resolveManifestHref("index.html")')
    t = t.replace('currentSlateBtn.href = "/index.html"', 'currentSlateBtn.href = "index.html"')

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


if __name__ == "__main__":
    for p in TARGETS:
        if p.is_file():
            patch(p)
