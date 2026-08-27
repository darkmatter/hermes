# AA booking via Kernel (session notes)

## Auth
- Himitsu: `kernel-api-key`
- `export KERNEL_API_KEY="$(himitsu read kernel-api-key)"`

## Form IDs (advanced search)
| Control | Selector |
|---|---|
| Trip type | `#trip-type` (mat-select) → One way / Round trip / Multi city |
| Origin | `#matOriginAirport` |
| Destination | `#matDestinationAirport` |
| Depart date | `#matDepartureDatePicker` |
| Search | `button` text exactly `Search` |

Do **not** use `getByLabel(/To/)` — matches **swap airports**.

## Working path (2026-07-31)
1. `browsers create --stealth -t 900 --start-url find-flights --name … -o json`
2. Playwright: One way → LAX → LHR → `08/02/2026` → Search
   (date: JS value events if input not clickable)
3. Land: `…/booking/choose-flights/1?sid=…` · Aug 2 from ~$836
4. Open first `Main One way from $836…more fare options`
5. Click `Select One way Main fare for $946` (Main product, not Basic)
6. Stay in Main; optional Continue as guest
7. Trip summary: **AA 6935** LAX 3:50p → LHR 10:15a+1 · **Total $945.50**
8. **STOP** before Purchase

## Profiles + HITL (validated same day)
```bash
kernel profiles create --name aa-cooper-test -o json
kernel browsers create --name aa-profile-hitl --profile-name aa-cooper-test \
  --save-changes --stealth -t 600 --start-url 'https://www.aa.com/' -o json
# seed cookies/localStorage via playwright execute
kernel browsers delete aa-profile-hitl   # saves into profile when --save-changes

kernel browsers create --name aa-profile-reload --profile-name aa-cooper-test \
  --stealth -t 300 --start-url 'https://www.aa.com/' -o json
# marker cookie + localStorage still present
```

### Live URL (always available when stuck)
```bash
kernel browsers view <session_id|name>
# or jq .browser_live_view_url from create/get -o json
```
- Create payload field: `browser_live_view_url`
- Re-fetch anytime; JWT present after 302 on viewer
- **AA cart `sid` expires** (`/booking/session-timeout`) — hand Cooper the **Kernel live** link, not a stale trip-summary URL

## Credit / ticket number
- PNR `WSZTVR` → canceled; not enough for Find travel credit
- Need **13-digit** `001…` / eCredit `00115`/`0012…`
- STT `0012342708964` **wrong** (clean Reynolds+DOB lookup empty — user-confirmed)
- Ask digits via **Studio BB → +12069542027** when that’s the ask (not 310 by default)

## Managed Auth (Gmail / site login)
See `references/managed-auth.md`. Profile `cooper-email` + domain `gmail.com` stood up for Cooper email; always print `hosted_url` immediately on `connections login`.

## Compare Studio cua
Kernel Playwright cleaner for Angular Material fares once ids known.
Studio cua for profile-bound **local** Chrome. Kernel for cloud + live-view HITL + optional remote profiles.
