# Charity Donor Outreach Agent Skill

This is an installable, dependency-free Agent Skill for generating personalized donor-letter drafts from an uploaded CSV, pasted donor list, or individual donor record. It requires no Python, Node.js, virtual environment, package manager, API server, database, external library, or separate API key. The executing agent reads `SKILL.md`, applies the included references, and returns HTML donor-letter drafts directly in the conversation.

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
tests/                       portable cases and an evaluation rubric
docs/                        assessment, design decisions, and migration notes
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

Review policy changes with fundraising, privacy, accessibility, and legal stakeholders before use.

## Limitations

This is a prompt-native skill, not a campaign platform. The executing model performs parsing, arithmetic, and substitution, so the repository cannot guarantee deterministic enforcement, transactional state, exactly-once batching, distributed processing, auditing, or delivery controls. Large donor lists must be processed in bounded batches that fit the runtime context.

Organizations may enforce consent, suppression, arithmetic, claims, auditing, and delivery in a surrounding application, but those external systems are not required to install or use this skill. Human review remains mandatory.
