# AA.com booking form pitfalls (Studio cua)

Session-hardened notes from online rebook (Telavaya / WSZTVR → Aug 2 LAX→LHR).

## Drive path
- **SSH + Studio `cua-driver`**, never Pro `computer_use` on Screen Sharing.
- `cua-driver serve --grant existing-profile`; JSON-stdin `call`; re-snapshot before every `element_index`.
- Web fields often need `delivery_mode: "foreground"`.

## Credit / ticket lookup
- Canceled PNR (`WSZTVR`) proves cancel; **no REST balance** on the cancel page AX tree.
- Find travel credit wants **13-digit** ticket/credit (`001…`, sometimes `00115`/`0012`), **not** 6-letter PNR.
- Phone path can capture ticket spoken as zero-groups → digits (example: `0012342708964` from Vapi call log).
- After fill, **re-read** ticket field. Placeholder `ex. 0012345678900` = DOM never took input — claim miss, not success.

## Search form traps
1. Force **One way** (not Multi city). Multi-city left empty Flight 2 and errors “fix the N errors.”
2. Labels are **`Departure airport` / `Arrival airport` / `Departure date`** (combo/text) — not always “From/To.”
3. Date must land only in **Departure date**. If Arrival shows `08/02/2026` or `mm/dd/yyyy`, clear and retype airport code + pick suggestion (down+return).
4. Use form **Search** (flight), not chrome **Submit search**.

## Fare ladder
- **“Main One way from $836”** opens a ladder: Basic Economy ~$836, **Main ~$946**, Main Extra, Premium…
- Click **`Select … One way Main fare for $946 …`**
- Exclude buttons with Basic / Main Extra / Premium in the label.
- “from $836” band button may *also* contain the word Select when options are “being displayed” — that **closes/toggles** the sheet; do **not** confuse it with product Select.
- Prefer URL advance to `your-trip-summary` + cabin **Main** + ~**$945.50** total (taxes) over list “from” prices.

## Summary → passenger
- Upsell blocks: “Stay in Main”, Premium/Business upgrade totals are **not** the chosen fare.
- Prefer **Continue as guest** unless Cooper wants login for AAdvantage / stored credits.
- **Stop before** Purchase / Pay now / card entry without explicit go-ahead.
- Travel credit may still need applying on payment step if Find-credit UI failed earlier.

## Related
- Umbrella: `studio-cua-drive`
- Phone ticket capture + outcome logs: `vapi-phone-ops`
