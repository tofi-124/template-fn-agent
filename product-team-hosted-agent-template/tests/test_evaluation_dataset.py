import json
import pathlib
import unittest


class EvaluationDataTests(unittest.TestCase):
    def test_data_structure(self):
        path = pathlib.Path(__file__).parent / 'evaluations' / 'smoke.json'
        suite = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(suite['schemaVersion'], '1.0')
        self.assertGreaterEqual(suite['minimumPassRate'], 0.0)
        self.assertLessEqual(suite['minimumPassRate'], 1.0)
        self.assertGreaterEqual(len(suite['cases']), 1)
        for case in suite['cases']:
            self.assertTrue(case['id'] and case['prompt'] and case['contains'])
