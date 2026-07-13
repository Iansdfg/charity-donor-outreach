# Charity Donor Outreach

`charity-donor-outreach` produces policy-governed fundraising **drafts** from mock or authorized donor data. It separates deterministic eligibility, segmentation, ask arithmetic, and claim authorization from optional LLM narrative drafting. Every successful result requires human review; this repository has no send-email function.

## Why replace the legacy prompt?

The legacy skill embedded mock donor records, keyed people by name, guessed honorifics, conflated lapsed engagement with financial value, and directed the model to invent matching gifts, offers, urgency, event counts, and relationship managers. It had no suppression, consent, schema, durable state, or output-safety boundary. The original is preserved at `docs/SKILL_LEGACY_REQUIREMENT.md` and assessed in `docs/ASSESSMENT.md`.

## Architecture and trust boundaries

Untrusted CSV/JSON enters typed validation. Gift transactions are normalized and reconciled against supplied summaries. Versioned policy alone determines suppression, financial tier, engagement, and ask. Only an approved `FactBundle` crosses into the drafting adapter. Narrative fields are escaped into controlled Jinja templates and validated for exact ask, authorized claims/URLs, placeholders, and unsafe markup. Results go to an append-only review queue, never a delivery system.

See `docs/ARCHITECTURE.md`, `docs/DATA_CONTRACTS.md`, and `docs/POLICY_MODEL.md`.

## Quick start

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
charity-donor-outreach validate --donors examples/donors.mock.csv --campaign examples/campaign.annual-fund.json
charity-donor-outreach generate --donors examples/donors.mock.csv --campaign examples/campaign.annual-fund.json --output runs/demo --provider fake
charity-donor-outreach summarize --run runs/demo
```

Inputs use stable `donor_id` values, transaction-level gifts, explicit communication controls, safe salutation fields, and a campaign with an HTTPS donation URL. JSON Schema contracts live under `schemas/`. Outputs include separate financial/engagement segments, a full deterministic calculation trace, used fact/claim IDs, warnings, accessible HTML/plain text, an idempotency key, and `approval_status: requires_review`.

## Restart and policy configuration

Each run atomically maintains complete JSON or JSONL documents under `runs/<run_id>/`. Reusing the same output path recomputes the same idempotency key and skips completed donor/campaign/policy/template combinations. Failed donors remain isolated and independently retryable. File storage is appropriate for one host; use a transactional ledger for distributed workers.

Policy files under `policies/` share one semantic version. Deploy and roll them back as an immutable set. Ask operations are base/multiplier, approved percentages, approved fixed amounts, caps, and exactly one final half-up rounding step.

## Adding a provider

Implement the `DraftingModel` protocol in `llm.py`. Accept only `FactBundle` plus the delimited prompt, return `NarrativeDraft`, enforce timeout behavior, and translate only transient transport/service failures to `TransientProviderError`. Do not pass raw uploads or add business decisions. The optional OpenAI adapter is lazy-imported and needs the `openai` extra and environment variables; offline behavior never needs credentials.

## Testing

```bash
ruff check .
ruff format --check .
mypy src tests
pytest -q
```

CI also validates JSON Schema, YAML, frontmatter, and security tests without external credentials.

## Limitations and review boundary

USD is the only supported currency. File storage is not a distributed lock. The conservative lexical claim validator complements, but does not replace, an organization-specific moderation and approval workflow. Operators must verify donor consent, campaign claims, accessibility, ask appropriateness, and legal requirements before any downstream use. Nothing in this repository constitutes tax or legal advice.

