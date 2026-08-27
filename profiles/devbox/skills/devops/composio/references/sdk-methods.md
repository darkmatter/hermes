# Composio SDK Method Reference

Extracted from `@composio/core@0.10.0` and `@composio/client@0.10.0` source.

## Composio Instance Methods

```
composio.authConfigs.list()                    → paginated list of auth configs
composio.connectedAccounts.list(query?)         → paginated list of connected accounts
composio.connectedAccounts.link(userId, authConfigId, options?)  → create OAuth link
composio.connectedAccounts.initiate(userId, authConfigId, options?) → alias for link
composio.connectedAccounts.waitForConnection(id) → poll until ACTIVE
composio.connectedAccounts.get(id)              → retrieve by ID
composio.connectedAccounts.delete(id)           → soft-delete
composio.connectedAccounts.refresh(id)          → refresh credentials
composio.connectedAccounts.updateStatus(id, ...) → enable/disable
composio.connectedAccounts.enable(id)
composio.connectedAccounts.disable(id)
composio.connectedAccounts.update(id, ...)
composio.create(userId)                        → tool router session
```

## Connected Accounts Link Response

```typescript
interface ConnectionRequest {
  id: string;              // "ca_..." connected account ID
  status: "INITIATED" | "ACTIVE" | "DISABLED" | ...;
  redirectUrl: string;     // URL to send user to for OAuth
}
```

## Auth Config Shape

```typescript
interface AuthConfig {
  id: string;              // "ac_..."
  name: string;
  toolkit: { slug: string; logo: string };
  authScheme: "OAUTH2" | "OAUTH1" | "API_KEY" | "BEARER" | "BASIC" | "DCR_OAUTH";
  noOfConnections: number;
  status: "ENABLED" | "DISABLED";
  isComposioManaged: boolean;
  credentials: <REDACTED>
}
```

## Known Auth Configs (as of 2026-06-09)

| ID | Name | Toolkit | Scheme | Managed | Connections |
|---|---|---|---|---|---|
| `ac_EGarnY8BniOm` | github-oliu9y | github | OAUTH2 | yes | 1 (ca_iz0FUDtCiUaw, bearer, ACTIVE) |
| `ac_Iw3pgdqfK2y9` | gmail-cooper-darkmatter | gmail | OAUTH2 | yes | 1 (ca_zmVgZXeN2nQW, Bearer, ACTIVE) |
| `ac_xcxJH3q8_ufS` | slack-x19r5m | slack | OAUTH2 | yes | 2 (ca_8fFPmpaCfb0B user ACTIVE, ca_G2L5JAlvOuYL user ACTIVE) |
| `ac_mY7qk2iuplTK` | mini cooper | slackbot | OAUTH2 | no | 3 bot connections (ca_7ArFskYXBqL0, ca_1uXTodyE3WHE, ca_-5EhGmAQEECe all ACTIVE) |
| `ac_SMjuEeZLEYDF` | slackbot-v96r9q | slackbot | OAUTH2 | yes | 1 (ca_s8BkZSBDxUlB, bot, ACTIVE — tool router-managed) |
| `ac_xrdicJpg3iZf` | slackbot-y7m2t3 | slackbot | OAUTH2 | yes | Composio-managed slackbot config |

Note: The `slackbot` toolkit slug is used for Slack bot/app connections (as opposed to the `slack` slug for user-level connections). The bot auth config is NOT Composio-managed — it uses a custom Slack app ("mini cooper") with its own client_id/client_secret.

## Tool Router Session Execution

The session created by `composio.create(userId)` exposes an `execute()` method:

```typescript
// Search for tools by natural language query
const search = await session.execute("COMPOSIO_SEARCH_TOOLS", { query: "..." });
// Returns: data.results (tool schemas + plans), data.session.id, data.toolkit_connection_statuses

// Execute a specific tool by its slug (e.g., SLACK_LIST_ALL_CHANNELS)
const result = await session.execute("SLACK_LIST_ALL_CHANNELS", { limit: 200 }, { sessionId });
// Response shape varies by tool; check data.* for the primary payload
```

Common Slack tool slugs:
- `SLACK_LIST_ALL_CHANNELS` — list channels with filters (limit, types, cursor, exclude_archived)
- `SLACK_FIND_CHANNELS` — search channels by name/topic/purpose
- `SLACK_RETRIEVE_CONVERSATION_INFORMATION` — get channel metadata by ID
- `SLACK_LIST_CONVERSATIONS` — list DMs/MPIMs as well as channels
- `SLACK_TEST_AUTH` — verify auth and get identity info
- `SLACK_OPEN_DM` — open/get DM channel with a user (returns channel ID)
- `SLACK_SEND_MESSAGE` — send a message (use `markdown_text`, NOT `text`)
- `SLACK_SCHEDULE_MESSAGE` — schedule a message for later
- `SLACK_FETCH_CONVERSATION_HISTORY` — read recent messages from a channel
- `SLACK_JOIN_AN_EXISTING_CONVERSATION` — join a channel (requires `channels:join` scope)

Slackbot tool slugs (bot token, separate toolkit):
- `SLACKBOT_SEND_MESSAGE` — send as the bot (requires bot in channel)
- `SLACKBOT_FIND_CHANNELS` — search channels visible to the bot
- `SLACKBOT_JOIN_AN_EXISTING_CONVERSATION` — bot joins a channel (requires `channels:join` scope on the Slack app)

**Important:** `SLACKBOT_*` tools require activating the `slackbot` toolkit via `COMPOSIO_MANAGE_CONNECTIONS` before first use in a session.

## REST API Endpoints (v3.1)

- `GET /api/v3.1/connected_accounts` — list connected accounts
- `POST /api/v3.1/connected_accounts` — create (deprecated for Composio-managed OAuth)
- `POST /api/v3.1/connected_accounts/link` — create auth link (preferred for OAuth)
- `GET /api/v3.1/connected_accounts/{id}` — retrieve
- `DELETE /api/v3.1/connected_accounts/{id}` — soft-delete
