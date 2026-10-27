#!/usr/bin/env python3
"""One-time offline customization of a fresh product-team starter repository."""
import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def replace(path, replacements):
    target = ROOT / path
    body = target.read_text(encoding="utf-8")
    for before, after in replacements.items():
        if before not in body:
            raise SystemExit(f"Expected placeholder {before!r} not found in {path}; already initialized?")
        body = body.replace(before, after)
    target.write_text(body, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="Customize product repo name, ownership and workflow refs")
    p.add_argument("--agent-name", required=True, help="Unique lowercase-kebab-case name")
    p.add_argument("--owner-team", required=True, help="GitHub team slug (no @)")
    p.add_argument("--support-contact", required=True)
    p.add_argument("--github-org", required=True)
    args = p.parse_args()
    for field in ("agent_name", "owner_team", "github_org"):
        if not re.fullmatch(r"[a-z][a-z0-9-]{2,62}" if field == "agent_name" else r"[A-Za-z][A-Za-z0-9-]{1,62}", getattr(args, field)):
            p.error(f"Invalid {field}: use alphanumeric letters and hyphens")
    if "@" not in args.support_contact:
        p.error("--support-contact must be an email-like address")
    replace("platform/contract.yaml", {
        "sample-hosted-agent": args.agent_name,
        "example-product-team@example.com": args.support_contact,
        "example-product-team": args.owner_team,
    })
    replace("azure.yaml", {
        "sample-hosted-agent": args.agent_name,
    })
    replace("src/agent/eval.yaml", {
        "sample-hosted-agent": args.agent_name,
    })
    replace(".github/CODEOWNERS", {
        "YOUR-ORG": args.github_org,
        "example-product-team": args.owner_team,
    })
    for wf in (".github/workflows/ci.yml", ".github/workflows/release.yml"):
        replace(wf, {"YOUR-ORG": args.github_org, "sample-hosted-agent": args.agent_name})
    print(f"Configured template for {args.agent_name} in org {args.github_org}.")
    print("Next: review azure.yaml, platform/contract.yaml, code, tests, required GitHub env vars.")


if __name__ == "__main__":
    main()
