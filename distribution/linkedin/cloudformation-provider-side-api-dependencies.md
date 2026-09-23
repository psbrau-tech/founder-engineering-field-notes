# LinkedIn Package: CloudFormation Provider-Side API Dependencies

## Headline

CloudFormation Least Privilege Can Fail in an Adjacent AWS Service

## Short post

A CloudFormation execution role can appear to cover every service in the template and still fail with an unexpected `AccessDenied`.

The missing permission may belong to an adjacent service used by the resource operation itself. In one validated case, a load-balancer path needed an EC2 lookup action. In another, a Web ACL association also depended on load-balancer-side permissions.

The important response is not to attach a broad managed policy. Capture the exact denied action, identify the active resource operation, verify the current provider path, and add only the narrow dependency with the strongest supported boundary.

There is another reason to verify rather than copy old fixes: AWS integration paths change. Current WAF documentation uses a newer ALB association permission model than the one involved in the earlier incident.

The field note turns those failures into a reusable dependency-discovery and preflight pattern for least-privilege CloudFormation.
