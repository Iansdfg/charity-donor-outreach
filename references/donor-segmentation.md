# Donor Segmentation

Classify financial value and engagement separately. Use USD unless the user supplies a different approved policy; do not silently convert currencies.

## Financial tier

Calculate lifetime giving from complete, parseable gift history first.

| Tier | Calculated lifetime giving |
|---|---:|
| Platinum | $50,000 or more |
| Gold | $10,000 through $49,999.99 |
| Silver | $1,000 through $9,999.99 |
| Bronze | Below $1,000 |

If history is unavailable, use a clearly supplied `Lifetime Total`. If neither is reliable, use the supplied Platinum/Gold/Silver/Bronze tier only for tone, label the financial tier `Unknown` in the review summary, and do not claim a lifetime total.

## Engagement status

Use the latest parseable gift date/year relative to the campaign `as_of_date` (or disclosed runtime date fallback):

- **Active:** latest gift is no more than three calendar years before the date basis.
- **Lapsed:** latest gift is more than three calendar years before the date basis.
- **Unknown:** no reliable latest gift date/year exists.

Example: with `as_of_date: 2026-07-01`, a latest gift in 2023 is Active; a latest gift in 2022 or earlier is Lapsed when only a year is known. With exact dates, compare the third anniversary exactly.

## Reconciliation

Complete gift history outranks summaries. Warn on every conflict and show both values outside the letter.

- Gifts total $17,000 but supplied tier is Silver → use Gold and warn.
- Gifts total $25,000 but supplied lifetime total is $7,500 → use $25,000 and Gold; warn about both conflicts.
- Supplied `Tier = Lapsed`, history totals $1,800, latest gift is 2019 → Silver + Lapsed.
- `Tier = Lapsed` with no usable amount → engagement Lapsed; financial tier Unknown; use the missing-history ask fallback only with review warning.

Never silently switch sources or fabricate transactions.
