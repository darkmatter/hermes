# AA passenger form (Kernel driver notes)

## Session fact (booking mid-state pattern)
Cart can sit forever on `passenger-ui` with trip total ~$945 and **no ticket** until Save/Continue actually advances. Do not narrate success from "fields look filled."

## Correct passenger defaults (Cooper quizzes)
| Field | Value |
|---|---|
| Name | Telavaya Reynolds |
| DOB | 1991-02-20 |
| Email | **telvaya@icloud.com** (typos: pelavaya = wrong) |
| Phone | 3109897067 (when collecting contact) |
| Gender | as passport / Secure Flight (Female used in successful partial fills) |
| Residence | US / CA when required |

## Expand form
1. Snapshot must show `button "Enter new passenger"`
2. Click that ref; wait; re-snapshot until `textbox "First name"` appears
3. If click no-ops: Kernel short evaluate over shadow roots clicking button text `Enter new passenger`, then agent-browser snap again

## Fill order (never index-only)
1. First name / Last name by **aria-label** (not "Nth large input")
2. Clear Middle if pollution
3. DOB month / day-of-birth / year comboboxes (first DOB set, not passport expiry set)
4. Gender, country ofresidence, then state (state often disabled until country = UNITED STATES)
5. Email/phone if present; else after Save
6. Passport block optional until AA demands int'l docs — don't invent passport #

## Validate before Continue
Compact snapshot must **not** contain:
- `Please correct the following errors`
- `First name is required`
- `Date of birth Required`
- `Gender is required`

If still present: re-fill via aria-label, not force Continue.

## Payment gate
Amex Platinum default from himitsu SA vault `cm` item; zip 90015 / 1111 S Grand #715. Fill card only after passenger Continue lands on payment. Purchase still Cooper-gated unless explicit "use my card and book" — then still evidence confirmation/PNR before success claim.

## Travel credit
Wrong spoken ticket `0012342708964` — do not retry as credit. PNR WSZTVR alone does not unlock Find travel credit. Skip credit when Cooper says forget it.
