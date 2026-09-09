#!/usr/bin/env python3
"""Archived sheets: show 'Archived Worst Pickz Cheat Sheet' in header."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVED = "Archived Worst Pickz Cheat Sheet"
DAILY = "Worst Pickz Cheat Daily MLB Sheet"

OLD_SYNC = """            function syncSheetLiveHeader() {
                const h1 = document.getElementById("sheetLiveTitle");
                const sub = document.getElementById("sheetLiveDate");
                const sd = (getSheetDateMeta() || "").trim();
                if (!sd || sd.length < 10) return;
                const p = sd.split("-");
                const d = new Date(+p[0], +p[1] - 1, +p[2]);
                const fmt = d.toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric", year: "numeric" });
                const t = new Date();
                const isToday = t.getFullYear() === d.getFullYear() && t.getMonth() === d.getMonth() && t.getDate() === d.getDate();
                if (h1) h1.textContent = isToday ? "Today's MLB HR Cheat Sheet" : "MLB HR Cheat Sheet";
                if (sub) sub.textContent = fmt + (isToday ? " — today's sheet" : "");
            }"""

NEW_SYNC = f"""            const SHEET_TITLE_DAILY = {DAILY!r};
            const SHEET_TITLE_ARCHIVED = {ARCHIVED!r};
            function isArchivedSheetPage() {{
                return /\\/archive\\//i.test(window.location.pathname || "");
            }}
            function syncSheetLiveHeader() {{
                const brand = document.getElementById("sheetBrandTag");
                const h1 = document.getElementById("sheetLiveTitle");
                const archived = isArchivedSheetPage();
                if (archived) {{
                    if (brand) brand.textContent = SHEET_TITLE_ARCHIVED;
                    if (h1) h1.textContent = SHEET_TITLE_ARCHIVED;
                    document.title = SHEET_TITLE_ARCHIVED;
                    const og = document.querySelector('meta[property="og:title"]');
                    if (og) og.setAttribute("content", SHEET_TITLE_ARCHIVED);
                }} else if (brand) {{
                    brand.textContent = SHEET_TITLE_DAILY;
                }}
                const sd = (getSheetDateMeta() || "").trim();
                if (!sd || sd.length < 10) {{
                    if (!archived && h1) h1.textContent = SHEET_TITLE_DAILY;
                    return;
                }}
                const p = sd.split("-");
                const d = new Date(+p[0], +p[1] - 1, +p[2]);
                const t = new Date();
                const isToday = !archived && t.getFullYear() === d.getFullYear() && t.getMonth() === d.getMonth() && t.getDate() === d.getDate();
                if (!archived && h1) h1.textContent = isToday ? "Today's MLB HR Cheat Sheet" : "MLB HR Cheat Sheet";
                if (!archived) {{
                    document.title = isToday ? "Today's MLB HR Cheat Sheet — Worst Pickz" : SHEET_TITLE_DAILY;
                    const og = document.querySelector('meta[property="og:title"]');
                    if (og) og.setAttribute("content", isToday ? "Today's MLB HR Cheat Sheet" : SHEET_TITLE_DAILY);
                }}
            }}"""


def patch_file(path: Path, *, archive: bool) -> None:
    t = path.read_text(encoding="utf-8")
    o = t

    if OLD_SYNC in t:
        t = t.replace(OLD_SYNC, NEW_SYNC, 1)
    elif "SHEET_TITLE_ARCHIVED" not in t and "function syncSheetLiveHeader" in t:
        print("warn: sync block mismatch in", path.name)

    brand_line = f'                    <motion.div class="brand-tag">{DAILY}</motion.div>'
    brand_line = f'                    <div class="brand-tag">{DAILY}</div>'
    title = ARCHIVED if archive else DAILY
    brand_new = f'                    <motion.div class="brand-tag" id="sheetBrandTag">{title}</div>'.replace(
        "<motion.div", "<div"
    )

    if f'id="sheetBrandTag">{title}' not in t and brand_line in t:
        t = t.replace(brand_line, brand_new, 1)

    h1_old = f"                    <h1>{DAILY}</h1>"
    h1_new = f'                    <h1 id="sheetLiveTitle">{title}</h1>'
    if h1_old in t:
        t = t.replace(h1_old, h1_new, 1)
    elif archive and f'<h1 id="sheetLiveTitle">{DAILY}</h1>' in t:
        t = t.replace(f'<h1 id="sheetLiveTitle">{DAILY}</h1>', h1_new, 1)

    if archive:
        t = t.replace(f"<title>{DAILY}</title>", f"<title>{ARCHIVED}</title>", 1)
        t = t.replace(
            f'<meta property="og:title" content="{DAILY}">',
            f'<meta property="og:title" content="{ARCHIVED}">',
            1,
        )

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


def main() -> None:
    for p in [ROOT / "preview" / "index.html", ROOT / "index.html"]:
        if p.is_file():
            patch_file(p, archive=False)
    for p in (ROOT / "preview" / "archive").glob("*.html"):
        patch_file(p, archive=True)


if __name__ == "__main__":
    main()
