# Staging paydec cards

## Chat rules (Cooper preference)

- ≤5 non-checkbox items per chat update
- Pure money keep/cancel → **feed cards**, not chat walls
- Dated deadline table separate from pay queue
- Once on feed, do not re-list the same paydec as a chat wall

## recommendations.json choice template

```json
{
  "t_XXXX": {
    "why_blocked": "Pay/Don't-pay — <service> <amount>",
    "category": "decision",
    "actions": [
      {
        "kind": "choice",
        "label": "Pay or don't pay?",
        "options": [
          {
            "label": "✅ Pay",
            "recommended": false,
            "prompt": "For kanban task t_XXXX (<title>): Cooper chose PAY. Account: …. Use official billing portal (not email links). Studio CUA + SA op. Stop before charge click unless amount/method already approved in-thread. Comment receipt/evidence, then complete card and mark feed response done."
          },
          {
            "label": "❌ Don't pay",
            "recommended": true,
            "prompt": "For kanban task t_XXXX (<title>): Cooper chose DON'T PAY. Do not charge. Cancel subscription / disable auto-renew via official portal when possible. Label related threads Triage/Done + archive. Comment decision; complete card; mark feed response done."
          }
        ]
      }
    ]
  }
}
```

## Rebuild

```bash
python3 ~/.hermes/scripts/build-feed.py
# pushes https://feed.cm.xyz when tokens available
```

## Idempotency keys

`paydec-<vendor-slug>-YYYY-MM` so re-runs do not duplicate cards.
