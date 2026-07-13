from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

Currency = Literal["USD"]
FinancialTier = Literal["bronze", "silver", "gold", "platinum"]
EngagementStatus = Literal["active", "lapsed", "never_gave"]


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Money(DomainModel):
    amount: Decimal = Field(ge=0)
    currency: Currency = "USD"

    @field_validator("amount")
    @classmethod
    def finite_amount(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("money amount must be finite")
        return value


class Gift(DomainModel):
    gift_id: str = Field(min_length=1, max_length=100)
    date: date
    amount: Money
    description: str | None = Field(default=None, max_length=500)


class RelationshipManager(DomainModel):
    manager_id: str
    display_name: str
    title: str


class MatchOffer(DomainModel):
    status: Literal["confirmed", "unconfirmed", "expired", "none"] = "none"
    ratio: Decimal | None = Field(default=None, gt=0)
    expires_on: date | None = None


class CampaignClaim(DomainModel):
    claim_id: str
    text: str = Field(min_length=1, max_length=500)
    status: Literal["approved", "pending", "rejected"]
    category: Literal["impact", "urgency", "match", "offer", "event", "general"]


class DonorInput(DomainModel):
    donor_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
    first_name: str | None = Field(default=None, max_length=100)
    preferred_name: str | None = Field(default=None, max_length=100)
    preferred_salutation: str | None = Field(default=None, max_length=150)
    household_id: str | None = Field(default=None, max_length=100)
    household_primary: bool = True
    gifts: list[Gift] = Field(default_factory=list)
    volunteer: bool = False
    do_not_contact: bool = False
    communication_status: Literal["opted_in", "unknown", "opted_out"] = "unknown"
    deceased: bool = False
    supplied_lifetime_total: Money | None = None
    supplied_largest_gift: Money | None = None
    supplied_last_gift_date: date | None = None
    supplied_tier: FinancialTier | None = None


class TypedWarning(DomainModel):
    code: str
    message: str
    expected: str | None = None
    supplied: str | None = None
    material: bool = False


class NormalizedDonor(DomainModel):
    donor_id: str
    first_name: str | None = None
    preferred_name: str | None = None
    preferred_salutation: str | None = None
    household_id: str | None = None
    household_primary: bool = True
    gifts: list[Gift]
    volunteer: bool
    do_not_contact: bool
    communication_status: Literal["opted_in", "unknown", "opted_out"]
    deceased: bool
    lifetime_giving: Money
    largest_gift: Money
    most_recent_gift_date: date | None
    warnings: list[TypedWarning] = Field(default_factory=list)


class Campaign(DomainModel):
    campaign_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
    name: str
    charity_name: str
    campaign_type: Literal["annual_fund", "emergency", "capital", "event"]
    as_of_date: date
    donation_url: HttpUrl
    currency: Currency = "USD"
    claims: list[CampaignClaim] = Field(default_factory=list)
    match: MatchOffer = Field(default_factory=MatchOffer)
    relationship_manager: RelationshipManager | None = None


class EligibilityResult(DomainModel):
    eligible: bool
    reason_codes: list[str] = Field(default_factory=list)
    requires_review: bool = False


class SegmentationResult(DomainModel):
    financial_tier: FinancialTier
    engagement_status: EngagementStatus
    policy_version: str


class CalculationStep(DomainModel):
    operation: str
    input_amount: Decimal
    value: Decimal | None = None
    output_amount: Decimal
    reason: str


class AskCalculationTrace(DomainModel):
    amount: Decimal
    currency: Currency
    calculation_trace: list[CalculationStep]
    policy_version: str


class ApprovedFact(DomainModel):
    key: str
    value: str
    source: Literal["gift_transactions", "normalized_donor", "campaign", "policy"]


class FactBundle(DomainModel):
    donor_id: str
    campaign_id: str
    salutation: str
    ask: Money
    financial_tier: FinancialTier
    engagement_status: EngagementStatus
    facts: list[ApprovedFact]
    claims: list[CampaignClaim]


class NarrativeDraft(DomainModel):
    subject: str = Field(max_length=150)
    opening: str = Field(max_length=1000)
    campaign_paragraph: str = Field(max_length=1500)
    ask_paragraph: str = Field(max_length=1000)


class LetterDraft(DomainModel):
    subject: str
    html: str
    plain_text: str


class GenerationResult(DomainModel):
    donor_id: str
    campaign_id: str
    status: Literal["draft_generated", "suppressed", "failed"]
    financial_tier: FinancialTier | None = None
    engagement_status: EngagementStatus | None = None
    recommended_ask: AskCalculationTrace | None = None
    personalization_facts_used: list[str] = Field(default_factory=list)
    campaign_claims_used: list[str] = Field(default_factory=list)
    warnings: list[TypedWarning] = Field(default_factory=list)
    letter: LetterDraft | None = None
    approval_status: Literal["requires_review"] = "requires_review"
    policy_version: str
    template_version: str
    model_identifier: str
    idempotency_key: str
    suppression_reasons: list[str] = Field(default_factory=list)


class RunManifest(DomainModel):
    run_id: str
    campaign_id: str
    policy_version: str
    template_version: str
    provider: str
    status: Literal["created", "running", "completed", "completed_with_errors", "failed"]
    created_at: datetime
    updated_at: datetime


class RunSummary(DomainModel):
    run_id: str
    total: int
    generated: int
    suppressed: int
    failed: int
    duplicates_skipped: int
    retries: int
    schema_valid_output_rate: Decimal
    human_review_rate: Decimal
