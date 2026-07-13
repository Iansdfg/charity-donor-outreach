# Task Plan

## Objective
Build a production-oriented, offline-testable `charity-donor-outreach` Python skill repository that deterministically validates, normalizes, reconciles, segments, calculates asks, controls claims, safely renders drafts, and durably processes resumable batches with mandatory human review.

## Scope
- Preserve and assess the legacy skill.
- Implement typed models, JSON Schemas, versioned YAML policies, deterministic business logic, safe drafting/rendering, batch persistence, CLI, tests, documentation, and CI.
- Verify offline quality gates and an end-to-end fake-provider workflow.

## Non-goals
- Sending email or integrating a downstream delivery platform.
- Production donor data, wealth screening, demographic inference, or autonomous approval.
- Letting an LLM decide eligibility, segmentation, financial values, or claims.

## Assumptions
- All included donor/campaign records are mock data.
- USD is the only initially supported currency; other currencies fail closed.
- Campaign `as_of_date` is authoritative for time-relative rules.
- Successful drafts always require human review.
- The fake provider is deterministic and used for offline tests only.

## Architecture Decisions
- Pydantic models at system boundaries; `Decimal` for money.
- Gift transactions outrank policy-derived normalized values, which outrank supplied summaries.
- Financial tier and engagement status are independent dimensions.
- Policy is loaded from versioned YAML; ask arithmetic lives only in `ask_calculator.py`.
- LLM input is a bounded typed fact bundle, never the raw donor record.
- Jinja autoescape plus explicit content/URL/output validation.
- Append-only JSONL records written atomically under a run directory; per-donor idempotency keys support resume.
- No communication-send capability.

## Implementation Phases
| # | Phase | Status |
|---|---|---|
| 1 | Legacy-skill audit and design decisions | complete |
| 2 | Repository scaffolding and typed domain models | complete |
| 3 | Schemas, policy files, validation, and normalization | complete |
| 4 | Reconciliation, eligibility, segmentation, and ask calculation | complete |
| 5 | Approved claims, fact bundles, prompting, and model abstraction | complete |
| 6 | Safe rendering and output validation | complete |
| 7 | Persistent batch workflow, restart, idempotency, and CLI | complete |
| 8 | Unit, integration, security, golden, and restart tests | complete |
| 9 | Documentation and canonical SKILL.md | complete |
| 10 | CI, final quality gates, and completion report | complete |

## Risks
- Ambiguous legacy arithmetic and lapsed behavior require explicit policy choices.
- Model-generated prose may introduce unsupported claims; validation must fail closed.
- JSONL crash consistency and duplicate prevention need careful atomic replacement.
- Local environment may not have Python 3.12 or all development dependencies installed.
- Git metadata is read-only in the managed workspace, which may prevent requested phase commits.

## Errors Encountered
| Error | Attempt | Resolution |
|---|---:|---|
| `python3 -m pytest`: `No module named pytest` | 1 | Create an isolated local virtual environment and install declared development dependencies before rerunning. |
| `git status`: not a Git repository | 1 | Phase commits are impossible in the provided workspace; continue with coherent file phases and document the limitation. |
| Editable install failed because declared `README.md` was not yet present | 1 | Completed package documentation, then repeated the isolated install successfully. |
| Initial test collection imported a nested `conftest.py` marker | 1 | Removed the conflicting marker and made tests a package with explicit shared-fixture imports. |
| Security test exposed Jinja suffix autoescape gap for `.html.j2` | 1 | Force autoescape for every controlled output template and retain explicit unsafe-markup validation. |
| JSONL ordering used idempotency hash rather than donor ID | 1 | Sort atomic records by stable donor ID while deduplicating by idempotency key. |

## Completion Criteria
- Required repository structure and responsibility separation exist.
- Required domain behavior and security controls are exercised by automated tests.
- `ruff check .`, `ruff format --check .`, `mypy src tests`, and `pytest -q` pass.
- JSON Schemas/YAML/frontmatter validate offline.
- Example validate/generate/resume/summarize workflow succeeds without duplicates.
- Generated artifacts contain no suppression violations, unconfirmed match, inferred honorific, unresolved placeholder, script/event handler, unsupported ask, or auto-approved draft.
- Documentation describes architecture, policy decisions, operations, limitations, and human-review boundary.
