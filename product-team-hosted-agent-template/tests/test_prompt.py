"""No Azure resources or runtime SDK required for this unit test."""
import pathlib
import sys
import unittest

AGENT_SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "agent"
sys.path.insert(0, str(AGENT_SRC))
from prompt import INSTRUCTIONS  # noqa: E402


class TestPrompt(unittest.TestCase):
    def test_nonempty_instructions(self):
        self.assertGreater(len(INSTRUCTIONS.strip()), 40)

    def test_no_false_action_claims(self):
        self.assertIn("Do not claim", INSTRUCTIONS)


if __name__ == "__main__":
    unittest.main()
