import importlib.util
import pathlib
import tempfile
import json
import unittest

ROOT = pathlib.Path(__file__).parents[1]
script = ROOT / '.github/actions/evaluate-hosted-agent/evaluate_agent.py'
spec = importlib.util.spec_from_file_location('central_eval', script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LiveGateTests(unittest.TestCase):
    def setUp(self):
        self.suite = {'schemaVersion': '1.0', 'minimumPassRate': 0.5, 'cases': [
            {'id': 'a', 'prompt': 'hello', 'contains': 'OK'},
            {'id': 'b', 'prompt': 'bye', 'contains': 'DONE'},
        ]}

    def test_threshold(self):
        self.assertTrue(module.run_suite(self.suite, lambda q: 'OK' if q == 'hello' else 'nope'))
        self.suite['minimumPassRate'] = 1.0
        self.assertFalse(module.run_suite(self.suite, lambda q: 'OK' if q == 'hello' else 'nope'))

    def test_load_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / 'suite.json'
            path.write_text(json.dumps(self.suite))
            self.assertEqual(len(module.load_suite(path)['cases']), 2)
            self.suite['minimumPassRate'] = 0
            path.write_text(json.dumps(self.suite))
            with self.assertRaises(ValueError):
                module.load_suite(path)
