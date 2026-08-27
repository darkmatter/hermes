# Cron JSON Output Schema

Each cron that wants to render in the feed writes a JSON file to `~/.hermes/feed/cron-json/<name>.json`.

## Format

```json
{
  "source": "human-readable name (e.g., 'Daily Comms Triage')",
  "run_time": "ISO timestamp of when the cron ran",
  "items": [
    {
      "type": "email|slack|imessage|github|linear|x_post|hn_post|alert|task",
      "source": "gmail|slack_dm|slack_channel|imessage|github_pr|github_issue|linear_issue|x|hackernews|...",
      "priority": "high|medium|low",
      "title": "Short title (1 line)",
      "summary": "One-line summary of why this needs attention or is interesting",
      "action_needed": true,
      "action_hint": "What to do (e.g., 'Reply to email', 'Review PR', 'Archive as spam')",
      "link": "URL if available, else empty string",
      "timestamp": "ISO timestamp or epoch of the item, else empty string",
      "author": "Who sent/posted it (optional)",
      "meta": {}
    }
  ]
}
```

## Rules

- Only include items that need attention or are genuinely interesting. Skip noise.
- Keep `summary` to one line (~100 chars max).
- `action_needed: false` for FYI/interesting items; `true` for things requiring a response.
- Write the file at the END of your run, after all analysis is complete.
- If there's nothing worth surfacing, write `{"source": "...", "run_time": "...", "items": []}`.
