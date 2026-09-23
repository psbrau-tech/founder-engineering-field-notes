---
title: "A Successful Docker Build Does Not Mean You Built a Runnable Release"
slug: "container-startup-health-before-push"
summary: "CI should start and health-check the exact container image before publishing it, because a successful image build does not prove the packaged process can run."
categories:
  - cloud-delivery
  - founder-engineering
tags:
  - "containers"
  - "docker"
  - "ci-cd"
  - "preflight"
published: true
canonical_path: "/articles/container-startup-health-before-push/"
linkedin_ready: true
dev_ready: true
verified_on: "2026-09-23"
sources:
  - "https://docs.docker.com/reference/cli/docker/container/run/"
  - "https://www.uvicorn.org/settings/"
---

# A Successful Docker Build Does Not Mean You Built a Runnable Release

## Problem

A container image can build successfully and still be unusable as a release artifact.

A successful image build proves that Docker could assemble the image filesystem and metadata. It does not prove that the image's configured process can start, import the application correctly, remain alive, or answer the application's minimum health contract.

The observed failure class was exactly that gap: the image existed and could be retrieved, but the application process failed because Uvicorn was pointed at the wrong application target.

## Failure Signature

The build and registry stages succeed, but the deployment never becomes healthy because the container's primary process exits or cannot initialize the application.

At that point the defect is surrounded by infrastructure noise:

- the registry already contains the candidate image;
- an orchestrator pulls it;
- health checks begin failing;
- deployment stabilization waits consume time;
- rollback or replacement may start;
- operators have to distinguish an application-startup defect from networking, load balancing, IAM, or orchestration problems.

If the same image would have failed immediately on a local runner, discovering it after publication is unnecessary delay.

## What We Expected

The release pipeline implicitly treated:

```text
source -> docker build -> registry push
```

as evidence that the artifact was deployable.

The stronger release contract should have been:

```text
source
  -> build image
  -> start that exact image
  -> wait for application readiness
  -> call a minimal health endpoint
  -> stop the container
  -> publish that exact image
```

## Root Cause

The CI contract validated **packaging**, not **runtime startup**.

In the observed case, the Uvicorn command did not match the application's factory-style startup contract. Uvicorn's current documentation still distinguishes the factory form: `--factory` tells Uvicorn to treat the referenced application target as a callable that returns an ASGI application.

A generic factory-style startup command looks like:

```text
uvicorn <APPLICATION_MODULE>:create_app --factory --host 0.0.0.0 --port 8000
```

The module and callable are application-specific. The reusable lesson is to make that startup contract executable in CI before the artifact becomes a release candidate.

## Why the Obvious Fix Was Wrong

Fixing the command in the deployment environment alone repairs one incident but leaves the detection gap intact.

The next malformed entry point, missing runtime dependency, import failure, or startup configuration error can still travel through image publication and reach the orchestrator before anyone discovers it.

A second weak fix is to build one image for the smoke test and then rebuild another image for publication. That proves one artifact and ships another.

## Minimal Correction

Run the exact built image as a container before publication and require a minimal health check to pass.

Docker's current CLI documentation defines `docker run` as creating and running a container from an image. A generic CI preflight can therefore use the same image reference that will later be pushed:

```bash
container_name="app-under-test"

cleanup() {
  docker rm -f "$container_name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d \
  --name "$container_name" \
  -p 127.0.0.1:8080:8000 \
  "$IMAGE_ID"

for attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:8080/health >/dev/null; then
    exit 0
  fi
  sleep 1
done

docker logs "$container_name"
exit 1
```

The details should match the application:

- use the real startup command baked into the image unless the test is explicitly validating an override;
- use a health endpoint that proves the application initialized far enough to serve its minimum contract;
- keep host port exposure loopback-only for the CI check;
- capture container logs when startup fails;
- guarantee cleanup on success and failure.

After the preflight passes, publish the **same image identity**. Do not rebuild between validation and push.

## Verification

The correction proves the relevant failure class when CI fails before publication if the configured process cannot start or the health endpoint never becomes ready.

A regression test should deliberately exercise the startup contract so that an invalid application target or equivalent startup defect is caught without a registry push, orchestrator rollout, or rollback.

The positive path should demonstrate that the exact image which passed the startup check is the image subsequently published.

## What Should Have Caught This Earlier

Container publication should have a release preflight with three explicit assertions:

1. **Process assertion:** the configured primary process remains running long enough to initialize.
2. **Health assertion:** the application responds successfully on its minimum local health contract.
3. **Artifact-identity assertion:** the image published is the same immutable artifact that passed the first two checks.

This is a good example of moving failure left without inventing a large test system. A short local container run can eliminate an entire class of slow deployment-time diagnosis.

## Reusable Rule

A Docker build proves that an image can be assembled. A release check must prove that the intended process starts and the application can answer a minimal health contract.

Build it, run it, health-check it, then publish that exact artifact.

## Sources

- [Docker: docker container run](https://docs.docker.com/reference/cli/docker/container/run/)
- [Uvicorn: Settings](https://www.uvicorn.org/settings/)
