# DEV Syndication

GitHub Pages is the canonical public copy. DEV is a downstream syndication target and must preserve the canonical Pages URL.

## Eligibility

An article is eligible for DEV only when both metadata flags are true:

- `published: true`
- `dev_ready: true`

Founder editorial approval still occurs at article-PR merge. DEV does not add another recurring editorial approval step.

## API contract

The workflow uses the current Forem API v1 contract:

- API base: `https://dev.to/api`
- Accept header: `application/vnd.forem.api-v1+json`
- authentication header: `api-key`
- list owned articles: `GET /articles/me/all`
- create: `POST /articles`
- update: `PUT /articles/{id}`

The repository secret is named `DEV_API_KEY`.

## Idempotency

Before writing, the syndicator retrieves the authenticated user's DEV articles and matches by canonical URL.

- no canonical match -> create the article;
- exactly one canonical match -> update that article;
- multiple canonical matches -> fail closed rather than guess.

Normal post-Pages runs syndicate only an eligible article changed by the commit that Pages just published. A manual `sync_all` dispatch exists for initial seeding or controlled recovery.

## Canonical URL

Canonical URLs use:

`https://psbrau-tech.github.io/founder-engineering-field-notes/articles/<slug>/`

The same origin and base path are configured in the Jekyll site so Pages, RSS, sitemap, and DEV agree on canonical location.

## Tags

DEV accepts up to four tags. Repository article tags are normalized to lowercase alphanumeric DEV tags, de-duplicated, and limited to the first four values. Payload validation runs in publication CI without network access.

## Failure behavior

- Pages must succeed before automatic DEV syndication is triggered.
- A DEV failure does not change or roll back the canonical Pages publication.
- API rate limiting is retried conservatively.
- Missing credentials fail live syndication without exposing the key.
- The API key is stored only as a GitHub Actions repository secret and must never be committed to this repository.

## LinkedIn

LinkedIn remains a generated manual package. DEV automation does not change that policy.
