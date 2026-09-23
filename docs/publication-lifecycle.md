# Publication Lifecycle

## 1. Private capture

A private engineering project records the failure, evidence, root cause, wrong-but-tempting fix, validated correction, and earlier detection control.

## 2. Sanitized handoff

Only the reusable lesson crosses into this public repository. Raw evidence and private topology stay private.

## 3. Public pull request

The article PR contains:

- sanitized article Markdown;
- complete publication metadata;
- safe examples using placeholders;
- current public source documentation;
- downstream LinkedIn copy when marked ready.

Validation CI checks metadata, forbidden identifiers, secret patterns, Markdown structure, links, and placeholders.

## 4. Founder editorial approval

The founder reviews the article PR. Merging the PR is the publication approval action.

## 5. Canonical publication

GitHub Pages is the canonical public copy. Pages deployment is gated by repository configuration and never runs for pull requests.

## 6. Syndication

DEV syndication is intentionally deferred until the first canonical Pages article is approved and published. LinkedIn remains a generated manual package until a stable approved write path exists.
