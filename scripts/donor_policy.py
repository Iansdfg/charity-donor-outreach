"""Canonical deterministic donor arithmetic and reconciliation policy.

This module intentionally uses only the Python standard library. It never
renders letters, authorizes campaign claims, sends data, or performs I/O.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from typing import Any, Iterable, Mapping


POLICY_VERSION = "1.0.0"


class FinancialTier(str, Enum):
    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"
    UNKNOWN = "Unknown"


class EngagementStatus(str, Enum):
    ACTIVE = "Active"
    LAPSED = "Lapsed"
    UNKNOWN = "Unknown"


TIER_THRESHOLDS = (
    (Decimal("50000"), FinancialTier.PLATINUM),
    (Decimal("10000"), FinancialTier.GOLD),
    (Decimal("1000"), FinancialTier.SILVER),
)
TIER_RATES = {
    FinancialTier.PLATINUM: Decimal("0.40"),
    FinancialTier.GOLD: Decimal("0.25"),
    FinancialTier.SILVER: Decimal("0.15"),
}
BRONZE_BASE = Decimal("150")
UNKNOWN_BASE = Decimal("50")
LOYALTY_MULTIPLIER = Decimal("1.10")
LAPSED_MULTIPLIER = Decimal("0.75")
EMERGENCY_MULTIPLIER = Decimal("1.20")
VOLUNTEER_ADDITION = Decimal("100")
MINIMUM_ASK = Decimal("50")
MAXIMUM_ASK = Decimal("100000")
ROUNDING_INCREMENT = Decimal("50")


class DonorPolicyError(ValueError):
    """Raised when donor input cannot safely participate in calculations."""


@dataclass(frozen=True)
class Gift:
    year: int
    amount: Decimal
    gift_date: date | None = None
    currency: str = "USD"


@dataclass(frozen=True)
class GiftHistory:
    gifts: tuple[Gift, ...]
    complete: bool
    errors: tuple[str, ...] = ()
    currency: str | None = None


@dataclass(frozen=True)
class SuppressionResult:
    suppressed: bool
    reasons: tuple[str, ...]
    consent_warning: bool


@dataclass(frozen=True)
class AskResult:
    amount: Decimal
    trace: tuple[str, ...]
    review_required: bool


_ENTRY_RE = re.compile(
    r"(?:^|[;,])\s*(?P<when>\d{4}(?:-\d{2}-\d{2})?)\s*:\s*"
    r"(?P<amount>.*?)(?=(?:[;,]\s*\d{4}(?:-\d{2}-\d{2})?\s*:)|$)"
)
_FIELD_NORMALIZER = re.compile(r"[^a-z0-9]+")
_CURRENCY_CODES = re.compile(r"\b([A-Z]{3})\b")


def _normalize_key(value: str) -> str:
    return _FIELD_NORMALIZER.sub("", value.casefold())


def normalize_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize supported CSV/JSON field names without interpreting values."""

    aliases = {
        "donorname": "donor_name",
        "donorid": "donor_id",
        "tier": "tier",
        "gifts": "gifts",
        "giftsyearamount": "gifts",
        "largestgift": "largest_gift",
        "lifetimetotal": "lifetime_total",
        "lastgiftyear": "last_gift_year",
        "volunteer": "volunteer",
        "donotcontact": "do_not_contact",
        "communicationstatus": "communication_status",
        "deceased": "deceased",
    }
    normalized: dict[str, Any] = {}
    for key, value in record.items():
        canonical = aliases.get(_normalize_key(str(key)))
        if canonical and canonical not in normalized:
            normalized[canonical] = value
    return normalized


def parse_money(value: Any) -> Decimal:
    """Parse a non-negative USD/bare monetary value without conversion."""

    if isinstance(value, bool) or value is None:
        raise DonorPolicyError("money value is missing or not numeric")
    if isinstance(value, Decimal):
        amount = value
    elif isinstance(value, (int, float)):
        # str(float) avoids importing binary floating-point error into Decimal.
        try:
            amount = Decimal(str(value))
        except InvalidOperation as exc:
            raise DonorPolicyError("money value is malformed") from exc
    else:
        text = str(value).strip()
        if not text:
            raise DonorPolicyError("money value is empty")
        if text[0] in "=+@":
            raise DonorPolicyError("spreadsheet formula-like money value rejected")
        if text.startswith("-") or text.startswith("(-") or (
            text.startswith("(") and text.endswith(")")
        ):
            raise DonorPolicyError("negative money value rejected")
        if any(symbol in text for symbol in "€£¥₹"):
            raise DonorPolicyError("unsupported or ambiguous currency")
        codes = {code.upper() for code in _CURRENCY_CODES.findall(text)}
        if codes - {"USD"} or len(codes) > 1:
            raise DonorPolicyError("unsupported or mixed currency")
        cleaned = re.sub(r"\bUSD\b", "", text, flags=re.IGNORECASE)
        cleaned = cleaned.replace("$", "").replace(",", "").strip()
        if not re.fullmatch(r"\d+(?:\.\d{1,2})?", cleaned):
            raise DonorPolicyError("money value is malformed or ambiguous")
        try:
            amount = Decimal(cleaned)
        except InvalidOperation as exc:
            raise DonorPolicyError("money value is malformed") from exc
    if not amount.is_finite() or amount < 0:
        raise DonorPolicyError("negative or non-finite money value rejected")
    return amount


def parse_gift_history(value: Any) -> GiftHistory:
    """Parse year/date-and-money entries and report whether all input parsed."""

    if value is None or not str(value).strip():
        return GiftHistory((), False, ("gift history is missing",), None)
    text = str(value).strip()
    matches = list(_ENTRY_RE.finditer(text))
    gifts: list[Gift] = []
    errors: list[str] = []
    consumed = "".join(match.group(0) for match in matches)
    comparable_source = re.sub(r"\s+", "", text).lstrip(";,")
    comparable_consumed = re.sub(r"\s+", "", consumed).lstrip(";,")
    if not matches or comparable_consumed != comparable_source:
        errors.append("gift history contains malformed or unparsed content")
    for match in matches:
        when = match.group("when")
        try:
            gift_date = date.fromisoformat(when) if "-" in when else None
            year = gift_date.year if gift_date else int(when)
            if year < 1900 or year > 9999:
                raise ValueError
        except ValueError:
            errors.append("gift history contains an invalid date or year")
            continue
        try:
            amount = parse_money(match.group("amount"))
        except DonorPolicyError as exc:
            errors.append(str(exc))
            continue
        gifts.append(Gift(year=year, amount=amount, gift_date=gift_date))
    return GiftHistory(tuple(gifts), bool(gifts) and not errors, tuple(errors), "USD" if gifts else None)


def calculate_lifetime_total(gifts: Iterable[Gift]) -> Decimal:
    return sum((gift.amount for gift in gifts), Decimal("0"))


def calculate_largest_gift(gifts: Iterable[Gift]) -> Decimal | None:
    amounts = [gift.amount for gift in gifts]
    return max(amounts) if amounts else None


def calculate_latest_gift_year(gifts: Iterable[Gift]) -> int | None:
    years = [gift.year for gift in gifts]
    return max(years) if years else None


def calculate_financial_tier(lifetime_total: Decimal | None) -> FinancialTier:
    if lifetime_total is None:
        return FinancialTier.UNKNOWN
    if lifetime_total < 0:
        raise DonorPolicyError("negative lifetime total rejected")
    for threshold, tier in TIER_THRESHOLDS:
        if lifetime_total >= threshold:
            return tier
    return FinancialTier.BRONZE


def calculate_engagement_status(
    latest_gift_year: int | None,
    as_of_date: date,
    latest_gift_date: date | None = None,
) -> EngagementStatus:
    if latest_gift_date is not None:
        try:
            third_anniversary = latest_gift_date.replace(year=latest_gift_date.year + 3)
        except ValueError:  # Feb. 29 becomes Feb. 28 in a non-leap anniversary year.
            third_anniversary = latest_gift_date.replace(
                year=latest_gift_date.year + 3, day=28
            )
        return (
            EngagementStatus.ACTIVE
            if as_of_date <= third_anniversary
            else EngagementStatus.LAPSED
        )
    if latest_gift_year is None:
        return EngagementStatus.UNKNOWN
    return (
        EngagementStatus.ACTIVE
        if as_of_date.year - latest_gift_year <= 3
        else EngagementStatus.LAPSED
    )


def _money(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _trace_money(value: Decimal) -> str:
    """Show at least cents while retaining any unrounded extra precision."""

    rendered = format(value, "f")
    if "." not in rendered:
        return rendered + ".00"
    decimals = len(rendered.rsplit(".", 1)[1])
    return rendered + ("0" * max(0, 2 - decimals))


def calculate_recommended_ask(
    financial_tier: FinancialTier | str,
    largest_gift: Decimal | None,
    latest_gift_year: int | None,
    engagement_status: EngagementStatus | str,
    campaign_type: str,
    volunteer: bool,
    as_of_date: date,
) -> AskResult:
    """Calculate the ask in canonical order, rounding exactly once at the end."""

    tier = FinancialTier(financial_tier)
    engagement = EngagementStatus(engagement_status)
    trace: list[str] = []
    review_required = False
    if tier in TIER_RATES and largest_gift is not None:
        rate = TIER_RATES[tier]
        amount = largest_gift * rate
        trace.append(
            f"{tier.value} base: {_trace_money(largest_gift)} × {rate} = {_trace_money(amount)}"
        )
    elif tier == FinancialTier.BRONZE:
        amount = BRONZE_BASE
        trace.append(f"Bronze base: {_trace_money(amount)}")
    else:
        amount = UNKNOWN_BASE
        review_required = True
        trace.append(f"Unknown-data fallback: {_trace_money(amount)}")

    if latest_gift_year == as_of_date.year - 1:
        before = amount
        amount *= LOYALTY_MULTIPLIER
        trace.append(
            f"Prior-year adjustment: {_trace_money(before)} × {LOYALTY_MULTIPLIER} = {_trace_money(amount)}"
        )
    if engagement == EngagementStatus.LAPSED:
        before = amount
        amount *= LAPSED_MULTIPLIER
        trace.append(
            f"Lapsed adjustment: {_trace_money(before)} × {LAPSED_MULTIPLIER} = {_trace_money(amount)}"
        )
    if campaign_type.strip().casefold() == "emergency appeal":
        before = amount
        amount *= EMERGENCY_MULTIPLIER
        trace.append(
            f"Emergency adjustment: {_trace_money(before)} × {EMERGENCY_MULTIPLIER} = {_trace_money(amount)}"
        )
    if volunteer:
        before = amount
        amount += VOLUNTEER_ADDITION
        trace.append(
            f"Volunteer adjustment: {_trace_money(before)} + {_trace_money(VOLUNTEER_ADDITION)} = {_trace_money(amount)}"
        )
    bounded = min(max(amount, MINIMUM_ASK), MAXIMUM_ASK)
    if bounded != amount:
        trace.append(f"Policy bounds: {_trace_money(amount)} → {_trace_money(bounded)}")
    # ROUND_HALF_UP makes an exact $25 midpoint move to the higher $50 increment.
    rounded = (
        (bounded / ROUNDING_INCREMENT).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        * ROUNDING_INCREMENT
    )
    trace.append(f"Final rounded ask: {_money(rounded)}")
    return AskResult(rounded, tuple(trace), review_required)


def _truthy(value: Any) -> bool:
    return str(value).strip().casefold() in {"1", "true", "yes", "y"}


def evaluate_suppression(record: Mapping[str, Any]) -> SuppressionResult:
    normalized = normalize_record(record)
    reasons: list[str] = []
    if _truthy(normalized.get("do_not_contact")):
        reasons.append("do_not_contact")
    status = str(normalized.get("communication_status", "")).strip().casefold()
    if status in {"opted_out", "opted out", "suppressed"}:
        reasons.append(status.replace(" ", "_"))
    if _truthy(normalized.get("deceased")):
        reasons.append("deceased")
    consent_warning = "do_not_contact" not in normalized and not status
    return SuppressionResult(bool(reasons), tuple(reasons), consent_warning)


def _warning(code: str, **details: Any) -> dict[str, Any]:
    return {"code": code, **details}


def _parse_optional_money(
    value: Any, field: str, warnings: list[dict[str, Any]]
) -> Decimal | None:
    if value is None or not str(value).strip():
        return None
    try:
        return parse_money(value)
    except DonorPolicyError as exc:
        warnings.append(_warning("INVALID_SUMMARY", field=field, reason=str(exc)))
        return None


def _parse_optional_year(value: Any, warnings: list[dict[str, Any]]) -> int | None:
    if value is None or not str(value).strip():
        return None
    try:
        year = int(str(value).strip())
        if year < 1900 or year > 9999:
            raise ValueError
        return year
    except ValueError:
        warnings.append(_warning("INVALID_SUMMARY", field="Last Gift Year"))
        return None


def reconcile_donor_record(
    record: Mapping[str, Any], as_of_date: date, campaign_type: str
) -> dict[str, Any]:
    """Reconcile one donor record and return a compact JSON-ready result."""

    normalized = normalize_record(record)
    warnings: list[dict[str, Any]] = []
    if any(
        isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@"))
        for value in normalized.values()
    ):
        warnings.append(_warning("SPREADSHEET_FORMULA_PREFIX"))
    donor_label = str(
        normalized.get("donor_id") or normalized.get("donor_name") or "Unidentified donor"
    ).strip()
    history = parse_gift_history(normalized.get("gifts"))
    supplied_total = _parse_optional_money(
        normalized.get("lifetime_total"), "Lifetime Total", warnings
    )
    supplied_largest = _parse_optional_money(
        normalized.get("largest_gift"), "Largest Gift", warnings
    )
    supplied_year = _parse_optional_year(normalized.get("last_gift_year"), warnings)

    if history.complete:
        lifetime = calculate_lifetime_total(history.gifts)
        largest = calculate_largest_gift(history.gifts)
        latest_year = calculate_latest_gift_year(history.gifts)
        latest_dates = [gift.gift_date for gift in history.gifts if gift.gift_date]
        latest_date = max(latest_dates) if latest_dates else None
        for code, supplied, calculated in (
            ("LIFETIME_TOTAL_CONFLICT", supplied_total, lifetime),
            ("LARGEST_GIFT_CONFLICT", supplied_largest, largest),
            ("LATEST_GIFT_YEAR_CONFLICT", supplied_year, latest_year),
        ):
            if supplied is not None and supplied != calculated:
                warnings.append(
                    _warning(
                        code,
                        supplied=_money(supplied) if isinstance(supplied, Decimal) else supplied,
                        calculated=_money(calculated)
                        if isinstance(calculated, Decimal)
                        else calculated,
                    )
                )
    else:
        lifetime, largest, latest_year, latest_date = (
            supplied_total,
            supplied_largest,
            supplied_year,
            None,
        )
        if normalized.get("gifts"):
            warnings.append(
                _warning("INCOMPLETE_GIFT_HISTORY", reasons=list(history.errors))
            )
        if any(value is not None for value in (lifetime, largest, latest_year)):
            warnings.append(_warning("SUMMARY_FALLBACK_USED"))

    financial_tier = calculate_financial_tier(lifetime)
    engagement = calculate_engagement_status(latest_year, as_of_date, latest_date)
    supplied_tier = str(normalized.get("tier", "")).strip()
    if supplied_tier.casefold() == "lapsed":
        engagement = EngagementStatus.LAPSED
        warnings.append(_warning("LEGACY_LAPSED_AS_ENGAGEMENT"))
    elif supplied_tier and supplied_tier.casefold() in {
        "platinum",
        "gold",
        "silver",
        "bronze",
    } and supplied_tier.casefold() != financial_tier.value.casefold():
        warnings.append(
            _warning(
                "TIER_CONFLICT",
                supplied=supplied_tier,
                calculated=financial_tier.value,
            )
        )

    suppression = evaluate_suppression(record)
    if suppression.consent_warning:
        warnings.append(_warning("CONSENT_STATUS_MISSING"))
    volunteer = _truthy(normalized.get("volunteer"))
    ask = calculate_recommended_ask(
        financial_tier,
        largest,
        latest_year,
        engagement,
        campaign_type,
        volunteer,
        as_of_date,
    )
    if ask.review_required:
        warnings.append(_warning("UNKNOWN_DATA_ASK_FALLBACK"))

    status = "suppressed" if suppression.suppressed else (
        "review_required" if warnings else "ok"
    )
    return {
        "donor_label": donor_label,
        "status": status,
        "financial_tier": financial_tier.value,
        "engagement_status": engagement.value,
        "calculated_lifetime_total": _money(lifetime) if lifetime is not None else None,
        "calculated_largest_gift": _money(largest) if largest is not None else None,
        "calculated_latest_gift_year": latest_year,
        "recommended_ask": None if suppression.suppressed else _money(ask.amount),
        "suppressed": suppression.suppressed,
        "suppression_reasons": list(suppression.reasons),
        "warnings": warnings,
        "calculation_trace": [] if suppression.suppressed else list(ask.trace),
        "policy_version": POLICY_VERSION,
    }
