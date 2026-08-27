# AA checkout → Amex SafeKey (3DS) → confirmation

Validated end-to-end 2026-07-30/31 on Kernel (computer-use drive, 2560x1440 viewport).
This is the stage **after** the passenger form (`references/aa-passenger-computer-use.md`).
First session that actually completed a purchase — earlier runs all died before Pay now.

## Stage map (what each page looks like)

| Order | URL shape | Marker text | Action |
|---|---|---|---|
| 1 | `…/passenger-ui/?search-journey-id=…&sid=…` | "Trip contact information" | fill contact, Continue |
| 2 | `…/ecommerce/checkout-app/cart/<uuid>` | **"Review and pay"** | decline insurance → Continue → card |
| 3 | same cart URL, modal | **"Follow payment instructions"** | Amex SafeKey 3DS |
| 4 | `…/ecommerce/checkout-app/confirm` | **"Your trip is booked"** | capture locators |

Note the host switches from `aa.com/airfare-sales/ui/...` to `aa.com/ecommerce/checkout-app/...`
at Review-and-pay. A stale `sid` from the airfare-sales stage is **not** reusable here.

## Trip protection (Allianz) — must answer before payment renders

The Payment information panel is **greyed/inert** until the Yes/No radio is answered.

- "No, do not protect my $945.50 trip" radio ≈ `(689, 765)` at 2560x1440
- After selecting No the copy turns red ("Your trip is not protected…") — this is the
  **selected** state, not an error
- Then `Continue` ≈ `(1384, 1079)` expands Payment information
- A "Privacy and cookies" dialog can sit on top — Dismiss ≈ `(1775, 1380)`

## Card entry (Amex, himitsu vault `cm`)

Fields at 2560x1440 after Credit/debit card radio `(669, 899)`:

| Field | Approx coords |
|---|---|
| First name | (883, 1039) |
| Last name | (1285, 1039) |
| Card number | (883, 1159) |
| Expiration | (1185, 1159) |
| CVV | (1370, 1159) |
| Billing address | (1285, 1279) |
| City | (816, 1401) |
| State (select) | (1083, 1401) |
| Postal code | (1352, 1401) |

Gotchas:
- 1P `expiry` is `203105` (YYYYMM) → type **`05/31`**. First attempt flagged
  "Enter a valid date." — clear with `press-key ctrl+a` + `Delete`, retype.
- Amex CVV is **4 digits**.
- Cardholder name is **Koutarou Maruyama** (card), *not* the passenger name.
- Billing = Cooper's address: 1111 S Grand Ave Apt 715, Los Angeles, California 90015.
- State select: click then `computer type --text "California"` + `press-key Return`.

## Pay now

Scroll to the bottom band: "By selecting 'Pay now', you agree to the…".
Button **Pay now** ≈ `(1733, 673)` after a `--delta-y 700` scroll from the card block.
Receipt email is displayed just above ("We'll send the receipt and any trip updates to:
TELVAYA@ICLOUD.COM") — good final sanity check that the passenger email stuck.

## Amex SafeKey (3-D Secure) — expect it, and it needs Cooper

After Pay now a modal appears: **"Follow payment instructions — Your form of payment
requires additional verification."** with an embedded SafeKey iframe showing card `31004`
and `USD 945.50`.

Two variants, in this order:

1. **Push to remembered device** — "we're sending a notification to your remembered
   device. Tap the notification to confirm your transaction."
   Links: `Resend notification`, `Send verification code instead`.
2. **Verification code** — if the push isn't actioned it flips to a code challenge:
   code is sent to the **cardholder**, i.e. `******7067` (Cooper's 310) and
   `m*****@cm.xyz`. Field ≈ `(1271, 877)`, `Continue` ≈ `(1271, 927)`.

**The code goes to Cooper, never to the passenger.** Ask him for it in plain text and
type it; do not attempt to fetch it from anywhere else. This is a legitimate stop-and-ask
point — surface the live-view URL at the same time so he can act there if he prefers.

Nothing is charged until the challenge passes. A modal sitting open is *pending*,
not booked and not declined.

## Confirmation — the evidence shape to quote

`aa.com/ecommerce/checkout-app/confirm` → heading **"Your trip is booked"**.

Fields to capture (real values from this run):

| Field | Value |
|---|---|
| American confirmation code | `OYVTLE` |
| British Airways confirmation code | `CEP4TZ` |
| Ticket number | `0012364615262` |
| Passenger status | **Ticketed** |
| Total | `$945.50` |

Only claim "booked" once you can read the locator **and** a `Ticketed` status off the
confirm page — same success-evidence discipline as the Vapi call-log rule.

### "On request" banner is not a failure
OAL (other-airline) metal shows a green-check banner:
> "On request — Flights on other airlines are subject to confirmation. You can view the
> status of your trip online to verify confirmation or contact Reservations."

For BA-operated AA flights this is normal. Report it as a caveat and suggest re-checking
the locator later; do **not** describe the booking as failed or pending-payment.

## Note on unused travel credit
This booking paid **full fare** because the spoken 13-digit ticket number from the phone
call (`0012342708964`) was wrong and the Find-travel-credit form returned nothing.
The checkout page does offer **"Add trip credit / flight credit"** ≈ `(858, 709)` before
card entry — use that path if a verified `001…` number ever turns up, and mention the
unclaimed credit in the wrap-up so it isn't silently lost.
