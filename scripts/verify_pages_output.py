#!/usr/bin/env python3
"""Verify that every published article is present in the built Pages artifact."""

from __future__ import annotations

from pathlib import Path

from prepare_pages import ARTICLES, ROOT, parse

OUTPUT = ROOT / "_site"


def main() -> int:
    errors: list[str] = []

    required = [OUTPUT / "index.html", OUTPUT / "feed.xml", OUTPUT / "sitemap.xml"]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required site output: {path.relative_to(ROOT)}")

    homepage = (OUTPUT / "index.html").read_text(encoding="utf-8") if (OUTPUT / "index.html").is_file() else ""
    feed = (OUTPUT / "feed.xml").read_text(encoding="utf-8") if (OUTPUT / "feed.xml").is_file() else ""
    sitemap = (OUTPUT / "sitemap.xml").read_text(encoding="utf-8") if (OUTPUT / "sitemap.xml").is_file() else ""

    published = 0
    for path in sorted(ARTICLES.rglob("*.md")):
        meta, _ = parse(path)
        if meta.get("published") is not True:
            continue

        published += 1
        slug = str(meta["slug"])
        title = str(meta["title"])
        canonical_path = str(meta["canonical_path"])
        article_output = OUTPUT / "articles" / slug / "index.html"

        if not article_output.is_file():
            errors.append(
                f"published article missing built page: {article_output.relative_to(ROOT)}"
            )
            continue

        rendered = article_output.read_text(encoding="utf-8")
        if title not in rendered:
            errors.append(f"built article page does not contain expected title: {slug}")
        if canonical_path not in homepage:
            errors.append(f"homepage does not link published article: {canonical_path}")
        if canonical_path not in feed:
            errors.append(f"feed does not reference published article: {canonical_path}")
        if canonical_path not in sitemap:
            errors.append(f"sitemap does not reference published article: {canonical_path}")

    if errors:
        print("Pages output verification failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Pages output verification passed for {published} published article(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
