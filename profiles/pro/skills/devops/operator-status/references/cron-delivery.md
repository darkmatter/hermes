# Cron Delivery — Resolving the Hermes Bot's Slack DM Channel

When a cron's `deliver` target is broken (e.g. `origin` fails for CLI-created crons), set it to a specific platform destination. For Slack DMs, you need the Hermes gateway bot's DM channel ID with the target user — this is not the same as the user's Slack ID.

## Resolve the Hermes bot identity and DM channel

The Hermes gateway runs as a Slack bot. To find its identity and the DM channel with a specific user:

1. **Get the bot's identity** — call `auth.test` with the `SLACK_BOT_TOKEN` from `~/.hermes/.env`:
   ```bash
   set -a; source ~/.hermes/.env 2>/dev/null; set +a
   curl -s -H "Authorization: Bearer <REDACTED>" https://slack.com/api/auth.test
   ```
   Returns `user_id` (e.g. `U0AKFCM04G0`), `bot_id`, `team`, `team_id`. The bot's display name (e.g. "openclaw") is NOT the app name — it's whatever the Slack admin renamed it to.

2. **List the bot's DM conversations** — find the DM channel with the target user:
   ```bash
   curl -s -H "Authorization: Bearer <REDACTED>" \
     "https://slack.com/api/conversations.list?types=im&limit=50" \
     | python3 -c "
   import sys, json
   d = json.load(sys.stdin)
   for ch in d.get('channels', []):
       print(f'{ch[\"id\"]} user={ch.get(\"user\",\"?\")}')
   "
   ```
   Match the `user` field to the target user's Slack ID (e.g. Cooper is `U092MDGBK0R`). The channel ID (e.g. `D0AK02MKFRP`) is the `deliver` value.

3. **Set the cron's deliver target**:
   ```
   cronjob(action='update', job_id='<id>', deliver='slack:D0AK02MKFRP')
   ```

## Deliver value formats

| Value | Behavior |
|---|---|
| `local` | Silent — no delivery. Output saved to session only. |
| `origin` | Resend to the chat that created the cron. **Fails for CLI-created crons** ("no delivery target resolved"). |
| `slack:<channel_id>` | Post to a specific Slack channel or DM. Use a `D…` ID for DMs, `C…` for channels. |
| `telegram:<chat_id>` | Post to a Telegram chat. |
| `all` | Fan out to every connected home channel. |

## Pitfalls

- **`deliver: origin` is the silent killer.** The cron runs, the agent produces a report, and the report vanishes. `last_delivery_error` in `cronjob(action='list')` shows the failure, but `last_status` still says `ok` because the agent *did* complete — only delivery failed. Always check `last_delivery_error` when auditing crons.
- **Two different Slack bots.** The Hermes gateway bot (e.g. "openclaw") and a Composio Slack bot (e.g. "mini cooper") are different Slack apps with different bot tokens and different DM channel IDs. Don't confuse their DM channels — the Hermes `SLACK_BOT_TOKEN` in `.env` is for the gateway bot only.
- **Gateway must be running.** Delivery requires the Hermes gateway (`hermes gateway status`) to be active. If the gateway is down, cron output is saved to the session but not delivered.
