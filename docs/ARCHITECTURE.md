# Architecture

## Goal

Demonstrate a **shift-left, security-gated delivery pipeline**: every change is
linted, tested, statically analysed, scanned for vulnerable dependencies and
container layers, and checked for infrastructure misconfiguration **before** it
can be promoted. A critical finding at any gate blocks promotion.

## Why gates as job dependencies

In GitHub Actions the promotion jobs declare:

```yaml
promote-qa:
  needs: [lint-test, sast, build-and-scan, iac-scan]
```

GitHub only runs a job when **all** of its `needs` succeed. So the promotion to
QA is not a separate "decision" step that could be bypassed — it is structurally
impossible for it to run if any gate failed. Prod then `needs: [promote-qa]`,
giving a strict Dev → QA → Prod order.

The Jenkinsfile expresses the same intent with sequential stages and
`waitForQualityGate abortPipeline: true`, so the pipeline aborts before the
promote stages if the SonarQube gate fails.

## The four gates

| Gate | What it catches | Failure threshold |
|------|-----------------|-------------------|
| Dev (ruff + pytest) | Style issues, broken logic | any error |
| SAST (SonarQube) | Bugs, code smells, security hotspots | quality gate != OK |
| Trivy | Vulnerable OS/app packages and image layers | CRITICAL (image), CRITICAL/HIGH (deps), fixable only |
| tfsec / Checkov | Insecure infrastructure-as-code | tfsec HIGH/CRITICAL |

`--ignore-unfixed` is used on Trivy so the build blocks on vulnerabilities that
a patch actually exists for, rather than failing permanently on an unfixable
upstream advisory.

## SonarQube in CI (self-contained)

Rather than depend on an external SonarCloud account, the SAST job:

1. raises `vm.max_map_count` (required by SonarQube's embedded Elasticsearch),
2. starts `sonarqube:9.9-community` as a container,
3. waits for `/api/system/status` to report `UP`,
4. bootstraps an analysis token via the API,
5. runs `sonar-scanner-cli`, then
6. polls the Compute Engine task and enforces the **quality gate**.

This keeps the whole pipeline reproducible from the repo alone, with no secrets
or external services to configure.

## Container hardening

The `Dockerfile` uses a multi-stage build (dependencies compiled in a builder
stage, only the virtualenv copied into a slim runtime), runs as a non-root
`appuser`, and defines a `HEALTHCHECK`. This both shrinks the attack surface and
reduces what Trivy can flag.

## Extending to a real deploy

The `promote-qa` / `promote-prod` jobs are currently echo placeholders. In a
real environment they would push the scanned image to a registry and trigger a
deploy (e.g. Argo CD / Helm) — which is exactly what the companion
`gitops-eks-argocd` project does.
