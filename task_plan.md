# Optional Deterministic Helper Implementation Plan

## Goal

Add a standard-library-only deterministic donor calculator, executable offline tests, optional-mode skill integration, repository validation, CI, and documentation while preserving the dependency-free prompt-native skill.

## Phases

1. **Repository and policy audit** — complete
   - Inspect current files, canonical references, templates, tests, and duplicated policy definitions.
2. **Canonical deterministic policy** — complete
   - Implement `scripts/donor_policy.py` with pure Decimal/date-based reconciliation, classification, suppression, ask, warnings, and traces.
3. **JSON/CSV CLI** — complete
   - Implement `scripts/calculate_donor.py` with ordered JSON output, clean stderr diagnostics, and safe failure behavior.
4. **Skill consent and fallback integration** — complete
   - Update `SKILL.md` with one-time consent, availability/failure handling, trust boundaries, and prompt-native fallback.
5. **Offline tests, fixtures, validation, and CI** — complete
   - Add required unittest suites/fixtures, `scripts/validate_repository.py`, and Python 3.11/3.12 CI.
6. **README and examples** — complete
   - Document optional modes, consent, manual commands, limitations, and standard-library/no-external-transfer properties.
7. **Final verification** — complete
   - Run the full tests, repository validator, CLI help, five representative CLI scenarios, dependency scan, and diff review.

## Constraints

- Keep Python optional and standard-library-only.
- Do not add sending, scheduling, approval, services, databases, package managers, or third-party dependencies.
- Preserve current prompt-native behavior, HTML output, safety rules, synthetic data labeling, and legacy fields.
- Do not duplicate canonical Python constants across modules.

## Errors Encountered

| Error | Attempt | Resolution |
|---|---:|---|
| Two policy tests failed on trace presentation | 1 | Preserve extra Decimal precision in intermediate trace values and inspect the correct pre-round trace line. Arithmetic itself was correct. |
| Repository validator treated `[label](URL)` inside code spans as links | 1 | Strip fenced and inline code before checking prose Markdown links. |
| Adding Python cache ignores replaced existing ignore entries | 1 | Restored all existing `.gitignore` entries and appended cache rules only. |
| Generic skill validator failed because `yaml` is not installed | 1 | Did not add a forbidden runtime dependency; used the passing standard-library `scripts/validate_repository.py` frontmatter/integrity checks instead. |
