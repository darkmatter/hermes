# AA booking / PNR lookup (Studio Chrome)

Session-hardened notes for Telavaya Reynolds work. Prefer live lookup over memory.

## Passenger facts (verify before acting)

| Field | Value |
|---|---|
| Name | Telavaya **Reynolds** |
| DOB | **1991-02-20** |
| AA conf | **WSZTVR** (was Jul |
| BA conf | **BRSK4R** (linked historically) |
| Old flight | AA 6991 LAX→LHR ~Jul 30 |
| Preferred rebook | **Aug 2** nonstop **AA 6935** ~15:50→10:15+1 LHR |

Email counterparts may show `telavaya@darkmatter.io` / Salam-ish icloud aliases — conf+name+DOB beat email for Find trip.

## Find reservation

URL: `https://www.aa.com/reservation/view/find-your-reservation`

Fill:

1. Last name: `Reynolds`
2. Confirmation: `WSZTVR`
3. Month: force **Feb** (do not accept Jan)
4. Day `20`, year `1991`
5. Submit **Find your trip**

### Observed cancel outcome (still true after multi-checks)

- Lands: `…/cancel?recordLocator=WSZTVR`
- Copy: **Your trip was canceled** / Status **Canceled**
- AX tree: **no residual balance, no “use credit” CTA** on that page
- Footer “Receipts and refunds” → generic help hub (receipt request / refund status), not auto credit amount

### Dead credit URLs (don’t waste the loop)

- `/refunds/travelCreditLookUp.do` → Cannot GET
- `/manageTravelCredit/lookupTravelCreditAccess.do` → “taken flight” dead page
- `/travelInformation/manageCredits` → same

Credit discovery next levers: AAdvantage **Log in**, refund status form, passenger email, phone residual (agents previously discussed credit).

## Shop one-way LAX–LHR

URL that works after filling form:

`https://www.aa.com/booking/find-flights?locale=en_US`

(Deeplink `?trips=LAX-LHR-20260802…` may bounce to empty Book form — **fill fields**.)

Fields:

| Control | Value |
|---|---|
| Trip type combo | **One way** |
| From combo | **LAX** (+ return to commit) |
| To combo | **LHR** |
| Depart date text | **08/02/2026** |
| Passengers | 1 Adult |
| Search | click |

### Results page AX goldmine

- Date carousel: `selected carousel flight N of 13, Sun, Aug 2 $836`
- Rows: times, `AA 6935`, Nonstop, `Main One way from $836… Click here for more fare options`
- Expanding Main reveals ladder e.g.:
  - **Basic Economy $836** — “No refunds allowed”
  - **Main $946** — refund-to-credit / OFP (+$ surcharge) radios
  - Premium Economy / Business higher

**Do not click Select … fare** unless Cooper approved a specific product.

### Shop snapshot reference (live 2026-07-30-ish)

Aug 2 Main-from ~$836; AA 6935 3:50p–10:15a+1 nonstop confirmed listed; same-day neighbors AA 134 / 6991 / 136 / 6983 also ~$836 Main-from.

## Safety

- Gmail AwardWallet / airline conf searches: valid sanity check, not improved by booking.
- Phone rebook history: cancel/credit + Amex decline — never assume ticketed without conf email or active PNR.
