---
name: financial-operations
description: >-
  Playbook for Cooper's financial operations — bank triage, fraud alerts, Zelle,
  corporate APIs (Brex/Stripe/Gusto), 1Password service-account injection, and
  third-party website payment repair (Studio CUA path, charge gates, Amex/Brex cards).
  Use for banking, payments, corporate cards, fraud verification, failed payment
  repair, subscription renewals, or billing changes. Absorbs payment-operations.
---

# Financial Operations

This skill defines the workflow for managing Cooper's financial operations, including bank triage, fraud alerts, Zelle transfers, and corporate API interactions (Brex, Stripe, Gusto).

## Security & Approval Boundaries
- **Read-Only by Default:** You may investigate, read balances, and scrape alerts autonomously.
- **GATED ACTIONS (Require Explicit Confirmation):** Sending money (Zelle, Wires), disputing fraud, clicking "Yes/No" on fraud alerts, rotating API keys, updating KYC details.
- **Observable Evidence:** Never mark a financial task "Done" without verifiable evidence (a receipt, a success JSON response, or explicitly handing off to Cooper).

## 1. Browser Access for Legacy Banks (BoA, Amex, Capital One)
Use the Live Chrome CDP workflow, NOT Camofox remote sessions, because these sites rely on device trust and passkeys.
- **Full reference:** `references/live-chrome-cdp.md` — setup, security rules, OAuth flows, DOM interaction patterns, **and AppleScript fallback when CDP port 9222 is down** (including the multi-instance Chrome targeting fix).
- **Endpoint:** `127.0.0.1:9222`
- **Helper Script:** `~/.hermes/scripts/live-chrome-cdp.js`
- **Workflow:** Navigate to a new tab, use DOM inspection to read alerts. Stop if "Remember this device" or "Fraud Yes/No" decisions are prompted, unless guided by the user.
- **CDP Down?** Fall back to AppleScript (`osascript`) + `computer_use`. See the "Fallback: AppleScript When CDP Is Down" section in `references/live-chrome-cdp.md` — covers the multi-instance Chrome problem (kill Playwright/Puppeteer Chrome processes so AppleScript targets Cooper's real Chrome) and enabling "Allow JavaScript from Apple Events".

## 1b. Zelle Transfers via AppleScript (CDP Down Fallback)

When CDP is unavailable and you've fallen back to AppleScript JS execution,
the complete BofA Zelle transfer flow (login → select recipient → enter
amount → set date → review → confirm) is documented in
`references/bofa-zelle-applescript.md` — includes all field selectors, the
multi-tab targeting pattern, and the Python subprocess technique for reliable
JS escaping in `osascript`.

**Key pitfalls:**
- BofA's `fsdgoto()` SPA navigation function is not accessible from
  AppleScript `execute javascript` context. Must find and click link elements
  directly, or check for an already-open Zelle tab.
- The **Pay button** (`#Pay-review-btn`) is a SPA button with no parent
  `<form>`. JS `.click()` via `execute javascript` silently fails and may
  cause a partial-submission error. Must use AppleScript AX
  `perform action "AXPress"` via `entire contents of w` to press it
  natively. See Step 7 in the reference for the full pattern.

## 2. 1Password Service Account Injection
**Never bare / interactive `op`** — that triggers the 1Password app biometric/GUI prompt and is forbidden for agents and subagents.

**Only allowed path:** `~/.local/bin/op` (must be first on `PATH`). The wrapper injects `OP_SERVICE_ACCOUNT_TOKEN` from **`himitsu read op-service-account/token`** (drkmttr.1password.com) and enforces a hard timeout (`OP_TIMEOUT`, default 5s; exit 124 = fail, never treat as success).

```bash
export PATH="$HOME/.local/bin:$PATH"
# REQUIRED: --vault on every call
op item list --vault cm --format=json
op item get <id-or-title> --vault cm --format=json
```

- **Token source of truth:** himitsu `op-service-account/token` only.
- **FORBIDDEN:** `/run/agenix/op-service-account-token` (personal **my.1password.com** — wrong account; never use for agent work).
- **FORBIDDEN:** `op signin`, desktop app unlock, biometric prompts, listing without `--vault`, calling `/etc/profiles/per-user/cm/bin/op` or `/opt/homebrew/bin/op` directly (those are the real CLI and will try interactive auth when SA is missing).
- **SA vaults (drkmttr):** `cm` | `cooper` | `dev` only. Name-only catalog (no secrets): `~/.hermes/op-sa-catalog.json` — parent agents should refresh this catalog; children must not thrash `op` or invent vaults.
- **If an item is missing from the catalog:** stop. Ask Cooper **as-needed** to move/copy **that one item** into vault **`cm`** (preferred shared vault for agent payment/login work). Do **not** bulk-nag; do **not** fall back to personal vaults or interactive `op`.
- **Standing cards:** default pay **Amex Platinum** vault `cm` id `nj33napkeiybo5o4fezookdb4i` (Koutarou Maruyama, ZIP 90015). Coinbase One is `p2yhadwwld4fpxilkw6w4hhvwa` only if user picks it. Vapi item is vault `dev` title `vapi`.
- Deep call flow: skill **`vapi-phone-ops`**. KB/Vapi Files may hold addresses/emails/cards; still gate spend; never invent PAN.
- **Pitfall:** Never print passwords/PANs to stdout or shell arrays. Scrub temp files. Pass secrets only into the process that needs them.
- Full SA catalog/refresh recipe: `references/op-service-account.md`.

## 3. Retrieving 2FA / OTP
If SMS 2FA is sent, extract it securely from the local macOS Messages database using SQLite:
```python
import sqlite3
# Example query logic for ~/Library/Messages/chat.db looking at recent rows where is_from_me=0
```

## 4. Brex API
Brex provides a developer API which is vastly preferred over UI automation.
- **Credential:** Stored in himitsu as `brex-api-token` (`himitsu read brex-api-token`, 40-char token; never print it).
- **Host (verified):** `https://api.brex.com` works. `platform-api.brex.com` and `platform.brexapis.com` timed out/were unreachable in testing — retry api.brex.com first.
- **Card PAN retrieval:** `GET /v2/cards` lists metadata only (never full PANs); full number comes from `GET /v2/cards/{id}/pan` (returns number/cvv/expiration_date/holder_name). Prefer ACTIVE VIRTUAL cards without `spend_controls`. Full recipe, selection criteria, and secret hygiene: `references/brex-card-retrieval.md`.
- **Usage:** `himitsu exec brex-api-token -- bash -c 'curl -s -X GET https://api.brex.com/v2/cards -H "Authorization: Bearer <REDACTED>"'`
- **Role in payments:** Brex is Cooper's FALLBACK card source, not the default (personal Amex Platinum first — see §6 website payment repair).
- **Pitfall:** Ensure you map API version requirements appropriately (e.g., `v2` for Users).

## 5. Stripe & Gusto Handling
- **Stripe:** Platform dictates strong KYC (address reviews, beneficial owner checks). Provide the direct `connect.stripe.com/express/...` link to Cooper as a HANDOFF task.
- **Gusto:** Used for domestic and international contractor payouts. Verify transaction completion statuses by querying Gmail for automated debit confirmations rather than interacting with the UI.

## 6. Website payment repair / checkout (absorbed from payment-operations)

When repairing a failed payment, renewing a subscription, purchasing a service, or changing billing on a **third-party website**:

### Hard preferences

- Use **Mac Studio + cua-driver** (`studio-cua-drive`) for every website interaction. Not headless, not Pro GUI, not AppleScript as the primary path.
- Studio first; **Kernel only as fallback** when Studio is unavailable.
- Secrets: `himitsu` first, then `op` service token (drkmttr.1password.com via `~/.local/bin/op` wrapper). Vaults: `cm` | `cooper` | `dev`. Never `/run/agenix/op-service-account-token` for darkmatter vaults (that token is personal my.1password.com).
- Cards: personal **Amex Platinum** (vault `cm`) first; **Brex** corporate fallback via API PAN endpoint. Never reuse a declined/expired default.
- Typing drkmttr-retrieved card data into payment forms via CUA **is** authorized. Never ask Cooper to hand-enter cards. Passwords/MFA/passkeys stay handoff-only. Never print secrets.

### Authorization boundary

Autonomous: investigation, billing-page inspection, invoice/status review, preparing checkout, **card entry + saving payment method**.

**Stop before** Pay / Submit payment / Place order / Subscribe / Renew / Confirm charge (or equivalent). At that boundary report service, amount, plan, cadence, method suffix, consequence — one confirmation. Pre-approved charges in-thread: do **not** re-ask unless amount/method/service changed.

The Flue `@agents/desktop` tools do **not** enforce this stop — `cua_click` has no Pay allowlist. Hermes `studio-cua-drive` (and the human) remain the gate. Do not “fix” secret retrieval by giving that agent `local()` sandbox; use allowlisted himitsu/`op` tools instead. Package map: `studio-cua-drive` → `references/flue-desktop-agent.md`.

### Workflow sketch

1. Kanban card with service, source email, deadline, proposed repair.
2. Verify account via known bookmark / authenticated link — not untrusted email links when a direct URL is known.
3. Studio CUA connectivity + fresh snapshot before every action.
4. Inspect failure reason, plan, amount, existing method.
5. Secrets via himitsu/op; fill + save method; stop at charge click unless pre-approved.
6. Verify receipt / success / provider txn id before Done.

Full body: `references/payment-operations.md`. Drive loop: `studio-cua-drive`.
