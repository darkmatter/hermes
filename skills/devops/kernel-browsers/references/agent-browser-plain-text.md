# Plain-text recon + booking pitfalls (Kernel + agent-browser)

## Prefer agent-browser-shaped observation
When exploring UI on Kernel, observations should look like:

```text
- button "Enter new passenger" [ref=e48]
- textbox "First name" [required, ref=e8]
```

Not HTML dumps, not 150-line Playwright megascripts as the primary driver.

Paths: `agent-browser -p kernel` or `agent-browser connect <cdp_ws_url>` then `snapshot -i`.

## CDP blank-tab trap
After `agent-browser connect $CDP`, `get url` may be `about:blank` even when Kernel Playwright still has the AA passenger page.

**Fix every connect:**
1. `agent-browser tab list`
2. If only blank / no aa.com: `agent-browser open <known passenger-ui URL with sid>` **or** use tiny Kernel `playwright execute` to `bringToFront` the passenger page, then re-snapshot
3. Never treat blank interactive snapshot as "form gone" until tabs + Kernel `page.url()` checked

## Ref parsing
- Snapshot lines are often indented; parsers must not require start-of-line match
- Skip lines containing `option "` when resolving control refs
- After **every** open/click/nav, **re-snapshot** — `@eN` ids are session-page local and churn when the form expands
- Prefer exact needles: `textbox "First name"`, `combobox "day of birth month"`, `button "Save"`

## AA passenger UI (international)
- Form lives in **shadow DOM** (`adc-input-*`, overlays)
- Interactive snapshot may stay at `Enter new passenger` until expand sticks; click + wait + re-snap; if refs never appear, open form via short shadow-aware Playwright once, then resume snapshot loop
- Field order is not reliable for fill-by-index: **last name can swallow email** if you map big inputs by position — always key on `aria-label` / name (`First name`, `Last name`, `Email`)
- Filled a11y values ≠ accepted state: Save can still show `First name is required` / `Date of birth Required` — verify after Save with compact snapshot for `Please correct` / `is required`
- Email for Telavaya bookings: **telvaya@icloud.com** (not pelavaya)
- Contact email/phone sometimes appear only after successful Save or on a later step
- Skip travel credit if lookup failed; full-fare card path is OK when Cooper says so
- **Never Purchase** without Cooper gate; pay payload via himitsu SA only (`op` interactive only after ask)

## Giant-script ban
Do not repair booking with ever-larger generated TS/JS ball of fill+pay. Pattern: snapshot → act one control → re-snapshot → short shadow fill helper only when refs cannot reach a field.

## Related
- `references/aa-kernel-booking.md` — fare ladder / selectors
- `references/gmail-profile-and-1p.md` — Gmail profile + 1P provider
- `references/managed-auth.md` — hosted login vs live-view
