// Template: Slack bot session via Composio tool router
// Usage: himitsu exec composio-api-key -- npx tsx slack-bot-session.ts

import { Composio } from "@composio/core";

const COMPOSIO_API_KEY = process.env.COMPOSIO_API_KEY || "";
const composio = new Composio({ apiKey: COMPOSIO_API_KEY });
const userId = "cooper-darkmatter";

// Pin to bot account; swap to ca_8fFPmpaCfb0B for user account
const BOT_ACCOUNT_ID = "ca_7ArFskYXBqL0";
const USER_ACCOUNT_ID = "ca_8fFPmpaCfb0B";

async function main() {
  const session = await composio.create(userId, {
    connectedAccountIds: [BOT_ACCOUNT_ID],
  });

  // Example: list channels
  const result = await session.execute("SLACK_LIST_ALL_CHANNELS", {
    limit: 200,
    types: "public_channel,private_channel",
    exclude_archived: true,
  });

  const channels = result.data?.channels || [];
  for (const ch of channels) {
    const vis = ch.is_private ? "[PRIV]" : "[PUB]";
    const joined = ch.is_member ? "JOINED" : "not-joined";
    console.log(vis, ch.name, "-", ch.num_members, "members,", joined);
  }
  console.log("\nTotal:", channels.length, "channels");
}

main();
