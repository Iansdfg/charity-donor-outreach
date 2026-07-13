from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import ValidationError

from .errors import InputValidationError
from .models import Campaign, DonorInput

FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def reject_formula(value: str, *, field: str) -> None:
    if value.lstrip().startswith(FORMULA_PREFIXES):
        raise InputValidationError(f"CSV formula injection detected in {field}")


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise InputValidationError("donation_url must be an absolute credential-free HTTPS URL")
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        raise InputValidationError("donation_url cannot target a local host")


def load_campaign(path: Path) -> Campaign:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        campaign = Campaign.model_validate(raw)
        validate_url(str(campaign.donation_url))
        return campaign
    except (OSError, json.JSONDecodeError, ValidationError, InputValidationError) as exc:
        raise InputValidationError(f"invalid campaign {path}: {exc}") from exc


def _gift_from_columns(row: dict[str, str]) -> list[dict[str, Any]]:
    if not row.get("gift_amount"):
        return []
    return [
        {
            "gift_id": row.get("gift_id") or f"{row.get('donor_id', 'unknown')}-gift-1",
            "date": row.get("gift_date"),
            "amount": {"amount": row["gift_amount"], "currency": row.get("currency") or "USD"},
        }
    ]


def load_donors_csv(path: Path) -> list[DonorInput]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except OSError as exc:
        raise InputValidationError(f"cannot read donors {path}: {exc}") from exc
    donors: list[DonorInput] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        for key, value in row.items():
            reject_formula(value or "", field=f"{key} at line {line}")
        raw: dict[str, Any] = {
            "donor_id": row.get("donor_id"),
            "first_name": row.get("first_name") or None,
            "preferred_name": row.get("preferred_name") or None,
            "preferred_salutation": row.get("preferred_salutation") or None,
            "household_id": row.get("household_id") or None,
            "household_primary": (row.get("household_primary") or "true").lower() == "true",
            "gifts": _gift_from_columns(row),
            "volunteer": (row.get("volunteer") or "false").lower() == "true",
            "do_not_contact": (row.get("do_not_contact") or "false").lower() == "true",
            "communication_status": row.get("communication_status") or "unknown",
            "deceased": (row.get("deceased") or "false").lower() == "true",
            "supplied_tier": row.get("supplied_tier") or None,
        }
        try:
            donor = DonorInput.model_validate(raw)
        except ValidationError as exc:
            raise InputValidationError(f"invalid donor at CSV line {line}: {exc}") from exc
        if donor.donor_id in seen:
            raise InputValidationError(f"duplicate donor_id {donor.donor_id!r} at line {line}")
        seen.add(donor.donor_id)
        donors.append(donor)
    return sorted(donors, key=lambda item: item.donor_id)
