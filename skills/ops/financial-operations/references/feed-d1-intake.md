# Feed D1 intake for payment decisions

Cooper marks Pay/Don't-pay on https://feed.cm.xyz (**Send to Hermes**). Agents do **not** ask for clipboard paste.

## Poll

```bash
bun ~/git/darkmatter/feed/scripts/poll-responses.ts --status pending
```

Auth via himitsu: `feed/ingest-token`, `cf-access-client-id`, `cf-access-client-secret`.

## Execute

| Choice | Action |
|---|---|
| ✅ Pay | `payment-operations.md` / §6 Studio CUA; SA `op` only; **charge gate** |
| ❌ Don't pay | Official portal cancel / stop retries; mail → Done; no charge |

Then kanban evidence + `bun …/poll-responses.ts --done <id>`.

## 1P missing

If catalog `~/.hermes/op-sa-catalog.json` lacks the login/card: ask Cooper **as-needed** to move **that one title** into vault **`cm`**. Never biometric `op`.

See umbrella skill **`feed-decisions`** for staging + UI pitfalls.
