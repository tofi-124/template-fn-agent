# Security and governance review

## Threat model and required controls

1. **Bypassing platform enforcement:** GitHub repository CODEOWNERS and branches are not a security boundary by themselves. Scope OIDC trust to the approved reusable workflow using an immutable `job_workflow_ref` where supported. Restrict who can edit the central workflow/action and its approved ref.
2. **Foundry resource escalation:** The central validator rejects manifest provisioning, undeclared services, hooks and unexpected runtime environments. Also apply least-privilege Azure permissions so a product repo cannot create VNets, Foundry projects, model deployments, role assignments outside the approved scope or arbitrary resources.
3. **Pipeline runner risk:** Code and Dockerfiles are untrusted source and must run on isolated, ephemeral approved runners. Avoid hosting the ACR-build job on a highly privileged shared machine. Do not expose registry credentials or any access token to Docker build secrets unless explicitly designed.
4. **Software supply chain:** Pin `actions/checkout`, `azure/login`, setup actions and shared workflow refs to reviewed immutable SHAs before production. Scan dependencies and containers, produce SBOM/provenance, approve base images and pin base image digests.
5. **Image immutability:** ACR SHA tags by themselves are mutable. Set registry immutability and provenance policy, verify the selected digest against the Dev release record, and promote the approved digest rather than reconstructing an image in higher environments.
6. **Per-environment authorization:** Scope identities and GitHub environments to the correct Foundry projects, model deployment names and ACR rights. Enforce Test/Prod approvals and authorized branches. Do not let callers select arbitrary subscriptions through unchecked workflow inputs.
7. **Network egress:** VNet/private DNS, ACR access and approved outbound connections remain platform responsibilities. `requiredConnections` and `outboundDestinations` are empty in v1 by default. Exceptions require a separate approved contract extension and policy implementation.
8. **Agent identity:** The hosted agent has a distinct runtime identity. Assign permissions to approved data/tools separately. Do not grant the deployment OIDC identity to the runtime or vice versa.
9. **Operational controls:** Centralize Foundry/Application Insights diagnostics, request correlation, sensitive data handling, retention, sampling and operational alerts. Configure model allowlists in Azure Policy/Foundry in addition to repository validation.
10. **Release and rollback:** This workflow validates that the agent can be invoked but not that it is safe or meets quality SLOs. Add evaluation datasets, red-teaming, human approvals, release ring routing, rollback automation, and a tested incident runbook. Agent 365 publication is not implemented.

## Deliberate scope exclusions in v1

- Full transitive dependency lock and full vulnerability scan
- Signed, attested artifacts and release approval database
- External tools, connection creation and egress exceptions
- Foundry resource provisioning/changes or runtime RBAC provisioning
- GitHub Enterprise Server compatibility for new `$/.github/actions` syntax
- APIM route changes, Agent 365 registration/publishing, rollback and production endpoint traffic switching

The starter demonstrates **convention + enforcement**, not guaranteed compliance. Treat it as a Dev pilot until these gaps are addressed.
