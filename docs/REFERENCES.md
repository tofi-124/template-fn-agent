# Verified public reference material (reviewed October 27, 2026)

- Microsoft Foundry `azure.yaml` schema, existing-project `endpoint`, image deployment, container CPU/memory, `AZD_AGENT_SKIP_ACR`:
  https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/azure-yaml-reference
- Microsoft's hosted-agent GitHub Actions example (OIDC, `azd deploy --no-prompt`, smoke invocation):
  https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/set-up-cicd-hosted-agent
- Minimal Agent Framework + `ResponsesHostServer` example (same imports/code concepts used by template):
  https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/framework-hosted-agents
- Hosted agent container runtime contract (port 8088, readiness, protocols):
  https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agent-contract
- Hosted-agent deployment flow and Foundry Project Manager permissions:
  https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent
- Microsoft Foundry hosted-agent samples:
  https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents
- GitHub reusable workflows, including same-repo `$/` syntax and nested workflows:
  https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
- GitHub action same-repository `$/.github/actions` convention:
  https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/workflow-syntax.md
- Docker remote image manifest reference:
  https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/
- Azure CLI ACR manifest metadata:
  https://learn.microsoft.com/en-us/cli/azure/acr/manifest

These are reference patterns, not proof of successful deployment in a particular organization's Azure tenant.

- Lee Stott CI/CD Foundry pipeline (CI, evaluation gates, Dev/Test/Prod approvals):
  https://github.com/leestott/foundry-cicd
- Microsoft Terraform/AzAPI logical hosted-agent deployment alternative:
  https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent-terraform
- GitHub 2026 self-repo $/ syntax for central composite actions:
  https://github.blog/changelog/2026-07-30-reference-same-repository-actions-with-self-repository-syntax/
- Microsoft Foundry hosted agent managed evaluation recipe with `eval.yaml` and `azd ai agent eval run`:
  https://learn.microsoft.com/en-us/azure/foundry/observability/quickstarts/quickstart-evaluate-hosted-agent
