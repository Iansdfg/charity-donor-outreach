# Legacy Skill Assessment

## Strengths

The original artifact recognized useful concepts: transaction history, tiers, campaign-aware prose, ask calculations, salutations, and HTML output. It was direct enough to prototype expected behavior.

## Risks and changes

| Legacy issue | Change | Expected impact |
|---|---|---|
| Activation covered nearly any money, email, charity, event, report, grant, or outreach task | Narrow activation to authorized donor-draft requests | Fewer accidental disclosures and inappropriate runs |
| Mock donor table embedded in instructions and keyed by name | Move mock data to examples and require stable IDs | Avoids name collisions and prompt/data coupling |
| No source-of-truth precedence | Gift transactions > versioned policy > normalized fields > supplied summaries | Reproducible values and visible conflicts |
| Inconsistent supplied tiers/totals | Recalculate and emit typed material warnings | Prevents silent bad asks |
| Lapsed treated as a tier | Separate financial tier and engagement status | Preserves high-value context without conflation |
| Ambiguous ask order/rounding and missing-data behavior | Decimal policy pipeline with one final round, caps, and explicit Bronze fallback | Exact, testable asks |
| Directed fabricated match language | Approved registry plus confirmed-match gate | Eliminates unsupported matching claims |
| Invented naming, tote bags, event counts, urgency, managers | Require approved claims/facts | Grounds every offer and identity |
| Guessed gendered honorifics | Safe explicit fallback chain only | Prevents demographic inference and misgendering |
| “Make assumptions” for missing values | Fail closed or warn/review | Makes uncertainty visible |
| No suppression or consent controls | Evaluate DNC, opt-out, deceased, household duplicate, and conflicts first | Prevents provider calls for suppressed donors |
| Raw HTML interpolation | Autoescape, controlled templates, URL/content validation | Reduces HTML/script/tracking injection |
| One in-chat batch | Atomic JSONL state, idempotency, isolated failures, resume | Scales reliably on one host |
| No structured result | Pydantic models and JSON Schemas | Machine-verifiable downstream contract |
| No human review | Every success is `requires_review` | Prevents autonomous use |
| No evaluation/observability | Offline tests, release gates, summaries, structured audit context | Detects regressions and supports operations |

