# LinkedIn Package: GitHub Actions OIDC Trust-Policy Diagnosis

## Post

One of the easiest ways to waste an afternoon in cloud deployment is to debug the wrong permission layer.

We hit a deployment failure where the natural instinct was to ask, “What AWS permission is missing?”

That was the wrong question.

The workflow was being rejected before it ever reached the role’s normal service permissions. The real problem was identity and trust: the credentials presented by the automation did not match what the role was configured to trust.

The reusable lesson is simple:

**When automation cannot assume a role, verify identity before authorization.**

Who is asking? What token is being presented? What audience and subject does it contain? Does the trust policy actually match those values?

Only after that succeeds should you troubleshoot what the role is allowed to do.

We turned that diagnosis into a preflight check so the same class of failure is caught before a deployment starts.

For a small team, that is the real payoff. A failed operation should not just get fixed. It should make the engineering system better at catching the next one.

## Optional canonical link

https://psbrau-tech.github.io/founder-engineering-field-notes/articles/github-actions-oidc-trust-policy-diagnosis/
