from typing import Any

from .errors import OutputValidationError
from .models import Campaign, CampaignClaim


def approved_claims(campaign: Campaign, policy: dict[str, Any]) -> list[CampaignClaim]:
    result = []
    allowed = set(policy["allowed_categories"])
    for claim in campaign.claims:
        if claim.status != "approved" or claim.category not in allowed:
            continue
        if claim.category == "match" and campaign.match.status != "confirmed":
            continue
        result.append(claim)
    return sorted(result, key=lambda item: item.claim_id)


def validate_claims(text: str, used: list[CampaignClaim], policy: dict[str, Any]) -> None:
    lowered = text.lower()
    approved_text = " ".join(claim.text.lower() for claim in used)
    for phrase in policy["forbidden_without_approved_claim"]:
        if phrase.lower() in lowered and phrase.lower() not in approved_text:
            raise OutputValidationError(f"unsupported claim phrase: {phrase}")
    if any(word in lowered for word in ("matched", "matching gift", "match your gift")):
        if not any(claim.category == "match" for claim in used):
            raise OutputValidationError(
                "matching language requires an approved confirmed match claim"
            )
