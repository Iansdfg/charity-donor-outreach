import json

import pytest

from charity_donor_outreach.batch import BatchProcessor
from charity_donor_outreach.llm import FakeDraftingModel
from tests.conftest import make_donor


@pytest.mark.parametrize(
    ("donor", "tier"),
    [
        (make_donor("60000"), "platinum"),
        (make_donor("12000", volunteer=True), "gold"),
        (make_donor("2000"), "silver"),
        (make_donor("500"), "bronze"),
        (make_donor("60000", gift_date=__import__("datetime").date(2020, 1, 1)), "platinum"),
        (make_donor("500", first_name=None), "bronze"),
    ],
)
def test_representative_structural_goldens(tmp_path, policies, campaign, donor, tier):
    run = tmp_path / donor.donor_id
    BatchProcessor(policies, FakeDraftingModel()).run([donor], campaign, run)
    result = json.loads((run / "generation_results.jsonl").read_text())
    assert result["financial_tier"] == tier
    assert result["letter"]["html"].startswith("<!doctype html>")
    assert f"{result['recommended_ask']['amount']}" in result["letter"]["plain_text"]
    assert result["approval_status"] == "requires_review"
