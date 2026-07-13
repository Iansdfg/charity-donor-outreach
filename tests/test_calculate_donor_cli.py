from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/calculate_donor.py"
AS_OF_ARGS = ["--as-of-date", "2026-07-01", "--campaign-type", "Annual Fund"]


class CalculateDonorCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI), *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_single_donor_json_emits_valid_json(self):
        completed = self.run_cli(
            "donor", "--input", ROOT / "examples/donor.single.json", *AS_OF_ARGS
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        result = json.loads(completed.stdout)
        self.assertEqual(result["donor_label"], "Ada Yamamoto-Pierce")
        self.assertEqual(result["policy_version"], "1.0.0")
        self.assertIn("TIER_CONFLICT", {item["code"] for item in result["warnings"]})

    def test_legacy_csv_preserves_order_and_suppression(self):
        completed = self.run_cli(
            "csv",
            "--input",
            ROOT / "tests/fixtures/conflicting_donors.csv",
            *AS_OF_ARGS,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        results = json.loads(completed.stdout)
        self.assertEqual(
            [result["donor_label"] for result in results],
            ["Conflict Example", "Suppressed Example"],
        )
        self.assertIn(
            "LIFETIME_TOTAL_CONFLICT",
            {item["code"] for item in results[0]["warnings"]},
        )
        self.assertTrue(results[1]["suppressed"])
        self.assertEqual(results[1]["status"], "suppressed")
        self.assertIsNone(results[1]["recommended_ask"])
        self.assertEqual(results[1]["calculation_trace"], [])

    def test_mock_csv_output_order_matches_input_order(self):
        completed = self.run_cli(
            "csv", "--input", ROOT / "examples/donors.mock.csv", *AS_OF_ARGS
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        results = json.loads(completed.stdout)
        self.assertEqual(results[0]["donor_label"], "Robert Svensson")
        self.assertEqual(results[1]["donor_label"], "Earl Fontaine")
        self.assertEqual(len(results), 50)
        self.assertFalse(
            any(
                warning["code"] == "INCOMPLETE_GIFT_HISTORY"
                for result in results
                for warning in result["warnings"]
            )
        )

    def test_malformed_json_has_nonzero_exit_and_stderr_only_diagnostic(self):
        secret = "Private Donor Full Record"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"Donor Name": "' + secret + '"', encoding="utf-8")
            completed = self.run_cli("donor", "--input", path, *AS_OF_ARGS)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertIn("error:", completed.stderr)
        self.assertNotIn(secret, completed.stderr)

    def test_invalid_usage_is_nonzero(self):
        completed = self.run_cli("donor")
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertIn("usage:", completed.stderr)

    def test_scripts_import_only_standard_library_or_local_policy(self):
        allowed_roots = {
            "__future__",
            "argparse",
            "csv",
            "dataclasses",
            "datetime",
            "decimal",
            "donor_policy",
            "enum",
            "json",
            "pathlib",
            "re",
            "subprocess",
            "sys",
            "typing",
            "unittest",
        }
        for path in (
            CLI,
            ROOT / "scripts/donor_policy.py",
            ROOT / "scripts/validate_repository.py",
        ):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertFalse(imports - allowed_roots, f"unexpected imports in {path}: {imports - allowed_roots}")


if __name__ == "__main__":
    unittest.main()
