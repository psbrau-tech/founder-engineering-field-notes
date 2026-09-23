#!/usr/bin/env python3
"""Deterministic public-content validation with no third-party dependencies."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLISHABLE_ROOTS = [ROOT / name for name in ("articles", "examples", "distribution", "site")]
ARTICLE_ROOT = ROOT / "articles"
DENYLIST = ROOT / ".publication" / "denylist-hashes.json"

TEXT_SUFFIXES = {".md", ".txt", ".json", ".yml", ".yaml", ".html", ".xml", ".css", ".sh"}
REQUIRED_FIELDS = {
    "title", "slug", "summary", "categories", "tags", "published",
    "canonical_path", "linkedin_ready", "dev_ready", "verified_on", "sources",
}
ALLOWED_CATEGORIES = {
    "cloud-delivery",
    "stateful-product-engineering",
    "ai-product-operations",
    "founder-engineering",
}

ERRORS: list[str] = []


def error(path: Path, message: str) -> None:
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    ERRORS.append(f"{rel}: {message}")


def iter_public_files():
    for base in PUBLISHABLE_ROOTS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                yield path


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        error(path, "missing YAML front matter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        error(path, "unterminated YAML front matter")
        return {}, text

    raw = text[4:end]
    body = text[end + 5:]
    data: dict[str, object] = {}
    current_list: str | None = None

    for lineno, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):
            if current_list is None:
                error(path, f"line {lineno}: list item without a list key")
                continue
            assert isinstance(data[current_list], list)
            data[current_list].append(strip_scalar(line[4:].strip()))
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):(?:\s*(.*))?", line)
        if not match:
            error(path, f"line {lineno}: unsupported front-matter syntax")
            current_list = None
            continue
        key, value = match.groups()
        value = (value or "").strip()
        if value == "":
            data[key] = []
            current_list = key
        else:
            data[key] = parse_scalar(value)
            current_list = None

    return data, body


def strip_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_scalar(value: str) -> object:
    bare = strip_scalar(value)
    if bare == "true":
        return True
    if bare == "false":
        return False
    return bare


def validate_metadata(path: Path) -> None:
    meta, _ = parse_frontmatter(path)
    missing = REQUIRED_FIELDS - meta.keys()
    if missing:
        error(path, f"missing metadata fields: {', '.join(sorted(missing))}")
        return

    for field in ("title", "slug", "summary", "canonical_path", "verified_on"):
        if not isinstance(meta[field], str) or not str(meta[field]).strip():
            error(path, f"{field} must be a non-empty string")

    slug = str(meta["slug"])
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        error(path, "slug must be lowercase kebab-case")
    if meta["canonical_path"] != f"/articles/{slug}/":
        error(path, "canonical_path must equal /articles/<slug>/")

    for field in ("categories", "tags", "sources"):
        if not isinstance(meta[field], list) or not meta[field]:
            error(path, f"{field} must be a non-empty list")

    categories = meta["categories"] if isinstance(meta["categories"], list) else []
    invalid = sorted(set(categories) - ALLOWED_CATEGORIES)
    if invalid:
        error(path, f"unknown categories: {', '.join(invalid)}")

    for field in ("published", "linkedin_ready", "dev_ready"):
        if not isinstance(meta[field], bool):
            error(path, f"{field} must be true or false")

    try:
        verified = dt.date.fromisoformat(str(meta["verified_on"]))
        if verified > dt.date.today():
            error(path, "verified_on cannot be in the future")
    except ValueError:
        error(path, "verified_on must use YYYY-MM-DD")

    sources = meta["sources"] if isinstance(meta["sources"], list) else []
    for source in sources:
        parsed = urlparse(str(source))
        if parsed.scheme != "https" or not parsed.netloc:
            error(path, f"source must be an absolute HTTPS URL: {source!r}")


def validate_unique_slugs(article_files: list[Path]) -> None:
    seen: dict[str, Path] = {}
    for path in article_files:
        meta, _ = parse_frontmatter(path)
        slug = meta.get("slug")
        if not isinstance(slug, str):
            continue
        if slug in seen:
            error(path, f"duplicate slug also used by {seen[slug].relative_to(ROOT)}")
        else:
            seen[slug] = path


def validate_code_fences(path: Path, text: str) -> None:
    fence_lines = [line for line in text.splitlines() if re.match(r"^\s*```", line)]
    if len(fence_lines) % 2:
        error(path, "unbalanced triple-backtick code fences")


def validate_links(path: Path, text: str) -> None:
    # Validate Markdown inline links. External reachability is intentionally not
    # required here because publication CI must remain deterministic.
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip().split()[0].strip("<>")
        if "{{" in target or "{%" in target:
            continue
        if target.startswith("#"):
            continue
        parsed = urlparse(target)
        if parsed.scheme:
            if parsed.scheme not in {"https", "mailto"}:
                error(path, f"unsupported link scheme: {target}")
            continue
        if target.startswith("/"):
            continue
        local = (path.parent / target.split("#", 1)[0]).resolve()
        if not local.exists():
            error(path, f"broken local link: {target}")


def normalize(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def load_hashed_denylist() -> list[tuple[int, str]]:
    raw = json.loads(DENYLIST.read_text(encoding="utf-8"))
    return [(int(item["length"]), str(item["sha256"])) for item in raw["entries"]]


def validate_hashed_denylist(path: Path, text: str, deny: list[tuple[int, str]]) -> None:
    normalized = normalize(text)
    by_length: dict[int, set[str]] = {}
    for length, digest in deny:
        by_length.setdefault(length, set()).add(digest)

    for length, digests in by_length.items():
        if len(normalized) < length:
            continue
        for i in range(0, len(normalized) - length + 1):
            window = normalized[i:i + length]
            if hashlib.sha256(window.encode("utf-8")).hexdigest() in digests:
                error(path, "matched a private deny-list term")
                return


def validate_leaks(path: Path, text: str) -> None:
    checks = [
        (r"(?<!\d)\d{12}(?!\d)", "possible 12-digit AWS account ID"),
        (r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b", "possible AWS access key"),
        (r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b", "possible GitHub token"),
        (r"\bgithub_pat_[A-Za-z0-9_]{20,}\b", "possible GitHub fine-grained token"),
        (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key material"),
        (r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b", "possible JWT"),
        (r"https://github\.com/[^<\s]+/actions/runs/\d+", "GitHub Actions run URL"),
        (r"/job/\d{6,}\b", "GitHub Actions job identifier"),
        (r"\b[0-9a-f]{40}\b", "possible private Git SHA"),
        (r"\bsha256:[0-9a-f]{64}\b", "possible private digest"),
        (r"\bZ[A-Z0-9]{10,}\b", "possible Route 53 hosted-zone identifier"),
        (r"\b[a-z]{2}-[a-z]+-\d_[A-Za-z0-9]{8,}\b", "possible Cognito user-pool identifier"),
        (r"(?i)\b(?:password|passwd|api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*(?!<)[^\s`\"']{8,}", "possible credential assignment"),
        (r"(?i)\b[A-Z0-9._%+-]+@(?!example\.com\b)[A-Z0-9.-]+\.[A-Z]{2,}\b", "non-example email address"),
    ]
    for pattern, label in checks:
        if re.search(pattern, text):
            error(path, label)

    # Repository URLs are not permitted in publishable prose. Use a placeholder.
    if re.search(r"https://github\.com/(?!<OWNER>/<REPOSITORY>)[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text):
        error(path, "literal GitHub repository URL; use https://github.com/<OWNER>/<REPOSITORY>")

    # ARNs in public examples must use an explicit account placeholder whenever
    # the ARN form contains an account segment.
    for line in text.splitlines():
        if "arn:aws" in line and re.search(r"arn:aws[^:\s]*:[^:\s]*:[^:\s]*:\d{12}:", line):
            error(path, "literal AWS account ID inside ARN")


def validate_placeholders(path: Path, text: str) -> None:
    # Catch angle-bracket examples that look like accidental real identifiers.
    allowed = {
        "AWS_ACCOUNT_ID", "AWS_REGION", "OWNER", "REPOSITORY", "ENVIRONMENT",
        "OWNER_ID", "REPOSITORY_ID", "APPLICATION_STACK", "EXECUTION_ROLE",
        "EXPECTED_BOUNDED_PREFIX", "IMAGE_ID", "TITLE", "slug", "one-sentence summary",
        "tag", "APPLICATION_MODULE", "HEALTH_PATH",
    }
    for token in re.findall(r"<([^>\n]+)>", text):
        if token in allowed:
            continue
        if token.startswith("https://"):
            continue
        # ARTICLE_TEMPLATE intentionally contains prose placeholders.
        if path.name == "ARTICLE_TEMPLATE.md":
            continue
        if re.fullmatch(r"[A-Z0-9_/-]+", token):
            # Unknown all-caps placeholders are still safe.
            continue


def main() -> int:
    public_files = list(iter_public_files())
    article_files = sorted(ARTICLE_ROOT.rglob("*.md")) if ARTICLE_ROOT.exists() else []
    article_files = [p for p in article_files if p.name != "README.md"]

    for path in article_files:
        validate_metadata(path)
    validate_unique_slugs(article_files)

    deny = load_hashed_denylist()

    for path in public_files:
        text = path.read_text(encoding="utf-8")
        validate_code_fences(path, text)
        if path.suffix.lower() == ".md":
            validate_links(path, text)
        validate_hashed_denylist(path, text, deny)
        validate_leaks(path, text)
        validate_placeholders(path, text)

    if ERRORS:
        print("Publication validation failed:")
        for item in ERRORS:
            print(f"- {item}")
        return 1

    print(f"Publication validation passed for {len(public_files)} public-content files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
