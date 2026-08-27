# Vapi call ops checklist (production)

## Preflight

- [ ] Goal one sentence; confirm pay authorize Y/N and fee cap
- [ ] Warm handoff number confirmed (E.164)
- [ ] Private key via `source …/vapi_env.sh` (not bare `op`)
- [ ] Card loaded non-interactively if pay: `himitsu exec op-service-account/token` + `op … --vault cm`
- [ ] Override restates **Levi Okada** + short relation line + **brief voice rules**
- [ ] Tools: at most **one** `dtmf`; warm-transfer if handoff; HITL if pay-sensitive
- [ ] `keypadInputPlan.enabled: false`; SIP INFO DTMF off (Twilio PSTN)
- [ ] Status ping path ready (Studio BB/iMessage) — do not rely on Twilio SMS alone

## After POST /call

- [ ] Save `id`, `controlUrl`
- [ ] Scrub any temp JSON that contained full PAN
- [ ] Status iMessage to handoff contact
- [ ] `watch_call.sh` background + notify

## During

- [ ] Phonetic conf codes; DTMF for press-1/2/0
- [ ] Warm transfer only after **live human** greets (once)
- [ ] `ask_cooper` before large fees / irreversible cancel without payment path
- [ ] Two card declines → stop thrashing
- [ ] Cardholder required → call Cooper (310) 989-7067 / warm-transfer

## After end / mess

- [ ] Zero active outbound calls (`GET /call` or analytics helper)
- [ ] Verify airline app/email/PNR before redial (esp. after cancel-for-credit)
- [ ] Kill watcher; report confs, amounts, ticketed Y/N, next call path

## Kill sequence

1. controlUrl stop `add-message` + `end-call`
2. `DELETE /call/{id}` if stuck emptytranscript
3. Twilio `Status=completed` on `phoneCallProviderId`
4. Confirm no other queued/in-progress

## Whale lessons (2026-07 AA)

- Long cancel→credit→unpaid rebook left booking messy — always verify before redial
- Invoice/payment inject mid-call can fail if model already committed to another card narrative
- Empty live transcript + stuck `in-progress` is real — DELETE works when end-call lags
