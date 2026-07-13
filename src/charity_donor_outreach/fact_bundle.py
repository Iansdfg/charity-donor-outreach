from .eligibility import safe_salutation
from .models import (
    ApprovedFact,
    AskCalculationTrace,
    Campaign,
    CampaignClaim,
    FactBundle,
    Money,
    NormalizedDonor,
    SegmentationResult,
)


def build_fact_bundle(
    donor: NormalizedDonor,
    campaign: Campaign,
    segment: SegmentationResult,
    ask: AskCalculationTrace,
    claims: list[CampaignClaim],
) -> FactBundle:
    facts = [
        ApprovedFact(key="charity_name", value=campaign.charity_name, source="campaign"),
        ApprovedFact(key="campaign_name", value=campaign.name, source="campaign"),
        ApprovedFact(key="donation_url", value=str(campaign.donation_url), source="campaign"),
        ApprovedFact(
            key="lifetime_giving",
            value=f"{donor.lifetime_giving.amount:.2f} {donor.lifetime_giving.currency}",
            source="gift_transactions",
        ),
    ]
    if donor.volunteer:
        facts.append(ApprovedFact(key="volunteer", value="true", source="normalized_donor"))
    return FactBundle(
        donor_id=donor.donor_id,
        campaign_id=campaign.campaign_id,
        salutation=safe_salutation(donor),
        ask=Money(amount=ask.amount, currency=ask.currency),
        financial_tier=segment.financial_tier,
        engagement_status=segment.engagement_status,
        facts=facts,
        claims=claims,
    )
