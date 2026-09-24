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

Validation CI checks metadata, forbidden identifiers, secret patterns, Markdown structure, links, placeholders, DEV payload generation, and the built Pages output.

## 4. Founder editorial approval

The founder reviews the article PR. Merging the PR is the publication approval action.

## 5. Canonical publication

GitHub Pages is the canonical public copy. Pull requests never deploy the public site. After an approved article merges to `main`, Pages builds and deploys the canonical copy, category index, RSS feed, and sitemap.

## 6. DEV syndication

After a successful Pages deployment, an eligible article (`published: true` and `dev_ready: true`) is syndicated to DEV using its GitHub Pages URL as the canonical URL.

The syndicator matches existing DEV articles by canonical URL before writing, so retries update the existing cross-post rather than create duplicates. DEV failures do not roll back or replace the canonical Pages copy.

See [`dev-syndication.md`](dev-syndication.md) for the API, credential, idempotency, and recovery contract.

## 7. LinkedIn

LinkedIn remains a generated manual package until a stable approved automation path exists.

The LinkedIn package is not a technical abstract or a shortened DEV article. It translates the verified engineering lesson for technical founders and engineering leaders, emphasizing the wasted effort or risk, the diagnostic lesson, the permanent control added, and the reusable rule. Detailed runbook material remains in the canonical article.

See [`linkedin-distribution.md`](linkedin-distribution.md) for the audience, editorial pattern, package format, and manual-publishing contract.
