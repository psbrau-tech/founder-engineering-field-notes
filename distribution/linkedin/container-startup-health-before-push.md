# LinkedIn Package: Container Startup Health Before Push

## Headline

A Successful Docker Build Does Not Prove the Release Can Run

## Short post

A container can build successfully, push successfully, and still fail immediately when the application process starts.

That is not a reason to make deployment troubleshooting better. It is a reason to catch the failure before publication.

The stronger CI contract is simple: build the image, start that exact image on the runner, wait for readiness, call a minimal health endpoint, clean it up, and only then publish the same image identity.

That catches broken entry points, import failures, missing runtime dependencies, and other startup defects before registry publication and orchestrator rollout turn a cheap local failure into a slow infrastructure incident.

The field note includes a compact preflight pattern and explains why rebuilding after the smoke test defeats artifact provenance.
