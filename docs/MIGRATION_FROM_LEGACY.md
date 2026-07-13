# Migration from the Legacy Skill

## What moved out of SKILL.md

- The embedded 50-record mock donor table moved to `examples/donors.mock.csv`.
- Tier and engagement rules moved to `references/donor-segmentation.md`.
- Exact ask arithmetic and worked examples moved to `references/ask-calculation.md`.
- Campaign tone/claim rules, input parsing, safety, and final review moved to focused references.
- HTML and text layouts moved to `templates/`.

The original requirement remains unchanged at `docs/SKILL_LEGACY_REQUIREMENT.md`.

## Compatible behavior

Users still upload or paste the original donor fields and request a campaign letter. No schema conversion or command is required. The default deliverable remains personalized HTML returned in conversation. Platinum, Gold, Silver, Bronze, volunteer, legacy Lapsed values, campaign types, and core letter placeholders remain supported.

## Intentionally removed behavior

The skill no longer invents matches, urgency, naming opportunities, legacy-giving offers, premiums, event counts, impact claims, or relationship managers. It never guesses titles or gender from names. Lapsed is engagement, not financial value. Missing data uses omission, neutral fallback, review warning, or a request for a critical value—not “reasonable assumptions.”

## Why Python was removed

The intermediate repository became a standalone Python application with dependencies, CLI commands, typed schemas, provider adapters, batch storage, and executable CI. That architecture offered stronger deterministic enforcement but violated the portable skill contract and required setup before normal use. Git history preserves it if an organization needs a reference.

## External production controls

A production organization may still enforce consent/suppression, arithmetic, claim registries, HTML sanitization, audit logging, durable batching, approvals, and delivery in surrounding systems. The dependency-free skill does not offer equivalent guarantees and does not claim to. Human review is required.
