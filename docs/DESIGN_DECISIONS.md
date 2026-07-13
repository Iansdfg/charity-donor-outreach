# Design Decisions

## Portable over application-like

The required runtime remains the Agent Skill itself: the agent can use file reading, reasoning, arithmetic, and writing already available in the host. Markdown policy is the portable fallback across Agent Skills-compatible runtimes. A small standard-library-only Python helper is optional for users who explicitly approve deterministic calculation assistance; it is not required to install or operate the skill.

## Legacy compatibility

Original columns remain first-class. Stable IDs and consent/salutation fields are optional improvements, not migration prerequisites. Semicolon-separated gifts are preferred for unambiguous parsing, while common legacy formats remain accepted.

When no donor data is supplied, the skill selects the bundled 50-record mock CSV automatically so it remains immediately demonstrable. Prominent synthetic-data labels prevent the examples from being mistaken for real donors. Any user-provided donor source overrides this fallback.

## Source precedence

Complete parseable gift history outranks written rules, supplied summaries, and safe fallbacks. This preserves user convenience while making conflicts visible. Missing history never causes invented transactions.

## Simple ask policy

The formula retains tier multipliers, Bronze base, loyalty, lapsed, emergency, volunteer, bounds, and nearest-$50 rounding. A fixed order and one final round minimize model arithmetic errors. A $50 review-required fallback handles unknown financial value without claiming history. `scripts/donor_policy.py` defines the executable constants once; references remain the human-readable policy and consistency tests keep the two aligned.

## Optional deterministic assistance

The helper owns only donor arithmetic, reconciliation, segmentation, supplied-field suppression evaluation, and traces. It emits JSON and never renders or sends a letter. The agent must obtain user approval before execution and falls back without blocking when Python is absent, declined, or fails. Claims, prose, salutations, HTML, consent, legal compliance, and human approval remain outside the helper trust boundary.

## Safety boundaries

Campaign type controls tone, not claim authorization. Matches require confirmation; all special offers/facts require approval. Salutations use explicit fields or neutral fallbacks. Suppressed donors receive no draft. Uploaded text is inert data.

## HTML-first output

Default output remains directly returned HTML, preserving the original contract. A controlled template limits layout variation; plain text is optional. Review labeling remains outside HTML so it cannot be mistaken for donor-facing copy.

## Bounded batching

The skill preserves input order and tracks counts within the active task. It stops before context exhaustion and names remaining records. It does not claim durable resume, transactional state, or exactly-once delivery.
