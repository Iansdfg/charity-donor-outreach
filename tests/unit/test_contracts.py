import json
from pathlib import Path

import yaml
from jsonschema.validators import validator_for


def test_json_schemas_and_yaml_parse():
    for path in Path("schemas").glob("*.json"):
        schema = json.loads(path.read_text())
        validator_for(schema).check_schema(schema)
    versions = {
        yaml.safe_load(path.read_text())["version"] for path in Path("policies").glob("*.yaml")
    }
    assert versions == {"1.0.0"}


def test_skill_frontmatter_is_narrow():
    text = Path("SKILL.md").read_text()
    assert text.startswith("---\nname: charity-donor-outreach\n")
    assert "Use only when" in text
    assert "mock donor table" not in text.lower()
