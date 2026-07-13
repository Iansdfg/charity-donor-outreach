# Findings

## Legacy Skill Problems
- Activation is over-broad and can trigger for unrelated money, communication, event, or reporting tasks.
- Mock donor PII-like records are embedded directly in instructions and keyed by names rather than stable IDs.
- Supplied tiers and totals conflict (for example, several donors labeled Silver calculate as Gold), with no source-of-truth or warning model.
- `lapsed` is incorrectly modeled as a financial tier.
- Ask ordering, midpoint rounding, caps, missing-history behavior, and lapsed/high-value interaction are ambiguous.
- The prompt directs fabrication of matches, deadlines/urgency, naming opportunities, tote bags, event counts, and relationship managers.
- Salutations direct gender/title inference from names.
- Missing data is handled by guessing.
- No consent/suppression controls, structured output, human review, durable batch state, evaluation, or observability.
- Raw HTML templating creates injection and unsafe-link risks and cannot safely scale.

## Ambiguous Business Rules Resolved
- Engagement becomes lapsed when the latest gift is more than 1,095 days before campaign `as_of_date`.
- Tier boundaries are Bronze `<1000`, Silver `1000–9999.99`, Gold `10000–49999.99`, Platinum `>=50000`.
- Missing/zero gift history remains Bronze but creates review warnings; ask policy uses the Bronze base.
- Ask adjustments execute base/multiplier, percentage adjustments, fixed adjustments, caps, then one final half-up rounding.
- Lapsed status applies a percentage reduction while preserving the financial tier; high-value donors are never collapsed to a flat restart ask.
- Only USD is supported initially.

## Security and Compliance Risks
- All CSV cells, donor names, campaign facts, and provider prose are untrusted.
- Suppressed donors must be rejected before any provider call.
- Free-form notes are excluded from fact bundles.
- Claims require registry approval; matching language additionally requires a confirmed match.
- Formula-prefixed CSV fields, unsafe URLs, scripts, handlers, iframes, tracking pixels, and unresolved placeholders fail closed.
- Logs and audit records should use donor IDs, not unnecessary names/contact details.

## Source of Truth
1. Validated gift transactions.
2. Versioned policy configuration.
3. Normalized donor fields.
4. Supplied summaries for comparison only.

## Design Tradeoffs
- File-based JSONL storage favors portability and inspectability over multi-host coordination; a database/object-store ledger is recommended for distributed production.
- Conservative output validation may reject benign prose containing restricted claim terms; reviewable false positives are preferred to unsupported claims.
- The offline fake produces bounded narrative fields rather than HTML, keeping templates authoritative.

## Test Findings
- Final offline suite: 46 tests passed with 86% line coverage.
- Ruff lint and format checks pass; mypy reports no issues across 37 source files.
- Security testing caught and fixed `.html.j2` autoescape suffix behavior.
- Restart produced three duplicate skips and no duplicate result/review lines.
- Annual example produced two drafts, one suppression, zero failures; all drafts require review.
- Unconfirmed emergency match produced no match language.
- Artifact scan found no scripts, handlers, iframes, inferred honorifics, unauthorized match language, or unresolved placeholders.
- Git commits could not be made because the provided workspace is not a Git repository.
