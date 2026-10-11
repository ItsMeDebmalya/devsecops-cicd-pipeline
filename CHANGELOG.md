# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Sample Flask service with unit tests (`app/`).
- Multi-stage, non-root `Dockerfile` with a healthcheck.
- Secure Terraform baseline (`iac/main.tf`) for IaC scanning.
- GitHub Actions `DevSecOps Pipeline` with security gates: ruff + pytest,
  self-hosted SonarQube quality gate, Trivy dependency & image scanning,
  tfsec + Checkov IaC scanning, and gated Dev → QA → Prod promotion.
- Declarative `Jenkinsfile` mirroring the same gates.
- README and architecture documentation.
