# Vapi Provider Recipe

This is the tested provider-specific implementation for `outbound-phone-operations`. Keep the main skill provider-neutral.

## Current environment wiring

As verified on 2026-08-26:

- API base: `https://api.vapi.ai`
- Create call: `POST /call`
- Poll one call: `GET /call/{call-id}`
- Active Twilio-backed outbound phone-number ID: `68092f67-e7eb-4df9-8a39-e930eb99270d`
- Vapi API credential: 1Password item `op://dev/vapi/credential`
- 1Password non-interactive service-account token: Himitsu path `op-service-account/token`
- `op` is **not** on the Hermes default PATH. Use `/nix/store/l1k64x85iqsq9xhmsnjf20k195c521qd-1password-cli-2.38.1/bin/op` (or `find /nix/store -name op -type f` if that store path rotates). A missing `op` is a PATH problem, not a missing credential.
- Hermes zsh has a read-only `status` variable. Never assign `status=...` in poll loops; use `call_state`.

The service account can read the `dev` vault but not the personal `Private` vault. Mac-local notes may mention `op://Private/vapi/credential`; do not assume that path is readable from the service account. Discover accessible vaults/items with metadata-only `op vault list` and `op item list` rather than printing secret fields.

A saved personal-assistant ID also exists, but routine vendor calls should use a transient assistant. Its standing prompt may contain unrelated sensitive personal and payment data.

## Secret-safe credential bridge

Bind Himitsu to Cooper’s home and keep both tokens in variables:

```bash
export HOME=~
export HIMITSU_AUTO_PULL=false
export PATH="~/.nix-profile/bin:/nix/store/l1k64x85iqsq9xhmsnjf20k195c521qd-1password-cli-2.38.1/bin:$PATH"

SERVICE_TOKEN=<REDACTED>
VAPI_KEY=<REDACTED>
  op read 'op://dev/vapi/credential')"
unset SERVICE_TOKEN
```

Rules:

- never enable shell tracing (`set -x`);
- never print either variable;
- never write the API key into a JSON request file;
- pass the key only in the HTTP `Authorization` header;
- `unset VAPI_KEY` after the request/poll sequence.

A safe auth/resource probe prints selected metadata only:

```bash
curl -sS \
  -H "Authorization: Bearer <REDACTED>" \
  "https://api.vapi.ai/phone-number/$PHONE_NUMBER_ID" \
| jq '{id, provider, status, createdAt}'
```

Do not dump a saved assistant object. If resource inspection is needed, select fields such as `{id,name,createdAt,updatedAt}` and omit model messages, tools, server URLs, credentials, and private metadata.

## Create a transient outbound call

Start from `templates/vapi-outbound-call.json`, replace placeholders, and submit:

```bash
curl -sS -X POST 'https://api.vapi.ai/call' \
  -H "Authorization: Bearer <REDACTED>" \
  -H 'Content-Type: application/json' \
  --data-binary @vapi-outbound-call.json \
  -o vapi-call-response.json

CALL_ID="$(jq -r '.id' vapi-call-response.json)"
test -n "$CALL_ID"
```

A successful create currently returns HTTP 201 with status `queued`. Save the ID before polling.

## Recommended assistant fields

Use:

- `firstMessageMode: "assistant-waits-for-user"` so the assistant can distinguish an IVR, voicemail, and live greeting;
- a narrow system message with the exact goal and negative authority;
- model tools `[{"type":"dtmf"},{"type":"endCall"}]`;
- a voice and transcriber known to work in the account;
- `maxDurationSeconds` and `silenceTimeoutSeconds` bounded for the task;
- metadata that identifies the purpose but contains no secrets.

Do not copy a broad personal assistant’s full model configuration into the transient request. Reuse only safe provider/model/voice identifiers that are required for operation.

## Poll until transcript finalization

Vapi call status typically moves through `queued` → `in-progress` → `ended`. Poll `GET /call/{id}`. After `ended`, allow several bounded re-fetches if `.transcript` is initially empty.

```bash
last=''
ended_polls=0
for _ in $(seq 1 110); do
  curl -sS \
    -H "Authorization: Bearer <REDACTED>" \
    "https://api.vapi.ai/call/$CALL_ID" \
    -o vapi-call-final.json

  status="$(jq -r '.status // "unknown"' vapi-call-final.json)"
  if [ "$status" != "$last" ]; then
    printf 'call_status=%s\n' "$status"
    last="$status"
  fi

  if [ "$status" = ended ]; then
    ended_polls=$((ended_polls + 1))
    transcript_len="$(jq -r '(.transcript // "") | length' vapi-call-final.json)"
    if [ "$transcript_len" -gt 0 ] || [ "$ended_polls" -ge 4 ]; then
      break
    fi
  fi

  sleep 5
done
```

Inspect only the needed final fields:

```bash
jq '{
  id,
  status,
  endedReason,
  startedAt,
  endedAt,
  transcript,
  summary: (.analysis.summary // .summary // null),
  successEvaluation: (.analysis.successEvaluation // null)
}' vapi-call-final.json
```

Use `.transcript` as primary evidence. Provider summaries and `successEvaluation` can be wrong about the user’s definition of completion—for example, they may label a voicemail as successful even though the user asked for a live price.

## IVR and voicemail prompt clauses

Include these operational clauses in the transient assistant:

```text
First classify IVR, voicemail, or live person.
For an IVR, wait for the complete menu and use DTMF without speaking over it.
Once a human answers, disclose AI identity and transcription and obtain consent.
If the target department goes to voicemail, leave a short message only if useful,
then follow the post-recording prompts and use DTMF to save it.
Do not treat voicemail as completion when the goal requires an answer.
```

If a department extension reaches voicemail during business hours, call a distinct official route such as the corporate number or general operator. Keep the recovery bounded and avoid repeatedly dialing the same mailbox.

## Verified response shape

Fields observed in completed Vapi call objects:

- `.id`
- `.status`
- `.endedReason`
- `.startedAt`
- `.endedAt`
- `.cost`
- `.transcript`
- `.analysis.summary`
- `.analysis.successEvaluation`

Do not assume the summary is available at the exact moment telephony ends; the transcript/artifact grace polling handles this race.
