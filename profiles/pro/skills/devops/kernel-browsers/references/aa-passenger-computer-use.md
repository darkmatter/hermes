# AA passenger + payment — validated computer-use drive

Status: **WORKS end-to-end** (2026-07-31). Reached AA "Review and pay" with card filled, stopped before purchase.

## Setup that made it work
```bash
export KERNEL_API_KEY=<REDACTED>
kernel browsers update <id> --viewport 2560x1440@10 --force   # DO THIS FIRST
```
At 1440x900 every step was scroll-hunting and overshoot. At 2560x1440 the date carousel, whole
fare ladder, and most of the passenger form fit in one screenshot. Cooper asked for the big
viewport explicitly; make it the default for checkout work.

## Loop
`screenshot → vision_analyze for pixel coords → click/type → screenshot verify`

```bash
kernel browsers computer screenshot  <id> --to /tmp/s1.png
kernel browsers computer click-mouse <id> --x 1449 --y 665
kernel browsers computer type        <id> --text "Telavaya"     # subcommand is `type`, flag --text
kernel browsers computer scroll      <id> --x 1280 --y 700 --delta-y 400
kernel browsers computer press-key   <id> --key ctrl+a
```
`type-text` is NOT a command (`Unknown flag: --text` comes from using the wrong subcommand name).

## Long native `<select>` lists — type to jump
DOB year, State, Country are long. Wheel scrolling overshoots wildly (jumped 2026→1907).
**Open the select, then type the value; the option highlights; click it.**
```bash
kernel browsers computer click-mouse <id> --x 991 --y 582   # open Year
kernel browsers computer type        <id> --text "1991"     # jumps + highlights
kernel browsers computer click-mouse <id> --x 978 --y 836   # confirm
```
Same trick for `California` and `United States`.

## Clear-then-retype
AA flagged `Enter a valid date.` on first expiry attempt:
`click-mouse` → `press-key ctrl+a` → `press-key Delete` → `type "05/31"` → error cleared.

## Full validated sequence (Aug 3 booking)
1. Date carousel tile **Mon, Aug 3 $836** → page reloads, header must read `Monday, August 3, 2026`
2. Main column "One way from $836" dropdown → fare ladder opens
3. **Select** under **Main $946** (NOT Basic Economy $836 — no changes allowed)
4. Trip summary → upsell modal → **Stay in Main**
5. Scroll down → **Continue as guest**
6. Passenger page → **Enter new passenger**
7. Fill: First `Telavaya`, Last `Reynolds`, DOB `February` / `20` / `1991`, Gender `Female`,
   Country `UNITED STATES`, **State `CALIFORNIA`**, Loyalty **left blank**
8. **Save** → card collapses to `TELAVAYA REYNOL…` with no red errors
9. Trip contact: email + confirm `telvaya@icloud.com`, phone type Mobile, **`2069542027`**
10. **Continue** → Review and pay
11. Trip protection → select **No, do not protect** (radio, not the Continue button)
12. **Continue** → Payment information
13. **Credit / debit card** radio → card fields render
14. First `Koutarou`, Last `Maruyama`, card number, Exp `05/31`, CVV (4-digit Amex),
    Billing `1111 S Grand Ave Apt 715`, City `Los Angeles`, State `California`, Zip `90015`
15. **STOP.** Report total and wait for Cooper.

## Card data shape (himitsu SA, vault `cm`)
- 1P `expiry` = **`203105`** (YYYYMM) → AA wants **`05/31`**
- Amex CVV = **4 digits**, field labeled `CVV`, right of Expiration
- Card number typed with no spaces; AMEX badge appears in-field on success

## Identity (do not get these wrong)
- Passenger **Telavaya Reynolds**, DOB 02/20/1991, Female, US / **California**
- Email **telvaya@icloud.com** (not pelavaya@)
- Contact phone **206-954-2027** — Telavaya/handoff number. **Never Cooper's 310-989-7067.**
- **Loyalty program + number stay EMPTY** unless Cooper says otherwise (a phone number once
  got stuffed into loyalty — he caught it)

## Still-true failure notes
- agent-browser `@fill` on this form mis-maps (phone→loyalty, email→last name). Use it for
  **recon snapshots only**, not fills.
- `computer click-mouse` can report SUCCESS without landing. Verify with `page.url()`; if the
  page didn't move, try `page.mouse.click(x,y)` via a one-line playwright execute.
- **ERRCODE858** after Continue = AA bounced the cart to choose-flights ("Our system is having
  trouble"). Reload the choose-flights URL, re-select the fare. Do NOT report it as booked/failed
  purchase.
- AA cart `sid` expires; a dead trip-summary link is not a live HITL link — recreate and re-drive.

## Live view
Send `browser_live_view_url` in the **first** user-facing line whenever stuck, whenever Cooper
says he's frozen, or whenever handing over. If he says "I can't click X", fill **only that field**
programmatically — don't restart the whole wizard.
