import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).parents[1] / '.github/actions/evaluate-foundry-quality/run_foundry_eval.py'
spec = importlib.util.spec_from_file_location('native_foundry_evals', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FoundryEvaluationGateTests(unittest.TestCase):
    def test_parse_summary_and_gate(self):
        output = 'Results:    3 total, 3 passed, 0 failed, 0 errored'
        self.assertEqual(m.parse_summary(output), (3, 3, 0, 0))
        self.assertTrue(m.meets_gate(m.parse_summary(output), 0.9))

    def test_fails_closed_for_missing_summary(self):
        with self.assertRaises(ValueError):
            m.parse_summary('Evaluation started but output is not complete')

    def test_fails_for_errors(self):
        self.assertFalse(m.meets_gate((5, 4, 0, 1), 0.75))
        self.assertFalse(m.meets_gate((5, 4, 1, 0), 0.75))
