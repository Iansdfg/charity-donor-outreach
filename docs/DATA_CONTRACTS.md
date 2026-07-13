# Data Contracts

Pydantic models are runtime contracts and JSON Schemas are interoperability contracts. Monetary amounts serialize as decimal strings and pair with ISO-like supported currency (`USD`). Dates are ISO 8601. Stable donor, gift, campaign, claim, household, and manager IDs—not names—are identifiers.

Gift transactions calculate lifetime total, maximum gift, and latest date. Supplied summaries exist only for reconciliation. `GenerationResult` distinguishes generated, suppressed, and failed outcomes, includes the complete ask trace, and always requires review. JSONL files contain exactly one complete object per line; no pickle or partial documents are used.

