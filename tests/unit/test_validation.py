from pathlib import Path

import pytest
from pydantic import ValidationError

from charity_donor_outreach.errors import InputValidationError
from charity_donor_outreach.models import DonorInput, Gift
from charity_donor_outreach.validation import load_donors_csv, validate_url


def test_missing_donor_id_and_invalid_gift_values():
    with pytest.raises(ValidationError):
        DonorInput(donor_id="")
    with pytest.raises(ValidationError):
        Gift.model_validate(
            {"gift_id": "g", "date": "bad", "amount": {"amount": -1, "currency": "USD"}}
        )
    with pytest.raises(ValidationError):
        Gift.model_validate(
            {"gift_id": "g", "date": "2025-01-01", "amount": {"amount": 1, "currency": "US"}}
        )


def test_duplicate_and_formula_injection(tmp_path: Path) -> None:
    header = "donor_id,first_name,gift_date,gift_amount\n"
    duplicate = tmp_path / "duplicate.csv"
    duplicate.write_text(header + "D-1,A,2025-01-01,1\nD-1,B,2025-01-01,2\n")
    with pytest.raises(InputValidationError, match="duplicate"):
        load_donors_csv(duplicate)
    injected = tmp_path / "injected.csv"
    injected.write_text(header + "D-1,=cmd,2025-01-01,1\n")
    with pytest.raises(InputValidationError, match="formula"):
        load_donors_csv(injected)


@pytest.mark.parametrize(
    "url",
    [
        "http://bad.example/a",
        "javascript:alert(1)",
        "https://localhost/a",
        "https://u:p@example.org/a",
    ],
)
def test_malicious_urls(url: str) -> None:
    with pytest.raises(InputValidationError):
        validate_url(url)
