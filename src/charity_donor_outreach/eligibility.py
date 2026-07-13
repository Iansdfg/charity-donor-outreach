from typing import Any

from .models import EligibilityResult, NormalizedDonor


def evaluate_eligibility(donor: NormalizedDonor, policy: dict[str, Any]) -> EligibilityResult:
    reasons: list[str] = []
    suppression = policy["suppress"]
    if donor.do_not_contact and suppression["do_not_contact"]:
        reasons.append("do_not_contact")
    if donor.communication_status == "opted_out" and suppression["opted_out"]:
        reasons.append("communication_opted_out")
    if donor.deceased and suppression["deceased"]:
        reasons.append("deceased")
    if not donor.household_primary and suppression["household_duplicate"]:
        reasons.append("household_duplicate")
    material = any(warning.material for warning in donor.warnings)
    if material and suppression["material_conflict"]:
        reasons.append("unresolved_material_conflict")
    if policy.get("require_opt_in") and donor.communication_status != "opted_in":
        reasons.append("explicit_opt_in_required")
    return EligibilityResult(eligible=not reasons, reason_codes=reasons, requires_review=material)


def safe_salutation(donor: NormalizedDonor) -> str:
    if donor.preferred_salutation:
        value = donor.preferred_salutation.rstrip()
        return value if value.endswith((",", "!")) else f"{value},"
    if donor.preferred_name:
        return f"Dear {donor.preferred_name},"
    if donor.first_name:
        return f"Dear {donor.first_name},"
    return "Dear Supporter,"
