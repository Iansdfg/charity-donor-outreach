# Policy Model

All four YAML files must have the same version. Transactions outrank policy, normalized fields, and supplied summaries. Tiers are Bronze below 1,000; Silver 1,000–9,999.99; Gold 10,000–49,999.99; Platinum 50,000+. Lapsed means latest gift is more than 1,095 days before campaign `as_of_date`; it is never a tier.

Bronze uses a 150 base even with zero/missing history (with a review warning). Other tiers multiply the largest transaction. Prior-calendar-year, lapsed, and emergency percentage adjustments apply in that order, followed by the verified-volunteer fixed adjustment, min/max caps, then exactly one nearest-50 half-up round. High-value lapsed donors retain their tier basis and receive the lapsed reduction. Only USD is supported.

Only approved claims are eligible. Match claims additionally require `match.status: confirmed`. Pending/rejected claims and unsupported offers, deadlines, urgency, statistics, tax language, and staff identities are omitted or rejected.

