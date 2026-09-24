# LinkedIn Package: CloudFormation Generated Role Names and Rollback

## Headline

CloudFormation Least Privilege Has to Match Physical IAM Names, Not Assumptions

## Short post

A least-privilege CloudFormation role can be scoped too narrowly for a reason that is easy to miss: the physical IAM role name CloudFormation actually creates may not match the naming pattern you inferred from the logical resource.

That can break twice. The forward deployment may fail on tagging or policy operations, and rollback can fail against the same generated role family when it tries to detach or delete what was created.

The wrong fix is to replace a bounded role ARN with `role/*`.

The safer sequence is to inspect the denied resource ARN, identify the actual physical-name pattern, update only the bounded role family, and verify both forward and rollback permissions. `iam:PassRole` should remain constrained by both role resource and destination service.

The field note turns a naming mismatch into a reusable lifecycle-permission preflight for CloudFormation.
