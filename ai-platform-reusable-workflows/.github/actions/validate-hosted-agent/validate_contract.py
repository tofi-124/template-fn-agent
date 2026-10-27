#!/usr/bin/env python3
"""Platform-owned validation of product repository v1 contract and azd manifest.

Usage (from a product repository root):
  python /path/to/validate_contract.py [expected-agent-name] [optional-env]

This is structural governance, not a replacement for Azure Policy, RBAC or scanning.
"""
import pathlib
import json
import re
import sys

import yaml

ROOT = pathlib.Path.cwd()
ERRORS = []
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]{2,62}$")


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject ambiguous YAML duplicate keys before azd interprets them."""


def construct_unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in result:
            raise yaml.constructor.ConstructorError(None, None, f"duplicate key: {key!r}", key_node.start_mark)
        result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping)


def check(condition, message):
    if not condition:
        ERRORS.append(message)


def load_yaml(filename):
    path = ROOT / filename
    if not path.is_file():
        ERRORS.append(f"Missing {filename}")
        return {}
    try:
        obj = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
        check(isinstance(obj, dict), f"{filename} must be a mapping")
        return obj if isinstance(obj, dict) else {}
    except yaml.YAMLError as exc:
        ERRORS.append(f"Invalid YAML in {filename}: {exc}")
        return {}


def mapping(obj, key):
    value = obj.get(key, {}) if isinstance(obj, dict) else {}
    check(isinstance(value, dict), f"{key} must be a mapping")
    return value if isinstance(value, dict) else {}


def main():
    expected_name = sys.argv[1] if len(sys.argv) > 1 else ""
    deploy_env = sys.argv[2] if len(sys.argv) > 2 else ""
    spec = load_yaml("platform/contract.yaml")
    manifest = load_yaml("azure.yaml")

    check(spec.get("contractVersion") == "1.0", "contractVersion must be '1.0'")
    agent = mapping(spec, "agent")
    runtime = mapping(spec, "runtime")
    gov = mapping(spec, "governance")
    release = mapping(spec, "release")
    agent_name = agent.get("name", "")
    check(isinstance(agent_name, str) and bool(NAME_PATTERN.fullmatch(agent_name)),
          "agent.name must be lowercase kebab-case (3..63 chars)")
    if expected_name:
        check(agent_name == expected_name, "Caller agent_name does not match contract")
    check(isinstance(agent.get("ownerTeam"), str) and bool(agent.get("ownerTeam").strip()),
          "agent.ownerTeam is required")
    check(isinstance(agent.get("supportContact"), str) and "@" in agent.get("supportContact", ""),
          "agent.supportContact must contain a valid contact address")
    for key, value in {
        "kind": "foundry-hosted",
        "protocol": "responses",
        "packaging": "container",
        "sourcePath": "src/agent",
        "dockerfile": "src/agent/Dockerfile",
    }.items():
        check(runtime.get(key) == value, f"runtime.{key} must be {value!r}")
    check(gov.get("dataClassification") in ("internal", "confidential", "restricted"),
          "governance.dataClassification must be internal/confidential/restricted")
    check(gov.get("approvedModelAlias") == "approved-chat",
          "governance.approvedModelAlias must be approved-chat (mapped by the platform)")
    for key in ("requiredConnections", "outboundDestinations"):
        check(isinstance(gov.get(key), list), f"governance.{key} must be a list")
        # This starter supports no unmanaged network dependencies; request separate exception design.
        check(gov.get(key) == [], f"governance.{key} requires platform approval in contract v1")
    allowed_envs = release.get("environments")
    check(allowed_envs == ["dev", "test", "prod"], "release.environments must be [dev, test, prod]")
    check(isinstance(release.get("smokePrompt"), str) and bool(release.get("smokePrompt").strip()),
          "release.smokePrompt is required")
    check(release.get("evaluationDataset") == "tests/evaluations/smoke.json",
          "release.evaluationDataset must be tests/evaluations/smoke.json")
    eval_path = ROOT / "tests/evaluations/smoke.json"
    if eval_path.is_file():
        try:
            suite = json.loads(eval_path.read_text(encoding="utf-8"))
            check(suite.get("schemaVersion") == "1.0", "Unsupported evaluation dataset version")
            minimum = suite.get("minimumPassRate")
            check(type(minimum) in (float, int) and 0.90 <= minimum <= 1,
                  "Evaluation minimumPassRate must be >=0.90 and <=1")
            cases = suite.get("cases", [])
            check(isinstance(cases, list) and bool(cases), "Evaluation suite must have cases")
            for case in cases if isinstance(cases, list) else []:
                check(isinstance(case, dict) and all(isinstance(case.get(k), str) and case[k].strip()
                      for k in ("id", "prompt", "contains")), "Invalid evaluation case")
        except (OSError, ValueError) as exc:
            ERRORS.append(f"Evaluation dataset is invalid: {exc}")
    else:
        ERRORS.append("Missing required tests/evaluations/smoke.json")
    foundry_eval = load_yaml("src/agent/eval.yaml")
    check(foundry_eval.get("agent", {}).get("name") == agent_name,
          "Foundry eval.yaml agent.name must match product contract")
    check(foundry_eval.get("agent", {}).get("kind") == "hosted",
          "Foundry evaluator must target a hosted agent")
    evaluators = foundry_eval.get("evaluators", [])
    check(isinstance(evaluators, list) and
          {"builtin.intent_resolution", "builtin.task_adherence"}.issubset(set(evaluators)),
          "Foundry evaluation must include intent_resolution and task_adherence")
    check(foundry_eval.get("dataset", {}).get("local_uri") == "tests/queries.jsonl",
          "Foundry evaluator dataset path must remain under the source tree")
    test_queries = ROOT / "src/agent/tests/queries.jsonl"
    if test_queries.is_file():
        try:
            entries = [json.loads(l) for l in test_queries.read_text(encoding="utf-8").splitlines() if l.strip()]
            check(bool(entries) and all(isinstance(q.get("query"), str) and q["query"].strip()
                                         for q in entries), "Foundry query dataset must have nonempty query rows")
        except ValueError as exc:
            ERRORS.append(f"Invalid Foundry query dataset: {exc}")
    else:
        ERRORS.append("Missing src/agent/tests/queries.jsonl")
    if deploy_env:
        check(deploy_env in ("dev", "test", "prod"), "Unsupported deployment environment")

    check("infra" not in manifest, "Product repositories may not declare infra provisioning")
    check(set(manifest).issubset({"name", "requiredVersions", "services"}),
          "azure.yaml contains unapproved top-level fields (for example hooks or infra)")
    check(isinstance(manifest.get("name"), str), "azure.yaml name is required")
    versions = mapping(manifest, "requiredVersions")
    check(set(versions).issubset({"azd", "extensions"}),
          "requiredVersions may only define azd and approved extension constraints")
    extensions = mapping(versions, "extensions")
    check(set(extensions) == {"azure.ai.agents", "azure.ai.projects"},
          "requiredVersions.extensions must contain only approved Foundry providers")
    services = mapping(manifest, "services")
    check(set(services) == {"ai-project", "sample-agent"},
          "azure.yaml may only declare ai-project and sample-agent services")
    proj = mapping(services, "ai-project")
    check(proj.get("host") == "azure.ai.project", "ai-project.host must be azure.ai.project")
    check(proj.get("endpoint") == "${FOUNDRY_PROJECT_ENDPOINT}",
          "ai-project.endpoint must use the platform-supplied FOUNDRY_PROJECT_ENDPOINT")
    check(set(proj) == {"host", "endpoint"},
          "ai-project cannot declare deployments, network, connections, or extra configuration")
    svc = mapping(services, "sample-agent")
    for field, required in {
        "host": "azure.ai.agent",
        "kind": "hosted",
        "name": agent_name,
        "language": "docker",
        "project": "src/agent",
        "image": "${AGENT_IMAGE}",
    }.items():
        check(svc.get(field) == required, f"sample-agent.{field} must be {required!r}")
    check(svc.get("uses") == ["ai-project"], "Hosted agent must only use ai-project")
    check(svc.get("protocols") == [{"protocol": "responses", "version": "2.0.0"}],
          "Agent must declare Responses protocol 2.0.0")
    env = mapping(svc, "env")
    check(env == {
        "AZURE_AI_MODEL_DEPLOYMENT_NAME": "${AZURE_AI_MODEL_DEPLOYMENT_NAME}",
        "PYTHONNOUSERSITE": "1",
        "FOUNDRY_PROJECT_ENDPOINT": "${FOUNDRY_PROJECT_ENDPOINT}",
    }, "Agent env may only contain platform-approved entries")
    check(set(svc).issubset({"host", "kind", "name", "description", "project", "language", "image", "uses", "protocols", "env", "container"}),
          "sample-agent contains an unapproved field")
    container = mapping(svc, "container")
    resources = mapping(container, "resources")
    try:
        cpu = float(resources.get("cpu"))
        mem = str(resources.get("memory", ""))
        gib = float(mem.removesuffix("Gi")) if mem.endswith("Gi") else -1
        check(0.25 <= cpu <= 4.0, "CPU must be between 0.25 and 4")
        check(0.5 <= gib <= 8, "Memory must be between 0.5Gi and 8Gi")
    except (ValueError, TypeError):
        ERRORS.append("Container resource requests must be valid numeric values")
    check((ROOT / "src/agent/main.py").is_file(), "Missing src/agent/main.py")
    check((ROOT / "src/agent/Dockerfile").is_file(), "Missing Dockerfile")
    check((ROOT / ".github/CODEOWNERS").is_file(), "Missing .github/CODEOWNERS")
    req_path = ROOT / "src/agent/requirements.txt"
    if req_path.is_file():
        requirements = [line.strip() for line in req_path.read_text().splitlines()
                        if line.strip() and not line.lstrip().startswith("#")]
        check(bool(requirements), "requirements.txt must not be empty")
        for requirement in requirements:
            check(bool(re.fullmatch(r"[A-Za-z0-9_-]+==[A-Za-z0-9.!+_-]+", requirement)),
                  f"Unpinned or unsupported direct dependency: {requirement}")
    else:
        ERRORS.append("Missing pinned src/agent/requirements.txt")

    if ERRORS:
        for error in ERRORS:
            print(f"::error::{error}")
        sys.exit(1)
    print(f"PASS: platform contract v1 / agent={agent_name} / environment={deploy_env or 'N/A'}")


if __name__ == "__main__":
    main()
