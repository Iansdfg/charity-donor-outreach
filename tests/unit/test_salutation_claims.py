from charity_donor_outreach.claims import approved_claims
from charity_donor_outreach.eligibility import safe_salutation
from charity_donor_outreach.models import CampaignClaim, MatchOffer
from charity_donor_outreach.normalization import normalize_donor
from tests.conftest import make_donor


def test_salutation_precedence_and_no_inference():
    assert (
        safe_salutation(normalize_donor(make_donor(preferred_salutation="Greetings friend")))
        == "Greetings friend,"
    )
    assert (
        safe_salutation(normalize_donor(make_donor(preferred_name="李雷", first_name="Robert")))
        == "Dear 李雷,"
    )
    assert safe_salutation(normalize_donor(make_donor(first_name="Sasha"))) == "Dear Sasha,"
    assert safe_salutation(normalize_donor(make_donor(first_name=None))) == "Dear Supporter,"


def test_match_must_be_approved_and_confirmed(policies, campaign):
    claim = CampaignClaim(
        claim_id="m", text="Gifts will be matched.", status="approved", category="match"
    )
    unconfirmed = campaign.model_copy(
        update={"claims": [claim], "match": MatchOffer(status="unconfirmed", ratio=1)}
    )
    confirmed = campaign.model_copy(
        update={"claims": [claim], "match": MatchOffer(status="confirmed", ratio=1)}
    )
    assert approved_claims(unconfirmed, policies.claims) == []
    assert approved_claims(confirmed, policies.claims) == [claim]
