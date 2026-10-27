# Proposed repository contract v1.0 — architecture note

## Scope

This contract applies to **one logical Microsoft Foundry hosted agent per GitHub repository**, with code owned by a product team. It is not an API/schema published by Microsoft. Product teams may use any approved programming framework in the future, but this reference implementation currently supports **Python Agent Framework**, **Responses protocol 2.0.0**, **container packaging**, and an **existing Foundry project** only.

## Required interface

| File | Contract requirement | Enforcement |
| --- | --- | --- |
| `platform/contract.yaml` | Agent identity, owner, support contact, runtime type, model alias, classifications and release environments | Central custom validator |
| `azure.yaml` | Existing `azure.ai.project.endpoint`, exactly one `azure.ai.agent`, prebuilt image variable and Responses 2.0.0 | Central validator + `azd` |
| `src/agent/main.py` | Foundry Responses protocol app; `/readiness` and `/responses` through adapter | Unit/build checks; runtime smoke invocation |
| `src/agent/Dockerfile` | Docker container targeting `linux/amd64`, port 8088, non-root startup | Docker build; runtime must be tested |
| `src/agent/requirements.txt` | Pinned direct dependencies | Central validator; add full dependency lock in production |
| `tests/` | Unit tests | Platform CI workflow |
| `.github/CODEOWNERS` | Ownership and PR review routing | GitHub branch protection (configure externally) |
| `.github/workflows/` | Small caller workflows to a versioned platform repo | GitHub reusable workflows and OIDC workflow trust |

## Contract field semantics

- `contractVersion`: version of the organization-defined contract. Make breaking changes through a new version and migration process.
- `agent.name`: stable logical Foundry agent name; deployments with the same name create additional versions. Avoid renaming after onboarding without migration/retirement planning.
- `agent.ownerTeam` / `supportContact`: accountable technical team and escalation contact, not IAM permissions.
- `runtime`: one of the platform-supported deployment adapters. V1 only supports `foundry-hosted`/`responses`/`container` at `src/agent`.
- `governance.dataClassification`: routing, logging and approval input; **not enforced by Azure just because it exists in YAML**.
- `governance.approvedModelAlias`: logical request for a platform-curated model. The concrete per-environment deployment name is set using GitHub environment configuration; enforce actual allowlists in Azure.
- `requiredConnections`/`outboundDestinations`: v1 requires empty arrays. Future versions should define a signed approval/entitlement process for these declarations.
- `release.environments`: Dev, Test, Prod. The appropriate repo GitHub environments must exist and be protected.
- `release.smokePrompt`: a benign post-deployment invocation. Pass/fail nonempty output is insufficient as an evaluation framework.

## Responsibility mapping

| Lifecycle activity | Product team | AI Platform | Security / Networking |
| --- | --- | --- | --- |
| Agent source, tests, dependencies | Owner | Supported runtime standards | Review gates |
| Metadata and requested model / tools | Declares | Validates, maps approved values | Exception/approval decisions |
| Foundry account, projects, models, ACR | Consulted | Owner (Terraform IaC) | Network / policy ownership |
| Product repo and PR approvals | Owner | Policy-reviewers and workflow providers | Security approval as required |
| Azure deployment identity & GitHub OIDC | No secret ownership | Owner | IAM review |
| Hosted-agent runtime identity and external rights | Requests | Coordinates provisioning | Grants scoped rights |
| Logging, telemetry, guardrails | Implements app-level instrumentation | Central diagnostics and standards | Privacy/security retention rules |
| Image promotion and release | Requests | Implements shared pipeline and release audit | Production approvals |

## Out of scope / version-2 candidates

- Multiple independent agents per repository and monorepo selective builds.
- Arbitrary framework and protocol adapters, `.NET` or non-container ZIP deployments.
- New Foundry project/model/connection creation.
- Agent 365 publish/registration, APIM API publication and public traffic switching.
- Automatically granting external tool/data access based on declarative requests.

Architectural decision: **separate application release from platform provisioning**, make the central deployment reusable, and enforce the contract in the centrally controlled workflow. The runtime contract itself is determined by Microsoft; the GitHub/release contract is organization-defined.


## V2: Lee Stott lifecycle integration

CI, build and live agent evaluation run through **platform-owned** workflows. The product release orchestrator calls CI -> image build+scan -> Dev deploy+eval -> Test deploy+eval -> Prod deploy+eval (manual release only). Product repos supply an evaluation suite under `tests/evaluations/smoke.json`; central validation enforces that the dataset exists. This baseline sample evaluates a response marker only; the enterprise must define domain-specific minimum quality/groundedness/safety thresholds independently.

Repo contract is for **hosted containers**, not generic Foundry prompt agents. The GitHub Environment protection rules, Entra RBAC, Foundry model allowlists, egress, deployment approvals, and endpoint routing are enforced outside this YAML schema.
