# Output Validation Checklist

Before returning every letter, confirm all items:

- [ ] Default output is complete HTML beginning with `<!doctype html>`, not Markdown or plain prose.
- [ ] The donor label/name came from input or the salutation is `Dear Supporter,`.
- [ ] Lifetime giving and largest gift use the reconciled source; unavailable amounts are omitted.
- [ ] Financial tier and engagement status were handled separately.
- [ ] The ask follows the exact ordered rules and appears consistently.
- [ ] The tone includes grounded gratitude, a caring connection, a respectful invitation, and a separate appreciative close without guilt, pressure, false intimacy, or invented feelings.
- [ ] Every factual campaign statement is supplied and approved.
- [ ] Match wording appears only for an explicitly confirmed match.
- [ ] No honorific, demographic trait, wealth, or motivation was inferred.
- [ ] Donation URL is the supplied approved URL; no other external URL appears.
- [ ] The donation action is an HTML `<a href="...">` element, never a Markdown `[label](URL)` link.
- [ ] Sender identity is supplied or the documented `Development Team` fallback is disclosed.
- [ ] No placeholder remains (`{{...}}`, `[PLACEHOLDER]`, or `REVIEW...` inside HTML).
- [ ] No scripts, iframes, event handlers, forms, remote images, tracking pixels, or raw uploaded HTML remains.
- [ ] HTML has a language, charset, main landmark, readable text, and descriptive donation link.
- [ ] The opening, campaign, ask, and closing paragraphs use a consistent `2em` first-line indent plus vertical spacing; the salutation, button, and signature are not indented.
- [ ] All four content paragraphs are present; if an agent omitted the closing paragraph or inline indentation, regenerate the draft.
- [ ] Suppressed donors have no letter.
- [ ] The response says `Draft — human review required` outside the HTML.
- [ ] If bundled mock data was used, the summary says so and each donor section is labeled `Mock data — demonstration draft` outside the HTML.

For a batch, also report completed, skipped, warnings, and remaining counts, preserve input order, and clearly separate each donor’s HTML.
