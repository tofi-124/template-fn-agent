"""Local regression tests for the PLATFORM-owned validator; no cloud needed."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests/fixtures/product-repo"
VALIDATOR = ROOT / ".github/actions/validate-hosted-agent/validate_contract.py"


class ContractValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "agent"
        shutil.copytree(SAMPLE, self.repo, ignore=shutil.ignore_patterns("__pycache__", ".venv"))

    def run_validator(self):
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "sample-hosted-agent", "dev"],
            cwd=self.repo, capture_output=True, text=True, check=False,
        )

    def test_valid_template(self):
        self.assertEqual(self.run_validator().returncode, 0)

    def test_rejects_provisioning(self):
        yaml_path = self.repo / "azure.yaml"
        yaml_path.write_text(yaml_path.read_text() + "\ninfra:\n  provider: terraform\n")
        self.assertNotEqual(self.run_validator().returncode, 0)

    def test_rejects_azd_hooks(self):
        yaml_path = self.repo / "azure.yaml"
        yaml_path.write_text(yaml_path.read_text() + "\nhooks:\n  postdeploy:\n    shell: sh\n    run: echo forbidden\n")
        self.assertNotEqual(self.run_validator().returncode, 0)

    def test_rejects_changed_project(self):
        yaml_path = self.repo / "azure.yaml"
        yaml_path.write_text(yaml_path.read_text().replace("${FOUNDRY_PROJECT_ENDPOINT}", "https://wrong.example.com"))
        self.assertNotEqual(self.run_validator().returncode, 0)

    def test_rejects_mismatched_name(self):
        path = self.repo / "platform/contract.yaml"
        path.write_text(path.read_text().replace("sample-hosted-agent", "other-agent"))
        self.assertNotEqual(self.run_validator().returncode, 0)


if __name__ == "__main__":
    unittest.main()
