# Template Placeholders

The controlled templates use only these placeholders:

- `SUBJECT`
- `DATE`
- `SALUTATION`
- `OPENING_PARAGRAPH`
- `CAMPAIGN_PARAGRAPH`
- `ASK_PARAGRAPH`
- `CLOSING_PARAGRAPH`
- `DONATION_URL`
- `SENDER_NAME`
- `SENDER_TITLE`
- `CHARITY_NAME`

Replace every placeholder before returning a draft. Treat inserted values as untrusted text, escape them for the output context, and never add executable markup.
