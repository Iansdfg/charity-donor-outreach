from __future__ import annotations

import csv
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_repository import _frontmatter, validate  # noqa: E402


class RepositoryIntegrityTests(unittest.TestCase):
    def test_repository_validator_reports_no_errors(self):
        self.assertEqual(validate(ROOT), [])

    def test_skill_frontmatter_name_and_description(self):
        metadata = _frontmatter((ROOT / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(metadata["name"], "charity-donor-outreach")
        self.assertTrue(metadata["description"])

    def test_all_skill_references_and_core_assets_exist(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        references = set(re.findall(r"references/[A-Za-z0-9_.-]+\.md", skill))
        self.assertTrue(references)
        for relative in references:
            self.assertTrue((ROOT / relative).is_file(), relative)
        for relative in (
            "templates/donor-letter.html",
            "templates/donor-letter.txt",
            "examples/campaign.annual-fund.yaml",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_mock_csv_legacy_columns_and_synthetic_labels(self):
        with (ROOT / "examples/donors.mock.csv").open(
            "r", encoding="utf-8-sig", newline=""
        ) as handle:
            headers = set(csv.DictReader(handle).fieldnames or [])
        self.assertTrue(
            {
                "Donor Name",
                "Tier",
                "Region",
                "Gifts (Year: Amount)",
                "Largest Gift",
                "Lifetime Total",
                "Last Gift Year",
                "Volunteer",
            }
            <= headers
        )
        for relative in ("README.md", "SKILL.md"):
            text = (ROOT / relative).read_text(encoding="utf-8").casefold()
            self.assertIn("synthetic", text)
            self.assertIn("mock", text)

    def test_python_is_optional_and_fallback_is_honest(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8").casefold()
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").casefold()
        self.assertIn("python is optional", readme)
        self.assertIn("still works without python", readme)
        self.assertIn("prompt-native fallback", readme)
        self.assertIn("do not execute the helper before the user approves", skill)
        self.assertIn("never claim deterministic validation unless", skill)

    def test_validation_command_succeeds(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_repository.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("passed", completed.stdout)


if __name__ == "__main__":
    unittest.main()
