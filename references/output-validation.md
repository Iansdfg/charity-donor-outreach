# Output Validation Checklist

Before returning every letter, confirm all items:

- [ ] The donor label/name came from input or the salutation is `Dear Supporter,`.
- [ ] Lifetime giving and largest gift use the reconciled source; unavailable amounts are omitted.
- [ ] Financial tier and engagement status were handled separately.
- [ ] The ask follows the exact ordered rules and appears consistently.
- [ ] Every factual campaign statement is supplied and approved.
- [ ] Match wording appears only for an explicitly confirmed match.
- [ ] No honorific, demographic trait, wealth, or motivation was inferred.
- [ ] Donation URL is the supplied approved URL; no other external URL appears.
- [ ] Sender identity is supplied or the documented `Development Team` fallback is disclosed.
- [ ] No placeholder remains (`{{...}}`, `[PLACEHOLDER]`, or `REVIEW...` inside HTML).
- [ ] No scripts, iframes, event handlers, forms, remote images, tracking pixels, or raw uploaded HTML remains.
- [ ] HTML has a language, charset, main landmark, readable text, and descriptive donation link.
- [ ] Suppressed donors have no letter.
- [ ] The response says `Draft — human review required` outside the HTML.

For a batch, also report completed, skipped, warnings, and remaining counts, preserve input order, and clearly separate each donor’s HTML.
