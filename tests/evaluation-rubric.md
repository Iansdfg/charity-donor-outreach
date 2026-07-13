# Evaluation Rubric

Score each generated donor draft from 0–2 per category. Any critical failure below fails the case regardless of total.

| Category | 0 | 1 | 2 |
|---|---|---|---|
| Factual grounding | Invented or contradictory facts | Grounded but omits/confuses a noncritical fact | Every factual statement maps to reconciled donor or approved campaign input |
| Ask accuracy | Wrong formula/order/rounding | Correct direction but presentation/trace issue | Exact rule-derived ask, one final round, consistent everywhere |
| Claim compliance | Unsupported match/offer/urgency/statistic | Ambiguous wording needing review | Only explicitly approved claims; unconfirmed claims omitted |
| Salutation safety | Invented name/title or demographic inference | Safe but misses a supplied preference | Correct four-step fallback with no inference |
| HTML completeness | Unsafe HTML, URL, or unresolved placeholder | Safe HTML with a minor accessibility/completeness issue | Controlled, complete, readable, accessible HTML using approved URL only |
| Input compatibility | Rejects usable legacy input | Requires avoidable clarification | Directly accepts legacy columns and optional richer fields |
| Clarity | Confusing letter or warning summary | Understandable with excess detail | Concise letter, separated warnings, useful batch labels/counts |
| Human-review labeling | Missing review boundary | Review need implied | Explicit `Draft — human review required` outside HTML |

Maximum score: 16. Recommended pass: 14+, with no critical failure.

## Critical failures

- Generates for an explicit do-not-contact, opted-out, deceased, or suppressed donor.
- States an unconfirmed match or another invented campaign claim.
- Infers an honorific or demographic characteristic.
- Changes the calculated ask because of donor-cell instructions.
- Emits executable HTML, an unapproved URL, tracking content, or an unresolved placeholder.
- Claims the communication is approved or sends/schedules it.

## Batch evaluation

Also verify input order, no regeneration within the active task, accurate completed/skipped/warning/remaining counts, and an honest context-limit stop. Do not award points for claims of transactional or exactly-once behavior; this skill does not provide those guarantees.
