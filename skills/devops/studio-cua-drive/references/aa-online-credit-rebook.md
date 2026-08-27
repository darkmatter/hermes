# AA online — canceled PNR vs travel credit / rebook

Session-grounded (Telavaya Reynolds / WSZTVR, 2026-07). Patterns generalize.

## Truth on website (check first)
- **Find trip** with last name + DOB + **6-letter conf** can open manage UI.
- Canceled example URL shape:
  `aa.com/manage-reservation/viewres/ui/app/cancel?recordLocator=XXXXXX`
- Cancel page may show only **“Your trip was canceled” + Status: Canceled** with **no** dollar balance and **no** 13-digit ticket in the AX tree.

## Find travel credit form

### Mode + submit
- Mode toggle: **Find trip** vs **Find travel credit** (use **radio** + submit **Find your travel credit**, not the radio label button alone).
- Helper copy (authoritative UX constraint):
  - Field wants **13-digit** number beginning **`00115` / `0012`** (credit) or **`001`** (ticket).
  - Six-letter **record locator alone is not enough** for credit/refund self-service even if the form accepts typing it.

### Field gate (do before claiming lookup)
1. Fill last name + DOB + 13-digit number.
2. **Re-read AX values** — ticket field must equal digits, not `ex. 0012345678900`.
3. Only then click **Find your travel credit**.

### Outcome classes after submit
| Result | Meaning |
|---|---|
| Balance / credit detail with `$` / expiry | Success — capture amount + number |
| Same empty form, **pre-submit gate had correct digits** | **AA no-match** for that number (not “automation lost the field”). Do not retry same digits as a code fix. |
| Placeholder still showing pre-submit | Type/commit failed — fix fill, don’t call AA wrong yet |

### Phone STT vs truth
- Vapi can “successfully” capture `001…` that is still **wrong**.
- Session: Levi call digits **`0012342708964`** — clean sticky fill + submit → empty form; Cooper: **“the number is wrong.”** Never reuse that string as valid credit/ticket.
- Treat phone-captured # as **hypothesis** until cancel/e-ticket email or AA balance confirms.

## Refund tools
- Refund request (`aa.com/refunds/#/lookup`): Last name + **Ticket Number** (`13–14 digits starting with '001'`). Continue disabled until ticket format validates.
- Refund status (`aa.com/selfServiceRefund/#/refund/status/lookup`): same ticket requirement.

## How AA says to get ticket / credit numbers (FAQ)
- Booking confirmation email, **cancellation email**, or credit-card statement.
- Ticket number = 13 digits, airline code prefix **`001`** for American.
- Separate ticket numbers for seats/upgrades/bags add-ons.
- AAdvantage: login → **Travel credit** → view details / copy Trip Credit or Flight Credit #.
- Guest: Find travel credit → last name + **confirmation code or 13-digit** → submit.

## Apply credit to new trip
1. Obtain Trip/Flight Credit ticket number (verified).
2. Search/select flights (see `aa-booking-form-pitfalls.md` — one-way, Main product vs Basic).
3. Payment step: travel-credit type; **Cooper gates Purchase**.
4. Credit **does not** cover extras (seats, upgrades, bags).

## Agent workflow preference
1. Verify PNR online before another phone thrash.
2. If canceled: do **not** invent credit balance — hunt real **001…** (mail/`gog`) or AAdvantage Travel credit UI.
3. If texting for digits: BB as `cooperton42391`; default handoff **`+12069542027`** when Cooper says 206 (not 310).
4. Stop before purchase; Cooper gates payment.
5. Prefer **Studio SSH + cua-driver** (`studio-cua-drive`), not Pro Screen Sharing.
6. Halt automation immediately on Cooper “stop” / interrupt.

## Mail search hints (when gog/Himalaya available)
- From: american / aa.com
- Subject: cancel, eTicket, receipt, WSZTVR, Telavaya
- Body regex: `\b001\d{10}\b`
- Exclude known-bad STT string `0012342708964` from “solved” paths
