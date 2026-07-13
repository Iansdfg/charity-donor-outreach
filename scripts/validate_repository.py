#!/usr/bin/env python3
"""Run lightweight, dependency-free repository integrity checks."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LEGACY_COLUMNS = {
    "Donor Name",
    "Tier",
    "Region",
    "Gifts (Year: Amount)",
    "Largest Gift",
    "Lifetime Total",
    "Last Gift Year",
    "Volunteer",
}
EXPECTED_PLACEHOLDERS = {
    "SUBJECT",
    "DATE",
    "SALUTATION",
    "OPENING_PARAGRAPH",
    "CAMPAIGN_PARAGRAPH",
    "ASK_PARAGRAPH",
    "CLOSING_PARAGRAPH",
    "DONATION_URL",
    "SENDER_NAME",
    "SENDER_TITLE",
    "CHARITY_NAME",
}


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    lines = text[4:end].splitlines()
    result: dict[str, str] = {}
    current: str | None = None
    for line in lines:
        match = re.match(r"^([a-zA-Z][\w-]*):(?:\s*(.*))?$", line)
        if match:
            current = match.group(1)
            result[current] = (match.group(2) or "").strip().strip("'\"")
        elif current and line.startswith("  "):
            result[current] = (result[current] + " " + line.strip()).strip()
    return result


def _local_markdown_links(path: Path, text: str):
    # Code examples often intentionally contain placeholder Markdown such as
    # `[label](URL)`; only prose links are repository navigation claims.
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    for target in re.findall(r"(?<!!)\[[^]]*\]\(([^)]+)\)", prose):
        target = target.strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        clean_target = target.split("#", 1)[0]
        if clean_target:
            yield target, (path.parent / clean_target).resolve()


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    required = [
        "SKILL.md",
        "README.md",
        "templates/donor-letter.html",
        "templates/donor-letter.txt",
        "examples/campaign.annual-fund.yaml",
        "examples/campaign.emergency-confirmed-match.yaml",
        "examples/campaign.emergency-no-match.yaml",
        "examples/donors.mock.csv",
        "scripts/donor_policy.py",
        "scripts/calculate_donor.py",
    ]
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = root / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""
    metadata = _frontmatter(skill)
    if metadata.get("name") != "charity-donor-outreach":
        errors.append("SKILL.md frontmatter has an invalid or missing name")
    if not metadata.get("description"):
        errors.append("SKILL.md frontmatter has a missing description")
    for reference in sorted(set(re.findall(r"references/[A-Za-z0-9_.-]+\.md", skill))):
        if not (root / reference).is_file():
            errors.append(f"SKILL.md names a missing reference: {reference}")

    mock_path = root / "examples/donors.mock.csv"
    if mock_path.exists():
        with mock_path.open("r", encoding="utf-8-sig", newline="") as handle:
            columns = set(csv.DictReader(handle).fieldnames or [])
        missing_columns = EXPECTED_LEGACY_COLUMNS - columns
        if missing_columns:
            errors.append(f"mock CSV missing legacy columns: {sorted(missing_columns)}")

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    for label, content in (("README.md", readme), ("SKILL.md", skill)):
        lowered = content.casefold()
        if "synthetic" not in lowered or "mock" not in lowered:
            errors.append(f"{label} must label bundled mock data as synthetic")
    if "python is optional" not in readme.casefold():
        errors.append("README.md must state that Python is optional")
    if "prompt-native fallback" not in readme.casefold():
        errors.append("README.md must document prompt-native fallback behavior")
    if "do not execute the helper before the user approves" not in skill.casefold():
        errors.append("SKILL.md must require approval before helper execution")
    if "never claim deterministic validation unless" not in skill.casefold():
        errors.append("SKILL.md must forbid false deterministic claims")

    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target, resolved in _local_markdown_links(path, text):
            if not resolved.exists():
                errors.append(f"broken local Markdown link in {path.relative_to(root)}: {target}")

    template_path = root / "templates/donor-letter.html"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
        placeholders = set(re.findall(r"\{\{([A-Z_]+)\}\}", template))
        if placeholders != EXPECTED_PLACEHOLDERS:
            errors.append(
                "HTML template placeholders differ from the documented expected set"
            )
        unsafe_patterns = {
            "script element": r"<script\b",
            "iframe element": r"<iframe\b",
            "form element": r"<form\b",
            "inline event handler": r"\son[a-z]+\s*=",
            "remote image": r"<img\b[^>]*\bsrc\s*=\s*['\"]?https?://",
        }
        for label, pattern in unsafe_patterns.items():
            if re.search(pattern, template, flags=re.IGNORECASE):
                errors.append(f"HTML template contains unsafe {label}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
