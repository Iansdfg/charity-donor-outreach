# Evaluation

Evaluate schema-valid output rate, deterministic ask accuracy, unsupported-claim rate, personalization-grounding rate, suppression violations, unresolved placeholders, duplicate outputs, human-review rate, latency, retry rate, and estimated token usage. Current file summaries calculate core counts, schema-valid success rate, review rate, duplicate skips, and retries; production telemetry should add latency/token estimates without donor prose.

Release gates are 100% ask accuracy, 0 unsupported claims, 0 suppression violations, 0 placeholders, 100% schema-valid successful outputs, 100% human-review status, and passing offline pytest, Ruff, mypy, Schema, YAML, and frontmatter checks. Golden cases assert structure, exact asks, grounded IDs, and claims rather than brittle full prose.

