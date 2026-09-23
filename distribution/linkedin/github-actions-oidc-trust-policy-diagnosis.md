# LinkedIn Package: GitHub Actions OIDC Trust-Policy Diagnosis

## Headline

When GitHub Actions OIDC Fails, Check Trust Before Permissions

## Short post

A GitHub Actions job that cannot assume an AWS role is easy to misdiagnose as an IAM permission problem.

But `AssumeRoleWithWebIdentity` fails before the role's normal AWS service permissions come into play. If the OIDC provider, audience, or subject claim does not match the trust policy, adding more service permissions cannot fix it.

The practical debugging order is identity first, authorization second: verify `id-token: write`, the provider, the expected audience, and the exact GitHub `sub` format before touching the role's service permissions.

That last step matters even more now because GitHub repositories created after July 15, 2026 use an immutable default subject format that includes owner and repository IDs.

The field note covers the diagnostic sequence, a safe generic trust-policy shape, and the preflight that should catch this before a deployment workflow starts.
