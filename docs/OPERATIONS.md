# Operations

Version code, policies, templates, and schemas independently and record relevant versions in every result. Deploy policies as an immutable matched-version set; canary them on synthetic fixtures and compare release-gate metrics before wider use. Roll back by restoring the previous immutable policy/template set and starting a new run ID.

Observe lifecycle counts, suppressions by reason, validation failures, latency, retries, duplicates, and reviewer dispositions using donor IDs only. To recover, inspect `manifest.json`, verify JSONL integrity, correct transient/provider configuration, and rerun the same inputs/output path; completed keys are skipped. For distributed work, migrate the ledger to transactional storage.

For incidents: stop generation/downstream use, preserve minimal audit evidence, quarantine affected drafts, rotate leaked secrets, identify input/policy/template/provider versions, notify privacy/security owners, remediate and add regression tests, canary again, and document reviewer decisions.

