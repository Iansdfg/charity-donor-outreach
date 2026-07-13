from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from charity_donor_outreach.config import load_policies
from charity_donor_outreach.models import Campaign, DonorInput, Gift, Money


@pytest.fixture
def policies():
    return load_policies()


@pytest.fixture
def campaign():
    return Campaign(
        campaign_id="C-1",
        name="Annual Fund",
        charity_name="Test Charity",
        campaign_type="annual_fund",
        as_of_date=date(2026, 7, 1),
        donation_url="https://give.example.org/a",
        currency="USD",
    )


def make_donor(
    amount: str = "1000", gift_date: date = date(2025, 1, 1), **updates: Any
) -> DonorInput:
    values = {
        "donor_id": "D-1",
        "first_name": "Alex",
        "communication_status": "opted_in",
        "gifts": [Gift(gift_id="G-1", date=gift_date, amount=Money(amount=Decimal(amount)))],
    }
    values.update(updates)
    return DonorInput(**values)
