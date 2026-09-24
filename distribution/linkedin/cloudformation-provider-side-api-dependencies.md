# LinkedIn Package: CloudFormation Provider-Side API Dependencies

## Post

Least privilege can fail in a way that makes the obvious fix dangerous.

We had a deployment role that appeared to have the permissions its infrastructure needed. Then the deployment failed with an access denial from a different AWS service than the one we were actively configuring.

The tempting response would have been to attach a broader policy and move on.

That would have fixed the symptom while weakening the security boundary.

The real issue was a hidden dependency in the execution path: the resource operation needed an adjacent service API behind the scenes.

The better debugging sequence was:

1. Capture the exact denied action.
2. Identify the resource operation that triggered it.
3. Verify the current platform behavior.
4. Add only the narrow dependency the operation actually needs.

The broader lesson applies well beyond AWS:

**Your system’s real dependency graph is defined by what executes, not by what the architecture diagram suggests.**

We now treat unexpected cross-service permissions as something to document and preflight rather than something to solve with broader access.

That turns a frustrating deployment failure into a permanent improvement in both reliability and least privilege.

## Optional canonical link

https://psbrau-tech.github.io/founder-engineering-field-notes/articles/cloudformation-provider-side-api-dependencies/
