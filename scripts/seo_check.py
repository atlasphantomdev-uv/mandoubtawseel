#!/usr/bin/env python3
"""Static SEO assertions over the built site (public/). Stdlib only.

Run after `hugo --minify`:  python3 scripts/seo_check.py

Errors (non-zero exit) break indexing; warnings are pre-launch data gaps.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "public"
ALIAS = "http-equiv=refresh"

errors: list[str] = []
warns: list[str] = []


def attr(html: str, pattern: str) -> str | None:
    m = re.search(pattern, html)
    return m.group(1) if m else None


def _walk_nulls(node, path: str = ""):
    """Yield (key, value) pairs whose value is None, at any depth."""
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else k
            if v is None:
                yield (p, v)
            else:
                yield from _walk_nulls(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk_nulls(v, f"{path}[{i}]")


def main() -> int:
    pages = sorted(p for p in ROOT.rglob("index.html") if ALIAS not in p.read_text())
    if not pages:
        print("public/ missing or empty — run `hugo --minify` first")
        return 2

    hreflang: dict[str, list[tuple[str, str]]] = {}
    for page in pages:
        rel = "/" + page.parent.relative_to(ROOT).as_posix().strip(".") + "/"
        rel = rel.replace("//", "/")
        html = page.read_text()

        h1 = len(re.findall(r"<h1[\s>]", html))
        if h1 != 1:
            errors.append(f"{rel}: {h1} <h1> (want exactly 1)")

        canonical = attr(html, r"rel=canonical href=([^ >]+)")
        if not canonical:
            errors.append(f"{rel}: no canonical")
        else:
            title = attr(html, r"<title>(.*?)</title>") or ""
            if "TODO_" in canonical or "TODO_" in title:
                warns.append(f"{rel}: TODO_ placeholder in <title>/canonical")

        if not attr(html, r'name=description content="([^"]+)"'):
            warns.append(f"{rel}: no meta description")

        # Minified output drops the attribute quotes, so match both forms —
        # otherwise this whole block silently never runs in production builds.
        ld_blocks = re.findall(
            r'<script type="?application/ld\+json"?>(.*?)</script>', html, re.S
        )
        if not ld_blocks:
            errors.append(f"{rel}: no JSON-LD block found")
        for block in ld_blocks:
            try:
                parsed = json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD ({exc})")
                continue
            if "TODO_" in block:
                errors.append(f"{rel}: TODO_ placeholder inside JSON-LD")
            # A null value (e.g. the old "logo": null) is invalid for consumers
            # that expect a type — omit the property instead.
            nulls = [k for k, v in _walk_nulls(parsed) if v is None]
            if nulls:
                errors.append(
                    f"{rel}: null value(s) in JSON-LD: {', '.join(nulls[:3])}"
                )

        langs = re.findall(r"hreflang=([a-z-]+) href=([^ >]+)", html)
        if langs:
            hreflang[rel] = langs
        if "TODO_" in html:
            warns.append(f"{rel}: TODO_ placeholder visible in page")

    # hreflang must be reciprocal: if A lists B, B must list A.
    for rel, alts in hreflang.items():
        for lang, url in alts:
            target = "/" + url.split("://", 1)[-1].split("/", 1)[-1]
            if target not in hreflang:
                continue
            back = [u for _, u in hreflang[target]]
            if not any(
                u.rstrip("/") == ("https:" + rel).rstrip("/") or u.endswith(rel)
                for u in back
            ):
                errors.append(f"{rel}: hreflang {lang} -> {target} not reciprocal")

    # ── URL identity ────────────────────────────────────────────────────────
    # relURL/relLangURL lowercase percent-escapes while .Permalink emits them
    # uppercase, so a naive build links every Arabic slug to a different URL
    # string than its own canonical. GitHub Pages is case-sensitive and serves
    # both, which splits the crawl (measured 2026-11-18: 380 of 703 internal page
    # links pointed at a non-canonical URL string). scripts/normalize_url_case.mjs
    # collapses them; these two assertions keep it collapsed.
    origin = ""
    canon_paths: set[str] = set()
    page_html: dict[str, str] = {}
    for page in pages:
        html = page.read_text()
        rel = "/" + page.parent.relative_to(ROOT).as_posix().strip(".") + "/"
        rel = rel.replace("//", "/")
        page_html[rel] = html
        m = re.search(r"rel=canonical href=([^ >]+)", html)
        if m:
            origin = origin or re.match(r"(https?://[^/]+)", m.group(1)).group(1)  # type: ignore[union-attr]
            canon_paths.add("/" + m.group(1).split("://", 1)[-1].split("/", 1)[-1])

    ASSET = re.compile(
        r"\.(css|js|png|jpe?g|svg|webp|woff2?|xml|txt|webmanifest|ico|json|pdf)$", re.I
    )
    for rel, html in page_html.items():
        bad_esc = [e for e in re.findall(r"%[0-9a-fA-F]{2}", html) if e != e.upper()]
        if bad_esc:
            errors.append(
                f"{rel}: {len(bad_esc)} lowercase percent-escape(s), e.g. {bad_esc[0]}"
            )
        if rel.endswith("404/"):
            continue
        for href in set(re.findall(r'href="?([^" >]+)', html)):
            if href.startswith(("#", "mailto:", "tel:")):
                continue
            if href.startswith("http"):
                if origin and not href.startswith(origin):
                    continue
                path = "/" + href.split("://", 1)[-1].split("/", 1)[-1]
            elif href.startswith("/"):
                path = href
            else:
                continue
            path = path.split("#")[0].split("?")[0]
            if ASSET.search(path):
                continue
            if not path.endswith("/") and not path.endswith(".html"):
                path += "/"
            if path.endswith(".html"):
                continue
            if path not in canon_paths:
                errors.append(f"{rel}: link {href} matches no page canonical")

    print(f"checked {len(pages)} HTML pages")
    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
