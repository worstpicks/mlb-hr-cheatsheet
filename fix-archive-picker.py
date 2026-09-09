#!/usr/bin/env python3
"""Fix archive date/select navigation (site root + manifest href values)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "preview" / "sheets-manifest.json").read_text(encoding="utf-8"))
MANIFEST_FB = (
    '<script type="application/json" id="sheets-manifest-fallback">'
    + json.dumps(MANIFEST, ensure_ascii=False).replace("</", "<\\/")
    + "</script>"
)

OLD_RESOLVE = """            function resolveManifestHref(href) {
                const h = (href || "").trim();
                if (!h) return window.location.href;
                if (h.startsWith("/")) return new URL(h, window.location.origin).href;
                const base = sheetsManifestBaseUrl || new URL("/", window.location.href).href;
                return new URL(h, base).href;
            }"""

NEW_RESOLVE = r"""            function getSheetSiteRoot() {
                let p = window.location.pathname || "/";
                if (p.endsWith("/index.html")) {
                    p = p.slice(0, -"/index.html".length);
                } else if (/\/archive\/[^/]+\.html$/i.test(p)) {
                    p = p.replace(/\/archive\/[^/]+\.html$/i, "");
                } else if (/\.html$/i.test(p)) {
                    p = p.replace(/\/[^/]+$/, "");
                }
                if (!p || p === "/") return "";
                return p;
            }
            function manifestBaseUrl() {
                if (sheetsManifestBaseUrl) return sheetsManifestBaseUrl;
                if (window.location.protocol === "file:") {
                    return new URL("./", window.location.href).href;
                }
                return new URL((getSheetSiteRoot() || "") + "/", window.location.origin).href;
            }
            function resolveManifestHref(href) {
                const h = (href || "").trim();
                if (!h) return window.location.href;
                if (/^https?:\/\//i.test(h)) return h;
                if (h.startsWith("/")) {
                    if (window.location.protocol === "file:") {
                        return new URL("." + h, window.location.href).href;
                    }
                    const root = getSheetSiteRoot();
                    const path = ((root || "") + h).replace(/\/{2,}/g, "/");
                    return new URL(path, window.location.origin).href;
                }
                return new URL(h, manifestBaseUrl()).href;
            }"""

OLD_OPTS = """                sheets.forEach((s) => {
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

OLD_FB_BASE = """                const fb = sheetsManifestFallback();
                if (fb) {
                    sheetsManifestBaseUrl = new URL("/", window.location.href).href;
                    return fb;
                }"""

NEW_FB_BASE = """                const fb = sheetsManifestFallback();
                if (fb) {
                    sheetsManifestBaseUrl = isArchivedSheetPage()
                        ? new URL("../", window.location.href).href
                        : new URL("./", window.location.href).href;
                    return fb;
                }"""

NEW_OPTS = """                sheets.forEach((s) => {
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


def patch_file(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    if OLD_RESOLVE in t:
        t = t.replace(OLD_RESOLVE, NEW_RESOLVE, 1)
    elif "function getSheetSiteRoot()" not in t and "function resolveManifestHref(href)" in t:
        t = t.replace(
            "            function resolveManifestHref(href) {",
            NEW_RESOLVE.split("function resolveManifestHref(href) {")[0].rstrip()
            + "\n            function resolveManifestHref(href) {"
            + NEW_RESOLVE.split("function resolveManifestHref(href) {", 1)[1],
            1,
        )
        print("inserted getSheetSiteRoot in", path.name)

    if OLD_OPTS in t:
        t = t.replace(OLD_OPTS, NEW_OPTS, 1)
    elif "opt.value = s.href" not in t:
        print("warn: options block missing in", path.name)

    if OLD_FB_BASE in t:
        t = t.replace(OLD_FB_BASE, NEW_FB_BASE, 1)
    elif 'sheetsManifestBaseUrl = new URL("/", window.location.href).href' in t:
        t = t.replace(
            'sheetsManifestBaseUrl = new URL("/", window.location.href).href',
            'sheetsManifestBaseUrl = isArchivedSheetPage()\n'
            '                        ? new URL("../", window.location.href).href\n'
            '                        : new URL("./", window.location.href).href',
            1,
        )
        print("fixed fallback base in", path.name)

    t = re.sub(
        r'<script type="application/json" id="sheets-manifest-fallback">.*?</script>',
        MANIFEST_FB,
        t,
        count=1,
        flags=re.DOTALL,
    )

    if path.name == "index.html" and "preview" in path.parts:
        t = re.sub(
            r'<meta name="sheet-date" content="[^"]*">',
            '<meta name="sheet-date" content="2026-05-18">',
            t,
            count=1,
        )

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


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
            patch_file(p)


if __name__ == "__main__":
    main()
