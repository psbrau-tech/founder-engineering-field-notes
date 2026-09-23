# Article Metadata Contract

Every file under `articles/` must begin with YAML front matter containing the following fields.

| Field | Type | Contract |
|---|---|---|
| `title` | string | Public article title. |
| `slug` | string | Lowercase kebab-case, unique across the repository. |
| `summary` | string | One-sentence public description. |
| `categories` | list | At least one public content track. |
| `tags` | list | At least one discoverability tag. |
| `published` | boolean | `true` means publish on merge to `main`; `false` means never include in Pages output. |
| `canonical_path` | string | Must equal `/articles/<slug>/`. |
| `linkedin_ready` | boolean | Whether a LinkedIn package is present and ready. |
| `dev_ready` | boolean | Whether the article metadata is ready for future DEV syndication. |
| `verified_on` | date string | `YYYY-MM-DD`; date current platform documentation was checked. |
| `sources` | list | One or more current public primary-documentation URLs. |

## Category values

Use one or more of:

- `cloud-delivery`
- `stateful-product-engineering`
- `ai-product-operations`
- `founder-engineering`

## Editorial semantics

A review-ready article PR may set `published: true`. That does **not** publish from the pull request. It means the PR is publication-ready and will become eligible for the site only after merge to `main`.

The merge is the founder editorial approval action.

## Private evidence

Private evidence references are intentionally excluded from this public metadata. The private source project is responsible for retaining the evidence-to-article mapping.
