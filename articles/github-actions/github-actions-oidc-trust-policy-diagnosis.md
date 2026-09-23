---
title: "GitHub Actions OIDC AccessDenied May Be a Trust-Policy Problem, Not a Permission-Policy Problem"
slug: "github-actions-oidc-trust-policy-diagnosis"
summary: "When GitHub Actions cannot assume an AWS role, diagnose OIDC trust claims before widening the role's service permissions."
categories:
  - cloud-delivery
tags:
  - "github-actions"
  - "aws-iam"
  - "oidc"
  - "least-privilege"
published: true
canonical_path: "/articles/github-actions-oidc-trust-policy-diagnosis/"
linkedin_ready: true
dev_ready: true
verified_on: "2026-09-23"
sources:
  - "https://docs.github.com/en/actions/reference/security/oidc"
  - "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws"
  - "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html"
---

# GitHub Actions OIDC AccessDenied May Be a Trust-Policy Problem, Not a Permission-Policy Problem

## Problem

When a GitHub Actions job cannot assume an AWS role through OpenID Connect, the first instinct is often to inspect or widen the role's attached AWS permissions. That can target the wrong layer.

`sts:AssumeRoleWithWebIdentity` is an identity-and-trust decision. AWS evaluates whether the incoming OIDC identity is allowed to obtain the role before the resulting session receives the role's service permissions.

## Failure Signature

The workflow reaches AWS role assumption and fails with an authorization error before it can call the AWS service the job was intended to use.

That is materially different from a workflow that assumes the role successfully and then receives `AccessDenied` from an AWS service API.

The first failure class points to OIDC identity and trust. The second points to the permissions granted after assumption.

## What We Expected

A GitHub Actions workload with `id-token: write` should request an OIDC token whose issuer, audience, and subject satisfy the AWS role's trust policy. AWS STS should then issue a short-lived role session, after which the role's normal permission policy governs service access.

## Root Cause

The failure class we diagnosed came from a mismatch between the workload identity GitHub presented and the identity the AWS trust policy permitted.

The important trust inputs are:

- the AWS OIDC provider for `token.actions.githubusercontent.com`;
- the audience expected by AWS STS, commonly `sts.amazonaws.com` when using the standard AWS credentials flow;
- the exact GitHub `sub` claim authorized by the trust policy.

The subject deserves special attention because it depends on workflow context. A job that references a GitHub Environment has an environment-oriented subject rather than the branch or pull-request subject a copied example may use.

There is also a newer compatibility boundary. GitHub documents that repositories created after **July 15, 2026** use an immutable default subject format that includes owner and repository IDs. Repositories created earlier keep the previous name-based format unless they opt in, while later renames or transfers also move to the immutable format. A trust policy should therefore be derived from the subject format the repository actually uses, not from a hard-coded historical example.

## Why the Obvious Fix Was Wrong

Adding `s3:*`, `cloudformation:*`, or another AWS service permission to the role cannot make a failed trust decision succeed. Those permissions are available only after AWS has issued the role session.

Widening them during an OIDC failure increases privilege without fixing the failing control.

## Minimal Correction

Keep the trust policy narrow and make its claims match the actual workflow identity.

A generic shape is:

```json
{
  "Effect": "Allow",
  "Principal": {
    "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
  },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "<GITHUB_SUBJECT>"
    }
  }
}
```

`<GITHUB_SUBJECT>` is deliberately a placeholder. Determine it from the repository's current OIDC subject mode and the job context. If the job uses a protected GitHub Environment, keep the trust relationship aligned with that environment and use the environment's protection rules as another control.

A useful diagnostic sequence is:

1. Confirm the job has `permissions: id-token: write`.
2. Confirm the AWS account has the intended GitHub OIDC provider.
3. Confirm the role trust policy names that provider as the federated principal.
4. Confirm the `aud` condition matches the audience requested by the credentials flow.
5. Confirm the `sub` condition matches the repository's current GitHub subject format and the job context.
6. Only after role assumption succeeds, diagnose service-level permissions.

## Verification

The correction is validated when the workflow can obtain the intended AWS role session under the expected GitHub context while a context outside the trust boundary remains unauthorized.

An identity-only preflight can stop after role assumption and an STS identity check. That cleanly proves the trust layer before any deployment or mutation is attempted.

## What Should Have Caught This Earlier

Treat OIDC trust as a testable contract.

Before a deployment workflow is allowed to execute protected operations, verify:

- the repository's current OIDC subject format;
- the expected audience;
- the environment, branch, or event context encoded in the subject;
- the exact federated provider ARN;
- a zero-change role-assumption preflight.

For long-lived repositories, record whether they use the previous or immutable GitHub subject format so a rename, transfer, or opt-in does not become a surprise production failure.

## Reusable Rule

If GitHub Actions fails at `AssumeRoleWithWebIdentity`, debug identity and trust first. Do not widen the role's AWS service permissions until the role can actually be assumed.

## Sources

- [GitHub: OpenID Connect reference](https://docs.github.com/en/actions/reference/security/oidc)
- [GitHub: Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [AWS IAM: Create a role for OpenID Connect federation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html)
