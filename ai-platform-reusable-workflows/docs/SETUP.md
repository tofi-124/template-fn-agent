# Platform setup checklist

## 1. Existing Azure platform

- [ ] Deploy the Azure Foundry account/project(s), approved model deployment(s), diagnostics, ACR, networking, APIM (if required), and private DNS via the **platform IaC repo**, not product repos.
- [ ] Record per-environment Foundry project endpoints and approved model deployment names.
- [ ] Decide whether Dev/Test/Prod share an ACR or use an artifact-copy mechanism. This template assumes a **single shared registry**; if different registries exist, adapt image promotion safely rather than rebuilding.
- [ ] For private ACR/Foundry, allocate an approved self-hosted runner group with required private DNS and outbound routes. Change the `runs-on` value in both workflows, not in untrusted product repos.
- [ ] Set Foundry project's managed identity permissions to read the ACR repository, and verify hosted agent container pulls succeed.

## 2. Identity and RBAC

- [ ] Register an Entra application or managed workload identity for deployment in each environment, with **GitHub OIDC federated credentials** scoped to the correct caller repository and GitHub environment.
- [ ] Limit trust to the centrally approved reusable workflow when supported (GitHub OIDC `job_workflow_ref` claim / custom subject), to stop product teams bypassing the platform workflow.
- [ ] Assign the Foundry Project Manager role at the required Foundry project scope for hosted-agent deployment, adjusting for chosen CLI flow according to Microsoft role guidance; some scenarios need additional control-plane role assignments.
- [ ] Give Dev the narrow ACR image write permission; grant Test/Prod only the ACR metadata/read permissions required to resolve existing images.
- [ ] Configure image pull permissions for the project managed identity. **Do not confuse that identity, the OIDC deployer, and the agent's runtime identity.**
- [ ] For any external agent tools, grant the agent's runtime Entra identity explicit least-privilege rights after review.

## 3. GitHub settings on calling product repo

- [ ] Repository variables on GitHub environments `dev`, `test`, `prod`: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_LOCATION`, `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`, `ACR_NAME`, `ACR_LOGIN_SERVER`.
- [ ] Require reviewers for Prod; protect branch/tag sources and restrict deployable branches to `main`. Confirm `workflow_dispatch` cannot bypass manual controls.
- [ ] Configure product CODEOWNERS and require code owner approval for `azure.yaml`, `platform/contract.yaml` and workflows.
- [ ] Permit access from product repos to platform reusable workflows in Actions settings. Restrict to signed/reviewed refs.
- [ ] Create protected `v1` workflow release tag after testing GitHub.com `$/.github/actions/...` support.

## 4. Test sequence

1. Run validator locally from `product-team-hosted-agent-template`: `python ../ai-platform-reusable-workflows/.github/actions/validate-hosted-agent/validate_contract.py sample-hosted-agent dev`.
2. Run `python -m unittest discover -s tests -v` from the product repository root.
3. Run `docker build --platform linux/amd64 -f src/agent/Dockerfile src/agent` on an approved runner with internet/package feeds.
4. Connect/bootstrap azd to the **already-existing** Dev project in a controlled platform validation session, if required by your azd extension version. Verify `azd deploy` using a prebuilt image works without provisioning.
5. Open a product PR and inspect centrally enforced validation.
6. Merge to main: confirm Dev build, ACR SHA tag, digest, deployed agent version, and smoke invocation.
7. Dispatch Test for **the same commit**; confirm digest equals Dev's image digest. Repeat for Prod only with approved sign-off.
8. Confirm rollback behavior, version/traffic routing, observability, data-classification policy, and external connectivity before any production release.

## References

- Existing project: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/azure-yaml-reference
- Hosted agent role requirements: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent
- GitHub OIDC: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure
- Azure CLI ACR manifest metadata: https://learn.microsoft.com/en-us/cli/azure/acr/manifest
