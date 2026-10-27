# Required enterprise setup and release sequence

## GitHub

1. Publish directories as two separate repositories in an **approved organization**, with platform workflow repo named `ai-platform-reusable-workflows`.
2. Tag a reviewed platform version `v2` (prefer immutable commit SHA in product callers); replace `YOUR-ORG` in the product `.github/workflows/*.yml` files.
3. Enable GitHub Actions sharing between private repositories and allow platform actions and required external third-party actions under enterprise policy.
4. Create product repository environments: `build`, `dev`, `test`, `prod`.
5. Apply branch protection to `main` and mandatory `CI validation` status checks; require approval for `test` and `prod` GitHub environments. Restrict each environment to `main`.
6. Environment-scoped vars (all environments unless otherwise stated): `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. `build` additionally needs `ACR_NAME`, `ACR_LOGIN_SERVER`. Dev/Test/Prod each need `ACR_LOGIN_SERVER`, `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`, `AZURE_LOCATION`.
7. Native Foundry evaluation: in `dev`, `test`, `prod`, set `FOUNDRY_EVAL_REQUIRED=true` after customizing `src/agent/eval.yaml`, configuring its approved judge model, testing `azd ai agent eval run --config eval.yaml`, and reviewing/ registering evaluation datasets/evaluators. The central action parses aggregate counts and blocks on errors or <90% passing results; review per-criterion scores as part of governance. `prod` **must** have this true. Set `PROD_TRAFFIC_PINNING_VERIFIED=true` only when the production endpoint is pinned to a stable version and separately tested routing/rollback management exists; without it the production deploy step fails closed **before** `azd deploy`.
8. For federated Entra credentials, bind identity to approved caller and **specific reusable workflow and environment** where supported (`job_workflow_ref`) so arbitrary product workflows cannot assume the platform's deployment identity. Scope Azure RBAC minimally.

## Azure and Networking

- AI Platform Terraform must already have provisioned per-environment Foundry projects, approved model deployments, guardrails, diagnostic settings, project connections, runtime identities, ACR connections and permissions; product repos never provision these.
- ACR write identity (build) requires only push rights. Foundry runtime identity **separately** needs permission to pull the same digest from the central registry.
- Verify whether environment-specific identities can create logical hosted agents without creating or modifying accounts, networks, or model deployments. Foundry roles may include Project Manager and additional delegated permissions; review exact API behavior.
- For private-only ACR and Foundry, run every build/deploy/evaluation job on an approved private runner with Docker engine/ACR/Foundry DNS and egress access. `ubuntu-latest` is only a placeholder.
- Validate region, container runtime and supported Foundry preview features before production.

## Release path

```text
PR --> central CI (policy, ruff, bandit, unit, Docker) --> protected main
          |
main push --> central CI --> image build/push --> Trivy gate --> Dev agent deployment --> live evaluation
          |
manual release on main --> repeat CI/build as a release run --> Dev gate --> Test [GitHub approval] gate --> Prod [GitHub approval] gate
                    same immutable image digest for all environments IN THIS RUN
```

The same digest passes Dev/Test/Prod **within one release execution**. A new run may yield a different digest for the same commit; for strict promotion of an earlier build add a signed release manifest/artifact lookup keyed to the approved SHA and digest.

Production endpoint/traffic promotion and rollback are deliberately **NOT automated here**. Hosted agent version creation is not equivalent to routing production clients to the new version. Add a pinned version / explicit release pointer and rollback plan before enabling production.

## Before declaring production-ready

- [ ] Replace placeholders; review branch trust/OIDC claims and GitHub protections.
- [ ] Verify all third-party action versions against org policy and SHA-pin actions.
- [ ] Freeze Python direct and transitive dependencies with organizational lockfile process.
- [ ] Run verified Foundry runtime protocol smoke tests (`GET /readiness`, `POST /responses`, port 8088).
- [ ] Customize and register/validate the Foundry `src/agent/eval.yaml` managed evaluation recipe, judge model and dataset. This preview CLI feature must be validated on the target Foundry resource.
- [ ] Add broader task-specific and safety/groundedness red-team evaluation beyond the two built-in illustrative evaluators.
- [ ] Add artifact attestation / SBOM provenance and CVE exception process; Trivy is one scan.
- [ ] Validate least privilege, model allowlist, guardrails, safe logging and PII controls in Azure.
- [ ] Define version routing, prod promotion, rollback, incident ownership, and Agent 365 publishing as separate workflows if required.
- [ ] Test private network self-hosted runners and actual Azure deployment end to end.
