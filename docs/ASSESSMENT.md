# Assessment

## Why the original skill needed improvement

The legacy prompt had a useful direct interaction model—upload donor data and receive HTML letters—but activated too broadly, embedded mock donor records, treated names as identifiers, conflated Lapsed with financial tier, and left ask order and missing data ambiguous. It explicitly encouraged fabricated matches, urgency, offers, event counts, naming opportunities, relationship managers, and gendered honorific guesses. It lacked suppression, consent, injection, HTML-safety, batching, review, and evaluation guidance.

## Why the final design is prompt-native

The requested artifact is a portable Agent Skill, not an application. `SKILL.md`, six focused references, legacy-compatible mock data, and controlled templates are sufficient for an installed agent to read input, reason through rules, calculate asks, and return HTML in chat. Removing the Python package eliminates interpreter, dependency, CLI, provider, and setup requirements and restores the original ease of use.

## Instruction-level safeguards

The final workflow explicitly defines source precedence, conflict warnings, separate tier/engagement classification, exact ask ordering, approved-claim gates, confirmed-match requirements, salutation fallbacks, suppression behavior, prompt-injection resistance, HTML restrictions, bounded batching, and mandatory review. Portable cases make expected behavior inspectable without a test runtime.

## Honest limitations

Instructions are not deterministic code. The model can make arithmetic, parsing, omission, or compliance mistakes; HTML is checklist-reviewed rather than parser-sanitized; batching is context-bound rather than transactional; and the skill provides no immutable audit log or delivery enforcement. These tradeoffs are why every output is a draft requiring human review.

An organization may optionally add deterministic consent, validation, calculation, auditing, approval, and delivery controls in its host application. Those systems are outside this portable skill and are not required for installation.

