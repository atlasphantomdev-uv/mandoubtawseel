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

        for m in re.finditer(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S
        ):
            try:
                json.loads(m.group(1))
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD ({exc})")
            if "TODO_" in m.group(1):
                errors.append(f"{rel}: TODO_ placeholder inside JSON-LD")

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

    print(f"checked {len(pages)} HTML pages")
    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
