# Founder Engineering Field Notes

Practical engineering lessons for founders and small technical teams, drawn from verified software work and rewritten as safe, reusable guidance.

The project focuses on four tracks:

- **Cloud & Delivery** — AWS, IAM, CloudFormation, GitHub Actions, CI/CD, rollback, and immutable artifacts.
- **Stateful Product Engineering** — autosave, recovery, exact-version persistence, stale-state protection, and browser acceptance.
- **AI Product Operations** — request lineage, model/config provenance, retries, token/cost provenance, and observability.
- **Founder Engineering Discipline** — preflight-first engineering, CI efficiency, synthetic testing, rollback design, and evidence-driven debugging.

## Publication model

GitHub is the canonical source. Public articles are prepared in pull requests, validated by sanitization CI, and published only when the founder merges the article PR as the editorial approval action.

Private incident evidence does **not** belong in this repository. Articles must teach the engineering pattern without exposing private topology, identifiers, logs, screenshots, credentials, or source-repository history.

## Repository layout

```text
articles/              Reviewable and published article sources
examples/              Generic reusable examples only
distribution/          Generated downstream publishing packages
docs/                  Public editorial and metadata contracts
scripts/               Deterministic validation and site-preparation scripts
site/                  GitHub Pages source
.github/workflows/      Validation and publication automation
```

## Publication states

- `published: false` — source may be committed for drafting, but is not eligible for the public site.
- `published: true` — the article is intended to publish when its PR is merged to `main`.
- Pull requests never deploy the public site.
- Merge of a review-ready article PR is the editorial approval event.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/metadata-contract.md`](docs/metadata-contract.md).
