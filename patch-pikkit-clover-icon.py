#!/usr/bin/env python3
"""Pikkit header: blue heart-clover icon on black (square button)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from patch_targets import SHEET_HTML  # noqa: E402

WORDMARK_CSS = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: auto;
            min-width: 42px;
            height: 42px;
            padding: 0 11px 0 9px;
            border-radius: 12px;
            border: 1px solid rgba(140, 146, 146, 0.45);
            background: #000;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            background: #0a0a0a;
            filter: brightness(1.08);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            height: 24px;
            width: auto;
            max-width: 112px;
            object-fit: contain;
        }"""

ICON_CSS = """        .pikkit-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            padding: 0;
            border-radius: 12px;
            border: 1px solid rgba(79, 95, 255, 0.55);
            background: #000;
            text-decoration: none;
            overflow: hidden;
            flex-shrink: 0;
        }
        .pikkit-link:hover {
            background: #0a0a0a;
            filter: brightness(1.1);
        }
        .pikkit-link:focus-visible {
            outline: 2px solid rgba(251, 191, 36, 0.95);
            outline-offset: 2px;
        }
        .pikkit-link__icon {
            display: block;
            width: 100%;
            height: 100%;
            border-radius: 11px;
            object-fit: contain;
        }"""

WORDMARK_MEDIA = """            .header-actions .pikkit-link {
                height: 38px;
                padding: 0 9px 0 7px;
            }
            .header-actions .pikkit-link__icon {
                height: 20px;
                max-width: 96px;
            }"""

ICON_MEDIA = """            .header-actions .pikkit-link,
            .header-actions .pikkit-link__icon { width: 38px; height: 38px; }"""

IMG_RE = re.compile(
    r'<img class="pikkit-link__icon" src="(?:\.\./)?assets/pikkit-(?:icon|logo)\.svg"[^>]*>',
)


def icon_img(asset: str) -> str:
    return (
        f'<img class="pikkit-link__icon" src="{asset}" width="42" height="42" alt="" decoding="async">'
    )


def patch_file(path: Path) -> None:
    t = path.read_text(encoding="utf-8")
    o = t
    asset = "../assets/pikkit-icon.svg" if "/archive/" in str(path).replace("\\", "/") else "assets/pikkit-icon.svg"

    if WORDMARK_CSS in t:
        t = t.replace(WORDMARK_CSS, ICON_CSS, 1)
    elif ICON_CSS not in t:
        pass

    if WORDMARK_MEDIA in t:
        t = t.replace(WORDMARK_MEDIA, ICON_MEDIA, 1)
    elif ICON_MEDIA not in t and ".header-actions .pikkit-link" in t:
        t = t.replace(
            ".header-actions .theme-toggle { width: 38px; height: 38px; }",
            ".header-actions .theme-toggle { width: 38px; height: 38px; }\n" + ICON_MEDIA,
            1,
        )

    m = IMG_RE.search(t)
    if m:
        t = t[: m.start()] + icon_img(asset) + t[m.end() :]

    if t != o:
        path.write_text(t, encoding="utf-8")
        print("patched", path.relative_to(ROOT))
    else:
        print("ok", path.relative_to(ROOT))


def main() -> None:
    icon = ROOT / "preview" / "assets" / "pikkit-icon.svg"
    if not icon.is_file():
        raise SystemExit(f"missing {icon}")
    for p in SHEET_HTML:
        if p.is_file():
            patch_file(p)


if __name__ == "__main__":
    main()
