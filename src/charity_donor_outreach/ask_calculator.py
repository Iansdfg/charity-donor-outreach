from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any, cast

from .errors import PolicyError
from .models import (
    AskCalculationTrace,
    CalculationStep,
    Campaign,
    NormalizedDonor,
    SegmentationResult,
)


def _step(
    steps: list[CalculationStep],
    operation: str,
    amount: Decimal,
    value: Decimal,
    output: Decimal,
    reason: str,
) -> Decimal:
    steps.append(
        CalculationStep(
            operation=operation,
            input_amount=amount,
            value=value,
            output_amount=output,
            reason=reason,
        )
    )
    return output


def calculate_ask(
    donor: NormalizedDonor,
    campaign: Campaign,
    segment: SegmentationResult,
    policy: dict[str, Any],
) -> AskCalculationTrace:
    if (
        campaign.currency != policy["currency"]
        or donor.lifetime_giving.currency != campaign.currency
    ):
        raise PolicyError(f"unsupported currency: expected {policy['currency']}")
    steps: list[CalculationStep] = []
    rule = policy["tier_rules"][segment.financial_tier]
    if "base_amount" in rule:
        amount = Decimal(str(rule["base_amount"]))
        steps.append(
            CalculationStep(
                operation="base",
                input_amount=Decimal("0"),
                value=amount,
                output_amount=amount,
                reason=f"{segment.financial_tier} configured base",
            )
        )
    else:
        multiplier = Decimal(str(rule["largest_gift_multiplier"]))
        amount = donor.largest_gift.amount * multiplier
        steps.append(
            CalculationStep(
                operation="multiply",
                input_amount=donor.largest_gift.amount,
                value=multiplier,
                output_amount=amount,
                reason=f"{segment.financial_tier} largest-gift multiplier",
            )
        )
    latest = donor.most_recent_gift_date
    if latest is not None and latest.year == campaign.as_of_date.year - 1:
        pct = Decimal(str(policy["percentage_adjustments"]["prior_calendar_year"]))
        amount = _step(
            steps,
            "percentage_adjustment",
            amount,
            pct,
            amount * (Decimal("1") + pct),
            "gift in prior calendar year",
        )
    if segment.engagement_status == "lapsed":
        pct = Decimal(str(policy["percentage_adjustments"]["lapsed"]))
        amount = _step(
            steps,
            "percentage_adjustment",
            amount,
            pct,
            amount * (Decimal("1") + pct),
            "lapsed engagement reduction",
        )
    if campaign.campaign_type == "emergency":
        pct = Decimal(str(policy["percentage_adjustments"]["emergency"]))
        amount = _step(
            steps,
            "percentage_adjustment",
            amount,
            pct,
            amount * (Decimal("1") + pct),
            "emergency appeal adjustment",
        )
    if donor.volunteer:
        fixed = Decimal(str(policy["fixed_adjustments"]["volunteer"]))
        amount = _step(
            steps, "fixed_adjustment", amount, fixed, amount + fixed, "verified volunteer"
        )
    minimum = Decimal(str(policy["minimum"]))
    maximum = Decimal(str(policy["maximum"]))
    capped = min(max(amount, minimum), maximum)
    if capped != amount:
        amount = _step(steps, "cap", amount, capped, capped, "configured minimum/maximum")
    quantum = Decimal(str(policy["round_to"]))
    rounded = (amount / quantum).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * quantum
    amount = _step(
        steps,
        "round",
        amount,
        quantum,
        rounded.quantize(Decimal("0.01")),
        "single final half-up rounding",
    )
    return AskCalculationTrace(
        amount=amount,
        currency=campaign.currency,
        calculation_trace=steps,
        policy_version=cast(str, policy["version"]),
    )
