#!/usr/bin/env python3
"""Prepare GitHub Pages input from articles marked published: true."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
SITE = ROOT / "site"
# Use a normal Jekyll source directory. Directories beginning with an underscore
# are reserved for Jekyll internals and are not emitted as ordinary pages.
GENERATED = SITE / "articles"
DATA = SITE / "_data" / "articles.yml"


def strip_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---\n", 4)
    if not text.startswith("---\n") or end < 0:
        raise ValueError(f"{path}: invalid front matter")
    raw = text[4:end]
    body = text[end + 5:]
    meta = {}
    current = None
    for line in raw.splitlines():
        if line.startswith("  - "):
            meta[current].append(strip_scalar(line[4:].strip()))
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):(?:\s*(.*))?", line)
        if not match:
            continue
        key, value = match.groups()
        value = (value or "").strip()
        if value == "":
            meta[key] = []
            current = key
        else:
            bare = strip_scalar(value)
            meta[key] = True if bare == "true" else False if bare == "false" else bare
            current = None
    return meta, body


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    shutil.rmtree(GENERATED, ignore_errors=True)
    GENERATED.mkdir(parents=True, exist_ok=True)
    DATA.parent.mkdir(parents=True, exist_ok=True)

    published = []
    for path in sorted(ARTICLES.rglob("*.md")):
        meta, body = parse(path)
        if meta.get("published") is not True:
            continue
        slug = str(meta["slug"])
        output = GENERATED / f"{slug}.md"
        front = [
            "---",
            "layout: default",
            f"title: {yaml_quote(str(meta['title']))}",
            f"permalink: {yaml_quote(str(meta['canonical_path']))}",
            "---",
            "",
        ]
        output.write_text("\n".join(front) + body.lstrip(), encoding="utf-8")
        published.append(meta)

    lines = []
    for meta in sorted(published, key=lambda item: str(item["title"]).lower()):
        lines.extend([
            f"- title: {yaml_quote(str(meta['title']))}",
            f"  summary: {yaml_quote(str(meta['summary']))}",
            f"  url: {yaml_quote(str(meta['canonical_path']))}",
            f"  verified_on: {yaml_quote(str(meta['verified_on']))}",
        ])
    if not lines:
        lines.append("[]")
    DATA.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Prepared {len(published)} published article(s) for Pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
