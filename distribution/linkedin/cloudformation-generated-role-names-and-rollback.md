# LinkedIn Package: CloudFormation Generated Role Names and Rollback

## Post

A security policy built on an assumption can fail just as badly as a missing permission.

We learned that during a deployment where our least-privilege policy assumed infrastructure-created roles would follow a particular naming pattern.

They did not.

That caused two problems: the deployment failed on the forward path, and rollback ran into the same boundary when it tried to clean up what had already been created.

The easy fix would have been to widen the policy until the deployment passed.

We deliberately did not do that.

Instead, we inspected the actual resource identities being created, tightened the policy around the verified pattern, and checked the permissions needed for both the forward path and rollback.

The reusable lesson was bigger than one IAM rule:

**Least privilege has to match what the system actually creates, and it has to cover the full lifecycle—including the undo path.**

That last part matters. A deployment is not safely permissioned if it can create resources but cannot unwind them when something later fails.

The permanent improvement was to treat physical resource identity and rollback permissions as part of deployment preflight, not something to discover during recovery.

## Optional canonical link

https://psbrau-tech.github.io/founder-engineering-field-notes/articles/cloudformation-generated-role-names-and-rollback/
