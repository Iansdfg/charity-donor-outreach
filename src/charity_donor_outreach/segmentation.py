from datetime import date
from decimal import Decimal
from typing import Any, cast

from .models import EngagementStatus, FinancialTier, NormalizedDonor, SegmentationResult


def financial_tier(amount: Decimal, policy: dict[str, Any]) -> FinancialTier:
    tiers = policy["tiers"]
    if amount >= Decimal(str(tiers["platinum"]["minimum"])):
        return "platinum"
    if amount >= Decimal(str(tiers["gold"]["minimum"])):
        return "gold"
    if amount >= Decimal(str(tiers["silver"]["minimum"])):
        return "silver"
    return "bronze"


def engagement_status(
    last_gift: date | None, as_of: date, policy: dict[str, Any]
) -> EngagementStatus:
    if last_gift is None:
        return "never_gave"
    if (as_of - last_gift).days > int(policy["lapsed_after_days"]):
        return "lapsed"
    return "active"


def segment(donor: NormalizedDonor, as_of: date, policy: dict[str, Any]) -> SegmentationResult:
    return SegmentationResult(
        financial_tier=financial_tier(donor.lifetime_giving.amount, policy),
        engagement_status=engagement_status(donor.most_recent_gift_date, as_of, policy),
        policy_version=cast(str, policy["version"]),
    )
