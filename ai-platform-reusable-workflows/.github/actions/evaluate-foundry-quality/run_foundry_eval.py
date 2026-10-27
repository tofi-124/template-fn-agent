#!/usr/bin/env python3
"""Runs Microsoft's azd managed evaluation and enforces summary-count gate.

Foundry's `azd ai agent eval run` is preview; this exact CLI output parser must be
revalidated when Foundry CLI changes. Fail closed if summary unavailable.
"""
import os
import re
import subprocess
import sys

SUMMARY = re.compile(r"Results:\s*(\d+)\s+total,\s*(\d+)\s+passed,\s*(\d+)\s+failed,\s*(\d+)\s+errored", re.I)


def parse_summary(output):
    # Remove ANSI SGR escape codes from CLI console output.
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    matches = list(SUMMARY.finditer(output))
    if not matches:
        raise ValueError("Foundry evaluation summary counts were missing. Check azd version / logs.")
    total, passed, failed, errored = map(int, matches[-1].groups())
    if total <= 0 or (passed + failed + errored) > total:
        raise ValueError("Invalid Foundry evaluation summary")
    return total, passed, failed, errored


def meets_gate(counts, threshold):
    total, passed, failed, errored = counts
    return failed == 0 and errored == 0 and passed / total >= threshold


def main():
    threshold = float(os.environ.get("MIN_PASS_RATE", "1.0"))
    if not 0 < threshold <= 1.0:
        raise ValueError("minimum-pass-rate must be >0 and <=1")
    config = os.environ.get("EVAL_CONFIG", "eval.yaml")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.yaml", config):
        raise ValueError("config must be basename ending with .yaml")
    proc = subprocess.run(["azd", "ai", "agent", "eval", "run", "--config", config],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, timeout=1800)
    # Evaluation logs should be reviewed; avoid putting sensitive agent data in them.
    print(proc.stdout)
    if proc.returncode:
        raise RuntimeError(f"Foundry evaluation command failed (exit {proc.returncode})")
    counts = parse_summary(proc.stdout)
    print(f"Native Foundry evaluation counts: total={counts[0]}, passed={counts[1]}, failed={counts[2]}, errored={counts[3]}")
    if not meets_gate(counts, threshold):
        raise RuntimeError(f"Managed evaluation failed threshold {threshold:.0%}")
    print("PASS: Foundry managed evaluation gate")


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as ex:
        print(f'::error::{ex}', file=sys.stderr)
        sys.exit(1)
