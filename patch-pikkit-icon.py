#!/usr/bin/env python3
"""Replace Pikkit text link with app icon (matches header action buttons)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

PIKKIT_URL = "https://links.pikkit.com/invite/worst"

OLD_CSS = """        .pikkit-link {
            display: inline-flex; align-items: center; justify-content: center;
            min-height: 42px; padding: 0 12px; border-radius: 12px;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border: 1px solid rgba(196, 181, 253, 0.55); color: #fff;
            font-size: 0.72rem; font-weight: 800; letter-spacing: 0.04em;
            text-decoration: none; white-space: nowrap;
        }
        .pikkit-link:hover { filter: brightness(1.1); color: #fff; }"""

NEW_CSS = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(254, 215, 170, 0.4);
            background: rgba(15, 23, 42, 0.55);
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            background: rgba(15, 23, 42, 0.88);
            filter: brightness(1.06);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 42px;
            height: 42px;
            border-radius: 11px;
        }"""

MEDIA_OLD = """            .header-actions .pikkit-link { min-height: 38px; padding: 0 10px; font-size: 0.68rem; }"""
MEDIA_NEW = """            .header-actions .pikkit-link,
            .header-actions .pikkit-link__icon { width: 38px; height: 38px; }"""

UX_MEDIA_OLD = """            .pikkit-link { font-size: 0.65rem; padding: 0 8px; }"""

LINK_RE = re.compile(
    r'<a\s+class="pikkit-link"\s+href="https://links\.pikkit\.com/invite/worst"[^>]*>\s*Pikkit\s*</a>',
    re.IGNORECASE,
)


def icon_markup(asset_href: str) -> str:
    return (
        f'<a class="pikkit-link" href="{PIKKIT_URL}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="Track on Pikkit — code WORST" title="Track on Pikkit — code WORST">'
        f'<img class="pikkit-link__icon" src="{asset_href}" width="42" height="42" alt="" decoding="async"></a>'
    )


def patch_file(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    asset = "../assets/pikkit-icon.svg" if "/archive/" in str(path).replace("\\", "/") else "assets/pikkit-icon.svg"
    new_link = icon_markup(asset)

    if LINK_RE.search(t):
        t = LINK_RE.sub(new_link, t, count=1)
    elif 'class="pikkit-link"' in t and "pikkit-link__icon" not in t:
        t = t.replace(">Pikkit</a>", f'><img class="pikkit-link__icon" src="{asset}" width="42" height="42" alt="" decoding="async"></a>', 1)

    if OLD_CSS in t:
        t = t.replace(OLD_CSS, NEW_CSS, 1)
    elif ".pikkit-link__icon" not in t and ".social-x {" in t:
        t = t.replace(".social-x {", NEW_CSS + "\n        .social-x {", 1)
    elif ".pikkit-link__icon" not in t and ".pikkit-link {" not in t:
        t = t.replace(".social-x {", NEW_CSS + "\n        .social-x {", 1)
    elif ".pikkit-link {" in t and ".pikkit-link__icon" not in t:
        t = re.sub(
            r"        \.pikkit-link \{[^}]+\}\s*\.pikkit-link:hover \{[^}]+\}",
            NEW_CSS.strip(),
            t,
            count=1,
            flags=re.DOTALL,
        )

    if MEDIA_OLD in t:
        t = t.replace(MEDIA_OLD, MEDIA_NEW, 1)
    elif MEDIA_NEW not in t and ".header-actions .pikkit-link" in t:
        t = t.replace(
            ".header-actions .theme-toggle { width: 38px; height: 38px; }",
            ".header-actions .theme-toggle { width: 38px; height: 38px; }\n" + MEDIA_NEW,
            1,
        )

    if UX_MEDIA_OLD in t:
        t = t.replace(UX_MEDIA_OLD, "", 1)

    if "html.theme-light .header-actions .social-x" in t and "html.theme-light .pikkit-link" not in t:
        t = t.replace(
            "html.theme-light .header-actions .social-x,",
            "html.theme-light .pikkit-link,\n        html.theme-light .header-actions .social-x,",
            1,
        )
        t = t.replace(
            "html.theme-light .header-actions .social-x:hover,",
            "html.theme-light .pikkit-link:hover,\n        html.theme-light .header-actions .social-x:hover,",
            1,
        )

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


def main() -> None:
    icon_src = ROOT / "preview" / "assets" / "pikkit-icon.svg"
    if not icon_src.is_file():
        raise SystemExit(f"missing {icon_src}")
    for p in SHEET_HTML:
        if p.is_file():
            patch_file(p)


if __name__ == "__main__":
    main()
