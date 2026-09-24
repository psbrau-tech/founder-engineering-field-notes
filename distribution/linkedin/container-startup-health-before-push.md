# LinkedIn Package: Container Startup Health Before Push

## Post

One of the most expensive places to discover a startup error is after you have already deployed it.

We had a container image that built successfully. That gave us confidence in the artifact—but it should not have.

The application inside the image could not start correctly.

By the time that became obvious, the failure was mixed in with deployment health checks, orchestration, waiting, and rollback. A defect that could have been found locally in seconds had become an infrastructure troubleshooting problem.

The root issue was not just the bad startup configuration. It was the release process.

We had treated **“the image built”** as evidence that **“the release can run.”** Those are different contracts.

The correction was small: after building the image, CI now starts that exact image, waits for the application to become ready, checks a minimal health endpoint, and only then publishes the same artifact.

The reusable rule is:

**Build proves packaging. Release validation should prove the application can actually start.**

For a small team, short preflight checks like this are disproportionately valuable. They move cheap failures earlier and keep slow deployment systems from becoming the first place basic defects are discovered.

## Optional canonical link

https://psbrau-tech.github.io/founder-engineering-field-notes/articles/container-startup-health-before-push/
