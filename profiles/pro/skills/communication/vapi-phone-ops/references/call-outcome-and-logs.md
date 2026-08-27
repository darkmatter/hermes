# Call outcome discipline + log mining

User rule: **success may be early with hard evidence; failure only after full call log.**

## Always before “failed / no digits / they didn’t answer meaningfully”

1. Enumerate every call id this session touched (including deleted).
2. `GET /call/<id>` for each.
3. Mine:
   - `messages` / `transcript` / `analysis.summary`
   - regex `001\d{10,14}`
   - user turns with spoken digit words
4. Only then declare miss.

## Anti-patterns already hit

| Signal alone | Not enough for failure |
|---|---|
| Watcher `silence-timed-out` / VM summary | Earlier live pickup may still hold payload |
| `call-deleted` after operator kill | Transcript can finalize post-DELETE |
| Mid-call empty `messages` | Not proof of no conversation |
| Later VM call | Does not erase prior success |

Concrete: live Cooper pickup gave ticket spoken as “zero zero one two three four two seven zero eight nine six four” → **`0012342708964`**. Operator DELETE + VM redial + watcher VM summary almost buried it.

## Create-call tip

- Prefer `curl` POST JSON file for `https://api.vapi.ai/call` (CF 1010 on some Python clients).
