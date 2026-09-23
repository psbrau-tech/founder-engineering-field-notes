---
title: "CloudFormation Least Privilege Can Fail Outside the Service You Think You Are Deploying"
slug: "cloudformation-provider-side-api-dependencies"
summary: "CloudFormation resource operations can depend on adjacent-service APIs, so least-privilege fixes should follow the exact denied action rather than the template's obvious service boundary."
categories:
  - cloud-delivery
tags:
  - "aws-cloudformation"
  - "aws-iam"
  - "least-privilege"
  - "infrastructure-as-code"
published: true
canonical_path: "/articles/cloudformation-provider-side-api-dependencies/"
linkedin_ready: true
dev_ready: true
verified_on: "2026-09-23"
sources:
  - "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-servicerole.html"
  - "https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_GetSecurityGroupsForVpc.html"
  - "https://docs.aws.amazon.com/waf/latest/developerguide/security_iam_service-with-iam.html"
---

# CloudFormation Least Privilege Can Fail Outside the Service You Think You Are Deploying

## Problem

A least-privilege CloudFormation execution role can look correct when compared with the resources in a template and still fail during deployment.

The reason is that CloudFormation does not merely translate each resource type into one same-service API call. The resource implementation can perform supporting lookups, associations, tagging, or cleanup through APIs in adjacent AWS services.

If the execution role was designed only from the visible service names in the template, a legitimate provider-side dependency can surface as an unexpected `AccessDenied`.

## Failure Signature

The stack reaches a valid resource operation and fails on an AWS API action that appears to belong to a different service than the resource being created or associated.

Two observed examples illustrate the class:

- an Application Load Balancer creation path required `ec2:GetSecurityGroupsForVpc`;
- a Web ACL association path required a load-balancer-side permission in addition to WAF permissions.

The first denial looked surprising because the resource was an Elastic Load Balancing resource and the missing EC2 action was not a `Describe*` call.

The second looked surprising because the operation was conceptually a WAF association, yet the integration crossed the WAF and load-balancer permission boundary.

## What We Expected

The execution role was intended to permit only the API surface required to create, update, and remove the stack's resources.

The mistaken assumption was that the required API surface could be inferred directly from the service namespace of each CloudFormation resource type.

## Root Cause

The policy model was based on **template service ownership**, while CloudFormation's actual resource operation depended on **provider-side API behavior**.

For the load-balancer case, the provider called the current EC2 API `GetSecurityGroupsForVpc`. A narrowly scoped correction can grant that action without granting broad EC2 access. For example:

```json
{
  "Effect": "Allow",
  "Action": "ec2:GetSecurityGroupsForVpc",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "aws:RequestedRegion": "<AWS_REGION>"
    }
  }
}
```

`Resource: "*"` does not mean the entire role should be broad. Some AWS APIs do not offer useful resource-level ARN scoping for the request. Least privilege then comes from granting the smallest action set and applying supported condition boundaries.

The Web ACL example also demonstrates why historical incident evidence must be rechecked before reuse. The observed denial involved `elasticloadbalancing:SetWebACL`. Current AWS WAF documentation now distinguishes that older Application Load Balancer setting from a newer association model that uses load-balancer-side `CreateWebACLAssociation` and `DeleteWebACLAssociation` permissions along with WAF permissions.

That change does not weaken the lesson. It strengthens it: provider and integration API paths can evolve, so the exact current denied action and current service documentation are better inputs than a permanent hard-coded permission list.

## Why the Obvious Fix Was Wrong

A common response to an unexpected provider-side denial is to attach a broad AWS managed policy for the adjacent service until the deployment succeeds.

That solves uncertainty by expanding privilege. It also discards the most useful evidence in the failure: AWS already told you the exact action that was denied.

For the observed EC2 lookup, broad EC2 read or write access was unnecessary. For the WAF/load-balancer association, broad load-balancer access was unnecessary. The correction could remain focused on the required integration action.

## Minimal Correction

Use the denial as a dependency-discovery signal:

1. Capture the exact denied action and resource, if one is reported.
2. Identify the CloudFormation resource or association operation active at the time.
3. Check the **current** AWS documentation for that provider/integration path.
4. Determine whether the missing API supports resource-level scoping.
5. Add only the required action and the strongest supported resource or condition boundary.
6. Review a fresh change set before protected execution.
7. Add the newly discovered dependency to a static policy-contract test.

Do not preserve an action forever merely because one historical provider path used it. Revalidate integration permissions when AWS changes the underlying association model.

## Verification

The correction is validated when the same resource operation succeeds under the narrowed execution role without requiring a broader managed policy.

For a provider-side dependency, verification should cover both the forward operation and any corresponding update or removal path that the stack can exercise. The policy-contract test should then assert the narrow dependency so a later refactor does not silently remove it.

## What Should Have Caught This Earlier

A useful preflight is a **resource-provider dependency ledger** for protected infrastructure changes.

For each resource family, record adjacent-service actions discovered through current documentation or validated deployment evidence. Static IAM tests can then check that the execution role includes the required narrow actions before a long-running CloudFormation operation begins.

The ledger should be treated as versioned knowledge rather than a permanent truth table. When an AWS integration changes, update the contract instead of accumulating obsolete permissions.

## Reusable Rule

When a least-privilege CloudFormation deployment fails, do not ask only, "What service is this resource from?" Ask, "What APIs does the current resource operation call to create, associate, inspect, update, and remove it?"

That question usually leads to a smaller and safer correction than attaching another broad policy.

## Sources

- [AWS CloudFormation: Set a service role](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-servicerole.html)
- [Amazon EC2 API: GetSecurityGroupsForVpc](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_GetSecurityGroupsForVpc.html)
- [AWS WAF: How AWS WAF works with IAM](https://docs.aws.amazon.com/waf/latest/developerguide/security_iam_service-with-iam.html)
