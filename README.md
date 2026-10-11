# devsecops-cicd-pipeline

[![DevSecOps Pipeline](https://github.com/ItsMeDebmalya/devsecops-cicd-pipeline/actions/workflows/pipeline.yml/badge.svg)](https://github.com/ItsMeDebmalya/devsecops-cicd-pipeline/actions/workflows/pipeline.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A CI/CD pipeline with **security gates at every stage** — SAST, dependency &
> container scanning, and IaC scanning — that **fails the build on critical
> findings before promotion** from Dev → QA → Prod, so insecure code and images
> never reach a deployment.

The application here (a tiny Flask service) is deliberately minimal; the
substance of this repo is the **security-gated pipeline** around it, built
twice — once in **GitHub Actions** (runs on every push/PR) and once as a
declarative **Jenkinsfile**.

---

## The gates

| Stage | Tool | Gate |
|-------|------|------|
| **Dev** — lint + unit tests | ruff, pytest | build fails on lint error / test failure |
| **SAST** | **SonarQube** (self-hosted in CI) | build fails if the **quality gate** fails |
| **Build + scan** | Docker + **Trivy** | fails on **CRITICAL** image vulns and CRITICAL/HIGH dependency vulns (fixable) |
| **IaC scan** | **tfsec** (+ Checkov) | tfsec fails on **HIGH/CRITICAL** misconfigurations |
| **QA** | — | only runs if **all** gates above pass |
| **Prod** | — | only runs after QA |

Promotion jobs (`promote-qa`, `promote-prod`) declare `needs:` on every gate,
so a single critical finding anywhere short-circuits the promotion — exactly
the "never reaches deployment" behaviour.

## Pipeline flow

```
         ┌─────────────┐
 push ──▶│  Dev: lint  │
         │  + pytest   │
         └──────┬──────┘
                │  (these four run in parallel, all must pass)
     ┌──────────┼───────────────┬──────────────────┐
     ▼          ▼               ▼                  ▼
┌─────────┐ ┌──────────┐ ┌───────────────┐  ┌────────────┐
│  SAST   │ │  Build + │ │   IaC scan    │  │   (deps)   │
│ Sonar   │ │  Trivy   │ │ tfsec/Checkov │  │   Trivy fs │
│  QG     │ │  image   │ │               │  │            │
└────┬────┘ └────┬─────┘ └───────┬───────┘  └─────┬──────┘
     └───────────┴───────────────┴────────────────┘
                         │ all gates green
                         ▼
                   ┌──────────┐      ┌────────────┐
                   │ Promote  │ ───▶ │  Promote   │
                   │   QA     │      │   Prod     │
                   └──────────┘      └────────────┘
```

## Repository layout

```
.
├── app/                     # sample Flask service + unit tests
├── Dockerfile               # multi-stage, non-root, healthcheck
├── iac/main.tf              # secure Terraform baseline (scanned by tfsec/Checkov)
├── sonar-project.properties # SonarQube analysis config
├── Jenkinsfile              # same gates as a declarative Jenkins pipeline
└── .github/workflows/pipeline.yml
```

## Run it locally

```bash
# App + tests
pip install -r app/requirements.txt ruff pytest
ruff check app && python -m pytest -q

# Container
docker build -t devsecops-demo:local .
docker run -p 8080:8080 devsecops-demo:local
curl localhost:8080/healthz

# Scans (same gates the pipeline enforces)
trivy fs --severity CRITICAL,HIGH --ignore-unfixed .
trivy image --severity CRITICAL --ignore-unfixed devsecops-demo:local
tfsec iac --minimum-severity HIGH
```

## Seeing a gate block a build

The pipeline is green because the code and IaC are clean. To watch a gate do
its job, introduce a critical finding, e.g. in `iac/main.tf` set
`restrict_public_buckets = false` on the public-access block (or pull a Docker
base image with a known CRITICAL CVE). The IaC / image scan stage then fails
and the `promote-qa` job never runs.

## License

MIT — see [LICENSE](LICENSE).
