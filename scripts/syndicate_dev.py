#!/usr/bin/env python3
"""Syndicate approved canonical articles to DEV/Forem.

GitHub Pages remains canonical. This script only considers article sources that are
both ``published: true`` and ``dev_ready: true``. Existing DEV articles are
matched by canonical URL, so retries update rather than duplicate a post.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from prepare_pages import ARTICLES, ROOT, parse

API_BASE = "https://dev.to/api"
API_ACCEPT = "application/vnd.forem.api-v1+json"
CANONICAL_SITE_URL = "https://psbrau-tech.github.io/founder-engineering-field-notes"
USER_AGENT = "founder-engineering-field-notes-syndicator/1.0"


def canonical_url(meta: dict[str, object]) -> str:
    return CANONICAL_SITE_URL.rstrip("/") + str(meta["canonical_path"])


def sanitize_tags(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    tags: list[str] = []
    for value in values:
        tag = re.sub(r"[^a-z0-9]", "", str(value).lower())
        if not tag or tag in tags:
            continue
        if len(tag) > 20:
            raise ValueError(f"DEV tag exceeds 20 characters after normalization: {tag}")
        tags.append(tag)
        if len(tags) == 4:
            break
    if not tags:
        raise ValueError("DEV requires at least one usable tag")
    return tags


def dev_body(meta: dict[str, object], body: str) -> str:
    """Remove the source H1 because DEV renders the API title separately."""
    rendered = body.lstrip()
    title_line = f"# {meta['title']}"
    if rendered.startswith(title_line):
        remainder = rendered[len(title_line):]
        if not remainder or remainder.startswith("\n"):
            rendered = remainder.lstrip("\n")
    return rendered.rstrip() + "\n"


def desired_article(meta: dict[str, object], body: str) -> dict[str, object]:
    tags = sanitize_tags(meta.get("tags"))
    return {
        "title": str(meta["title"]),
        "body_markdown": dev_body(meta, body),
        "published": True,
        "canonical_url": canonical_url(meta),
        "description": str(meta["summary"]),
        "tags": ",".join(tags),
    }


def changed_article_paths() -> set[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD", "--", "articles"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return set(ARTICLES.rglob("*.md"))

    paths: set[Path] = set()
    for line in result.stdout.splitlines():
        if not line.endswith(".md"):
            continue
        path = ROOT / line
        if path.is_file():
            paths.add(path)
    return paths


def eligible_articles(sync_all: bool) -> list[tuple[Path, dict[str, object], str]]:
    candidates = set(ARTICLES.rglob("*.md")) if sync_all else changed_article_paths()
    eligible: list[tuple[Path, dict[str, object], str]] = []
    for path in sorted(candidates):
        meta, body = parse(path)
        if meta.get("published") is not True or meta.get("dev_ready") is not True:
            continue
        eligible.append((path, meta, body))
    return eligible


def request_json(
    method: str,
    path: str,
    api_key: str,
    payload: dict[str, object] | None = None,
) -> object:
    url = API_BASE + path
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Accept": API_ACCEPT,
        "api-key": api_key,
        "User-Agent": USER_AGENT,
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    for attempt in range(1, 4):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")[:2000]
            if exc.code == 429 and attempt < 3:
                retry_after = exc.headers.get("Retry-After")
                delay = int(retry_after) if retry_after and retry_after.isdigit() else 31
                print(f"DEV rate limited request; retrying after {delay}s.")
                time.sleep(delay)
                continue
            raise RuntimeError(
                f"DEV API {method} {path} failed with HTTP {exc.code}: {response_body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DEV API {method} {path} failed: {exc.reason}") from exc

    raise RuntimeError(f"DEV API {method} {path} failed after retries")


def list_existing(api_key: str) -> dict[str, list[dict[str, object]]]:
    by_canonical: dict[str, list[dict[str, object]]] = {}
    page = 1
    per_page = 1000
    while True:
        result = request_json(
            "GET", f"/articles/me/all?page={page}&per_page={per_page}", api_key
        )
        if not isinstance(result, list):
            raise RuntimeError("DEV API returned an unexpected article-list payload")
        for article in result:
            if not isinstance(article, dict):
                continue
            value = article.get("canonical_url")
            if not value:
                continue
            key = str(value).rstrip("/")
            by_canonical.setdefault(key, []).append(article)
        if len(result) < per_page:
            break
        page += 1
    return by_canonical


def sync(api_key: str, articles: list[tuple[Path, dict[str, object], str]]) -> None:
    existing = list_existing(api_key)
    for path, meta, body in articles:
        desired = desired_article(meta, body)
        canonical = str(desired["canonical_url"])
        matches = existing.get(canonical.rstrip("/"), [])
        if len(matches) > 1:
            raise RuntimeError(
                f"Multiple DEV articles already use canonical URL {canonical}; refusing to guess."
            )

        payload = {"article": desired}
        if matches:
            article_id = matches[0].get("id")
            if not isinstance(article_id, int):
                raise RuntimeError(f"DEV article matched {canonical} without a numeric id")
            response = request_json("PUT", f"/articles/{article_id}", api_key, payload)
            action = "updated"
        else:
            response = request_json("POST", "/articles", api_key, payload)
            action = "created"

        if not isinstance(response, dict):
            raise RuntimeError(f"DEV API returned an unexpected response for {path}")
        returned_canonical = str(response.get("canonical_url") or "").rstrip("/")
        if returned_canonical != canonical.rstrip("/"):
            raise RuntimeError(
                f"DEV {action} article but canonical URL verification failed for {path.name}"
            )
        print(f"DEV {action}: {path.name} -> {response.get('url', canonical)}")


def dry_run(articles: list[tuple[Path, dict[str, object], str]]) -> None:
    for path, meta, body in articles:
        desired = desired_article(meta, body)
        print(
            "DEV dry-run: "
            f"{path.relative_to(ROOT)} -> {desired['canonical_url']} "
            f"tags={desired['tags']}"
        )
    print(f"DEV dry-run validated {len(articles)} eligible article(s).")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true", help="sync all eligible articles")
    mode.add_argument("--changed", action="store_true", help="sync eligible articles changed in HEAD")
    parser.add_argument("--dry-run", action="store_true", help="validate payloads without network access")
    args = parser.parse_args()

    articles = eligible_articles(sync_all=args.all)
    try:
        if args.dry_run:
            dry_run(articles)
            return 0
        if not articles:
            print("No changed articles are eligible for DEV syndication.")
            return 0
        api_key = os.environ.get("DEV_API_KEY", "").strip()
        if not api_key:
            print("DEV_API_KEY is required for live syndication.", file=sys.stderr)
            return 2
        sync(api_key, articles)
    except (KeyError, ValueError, RuntimeError) as exc:
        print(f"DEV syndication failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
