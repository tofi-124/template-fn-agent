# Enterprise Microsoft Foundry hosted-agent repository contract — v2

This bundle contains **two independently publishable GitHub repositories** and design/reference documentation.

1. `product-team-hosted-agent-template/`: product team's source, tests, Foundry `azure.yaml`, and *thin* caller workflows.
2. `ai-platform-reusable-workflows/`: centralized CI, build, deployment, evaluation, and validation governance.
3. `docs/`: architectural contract, Lee Stott traceability matrix, Azure onboarding, and explicit limitations.

**Architecture:** Platform Terraform owns existing Foundry projects, model deployments, networking, private DNS, ACR and project connections. Product changes build and publish an immutable container, deploy a logical agent into those existing projects, and run quality gates. This template intentionally does not run `azd provision`, `azd up`, or `terraform apply`.

## Why v2 exists

v1 lacked Lee Stott's dedicated evaluation and promotion gates. v2 introduces central CI (Ruff, Bandit, unit tests and container build), image vulnerability scanning, one immutable ACR image per release, post-deployment live evaluation, and GitHub Environment approvals for Dev → Test → Prod. These are **adaptations of public patterns**, not copied Microsoft/Lee Stott code.

## Begin here

- `docs/RESEARCH_TRACEABILITY.md` maps research to actual files.
- `docs/ONBOARDING.md` is the checklist for GitHub + Entra + Foundry.
- `docs/CONTRACT_SPEC.md` explains what products may/ may not control.
- `product-team-hosted-agent-template/README.md` describes customizing and testing the product repo.
- `ai-platform-reusable-workflows/README.md` describes publishing the platform repo.

**Not plug-and-play:** Replace `YOUR-ORG`, create GitHub environments and federation, provide Azure project-specific variables, enable private runner connectivity, choose region/model, and validate permissions. Run a live Dev deployment prior to accepting a production design. The `contains` evaluation is a sample smoke-quality gate; a separate optional **native Foundry managed evaluation** action is included and is required in Prod, but must be configured/verified in your tenant. Neither replaces groundedness, safety, red-team, and regression evaluation.
