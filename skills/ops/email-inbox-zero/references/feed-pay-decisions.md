# Pay / Don't-pay → feed → D1

## When

Failed charges, renewals, past-due invoices, domain auto-renews — anything that is a pure **Pay vs Don't pay** checkbox. Not KYC forms, not human threads, not security review.

## Stage

1. One blocked `email-triage` card per vendor (or tight batch), `--idempotency-key paydec-<vendor>-YYYY-MM`.
2. `~/.hermes/feed/recommendations.json`:

```json
{
  "t_XXXX": {
    "why_blocked": "Pay/Don't-pay — <service> <amount>",
    "category": "decision",
    "actions": [{
      "kind": "choice",
      "label": "Pay or don't pay?",
      "options": [
        {"label": "✅ Pay", "recommended": false, "prompt": "… charge gate …"},
        {"label": "❌ Don't pay", "recommended": true, "prompt": "… cancel path …"}
      ]
    }]
  }
}
```

3. `python3 ~/.hermes/scripts/build-feed.py` (pushes prod when tokens present).

## Cooper UX

- https://feed.cm.xyz (prefer over localhost)
- Pick option → **Send to Hermes** (writes D1). No copy/paste.
- If options won't click: UI bug was `preventDefault` on composer — fixed in prod; hard-refresh.

## Agent execute

```bash
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --status pending
# optional: --claim
# execute Pay under financial-operations charge gate / Don't pay cancel path
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --done <id>
```

Auth: himitsu `feed/ingest-token` + `cf-access-client-id` / `cf-access-client-secret`.

## Chat discipline

- ≤5 non-checkbox action items per update
- Dated deadline table separate from pay queue
- Do not re-list paydec cards as chat walls once they are on the feed
