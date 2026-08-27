---
name: vapi-phone-ops
description: >-
  Operate Cooper's Vapi phone stack — outbound AI calls (Levi Okada), live call control,
  warm-transfer-experimental with Levi fallback, DTMF/IVR, mid-call HITL (ask_cooper),
  BB iMessage status (not Twilio SMS), analytics/CLI, and payment guardrails.
version: 3.3.3
metadata:
  hermes:
    tags: [vapi, phone, telephony, analytics, transfer, twilio, elevenlabs, hitl, dtmf]
    category: communication
    related_skills: [communications, bluebubbles-studio, studio-cua-driver]
---

# Vapi phone ops (outbound · control · analytics · HITL)

Stack: **Vapi** → **Twilio** → **ElevenLabs**. Permanent assistant **Personal Concierge**.
Persona **Levi Okada**. One-off jobs: prefer `assistantOverrides`; standing prompt holds
identity/voice/billing for all calls.


## iMessage identity (critical)

**Always send as Studio** `cooperton42391@gmail.com` via `https://bb-api.cm.xyz`.

**Never** use Mac\end Pro local Messages / osascript (`koutaroum@icloud.com`) for Hermes→Cooper pings — that account can message itself / look like a self-chat.

HITL (`ask_cooper_server.py`) refuses sends unless `detected_imessage` matches `cooperton42391@gmail.com`.

If send fails with **Private API Helper is not connected**, fix helper on Studio BB (or re-enable Private API); do not fall back to local Messages.

## Identity (standing)

- **Name:** Levi Okada — always a last name when asked.
- **Relation (immediate):** "I'm Levi Okada, Cooper Maruyama's assistant." No authorization monologue unless pressed.
- **First message:** "Hey — Levi, Cooper's assistant."
- Callback: Cooper (310) 989-7067 · me@cooperm.com.

## Voice (user preference — NON-NEGOTIABLE)

- **Concise.** Real person, not call-center script.
- **Do NOT parrot** what the agent just said. No "just to confirm you said…".
- Don't recap booking/payment every turn — only correct errors or answer direct asks.
- Prefer "got it" / "sure" / "yep" / "one sec" then the next needed fact.
- No stacked thanks/apologies; no hold narration ("still holding, thank you").
- Yes/no first, then one short clause. One goodbye and hang up — don't reopen.

## Credentials

1Password item **`vapi`** (use non-interactive 1P — never bare biometric `op`):
```bash
himitsu exec op-service-account/token -- bash -lc \
  'OP_SERVICE_ACCOUNT_TOKEN=$TOKEN op item get vapi --vault <vault> --format json'
# Service accounts REQUIRE --vault.
```
- `credential` = private key → `Authorization: Bearer` / CLI
- Also: `twilio-sid` / `twilio-token` (SMS often useless — see Messaging)

Or:
```bash
export PATH="$HOME/.vapi/bin:$HOME/.local/bin:$PATH"
source ~/.hermes/skills/communication/communications/scripts/vapi_env.sh
```

Standing defaults (verify live if stale):
- `phoneNumberId`: `68092f67-e7eb-4df9-8a39-e930eb99270d`
- `assistantId`: `86a092df-2332-4092-bf2d-2cd02c66ac4a`
CLI: `~/.vapi-cli.yaml` (600). Install: `curl -sSL https://vapi.ai/install.sh | bash`.

## Outbound call workflow

1. **Gather up front:** callee E.164, goal, facts (names, PNR, DOB, dates), fee tolerance, date preference order, guardrails, warm-transfer number, whether payment authorized this call.
2. Payload from `communications/templates/` (`vapi_call_flight_change_warm_transfer.json` etc.) with `assistantOverrides`.
3. Hold-proof overrides:
   - `"firstMessageMode": "assistant-waits-for-user"` — **required** or talks over IVR
   - `"maxDurationSeconds": 7200`, `"silenceTimeoutSeconds": 3600`
4. Tools: existing `toolIds` (dtmf, ask_cooper) + warm-transfer tool in override — **don't duplicate** a builtin dtmf tool (duplicate tools → call create errors).
5. `POST https://api.vapi.ai/call` → keep `id`, `monitor.listenUrl`, `monitor.controlUrl`.
6. **Status text via BlueBubbles**, not Twilio SMS (error **30034** A2P). See skill **bluebubbles-studio**.
7. Monitor: `watch_call.sh <call_id>` background + `notify_on_complete=true`.
8. **Don’t declare failure until the log is checked** — see next section. Success may be
   called early when evidence is already conclusive.

### Call outcome: success may be early · failure only after the log

**Success (OK to decide early)** when you already have concrete success evidence, e.g.:

- live transcript just captured the needed fact (`001…` ticket, ticketed conf, USD amount)
- user confirms mid-call the goal is done
- structured artifact clearly has the payload

You may proceed to the next step on success without waiting for our watcher/report — still
prefer a quick `GET /call/<id>` when cheap, but don’t block progress.

**Failure (NOT allowed until log checked).** Never mark failed / give up / redial “as
failed” / say “no digits” / open a replacement path *as if the prior call failed* based only on:

- watcher summary one-liners
- `endedReason` alone (`silence-timed-out`, `customer-ended-call`, `call-deleted`, …)
- cost / short duration
- mid-call empty `messages`
- a *later* call’s outcome (VM leave-behind does **not** mean the earlier live pickup failed)
- “we DELETEd it so it didn’t count”

**Before any failure determination**, for **every** relevant call id (not just the latest):

1. `GET https://api.vapi.ai/call/<id>` (or `vapi_analytics.sh get <id>`).
2. Read full **`messages` / `transcript` / `analysis`** end-to-end.
3. Extract facts: `001\d{10,}`, PNRs, amounts, “I have the ticket number”, spoken digits.
4. Only then say fail / miss / no-op.

Skeleton (run before claiming failure):

```bash
source ~/.hermes/skills/communication/communications/scripts/vapi_env.sh
curl -sS -H "Authorization: Bearer <REDACTED>" \
  "https://api.vapi.ai/call/$CALL_ID" | python3 -c '
import sys,json,re
c=json.load(sys.stdin)
print(c.get("status"), c.get("endedReason"), c.get("cost"))
raw=json.dumps(c)
print("001:", re.findall(r"001\\d{10,14}", raw))
for m in c.get("messages") or []:
    role=m.get("role"); t=(m.get("message") or m.get("content") or "")
    if role in ("bot","user","assistant") and t:
        print(f"{role}: {t[:300]}")
'
```

If YOU issued `DELETE` / `end-call` mid-flight: still `GET` that id after it settles —
live legs can keep writing transcripts after control returns. The deleted call
`019fb465-5f72-…` still held ticket `0012342708964` after DELETE; ignoring it was wrong.

**Spoken-digit capture (user said “Levi got it”):** Prefer full `GET /call/<id>` over watcher
summary. Extract with `001\d{10,14}` on the JSON **and** read user turns that spell digits
(“zero zero one two three…”). Do not trust Levi’s abbreviated readback alone if it drops a leading zero.

**Online verify after phone-captured digits (CRITICAL):** A call can “successfully” capture a
13-digit string that is still **wrong** (STT). Before booking/payment against that number,
run AA Find travel credit with verified field sticky + submit. Session: clean lookup of
Levi-captured `0012342708964` (Reynolds + DOB) returned empty form → Cooper: **number is wrong**.
Treat phone-captured ticket/credit # as hypothesis until aa.com or email confirms.

**Delete held live call with payload risk:** If Cooper says “VM only / kill interactive,”
still `GET` the killed id before treating the thread as empty — and before starting a second
dial whose VM summary might overshadow the first success.

**POST /call transport:** Python `urllib` can get Cloudflare **1010** while `curl` returns 201.
Prefer `curl --data-binary @payload.json` for create.

### Prompt sections (minimum)

Identity/authority (Levi Okada, short) → GOAL → facts → IVR/DTMF/phonetic → silent hold → **after live human: warmTransfer once** → if transfer fails stay and finish → payment only if authorized → WRAP-UP. DO NOT: SSN, invent PAN, parrot, multi-cancel loops.

**Codes:** slow character-by-character + **phonetic** (W whiskey / S sierra / Z zulu …). Letter-soup → garbage like `WSZTVR4ALAX2` / IVR hangup.



## Knowledge base (query-cooper-records)

Files on Vapi (local copies `~/.hermes/vapi/kb/`):

| File | Contents |
|---|---|
| `cooper-contacts-addresses.md` | Phones, emails, home Apt 715 billing, condo 1810 AT&T |
| `cooper-payment-methods.md` | Amex Platinum primary + Coinbase One backup (full card fields) |
| `levi-tools-and-ops.md` | Tool when/don't + IVR habits |

- Tool id: see `~/.hermes/vapi/kb/manifest.json`
- Standing prompt instructs Levi to **query before inventing** address/email/card.
- Re-upload + patch fileIds when facts change.

## HITL ask_cooper (durable)

- Server LaunchAgent: `dev.hermes.ask-cooper` → `:8788`
- Public: `https://ask-cooper.cm.xyz/vapi/tools` (named CF host on Pro multi-ingress tunnel w/ bb-hook — HMS plist must not clobber multi-host yaml)
- Slack DM: `D0BG4HJ47GE` (primary offline reply channel when BB send is down)
- **Reply channels (all accepted):**
  1. **iMessage** back to the HITL bubble from Cooper's numbers (`+1310…7067` / `+1206…2027`) — polled from BB webhook inbox on Pro (`bb-hook` `/messages`). Notify text must say reply *to this iMessage*.
  2. Slack DM to hermes_bot
  3. `POST /reply` `{"id","answer"}` (include id if multiple open)
- Send path refuses anything other than Studio outer id `cooperton42391@gmail.com`. No Pro Messages fallback.
- Tool schema extractions must include top-level `toolCallList` (not only nested message shapes).

## Tool usage (teach the model — don't leave names only)

Standing prompt and each tool `function.description` must explain **what / when / don't**.

| Tool | What | When | Don't |
|---|---|---|---|
| **dtmf** | Keypad tones to the *other* party | IVR "press 1/2/0" | Spelling PNR to a human; messaging Cooper |
| **ask_cooper** | Blocking Slack question (~90s wait) | Overspend, itinerary fork, cardholder after 2 declines, gap in brief | IVR, routine chat, status-only |
| **text_cooper** | Fire-and-forget short status iMessage | Milestones (hold, agent, declined, ticketed) | Questions needing answers; PANs |
| **warmTransferToHuman** | Warm transfer; cancel → Levi stays | **Once**, after live human greets | During IVR/hold; transfer loops |

On call create: keep standing `toolIds` + add warm-transfer via `tools` array without duplicating builtin dtmf.
If HITL tunnel dies, `ask_cooper`/`text_cooper` server.url must be re-PATCHed.

## Transfers

| Mode | Behavior |
|---|---|
| **warm-transfer-experimental** (preferred) | Only after live human greets. Miss/VM/timeout → cancel, Levi stays (`endCallAfterSpokenEnabled: false` on request-failed). |
| Cold `control.type=transfer` | Levi leaves. End `assistant-forwarded-call`. No reconnect / no further control. |
| Conference rejoin after drop | **Not** stock Vapi — custom Twilio Conference. |

Templates: `vapi_warm_transfer_tool.json`, `vapi_call_flight_change_warm_transfer.json`.

**Pitfalls:** Transfer during IVR parks the handoff number in queue. No bridged-leg transcript after forward. Restate PNR/DOB/goal to the human on 206 offline if needed.

## IVR / DTMF

- Short openers + **dtmf tool** for press-1/2/0.
- Twilio PSTN: leave **SIP INFO DTMF off** (RFC 2833 default).
- **keypadInputPlan** (digits *inbound to* Levi) ≠ outbound dtmf — leave **off** for airline outbound.
- If tree loops on conf/code: 0/rep sooner; don't try five free-speech retries.

## Messaging (status to 206 / Cooper)

- Twilio SMS from Vapi long code → often **30034** undelivered. Do not rely on it.
- Prefer BlueBubbles: API `https://bb-api.cm.xyz`, webhook/inbox `https://bb-hook.cm.xyz` (skill **bluebubbles-studio**).
- Send short hold/milestone updates at call start and material changes. Never put PANs in texts.

## Mid-call HITL

- **ask_cooper** (blocking server tool): Slack via hermes_bot → DM **D0BG4HJ47GE** (Cooper×hermes_bot IM, not openclaw). Reply in DM or `POST /reply`. Timeout ≈90s → stay on existing guardrails.
- **text_cooper**: fire-and-forget short status (BB). Tunnel URL on tool `server.url` dies when quick tunnel restarts — PATCH after restart.
- Live control while `in-progress` on `monitor.controlUrl` (no Bearer):

| type | Use |
|---|---|
| `say` | Speak now |
| `add-message` | Silent policy (`triggerResponseEnabled: false` on hold) |
| `transfer` / `end-call` | Bridge / hang up |

Stuck empty-transcript in-progress: `end-call` → if sticky, Vapi DELETE call → confirm no other live calls; kill watchers.

## Payment

Only when **this call** authorizes payment.

- Default **Amex Platinum** (1P vault `cm`):
  ```bash
  himitsu exec op-service-account/token -- bash -lc \
    'OP_SERVICE_ACCOUNT_TOKEN=$TOKEN op item get nj33napkeiybo5o4fezookdb4i --vault cm --format json'
  ```
- Cardholder name may be **Koutarou Maruyama** (not Cooper). Need cardholder → call Cooper (310) 989-7067 / warm-transfer. Don't bluff.
- Prefer standing assistant billing block over mid-call inject (inject can be ignored if model locked on another card).
- **Stop after 2 hard declines.** Never invent PAN. Scrub temp files after inject.
- Don't redial AA after messy cancel/credit without **explicit** user go-ahead.
- **Attempt budget (user preference):** if Levi is not successful after **2 failed outcomes**, stop and review with Cooper — no autopilot thrash. **Callback-queue / hold-your-place** establishes a pending AA callback (not a thrash fail and not auto-redial while awaiting). IVR conf STT miss alone is a fail only if the call ends without a human path.
- **Online verification first when phone is messy:** AA manage booking / Find trip. Confirmed 2026-07-29: **WSZTVR status Canceled** on aa.com (`…/cancel?recordLocator=WSZTVR`). Prefer travel-credit or new book path; do not assume still ticketed Jul 30 / Aug 2.

## Analytics + CLI

```bash
SCRIPTS=~/.hermes/skills/communication/communications/scripts
$SCRIPTS/vapi_analytics.sh summary|ends|cost|calls|get <id>
```

- Analytics body `{"queries":[...]}`; **`groupBy` must be an array**.
- CLI `vapi call list` (0.2.1) can schema-drift; use analytics `calls` or `GET /call`.
- `curl | python3 <<'PY'` steals stdin — temp file or `python3 -c`.

## Related paths

- Portal: https://dashboard.vapi.ai/
- Docs: https://docs.vapi.ai/cli · warm-transfer · DTMF
- **bluebubbles-studio** — iMessage transport
- **communications** — multi-channel map + scripts/templates
- Support: `references/analytics-cli.md`, `references/live-control-and-transfer.md`, `references/warm-transfer-and-hitl.md`, `references/call-outcome-and-logs.md`, `references/call-outcome-discipline.md`, `references/digit-and-outcome-discipline.md`
- **bluebubbles-studio** references: `imessage-vs-twilio.md`, `darwin-host-and-rebuild.md`
