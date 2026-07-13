# Design Decisions

## Portable over application-like

The repository contains no executable runtime. The agent uses file reading, reasoning, arithmetic, and writing already available in the host. Policy is Markdown because it is the clearest portable execution format across Agent Skills-compatible runtimes.

## Legacy compatibility

Original columns remain first-class. Stable IDs and consent/salutation fields are optional improvements, not migration prerequisites. Semicolon-separated gifts are preferred for unambiguous parsing, while common legacy formats remain accepted.

## Source precedence

Complete parseable gift history outranks written rules, supplied summaries, and safe fallbacks. This preserves user convenience while making conflicts visible. Missing history never causes invented transactions.

## Simple ask policy

The formula retains tier multipliers, Bronze base, loyalty, lapsed, emergency, volunteer, bounds, and nearest-$50 rounding. A fixed order and one final round minimize model arithmetic errors. A $50 review-required fallback handles unknown financial value without claiming history.

## Safety boundaries

Campaign type controls tone, not claim authorization. Matches require confirmation; all special offers/facts require approval. Salutations use explicit fields or neutral fallbacks. Suppressed donors receive no draft. Uploaded text is inert data.

## HTML-first output

Default output remains directly returned HTML, preserving the original contract. A controlled template limits layout variation; plain text is optional. Review labeling remains outside HTML so it cannot be mistaken for donor-facing copy.

## Bounded batching

The skill preserves input order and tracks counts within the active task. It stops before context exhaustion and names remaining records. It does not claim durable resume, transactional state, or exactly-once delivery.
