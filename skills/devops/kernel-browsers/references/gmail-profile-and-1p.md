# Gmail profile + 1Password (2026-07-31)

## What worked
1. Profile **`cooper-email`** (`ferrxe5t2ctgseagxkhfkdew`).
2. Browser **`cooper-gmail-hitl`** with `--save-changes`, start Google ServiceLogin → Gmail.
3. Cooper finished login via **live view** (`browsers view` / `browser_live_view_url`).
4. Playwright verified:
   - `https://mail.google.com/mail/u/0/#inbox` — **me@cm.xyz**
   - (same session had) `u/1` — **cooper@darkmatter.io**
   - Google cookies including `SID` / `__Secure-1PSID` (~55)
5. `browsers delete cooper-gmail-hitl` → recreate **`cooper-gmail-verify`** on same profile → **still logged in**.

## What did not work
| Attempt | Error / outcome |
|---|---|
| Managed Auth Hosted UI | `flow_status=FAILED`, `error_code=stuck_in_loop`, “Login flow stuck - page not advancing” |
| Relying on 1P auto for Gmail | Provider OK; **no Google/Gmail Login item** in SA-visible vaults |

## 1Password provider
```bash
export KERNEL_API_KEY=<REDACTED>
export OP_SA_TOKEN=<REDACTED>
kernel credential-providers create --provider-type onepassword \
  --name cooper-1p --token "$OP_SA_TOKEN" -o json
unset OP_SA_TOKEN
```
- Provider **`cooper-1p`** id example `tnlrgf0vmtdq0b9djajjb71b` (re-list if rotated).
- `credential-providers test` vaults: **cm, cooper, dev**.
- `list-items` (~36) had no google/gmail titles/URLs — add a Login item with `accounts.google.com` / `mail.google.com` in an SA vault before `--credential-provider cooperatives` auto helps Gmail.

Never print `ops_` tokens. No biometric `op` GUI.

## Operator preference
- Ask “can it give browser control?” → **yes**: `kernel browsers view` is the first-class fallback when Hosted UI fails or Cooper prefers driving the browser.
- Put the URL in the chat reply **before** long status polls.

## Day-to-day email vs Kernel Gmail UI
- Agent **read/triage mail**: prefer **gog**/Himalaya (API).
- Kernel Gmail profile: when a **browser UI** session is required (links only in Gmail, UI-only flows).
