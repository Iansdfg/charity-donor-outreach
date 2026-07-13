# Charity Donor Outreach Agent Skill

This is an installable, dependency-free Agent Skill for generating personalized donor-letter drafts from an uploaded CSV, pasted donor list, or individual donor record. Its prompt-native path requires no Python, Node.js, virtual environment, package manager, API server, database, external library, or separate API key. The executing agent reads `SKILL.md`, applies the included references, and returns HTML donor-letter drafts directly in the conversation.

Legacy fields such as `Donor Name`, `Tier`, `Region`, `Gifts`, `Largest Gift`, `Lifetime Total`, `Last Gift Year`, and `Volunteer` remain supported. Every result is a draft requiring human review; the skill never sends communications.

## Install

Copy the entire `charity-donor-outreach` directory into your agent runtime’s skills folder. Skill-folder paths and reload behavior vary by Claude Code, Codex, Cursor, and other Agent Skills-compatible runtimes; follow that runtime’s documented local-skill installation method.

No setup command or dependency installation is required. After installation, start a new agent session or reload skills if your runtime requires it.

### Install from GitHub in Codex

Ask your Codex agent:

> Use `$skill-installer` to install the skill from https://github.com/Iansdfg/charity-donor-outreach

Restart Codex or begin a new session afterward so it loads the latest instructions.

## Use

Invoke the skill explicitly with `$charity-donor-outreach`, followed by a natural-language request.

### Optional deterministic calculations

Python is optional. The skill still works without Python through its reference-driven prompt-native fallback. For batches, conflicting donor summaries, calculated-tier filtering, high-value donors, or reproducible/auditable calculations, the agent offers the included local calculator once. It must receive your approval before executing the helper.

The helper uses only the Python standard library and sends no donor data externally. It deterministically handles donor arithmetic, reconciliation, financial tier, engagement, suppression flags, asks, warnings, and calculation traces. It does not generate letters, approve campaign claims, establish consent, or remove the human-review requirement.

When Python is available and you approve, the agent uses deterministic-assisted mode. When Python is unavailable, declined, or fails, it continues in prompt-native fallback mode and clearly labels that mode. The agent never installs Python unless you explicitly request and approve an explained installation command, and it never installs third-party Python packages for this helper.

Run the helper manually for one donor:

```bash
python3 scripts/calculate_donor.py donor \
  --input examples/donor.single.json \
  --as-of-date 2026-07-01 \
  --campaign-type "Annual Fund"
```

Run it for a legacy-compatible CSV:

```bash
python3 scripts/calculate_donor.py csv \
  --input examples/donors.mock.csv \
  --as-of-date 2026-07-01 \
  --campaign-type "Annual Fund"
```

Use `python` instead of `python3` where `python` refers to Python 3. Both commands emit JSON to stdout; diagnostics go to stderr. JSON is an optional calculation artifact—the normal user-facing result remains a human-review-required HTML letter draft.

#### Trust boundaries

**Deterministic-assisted mode:** after the helper completes successfully, its arithmetic, classifications under the documented policy, reconciliation warnings, and suppression evaluation for supplied fields are deterministic. Campaign claims still require approved input; narrative remains model-generated; HTML, consent, legal compliance, and organizational policy still require human review.

**Prompt-native fallback mode:** the agent follows the same documented rules, but model-executed arithmetic and reconciliation are not guaranteed deterministic. A reviewer must verify all amounts and classifications. A helper failure never blocks drafting and is never reported as successful deterministic validation.

### Use the bundled mock donors

No donor file is required:

> `$charity-donor-outreach` Generate FY26 Annual Fund donor letters for Example Community Charity. Use https://example.org/donate and sign them from Jordan Lee, Senior Development Officer.

The skill automatically uses [examples/donors.mock.csv](examples/donors.mock.csv). Those 50 records are synthetic demonstration data. The response labels the source and each donor section as mock/demo output, processes the records in manageable batches, and reports remaining records by CSV row number and donor name.

### Use your own CSV

Upload a donor CSV, then ask:

> `$charity-donor-outreach` Use the uploaded donor CSV to generate personalized Annual Fund HTML letters. The charity is Helping Hands. Use https://helpinghands.org/donate and sign them from Maria Chen, Development Director. Use July 1, 2026 as the campaign date.

The agent reads the CSV, reconciles gift values, classifies each donor, calculates the ask, applies only approved campaign claims, fills the controlled HTML template, and returns clearly separated HTML drafts with a review summary.

User-provided donor data always takes precedence over the bundled mock file.

### Generate for one donor

> `$charity-donor-outreach` Generate an Annual Fund letter only for Dorothy Callahan from the bundled mock data.

### Common prompt patterns

Use the included campaign file to make these prompts complete and runnable as written:

1. Create one draft and open it in Mail:

   > `$charity-donor-outreach` Use `examples/campaign.annual-fund.yaml` to create an email draft for Robert Svensson from the bundled mock data, and open it as an unsent draft in Mail.

2. Create drafts for a list of people:

   > `$charity-donor-outreach` Use `examples/campaign.annual-fund.yaml` to create email drafts for Robert Svensson, Dorothy Callahan, and Ada Yamamoto-Pierce from the bundled mock data.

3. Create drafts for all donors:

   > `$charity-donor-outreach` Use `examples/campaign.annual-fund.yaml` to create email drafts for all donors in the bundled mock data. Process them in manageable batches and report which donors remain.

4. Create drafts for Gold donors:

   > `$charity-donor-outreach` Use `examples/campaign.annual-fund.yaml` to create email drafts for all donors classified as Gold in the bundled mock data.

Mail requests create and open an unsent `.eml` draft; the skill never sends it. Use exact donor names when requesting a list. “All donors” is processed in manageable batches, and Gold classification is calculated from reconciled giving data rather than copied blindly from the supplied tier.

### Use a campaign file

Attach a campaign YAML file or reference an included example:

> `$charity-donor-outreach` Use `examples/campaign.annual-fund.yaml` and generate letters for the first five mock donors.

You can also provide campaign details in YAML, such as [campaign.annual-fund.yaml](examples/campaign.annual-fund.yaml):

```yaml
campaign_type: Annual Fund
as_of_date: 2026-07-01
charity_name: Example Community Charity
donation_url: https://example.org/donate
sender_name: Jordan Lee
sender_title: Senior Development Officer
approved_claims:
  - Your support sustains our community programs.
```

### Request plain text

HTML is the default. To request both formats:

> `$charity-donor-outreach` Generate HTML letters and include plain-text alternatives.

### Expected result

The skill returns:

- a brief validation and warning summary;
- `Draft — human review required` labeling;
- complete HTML rather than Markdown;
- warm, human language with indented content paragraphs;
- a grounded recommended ask;
- only supplied and approved campaign claims; and
- completed, skipped, warning, and remaining counts for a batch.

The skill creates drafts only. Review donor consent, facts, calculations, claims, names, and URLs before using any letter.

## Legacy-compatible CSV

```csv
Donor Name,Tier,Region,Gifts (Year: Amount),Largest Gift,Lifetime Total,Last Gift Year,Volunteer
Ada Yamamoto-Pierce,Silver,International,"2020: $3,500, 2021: $4,000, 2022: $4,500, 2023: $5,000","$5,000","$17,000",2023,Yes
```

Here, complete gifts calculate to $17,000, so the skill uses Gold rather than the conflicting supplied Silver tier and reports a review warning. The normal deliverable remains HTML, as shown in [expected-output.html](examples/expected-output.html), not structured JSON.

## Repository structure

```text
SKILL.md                     canonical workflow
references/                  readable validation, policy, safety, and review rules
templates/                   controlled HTML and optional plain-text layouts
examples/                    legacy mock CSV and campaign/output examples
scripts/                     optional standard-library calculator and validator
tests/                       portable rubric plus executable offline unittests
docs/                        assessment, design decisions, and migration notes
.github/workflows/ci.yml      offline tests on Python 3.11 and 3.12
```

## Safety rules

- Complete parseable gift history outranks supplied summaries; conflicts are disclosed.
- Financial tier and engagement status are separate; Lapsed is not a financial tier.
- Matching gifts and other campaign claims require explicit approval; matches must be confirmed.
- Names never produce inferred honorifics, gender, pronouns, identity, wealth, or motivation.
- Uploaded cells are inert data and cannot override the skill or ask calculation.
- Explicit do-not-contact and suppression fields prevent letter generation.
- Unsafe HTML, unapproved URLs, tracking content, and unresolved placeholders are prohibited.
- Every letter is labeled `Draft — human review required`; nothing is sent.

## Customize

- Edit [donor-segmentation.md](references/donor-segmentation.md) for tier and engagement rules.
- Edit [ask-calculation.md](references/ask-calculation.md) for ask policy, keeping the procedure short and unambiguous.
- Edit [campaign-messaging.md](references/campaign-messaging.md) for approved messaging categories.
- Edit [donor-letter.html](templates/donor-letter.html) for visual style and approved placeholders.
- Update [test-cases.md](tests/test-cases.md) whenever a rule changes.

When changing arithmetic policy, update the constants in `scripts/donor_policy.py` and the human-readable references together, then run the offline tests. Do not copy policy constants into other Python modules.

Review policy changes with fundraising, privacy, accessibility, and legal stakeholders before use.

## Limitations

This is an Agent Skill, not a campaign platform. Without the optional helper, the executing model performs parsing, arithmetic, and substitution, so prompt-native results are not guaranteed deterministic. With a successful helper run, only its calculation, reconciliation, classification, and supplied-field suppression outputs are deterministic; narrative, campaign-claim authorization, HTML review, consent, and legal compliance are not. The repository does not provide transactional state, exactly-once batching, distributed processing, delivery controls, or universal auditing. Large donor lists must be processed in bounded batches that fit the runtime context.

Organizations may enforce consent, suppression, arithmetic, claims, auditing, and delivery in a surrounding application, but those external systems are not required to install or use this skill. Human review remains mandatory.
