from __future__ import annotations

from .models import DonorInput, NormalizedDonor, SegmentationResult, TypedWarning


def reconcile(
    supplied: DonorInput, normalized: NormalizedDonor, segment: SegmentationResult
) -> NormalizedDonor:
    warnings: list[TypedWarning] = []
    comparisons = [
        ("lifetime_total_mismatch", normalized.lifetime_giving, supplied.supplied_lifetime_total),
        ("largest_gift_mismatch", normalized.largest_gift, supplied.supplied_largest_gift),
    ]
    for code, calculated, given in comparisons:
        if given is not None and given != calculated:
            warnings.append(
                TypedWarning(
                    code=code,
                    message="supplied summary conflicts with gift transactions",
                    expected=str(calculated.amount),
                    supplied=str(given.amount),
                    material=True,
                )
            )
    if (
        supplied.supplied_last_gift_date is not None
        and supplied.supplied_last_gift_date != normalized.most_recent_gift_date
    ):
        warnings.append(
            TypedWarning(
                code="last_gift_date_mismatch",
                message="supplied date conflicts with gift transactions",
                expected=str(normalized.most_recent_gift_date),
                supplied=str(supplied.supplied_last_gift_date),
                material=True,
            )
        )
    if supplied.supplied_tier is not None and supplied.supplied_tier != segment.financial_tier:
        warnings.append(
            TypedWarning(
                code="tier_mismatch",
                message="supplied tier conflicts with calculated lifetime giving",
                expected=segment.financial_tier,
                supplied=supplied.supplied_tier,
                material=True,
            )
        )
    if not normalized.gifts:
        warnings.append(
            TypedWarning(
                code="missing_gift_history",
                message="no validated gift transactions supplied",
                material=False,
            )
        )
    return normalized.model_copy(update={"warnings": warnings})
