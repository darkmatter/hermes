# CFTC Portal Handoff Notes

Session-derived reference for future official CFTC portal work. Keep this as a handoff/checkpoint recipe, not a task narrative.

## Predicate first (user correction)

Before driving the portal at all, determine whether the user actually qualifies as a reporting trader from their **actual positions** — do not start with the portal. For crypto: log the user into Coinbase (user enters credentials manually), open advanced-trade **futures → Positions** tab, read contract/side/quantity/notional.

An FCM-issued **Form 40 notice is itself evidence** the CFTC reporting level was already crossed — Coinbase only demands Form 40 from traders whose positions exceed the 17 CFR 15.03(b) contract-specific reporting level. The notice answers "do I qualify"; the position read answers "which contract."

Portal **Organization Type** follows from that finding: **LTR (Large Trader)** when positions qualify; the other options (DCM/DCO/DCO Applicant/EDCO/FBOT/FCM/HCR/SDR/SEF) are for exchanges, clearinghouses, repositories, and regulators — none is a generic individual/public account type. Do NOT guess org type.

## Consent gates (user correction)

The portal's government-system warning / terms **Accept gate is PRE-AUTHORIZED**. "Get through the portal without issues" includes clicking it. Never ask permission to click agree/accept — click it, re-snapshot, proceed. The only hard stop downstream is the final Form 40 certification/submission and credential/MFA entry.

## Verified navigation path

1. Official portal URL: `https://portal.cftc.gov`.
2. First visit shows a government-system warning with an `Accept` control — click it (pre-authorized).
3. Acceptance advances to `Sign In`; the portal may briefly show `Checking your Browser…` before exposing the sign-in form.
4. The sign-in page includes `Request an account` for users without credentials.
5. The New User Request Form currently exposes:
   - Organization Type (dropdown — options incl. DCM/DCO/DCO Applicant/EDCO/FBOT/FCM/HCR/LTR/SDR/SEF)
   - First Name
   - Last Name
   - Business Email Address
   - Confirm Business Email Address
   - Business Phone Number (numbers only)
6. Fill permitted non-secret fields once the predicate/org-type and the user's legal name + business email are known. Stop before submitting the request unless authorized.

## Verified field values (this user)

- Organization Type: **LTR**
- First/Last: `Koutarou` / `Maruyama`
- Business Email / Confirm: `cooper@darkmatter.io`
- Business Phone: digits only (user's phone)

## Position evidence (this user, 2026-07-31)

Coinbase advanced-trade futures → Positions (1):
- **ETH PERP** (nano ETH perp, 0.1 ETH/contract), **4,236 contracts** = 423.6 ETH, notional ~$788K, avg entry $1,873.8, mark $1,860.5, est liq $1,566.8, funding -$177.42, uPnL -$5,640.10.
- This is the position that crossed the reporting level and triggered the Form 40 notice. Positions are under a **Positions (n)** tab; the AXTable rows expose Market/Quantity/Notional/etc. as AXStaticText — scroll the page region to bring rows into the AX tree.

## Reading Coinbase futures positions (verified technique)

- The positions live under the **Positions (n)** tab on any advanced-trade futures page (e.g. `/advanced-trade/futures/<symbol>`). The tab label is an `AXStaticText` that does NOT advertise AXPress — clicking it by element index returns `suspected_noop`. Use a **pixel click** at the tab's frame coordinates instead.
- After activating the tab, the position rows may be below the fold. Scroll the page region (pixel wheel) until the `AXTable` appears in the AX tree. Rows expose Market / Quantity / Value / Avg Entry / Mark / Est Liq / Margin / Funding / P&L as `AXStaticText`.
- A **Positions (1)** count of ≥1 confirms an open reportable futures position; the quantity column gives contracts directly (e.g. `4,236 contracts`).
- **Screenshot+vision fallback:** if the AX tree truncates before the table renders (dense TradingView SPA), take `get_window_state(include_screenshot=true)` and read the table from the image with `vision_analyze`.

## CFTC Portal organization types (verified full list)

The New User Request Form's Organization Type dropdown exposes exactly these options — none is a generic "individual" or "other":

| Code | Meaning |
|---|---|
| DCM | Designated Contract Market (futures exchange) |
| DCO | Derivatives Clearing Organization (clearinghouse) |
| DCO Applicant | Organization applying to become a DCO |
| EDCO | Exempt DCO |
| FBOT | Foreign Board of Trade |
| FCM | Futures Commission Merchant (futures broker) |
| HCR | Home Country Regulator |
| **LTR** | **Large Trader — reportable-position trader** |
| SDR | Swap Data Repository |
| SEF | Swap Execution Facility |

Select **LTR** only when positions actually qualify. The other codes are for exchanges, clearinghouses, repositories, brokers, and regulators. Do NOT guess; read the actual list from the form.

## Large Trader determination (verified rule)

Large Trader status is determined by **open positions at or above the CFTC reporting level for a specific contract/month** (17 CFR 15.03(b)) — NOT by net worth, account value, or monthly trading volume.

- Related positions aggregate across accounts the trader controls or has financial interest in.
- Once reportable, the FCM reports the position daily to the CFTC; the CFTC then issues a Form 40 demand.
- **The Form 40 notice is itself the determination** — Coinbase only sends it after the position crossed the reporting level. No separate threshold math needed once the notice exists.
- Practical check: Coinbase advanced-trade → futures → Positions; ≥1 open reportable futures position + a Form 40 notice = Large Trader.

## Where the CFTC code is NOT (verified dead ends — do not re-search)

- Coinbase **notifications bell** panel: only price alerts and trading insights, no regulatory notices.
- Coinbase **profile menu / Settings → Notifications**: alert preferences only, no documents or compliance messages.
- The 9-digit CFTC code comes only in the **Form 40 request email** Coinbase sends to the registered email address. If gog/Gmail is unreachable, ask the user to search their email for "CFTC" or "Form 40" and read the code — do not burn time hunting for it inside the Coinbase UI.

## Verification and action policy

- Re-snapshot after every navigation: AX element indices change after acceptance and after the sign-in/browser-check transition.
- A visible `Success!` browser-check message is not authentication; it only indicates the anti-bot check passed.
- Chrome URL navigation: Return on an existing tab's address bar repeatedly no-ops. Use `cmd+t` fresh tab + foreground keystrokes.
- Hard stops: credential/MFA entry, and final Form 40 certification/submission.
