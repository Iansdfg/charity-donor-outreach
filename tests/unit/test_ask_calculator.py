from datetime import date
from decimal import Decimal

import pytest

from charity_donor_outreach.ask_calculator import calculate_ask
from charity_donor_outreach.errors import PolicyError
from charity_donor_outreach.normalization import normalize_donor
from charity_donor_outreach.segmentation import segment
from tests.conftest import make_donor


@pytest.mark.parametrize(
    ("amount", "expected"),
    [("500", "150.00"), ("2000", "300.00"), ("12000", "3000.00"), ("60000", "24000.00")],
)
def test_each_tier_is_reproducible(policies, campaign, amount, expected):
    donor = normalize_donor(make_donor(amount, date(2024, 1, 1)))
    segmented = segment(donor, campaign.as_of_date, policies.segmentation)
    first = calculate_ask(donor, campaign, segmented, policies.ask)
    second = calculate_ask(donor, campaign, segmented, policies.ask)
    assert first == second
    assert first.amount == Decimal(expected)


def test_adjustment_order_and_rounding(policies, campaign):
    donor = normalize_donor(make_donor("1000", date(2025, 1, 1), volunteer=True))
    result = calculate_ask(
        donor, campaign, segment(donor, campaign.as_of_date, policies.segmentation), policies.ask
    )
    assert result.amount == Decimal("250.00")
    assert result.calculation_trace[-1].operation == "round"


def test_emergency_and_lapsed_high_value(policies, campaign):
    emergency = campaign.model_copy(update={"campaign_type": "emergency"})
    donor = normalize_donor(make_donor("60000", date(2020, 1, 1)))
    result = calculate_ask(
        donor, emergency, segment(donor, campaign.as_of_date, policies.segmentation), policies.ask
    )
    assert result.amount == Decimal("21600.00")


def test_minimum_and_maximum_caps(policies, campaign):
    donor = normalize_donor(make_donor("2000", date(2024, 1, 1)))
    segmented = segment(donor, campaign.as_of_date, policies.segmentation)
    high_minimum = {**policies.ask, "minimum": "500.00"}
    low_maximum = {**policies.ask, "maximum": "200.00"}
    assert calculate_ask(donor, campaign, segmented, high_minimum).amount == Decimal("500.00")
    assert calculate_ask(donor, campaign, segmented, low_maximum).amount == Decimal("200.00")


def test_unsupported_currency_fails_closed(policies, campaign):
    donor = normalize_donor(make_donor())
    segmented = segment(donor, campaign.as_of_date, policies.segmentation)
    unsafe = campaign.model_copy(update={"currency": "EUR"})
    with pytest.raises(PolicyError, match="unsupported currency"):
        calculate_ask(donor, unsafe, segmented, policies.ask)
