# Research traceability: what was applied, where, and what remains

| Source pattern | Evidence / source | Implementation in this ZIP | Boundary / caveat |
|---|---|---|---|
| Lee Stott: CI build, validate | https://github.com/leestott/foundry-cicd | `ai-platform-reusable-workflows/.github/workflows/ci-hosted-agent.yml` | Python Ruff, Bandit and unit tests run on each PR and release |
| Lee Stott: evaluation quality gates | Same source | `.../.github/actions/evaluate-hosted-agent/` + product `tests/evaluations/smoke.json` | Fixed-response smoke gate plus native `azd ai agent eval run` gate with built-in Task Adherence/Intent Resolution where enabled. Judge model, dataset registration and measured scores need Azure validation |
| Lee Stott: Dev → Test → Prod | Same source | product `.github/workflows/release.yml`; central `deploy-hosted-agent.yml` | Main push releases only to Dev; manual release proceeds through Test and Prod with environment protection |
| Lee Stott: approvals / DevSecOps | Same source | Called job `environment: ${{ inputs.environment }}`, Bandit, Trivy | Actual protection rules and org policy are GitHub/Entra setup, not YAML-only |
| Microsoft: prebuilt container into existing Foundry | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/azure-yaml-reference | product `azure.yaml`, central `build-hosted-agent.yml`, `deploy-hosted-agent.yml` | No `azd provision`. Shared platform prerequisites must already exist |
| Microsoft: Managed evaluations | https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent | `product-team-hosted-agent-template/src/agent/eval.yaml`, `tests/queries.jsonl`, and central `evaluate-foundry-quality` action | Preview CLI; configure judge model, permissions and reviewed evaluation suite; requires `FOUNDRY_EVAL_REQUIRED=true` |
| Microsoft: OIDC + azd deploy + invoke | https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/set-up-cicd-hosted-agent | central `deploy-hosted-agent.yml` and evaluator | Real integration depends on Foundry runtime, azd CLI version and Azure permissions |
| Microsoft: logical agent owned separately from shared IaC | https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent-terraform | Separate product and platform repos; no infra in product contract | Alternative for teams wishing AzAPI ownership rather than azd release |
| GitHub: reusable workflows | https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows | product caller `.github/workflows/` references central versioned jobs | Pin to immutable SHA for production; allow private-repo sharing |
| GitHub: `$/` for platform actions in reused workflows | https://github.blog/changelog/2026-07-30-reference-same-repository-actions-with-self-repository-syntax/ | `uses: $/.github/actions/...` in central repo workflows | GitHub.com with compatible Actions runners; GHES must use an alternative |
| Foundry hosted agent runtime | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agent-contract | agent `main.py`, `Dockerfile`, `azure.yaml` | Foundry SDK packages must be validated in your own runtime environment |

## Intentional differences from Lee Stott's reference

Lee Stott presents an end-to-end reference CI/CD pipeline and includes Azure DevOps. **This design is GitHub-only**, decomposes CI/CD into platform-owned reusable workflows, and targets **hosted containers in an already-provisioned Foundry project** (not provisioned by the product repository).

The evaluation step includes a gated response check and optional native Foundry evaluator execution with parsed pass/fail counts. Native evaluation is in preview and requires a provisioned judge model and registered/reviewed datasets. Even built-in metrics alone are not a full release-risk assessment. Before using it for high-risk workloads, integrate the organization's managed evaluation tools for task-specific datasets, answer relevance/groundedness, security, bias, privacy, tool-use correctness and compliance.
