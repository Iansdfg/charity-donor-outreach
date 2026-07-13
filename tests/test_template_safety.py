from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "templates/donor-letter.html").read_text(encoding="utf-8")


class TemplateSafetyTests(unittest.TestCase):
    def test_accessible_document_structure(self):
        lowered = TEMPLATE.casefold()
        self.assertTrue(lowered.startswith("<!doctype html>"))
        self.assertRegex(TEMPLATE, r'<html\s+lang="[^"]+"')
        self.assertRegex(lowered, r'<meta\s+charset="utf-8"')
        self.assertIn("<main", lowered)
        self.assertIn('role="presentation"', lowered)

    def test_donation_anchor_is_descriptive_and_templated(self):
        self.assertRegex(
            TEMPLATE,
            r'<a\s+href="\{\{DONATION_URL\}\}"[^>]*>Make a secure donation</a>',
        )

    def test_no_active_or_tracking_content(self):
        lowered = TEMPLATE.casefold()
        for element in ("<script", "<iframe", "<form", "<object", "<embed"):
            self.assertNotIn(element, lowered)
        self.assertIsNone(re.search(r"\son[a-z]+\s*=", TEMPLATE, flags=re.IGNORECASE))
        self.assertIsNone(
            re.search(r"<img\b[^>]*\bsrc\s*=\s*['\"]?https?://", TEMPLATE, re.I)
        )
        self.assertNotIn("tracking", lowered)

    def test_placeholders_are_exactly_documented(self):
        placeholders = set(re.findall(r"\{\{([A-Z_]+)\}\}", TEMPLATE))
        documentation = (ROOT / "references/template-placeholders.md").read_text(
            encoding="utf-8"
        )
        documented = set(re.findall(r"`([A-Z_]+)`", documentation))
        self.assertEqual(placeholders, documented)

    def test_no_unresolved_legacy_placeholder_syntax(self):
        self.assertNotRegex(TEMPLATE, r"\[[A-Z][A-Z_ ]+\]")
        self.assertNotRegex(TEMPLATE, r"\$\{[A-Z_]+\}")

    def test_human_review_compatible_four_paragraph_structure(self):
        for placeholder in (
            "OPENING_PARAGRAPH",
            "CAMPAIGN_PARAGRAPH",
            "ASK_PARAGRAPH",
            "CLOSING_PARAGRAPH",
        ):
            self.assertRegex(
                TEMPLATE,
                rf'<p[^>]*text-indent:\s*2em[^>]*>\{{\{{{placeholder}\}}\}}</p>',
            )


if __name__ == "__main__":
    unittest.main()
