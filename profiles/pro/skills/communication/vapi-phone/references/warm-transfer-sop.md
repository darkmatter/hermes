# Warm-transfer SOP (checklist)

## When to use
Support/reservations lines where Cooper wants a human (@206 default airline) connected **only after** a live agent, with **Levi fallback** if the human misses.

## Never use cold transfer when fallback is required
Cold: `POST {controlUrl}` `{"type":"transfer","destination":{"type":"number","number":"+1..."}}`
→ `endedReason=assistant-forwarded-call`; Levi gone; no auto-resume.

## Payload ingredients
1. `assistantOverrides.firstMessageMode = assistant-waits-for-user`
2. Long hold: `maxDurationSeconds=7200`, `silenceTimeoutSeconds=3600`
3. `model.tools[]` includes `transferCall` named `warmTransferToHuman`:
   - `destinations[0].transferPlan.mode = warm-transfer-experimental`
   - transferAssistant `maxDurationSeconds` ~75, cancel on VM/silence
   - built-ins `transferSuccessful` + `transferCancel`
   - message `request-failed.endCallAfterSpokenEnabled = false`
4. System prompt phases:
   - PHASE 1 IVR/hold alone
   - PHASE 2 human greet → `warmTransferToHuman` once
   - PHASE 3 on cancel → finish GOAL
5. Destination enum + number + SMS To must match.

## Call-day order
1. Confirm facts + handoff number with Cooper if ambiguity.
2. Strip `_comment` from JSON template → POST `/call`.
3. SMS handoff immediately on queued/in-progress.
4. `watch_call.sh <id>` background notify.
5. Report: endedReason, whether warm merge happened, transcript summary, case #s/fees.

## Templates (shared communications skill dir)
- `templates/vapi_call_flight_change_warm_transfer.json`
- `templates/vapi_warm_transfer_tool.json`

## Related endedReasons
- `assistant-forwarded-call` — cold forward completed (Vapi left).
- Warm cancel returns control to original assistant (continue TASK); watch for transfer tool messages in transcript.
