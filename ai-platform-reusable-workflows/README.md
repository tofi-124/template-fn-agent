# AI Platform — central reusable GitHub workflows (v2)

This directory is published as a separate **AI Platform owned** GitHub repository. Product repositories call versioned reusable workflows and cannot change the centrally stored validation logic by modifying their own repositories.

| Workflow / action | Executes |
|---|---|
| `.github/workflows/ci-hosted-agent.yml` | contract validation, Ruff lint, Bandit security check, unit tests, evaluation dataset validation, Docker build |
| `.github/workflows/build-hosted-agent.yml` | build-once Linux AMD64 container, OIDC login, ACR push, Trivy vulnerability gate, immutable digest output |
| `.github/workflows/deploy-hosted-agent.yml` | environment-scoped identity, prebuilt image `azd deploy` into *existing* Foundry project, deploy status, live response evaluation, audit |
| `.github/actions/validate-hosted-agent/` | prevents infra provisioning, enforces approved model alias, runtime, image token and fixed repo interface |
| `.github/actions/evaluate-hosted-agent/` | live fixed-marker smoke quality gate |
| `.github/actions/evaluate-foundry-quality/` | invokes `azd ai agent eval run --config eval.yaml`, parses pass/fail counts, blocks if below managed evaluation threshold when enabled |

## Important governance

- Treat `build`, `dev`, `test`, `prod` GitHub environments as different trust boundaries. Setting `environment:` in YAML does **not** configure mandatory reviewers: do that in GitHub settings.
- Pin this repo's release to a reviewed immutable SHA; for GitHub.com, self-repo `$/` action references resolve to the central repo commit. GHES may not support it.
- Validate OIDC federation with `job_workflow_ref` where available, so the product source alone cannot independently exercise production identities.
- This repo is not an infrastructure repo. AI Platform Terraform must provision Foundry projects, ACR, networking, runtime identity, guardrails, and monitoring before agent releases.
- Adapt `runs-on:` to private GitHub runners for private project/ACR connectivity.
- **No automatic release routing, Agent 365 publishing, rollback, or Foundry SDK evaluator integrated yet.** The `contains` gate is an executable demonstration to be replaced for production.

Full onboarding: `../docs/ONBOARDING.md` in distribution bundle. Research mappings: `../docs/RESEARCH_TRACEABILITY.md`.
