# Findings

## Specification

- Required helper files: `scripts/donor_policy.py`, `scripts/calculate_donor.py`, `scripts/validate_repository.py`.
- Required executable suites: policy, CLI, integrity, and template safety using only `unittest`.
- Existing Markdown rubric must remain.
- Deterministic assistance is opt-in and offered once for batches, conflicts, calculations, tier filters, high-value donors, audit requests, or larger inputs.
- Successful helper output is authoritative only for arithmetic, classification, reconciliation, suppression, and traces; claims, prose, HTML, consent, and legal review remain outside its trust boundary.

## Repository Audit

- Current repository has no executable runtime or CI; only Markdown test cases and rubric exist.
- Canonical current policy is split between `references/ask-calculation.md`, `references/donor-segmentation.md`, `references/input-validation.md`, and `references/safety-and-compliance.md`.
- The legacy requirement intentionally contains obsolete/unsafe rules and must not become executable policy.
- Gift CSV header is `Gifts (Year: Amount)` while `SKILL.md` also describes the legacy alias `Gifts`; normalized field matching must support both.
- Complete gift history outranks supplied summaries. Incomplete history may fall back to supplied summary values with warnings.
- Engagement by year: latest year within three calendar years of `as_of_date` is Active; older is Lapsed.
- Ask order and constants are defined once in `donor_policy.py`; documentation remains the human-readable canonical policy and consistency tests will pin key values.
- Template already meets core accessibility/layout requirements and has a finite documented placeholder set.
- Existing README currently says no Python is required; retain that statement while documenting optional deterministic assistance.
- `docs/DESIGN_DECISIONS.md` says there is no executable runtime and will need a narrow update acknowledging the optional helper without changing runtime requirements.
