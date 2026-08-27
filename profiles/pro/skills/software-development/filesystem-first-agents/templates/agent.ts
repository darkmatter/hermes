import { anthropic } from "@ai-sdk/anthropic";
import { defineAgent } from "eve";

/**
 * Direct provider — no Vercel AI Gateway.
 * Swap to openai('...') from @ai-sdk/openai, or a gateway string id
 * like "anthropic/claude-sonnet-5" if AI_GATEWAY_API_KEY is set.
 */
export default defineAgent({
  model: anthropic("claude-sonnet-4-5"),
  // Local durable workflow state: .eve/.workflow-data
  // experimental: { workflow: { world: "@workflow/world-postgres" } },
});
