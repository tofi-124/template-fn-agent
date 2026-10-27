# Product-team Foundry hosted-agent template (v2)

The **product repo** owns agent application code, test cases, prompt content and the enterprise contract declaration. It invokes AI Platform's reusable workflows; it does **not** deploy Foundry infrastructure or create its own Azure permissions.

## CI/CD flow

- PR / push: `.github/workflows/ci.yml` calls platform `ci-hosted-agent.yml`: contract + lint + security + unit + container build.
- Push to `main`: `.github/workflows/release.yml` validates, builds and scans a digest-pinned ACR image, deploys to existing Dev Foundry and runs a **live evaluation gate**.
- Manual release from `main`: performs Dev -> Test -> Prod in order; Test/Prod must have environment approvals configured by your GitHub administrator.
- The central hosted-agent workflow uses `azd deploy` (never `azd provision` or `azd up`).

## Customize

1. Run `python scripts/customize_template.py --help` for agent identity customization, or manually update names in `platform/contract.yaml`, `azure.yaml`, caller workflow arguments, and repo CODEOWNERS.
2. Replace `YOUR-ORG` and pin approved platform workflow refs.
3. Replace `src/agent/` and `tests/evaluations/smoke.json` with the real workload; customize `src/agent/eval.yaml` and `src/agent/tests/queries.jsonl` with Foundry's preview managed evaluation recipe, approved judge model and golden dataset.
4. Configure approved GitHub environments, Azure Entra federation and shared ACR/project access; see `../docs/ONBOARDING.md` in the distribution bundle.
5. Merge to protected `main` only after central CI passes. First prove Dev deployment and runtime compatibility.

## Contract constraints

`platform/contract.yaml` is an enterprise schema, not a native Foundry manifest. `azure.yaml` is Microsoft's deployed hosted-agent declaration. Platform CI prevents adding VNet, model provisioning or connections to the product manifest, and cannot by itself enforce Azure RBAC or guardrail policy.

## Limitations

This example's dataset only verifies a deterministic readiness token in a live agent invocation. It is **not** true semantic performance evaluation. Production should use Foundry model evaluation and reviewed enterprise safety/quality metrics. Python package versions and CLI integration require testing against your specific supported Azure Foundry release.
