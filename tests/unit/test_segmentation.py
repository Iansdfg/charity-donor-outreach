from datetime import date
from decimal import Decimal

import pytest

from charity_donor_outreach.normalization import normalize_donor
from charity_donor_outreach.reconciliation import reconcile
from charity_donor_outreach.segmentation import engagement_status, financial_tier, segment
from tests.conftest import make_donor


@pytest.mark.parametrize(
    ("amount", "tier"),
    [
        ("0", "bronze"),
        ("999.99", "bronze"),
        ("1000", "silver"),
        ("9999.99", "silver"),
        ("10000", "gold"),
        ("49999.99", "gold"),
        ("50000", "platinum"),
        ("50001", "platinum"),
    ],
)
def test_tier_boundaries(policies, amount, tier):
    assert financial_tier(Decimal(amount), policies.segmentation) == tier


def test_lapsed_is_independent(policies):
    donor = normalize_donor(make_donor("60000", date(2020, 1, 1)))
    result = segment(donor, date(2026, 7, 1), policies.segmentation)
    assert (result.financial_tier, result.engagement_status) == ("platinum", "lapsed")
    assert engagement_status(None, date(2026, 1, 1), policies.segmentation) == "never_gave"


def test_conflicts_are_material(policies):
    source = make_donor(
        "12000", supplied_tier="silver", supplied_lifetime_total={"amount": "1", "currency": "USD"}
    )
    normalized = normalize_donor(source)
    result = reconcile(
        source, normalized, segment(normalized, date(2026, 1, 1), policies.segmentation)
    )
    assert {warning.code for warning in result.warnings} == {
        "tier_mismatch",
        "lifetime_total_mismatch",
    }
    assert all(warning.material for warning in result.warnings)
