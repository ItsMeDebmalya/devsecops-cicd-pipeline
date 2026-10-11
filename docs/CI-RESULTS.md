# CI Results

The `DevSecOps Pipeline` workflow runs on every push and pull request. On a
clean `main` all gates pass and the change flows Dev → QA → Prod:

| Job | Result | Notes |
|-----|--------|-------|
| Dev · lint + unit tests | ✅ pass | ruff clean, 3/3 pytest |
| SAST · SonarQube quality gate | ✅ pass | SonarQube 9.9 booted in CI, quality gate OK |
| Build + container & dependency scan (Trivy) | ✅ pass | image builds; no fixable CRITICAL vulns |
| IaC scan (tfsec + Checkov) | ✅ pass | Terraform baseline clean at HIGH/CRITICAL |
| QA · promote | ✅ pass | runs only because all gates passed |
| Prod · promote | ✅ pass | runs only after QA |

## The gate in action

The promotion jobs declare `needs:` on all four gate jobs, so a critical
finding anywhere blocks promotion. To demonstrate a **blocked** build, introduce
a misconfiguration (e.g. set `restrict_public_buckets = false` in
`iac/main.tf`): the `iac-scan` job fails and `promote-qa` / `promote-prod` are
skipped — insecure infrastructure never reaches a deploy stage.

See the live run history under the repository's **Actions** tab.
