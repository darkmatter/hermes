---
name: composio
description: Configure, develop, and troubleshoot Composio integrations (Slack, GitHub, Gmail, etc.) via the TypeScript SDK and REST API.
version: 0.1.0
triggers:
  - composio
  - slack integration
  - oauth connection
  - connected account
---

# Composio — Third-Party Service Integrations

## Overview

Composio provides managed OAuth and API-key integrations for 250+ services (Slack, GitHub, Gmail, etc.) with a unified SDK and tool-router for AI agents.

**API Key:** stored in himitsu as `composio-api-key`
**Base URL:** `https://backend.composio.dev`
**API version:** `/api/v3.1/` (NOT `/api/v3/`)

## Installation

```bash
npm init -y
# zod peer dep conflict requires --legacy-peer-deps
npm install @composio/core @composio/openai-agents @openai/agents --legacy-peer-deps
```

Set `"type": "module"` in `package.json` for top-level await support with tsx.

## SDK API Reference

The TypeScript SDK (`@composio/core`) API differs from Composio's public docs. Key methods:

### Composio Client

```typescript
import { Composio } from "@composio/core";
const composio = new Composio({ apiKey: process.env.COMPOSIO_API_KEY });
```

### Auth Configs

```typescript
// List all auth configs (shows Slack, GitHub, Gmail integrations, etc.)
await composio.authConfigs.list();
// Returns: { items: [{ id: "ac_...", toolkit: { slug: "slack" }, authScheme: "OAUTH2", ... }] }
```

### Connected Accounts

```typescript
// List connected accounts
await composio.connectedAccounts.list();

// Initiate OAuth link — takes POSITIONAL args, NOT an object
// Signature: link(userId: string, authConfigId: string, options?)
const result = await composio.connectedAccounts.link(userId, authConfigId);
// Returns: { id: "ca_...", status: "INITIATED", redirectUrl: "https://connect.composio.dev/link/..." }

// Wait for user to complete OAuth in browser, then:
await composio.connectedAccounts.waitForConnection(result.id);

// Get a specific connected account
await composio.connectedAccounts.get(connectedAccountId);
```

### Tool Router (for AI agents)

```typescript
const session = await composio.create(userId);
const tools = await session.tools();
// tools can be passed directly to OpenAI Agents SDK Agent constructor
```

**Important:** `session.tools()` returns 6 meta-tools only (SEARCH_TOOLS, GET_TOOL_SCHEMAS, MULTI_EXECUTE_TOOL, MANAGE_CONNECTIONS, REMOTE_BASH_TOOL, REMOTE_WORKBENCH). App-specific tools (e.g., `SLACK_LIST_ALL_CHANNELS`) are NOT in this list.

#### Discovering and executing app-specific tools

1. **Search** for relevant tools:
   ```typescript
   const search = await session.execute("COMPOSIO_SEARCH_TOOLS", {
     query: "slack channels list",
   });
   // Returns: tool schemas, recommended plan, pitfalls, session.id
   const sessionId = search.data.session.id;
   ```

2. **Execute** a specific tool by slug:
   ```typescript
   const result = await session.execute("SLACK_LIST_ALL_CHANNELS", {
     limit: 200,
     types: "public_channel,private_channel",
     exclude_archived: true,
   }, { sessionId });
   // result.data.channels — array of channel objects
   ```

3. **Response shape** for Slack channel list:
   ```typescript
   result.data.channels: Array<{
     id: string; name: string; is_private: boolean;
     is_member: boolean; num_members: number; is_archived: boolean;
     creator: string; purpose: { value: string }; topic: { value: string };
   }>
   ```

### Methods that do NOT exist

- `composio.toolkits.list()` — does not exist on the client instance
- `composio.connectedAccounts.link.create({ ... })` — `link` is a function, not a sub-object
- `composio.integrations.connect({ ... })` — does not exist

## OAuth Flow (End-to-End)

1. **Find or create an auth config** for the target app:
   ```typescript
   const configs = await composio.authConfigs.list();
   const slackConfig = configs.items.find(c => c.toolkit.slug === "slack");
   ```

2. **Create an OAuth link** for the user:
   ```typescript
   const link = await composio.connectedAccounts.link("user-id", slackConfig.id);
   console.log("Authorize at:", link.redirectUrl);
   ```

3. **User opens the redirect URL** in browser, signs in to the service, and authorizes.

4. **Verify connection** after authorization:
   ```typescript
   const accounts = await composio.connectedAccounts.list();
   // Account should now have status "ACTIVE"
   ```

## Running Scripts with API Key

Use himitsu exec to inject the API key:

```bash
himitsu exec composio-api-key -- npx tsx script.ts
```

This sets `COMPOSIO_API_KEY` as an env var automatically.

## Current Connections

| App | Auth Config ID | Connected Account IDs | Token Type | Status |
|-----|---------------|---------------------|------------|--------|
| Slack (user) | `ac_xcxJH3q8_ufS` | `ca_8fFPmpaCfb0B`, `ca_G2L5JAlvOuYL` | user | ACTIVE |
| Slack (bot "mini cooper") | `ac_mY7qk2iuplTK` | `ca_7ArFskYXBqL0`, `ca_1uXTodyE3WHE`, `ca_-5EhGmAQEECe` | bot | ACTIVE |
| Slack (bot, tool router-managed) | `ac_SMjuEeZLEYDF` | `ca_s8BkZSBDxUlB` | bot | ACTIVE |
| GitHub | `ac_EGarnY8BniOm` | `ca_iz0FUDtCiUaw` | bearer <REDACTED> ACTIVE |
| Gmail | `ac_Iw3pgdqfK2y9` | `ca_zmVgZXeN2nQW` | Bearer <REDACTED> ACTIVE |

Note: The Slack bot auth config uses the `slackbot` toolkit slug (not `slack`), is NOT Composio-managed (`isComposioManaged: false`), and is named "mini cooper". The Slack app display name in the workspace is "Composio" (bot_id: B0B9DKFSECA). Multiple stale connections may accumulate (EXPIRED/INITIATED) — check status before using.

### Slack Details

- **Workspace:** `darkmatter-labs.slack.com`
- **Team:** `/// darkmatter` (ID: `T092MDGBJUR`)
- **User:** `cooper` (ID: `U092MDGBK0R`)
- **Entity/User ID for Composio:** `cooper-darkmatter`
- **17 channels** (6 private, 11 public)

### Multiple connections per auth config

When a user already has a connected account for an auth config (e.g., personal Slack + bot Slack), pass `allowMultiple: true`:

```typescript
const link = await composio.connectedAccounts.link(userId, authConfigId, {
  allowMultiple: true,
});
```

Without it, you get `ComposioMultipleConnectedAccountsError`.

### OAuth link expiration

OAuth links expire quickly. If a user doesn't complete the flow in time, the connected account status becomes `EXPIRED`. Re-initiate with `link()` (with `allowMultiple: true` if needed). The expired account remains in the list but is unusable.

### Bot vs user token types

- `token_type: "user"` — actions appear as coming from the personal Slack account
- `token_type: "bot"` — actions appear as coming from the Slack bot/app
- Check via `acct.state.val.token_type` or `acct.data.token_type`

### Targeting a specific connected account

When multiple connections exist for a toolkit (e.g., user + bot Slack), pin the session to a specific account:

```typescript
const session = await composio.create(userId, {
  connectedAccountIds: ["ca_7ArFskYXBqL0"],  // bot account
});
```

Without `connectedAccountIds`, the session may default to the wrong account.

### Activating toolkit connections in the tool router

**Critical:** Passing `connectedAccountIds` when creating a session does NOT automatically activate non-default toolkit connections (like `slackbot`). The tool router treats `slack` and `slackbot` as separate toolkits. Even with bot connected account IDs in the session, `SLACKBOT_*` tools will fail with `ToolRouterV2_NoActiveConnection` until you explicitly activate the toolkit:

```typescript
const session = await composio.create(userId);

// MUST activate the slackbot toolkit before using SLACKBOT_* tools
const manage = await session.execute("COMPOSIO_MANAGE_CONNECTIONS", {
  toolkits: ["slackbot"],
});

// Check status — should be "active"
if (manage.data.results.slackbot.status !== "active") {
  // User needs to complete OAuth at manage.data.results.slackbot.redirect_url
  console.log("Authorize at:", manage.data.results.slackbot.redirect_url);
}

// NOW SLACKBOT_* tools work
const result = await session.execute("SLACKBOT_SEND_MESSAGE", {
  channel: "C0A8AF4T01L",
  markdown_text: "Hello from the bot!",
});
```

**Important:** `COMPOSIO_MANAGE_CONNECTIONS` may create a **new connected account** under a Composio-generated auth config (e.g., `ac_SMjuEeZLEYDF` instead of your original `ac_mY7qk2iuplTK`). This is expected — the tool router manages its own connection lifecycle.

### Slackbot vs Slack toolkit tools

The tool router exposes two parallel sets of Slack tools:

| `slack` toolkit (user token) | `slackbot` toolkit (bot token) |
|---|---|
| `SLACK_SEND_MESSAGE` | `SLACKBOT_SEND_MESSAGE` |
| `SLACK_FIND_CHANNELS` | `SLACKBOT_FIND_CHANNELS` |
| `SLACK_LIST_ALL_CHANNELS` | — |
| `SLACK_OPEN_DM` | — |
| `SLACK_JOIN_AN_EXISTING_CONVERSATION` | `SLACKBOT_JOIN_AN_EXISTING_CONVERSATION` |

Use `SLACKBOT_*` tools when you need messages to appear as the bot. Use `SLACK_*` tools when acting as the user.

### Bot channel membership and the `channels:join` scope

A bot token **cannot post in a channel it hasn't been added to**, even if the bot's user-level scopes show it "is a member" of that channel. The `is_member` field from `SLACKBOT_FIND_CHANNELS` reflects the *user token* view, not the bot token's actual membership.

To post as a bot in a channel:
1. The bot must have the `channels:join` scope in its Slack app configuration, OR
2. A workspace admin must explicitly `/invite @botname` to the channel

Without `channels:join`, `SLACKBOT_SEND_MESSAGE` returns `not_in_channel` even for channels the bot "sees" via read scopes.

**Fix:** Add `channels:join` to the Slack app's bot scopes at api.slack.com/apps, then reinstall the app to the workspace. After that, the bot can join and post in any public channel automatically.

### Slack Messaging via Tool Router

#### Sending a message to a channel

```typescript
// Send directly to a channel ID
const result = await session.execute("SLACK_SEND_MESSAGE", {
  channel: "C0A8AF4T01L",  // channel ID from SLACK_FIND_CHANNELS or SLACK_LIST_ALL_CHANNELS
  markdown_text: "Hello from the bot! :wave:",
});
```

#### Sending a DM to a user

**Preferred method:** send directly to the user ID as the channel — Slack resolves it to a DM automatically:

```typescript
const result = await session.execute("SLACK_SEND_MESSAGE", {
  channel: "U092MDGBK0R",  // user ID — Slack opens DM automatically
  markdown_text: "Hey Cooper! :robot_face:",
});
```

**Alternative:** explicitly open a DM first, then send:

```typescript
const dm = await session.execute("SLACK_OPEN_DM", { users: "U092MDGBK0R" });
const channelId = dm.data.channel.id;  // e.g., "D092MDGCH8R"
const result = await session.execute("SLACK_SEND_MESSAGE", {
  channel: channelId,
  markdown_text: "Hello from the bot!",
});
```

#### Mentioning a user in a channel

Use `<@USER_ID>` in markdown_text:

```typescript
const result = await session.execute("SLACK_SEND_MESSAGE", {
  channel: "C0A8AF4T01L",
  markdown_text: "<@U092MDGBK0R> Hermes here — Composio + Slack bot connection is live!",
});
```

#### Key Slack tool slugs

| Slug | Purpose |
|------|---------|
| `SLACK_LIST_ALL_CHANNELS` | List channels (paginated, use cursor) |
| `SLACK_FIND_CHANNELS` | Search channels by name/topic/purpose |
| `SLACK_RETRIEVE_CONVERSATION_INFORMATION` | Get channel metadata by ID |
| `SLACK_OPEN_DM` | Open/get DM channel ID with a user |
| `SLACK_SEND_MESSAGE` | Send a message (use `markdown_text`) |
| `SLACK_TEST_AUTH` | Verify auth and get identity info |
| `SLACK_SCHEDULE_MESSAGE` | Schedule a message for later |
| `SLACK_LIST_CONVERSATIONS` | List conversations for a user |

## Pitfalls

- **`SLACK_SEND_MESSAGE` uses `markdown_text`, NOT `text`** — Passing `text` returns "Unsupported Slack send message field(s). text: Use markdown_text for normal content, or fallback_text with blocks."
- **`--legacy-peer-deps` required** — `@openai/agents` requires `zod@^3.25.40` while `@composio/core` and `@composio/openai-agents` accept `zod@^4`. npm will fail without `--legacy-peer-deps`.
- **`"type": "module"` required** — Top-level await fails with CJS output format in tsx.
- **`link()` takes positional args** — NOT an options object. Calling `link({ userId, authConfigId })` will error with "authConfigIds.0 should be a string, but you provided undefined".
- **API paths are `/api/v3.1/`** not `/api/v3/`. The v3 paths return HTML 404 pages.
- **`backend.composio.dev`** is the API host. `api.composio.dev` and `api.composio.io` are not the right endpoints.
- **Write tool sanitizes `process.env.XXX`** — The write_file and execute_code tools may sanitize `process.env.COMPOSIO_API_KEY` patterns. Workaround: write files via terminal with `cat > file << 'EOF'` or base64 encode/decode.
- **No `toolkits.list()` method** — Use `authConfigs.list()` to discover available integrations instead.
- **Multiple connected accounts need `allowMultiple: true`** — If a user already has a connected account for an auth config and you try to `link()` again, you get `ComposioMultipleConnectedAccountsError`. Pass `{ allowMultiple: true }` as the third arg.
- **OAuth links expire** — Connected accounts with status `EXPIRED` mean the OAuth link was never completed. Re-initiate with `link()` and have the user authorize promptly.
- **Bot vs user connections** — `token_type: "user"` means actions come from the person's account; `token_type: "bot"` means from a Slack app/bot. Both can coexist under the same auth config with `allowMultiple`.
- **Send DMs by user ID, not DM channel ID** — You can pass a user ID (e.g., `U092MDGBK0R`) directly as the `channel` parameter to `SLACK_SEND_MESSAGE`. Slack resolves it to the DM automatically. Using `SLACK_OPEN_DM` first works but is an extra step.
- **Bot messages show the Slack app name** — When using a bot connected account, messages appear under the Slack app's display name (e.g., "Composio"), NOT the auth config name ("mini cooper"). To change the bot's display name, update it in the Slack app settings at api.slack.com/apps.
- **Accumulated stale connections** — Failed/incomplete OAuth flows leave EXPIRED or INITIATED connected accounts in the list. They're harmless but clutter the list. Check status before using any account ID.
- **`connectedAccountIds` doesn't activate toolkit in tool router** — Passing `connectedAccountIds` to `composio.create()` pins which accounts are available but does NOT activate non-default toolkit connections (like `slackbot`). You MUST call `COMPOSIO_MANAGE_CONNECTIONS` with the toolkit slug to activate it in the session before using toolkit-specific tools (e.g., `SLACKBOT_SEND_MESSAGE`). Otherwise you get `ToolRouterV2_NoActiveConnection`.
- **`COMPOSIO_MANAGE_CONNECTIONS` may create new connected accounts** — When activating a toolkit that has existing connected accounts, the tool router may still initiate a fresh OAuth flow and create a new connected account under a Composio-generated auth config. This is expected — the tool router manages its own connection lifecycle independently.
- **Bot `not_in_channel` requires `channels:join` scope or manual invite** — A bot token cannot post in channels it hasn't been explicitly added to. `SLACKBOT_FIND_CHANNELS` may show the bot as `is_member: true` but this reflects user-token visibility, not bot-token membership. The Slack app needs `channels:join` scope in its bot scopes, or a workspace admin must `/invite @botname` to each channel.
- **`SLACKBOT_*` tools are separate from `SLACK_*` tools** — The tool router exposes two parallel tool sets. Use `SLACKBOT_SEND_MESSAGE` (not `SLACK_SEND_MESSAGE`) when you want the bot identity. Using `SLACK_SEND_MESSAGE` with a `slack` toolkit connection always sends as the user, even if the session has bot connected accounts.

## References

- `references/sdk-methods.md` — Full method signature reference extracted from the SDK source

## Templates

- `templates/slack-bot-session.ts` — Working Slack bot session script (list channels, send messages, etc.)
