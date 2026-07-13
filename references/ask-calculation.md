# Ask Calculation

Use this exact procedure. Keep all intermediate values unrounded and round only once in step 7.

## Rules

1. **Choose the starting amount.**
   - Platinum: largest gift × 40%.
   - Gold: largest gift × 25%.
   - Silver: largest gift × 15%.
   - Bronze: flat $150.
   - Financial tier Unknown or missing usable history: $50 review-required fallback.
2. **Loyalty adjustment.** If the latest gift was in the calendar year immediately before the date basis, multiply by 1.10. “Last year” always means `as_of_date year − 1`, not the last 365 days.
3. **Lapsed adjustment.** If engagement is Lapsed, multiply by 0.75. Keep the financial-tier starting rule; do not collapse high-value donors to a flat restart ask.
4. **Emergency adjustment.** For an Emergency Appeal, multiply by 1.20. This changes the amount only; it does not authorize urgency or match claims.
5. **Volunteer adjustment.** If `Volunteer` is explicitly true/yes, add $100.
6. **Apply bounds.** Raise values below $50 to $50; lower values above $100,000 to $100,000.
7. **Round once.** Round to the nearest $50, with exact $25 midpoints rounding upward. Format as whole dollars unless cents are requested.

Order is starting amount → loyalty → lapsed → emergency → volunteer → bounds → one final round. Never reorder adjustments and never let letter prose change the result.

## Worked examples

| Case | Calculation | Ask |
|---|---|---:|
| Platinum, largest $50,000 | 50,000 × .40 | $20,000 |
| Gold, largest $12,000 | 12,000 × .25 | $3,000 |
| Silver, largest $1,400 | 1,400 × .15 = 210 → round | $200 |
| Bronze | flat 150 | $150 |
| Silver volunteer | 1,400 × .15 + 100 = 310 → round | $300 |
| Lapsed Platinum | 50,000 × .40 × .75 | $15,000 |
| Lapsed Bronze | 150 × .75 = 112.50 → round | $100 |
| Emergency Gold | 12,000 × .25 × 1.20 | $3,600 |
| Active Gold volunteer, prior-year gift | 4,000 × .25 × 1.10 + 100 = 1,200 | $1,200 |
| Emergency Silver volunteer, prior-year gift | 1,400 × .15 × 1.10 × 1.20 + 100 = 377.20 → round | $400 |

## Compact trace format

When a trace is needed, use: `Gold base: $12,000 × 25% = $3,000; emergency × 1.20 = $3,600; final rounded ask: $3,600.` Keep it outside the HTML letter.
