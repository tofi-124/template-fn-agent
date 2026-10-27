#!/usr/bin/env python3
"""Illustrative live outcome gate, not Microsoft Foundry's managed evaluation service.

Tests the deployed agent via Azure Developer CLI (after deployment). Checks an expected
response marker and a minimum pass rate. Replace with trusted structured responses and
Foundry evaluations for safety, relevance, groundedness, and task completion before prod.
"""
import json
import pathlib
import subprocess
import sys


def load_suite(path):
    obj = json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    if obj.get('schemaVersion') != '1.0':
        raise ValueError('evaluation suite schemaVersion must be 1.0')
    cases = obj.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('evaluation cases required')
    threshold = obj.get('minimumPassRate')
    if not isinstance(threshold, (float, int)) or isinstance(threshold, bool) or not (0 < threshold <= 1):
        raise ValueError('minimumPassRate must be (0,1]')
    for case in cases:
        if not isinstance(case, dict) or not all(isinstance(case.get(k), str) and case[k].strip()
                                                    for k in ('id', 'prompt', 'contains')):
            raise ValueError('evaluation cases require id, prompt and contains')
    return obj


def run_suite(data, invoker):
    passed = 0
    for case in data['cases']:
        try:
            result = invoker(case['prompt'])
            # CLI human-readable output may vary: restrict this simple gate to stable
            # marker smoke-tests. A production evaluator must parse structured output.
            success = case['contains'].casefold() in result.casefold()
        except (subprocess.SubprocessError, OSError, ValueError):
            success = False
        print(f"{'PASS' if success else 'FAIL'}: {case['id']}")
        passed += bool(success)
    rate = passed / len(data['cases'])
    print(f'Evaluation pass rate: {rate:.1%}; required: {data["minimumPassRate"]:.1%}')
    return rate >= data['minimumPassRate']


def cli_invoke(prompt):
    command = ['azd', 'ai', 'agent', 'invoke', prompt]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=180, check=True)
    if not proc.stdout.strip():
        raise ValueError('No agent response returned')
    return proc.stdout


if __name__ == '__main__':
    try:
        suite = load_suite(sys.argv[1])
        sys.exit(0 if run_suite(suite, cli_invoke) else 1)
    except (OSError, ValueError, IndexError, json.JSONDecodeError) as ex:
        print(f'::error::{ex}', file=sys.stderr)
        sys.exit(1)
