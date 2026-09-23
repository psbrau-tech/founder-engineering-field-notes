# Contributing

This repository is optimized for evidence-backed engineering field notes rather than high-volume publishing.

## Article acceptance standard

An article must be supported by private evidence showing:

1. an observed failure;
2. the actual root cause;
3. the correction;
4. proof that the correction resolved the relevant failure class.

Public text must distinguish observed facts, current platform documentation, recommendations, and inference.

## Required article shape

Use the structure in [`ARTICLE_TEMPLATE.md`](ARTICLE_TEMPLATE.md) when it fits the lesson:

- Problem
- Failure Signature
- What We Expected
- Root Cause
- Why the Obvious Fix Was Wrong
- Minimal Correction
- Verification
- What Should Have Caught This Earlier
- Reusable Rule

## Public/private boundary

Do not commit:

- cloud account IDs, private ARNs, internal domains, private email addresses, or private repository URLs;
- internal stack, environment, workflow, IAM-role, identity-provider, DNS, or resource identifiers;
- GitHub Actions run/job IDs;
- private SHAs, digests, confirmation values, logs, screenshots, user-identifying information, or credentials;
- raw incident evidence or private source-repository history.

Use placeholders such as `<AWS_ACCOUNT_ID>`, `<AWS_REGION>`, `<OWNER>/<REPOSITORY>`, `<APPLICATION_STACK>`, and `<EXECUTION_ROLE>`.

## Editorial workflow

1. Prepare a sanitized article branch.
2. Set `published: true` only when the PR is ready to publish if merged.
3. Run publication validation.
4. Review the technical claims and current source documentation.
5. Founder merge is the editorial approval action.
6. After merge, the canonical GitHub Pages workflow may publish the article.

Do not weaken sanitization checks to make a PR pass. Fix the content or refine a false-positive rule narrowly.
