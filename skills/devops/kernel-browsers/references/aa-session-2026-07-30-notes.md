# AA Telavaya session notes (2026-07-30/31)

## Facts
- Passenger: **Telavaya Reynolds**, DOB **02/20/1991**, email **telvaya@icloud.com** (not pelavaya@)
- Phone contact: Cooper **3109897067** — **never** as loyalty number
- PNR **WSZTVR** canceled online; need real 13-digit `001…` for credit/refund self-serve
- Levi STT ticket **0012342708964** — **wrong** (clean Find credit submit returned empty form)
- Booking target: LAX→LHR **Aug 2 2026** AA **6935** Main ~**$945.50** (Basic teaser $836 = not Main)
- Pay: Amex Platinum ···1004 (himitsu SA / vault cm) — **no Purchase without Cooper**
- HITL ticket ask: Studio BB → **+12069542027** when Cooper says 206 (not default 310)

## What worked
- Kernel stealth browser + short Playwright search (One way LAX/LHR, Main $946 select)
- Profiles CS: save-changes + delete → reload
- Gmail: live-view login on profile `cooper-email` (Hosted Managed Auth `stuck_in_loop`)
- agent-browser `snapshot -i` after CDP when tab is the real AA page
- Live URL as HITL when automation stalls on passenger

## What failed / correct next time
- Agent-browser field fill: wrong index mapping (email into last name; phone into loyalty; State skipped)
- Giant one-shot Playwright fill+pay scripts: corrupt/timeout; abandon
- CDP `connect` → often **about:blank**; must tab to passenger-ui before recon
- Do not declare call/ticket success/fail on stub transcript — full GET /call (vapi-phone-ops)
- Cookie/OneTrust Can hide passenger CTA; Accept / remove banners before mapping form

## Driver preference for this user
1. Search/select flight: short known Playwright on Kernel
2. Passenger/pay: computer screenshots + computer click/type **or** Cooper on live view
3. Always plain evidence (values, URL, total) before next step
