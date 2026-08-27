# Airline rebook lessons (AA / Telavaya WSZTVR)

Session-hardened notes for LAX→LHR date changes. Facts change — verify PNR before acting.

## Outcomes seen

| Path | Result |
|---|---|
| IVR free-speech conf | AA mangled `WSZTVR` → `WSVTVR` / `WFZTVR` / `w s v t v r`; hangups |
| Phonetic + DTMF | Still hard; force 0/rep after ~3 fails; Levi once said wrong letters mid-phonetic |
| Long agent call | Cancel→credit vs change fee conflict; unpaid rebook; not ticketed (~$5–6) |
| Payment call | Remaining due ~$697–$906 band quoted; Amex multi-decline; not ticketed |
| Low-drama retry | IVR → queue → **callback** to Cooper (310) 989-7067; ~$0.48; not ticketed |

## Retry budget (user preference)

1. Cap **2 failed dial outcomes**, then **stop for human review**.
2. Live monitor every dial (`watch_call.sh` + status pings).
3. **Callback-in-queue does not spend a thrash-fail** — do **not** redial while AA holds place and will call Cooper’s cell. Status: `awaiting_aa_callback` until callback finishes or user cancels that path.
4. User force-kill of runaway = stop; review before rebook.

## Online preferred after phone thrash

- No dedicated AA booking tool — use browser / computer_use; **gate payment submit**.
- Verify PNR/credit first: Find trip → last **Reynolds** · DOB **02/20/1991** · conf **WSZTVR**.
- Prefer apply travel credit if Jul 30 canceled; goal **Aug 2** BA 6935-style if inventory.
- Card: standing Platinum only unless brief says otherwise; cardholder name may be **Koutarou Maruyama**.

## Standing vs call override vs Files/KB

Context is **not** a lone `instructions.md` file:

1. **Standing** assistant system prompt — identity, voice, billing rules, tool when/don’t, KB pointer
2. **Per-call** `assistantOverrides.model.messages` — goal, PNR, spend caps, stop rules
3. **Vapi Files / Knowledge Base** (query tool) — bulky reference: addresses, emails, cards/backups, ops. Retrieval on demand, not always injected. Keep live secrets call-scoped where possible; still teach model **when to query**.

## Tool teaching

Name-only tools undersued. Standing + each `function.description` need what/when/don’t (dtmf, ask_cooper, text_cooper, query-cooper-records, warmTransferToHuman). Overrides that set `model.tools` must re-include standing toolIds.

## HITL replies

Order: (1) iMessage reply on **Studio BB** thread (`cooperton42391@gmail.com` only — never Pro Messages/osascript), (2) Slack `D0BG4HJ47GE`, (3) `POST /reply`. Extractor must handle top-level toolCalls **and** `message.toolCallList`. Durable URL: `https://ask-cooper.cm.xyz/vapi/tools`.

## Status messaging

206 / Cooper hold updates via Studio BB iMessage — **not** Twilio SMS from Vapi long code (**30034** A2P).

## Brief card (verify live)

- Passenger: Telavaya Reynolds · DOB 1991-02-20
- AA `WSZTVR` · BA `BRSK4R`
- Prefer Aug 2 LAX→LHR; travel credit possible if Jul 30 canceled
- Handoff +1 (206) 954-2027 · Cooper (310) 989-7067

## Related

`vapi-call-ops` · `bluebubbles-studio` · `financial-operations` (1P SA + gated pay)
