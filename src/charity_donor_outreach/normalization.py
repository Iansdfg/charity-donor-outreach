from decimal import Decimal

from .models import DonorInput, Money, NormalizedDonor


def normalize_donor(donor: DonorInput) -> NormalizedDonor:
    gifts = sorted(donor.gifts, key=lambda gift: (gift.date, gift.gift_id))
    total = sum((gift.amount.amount for gift in gifts), start=Decimal("0"))
    largest = max((gift.amount.amount for gift in gifts), default=Decimal("0"))
    latest = max((gift.date for gift in gifts), default=None)
    return NormalizedDonor(
        donor_id=donor.donor_id,
        first_name=donor.first_name,
        preferred_name=donor.preferred_name,
        preferred_salutation=donor.preferred_salutation,
        household_id=donor.household_id,
        household_primary=donor.household_primary,
        gifts=gifts,
        volunteer=donor.volunteer,
        do_not_contact=donor.do_not_contact,
        communication_status=donor.communication_status,
        deceased=donor.deceased,
        lifetime_giving=Money(amount=total),
        largest_gift=Money(amount=largest),
        most_recent_gift_date=latest,
    )
