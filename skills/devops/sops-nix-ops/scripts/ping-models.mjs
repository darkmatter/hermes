// Live 1-token ping of candidate model ids against an OpenAI-compatible endpoint.
// Usage:
//   <secret-store> read openrouter/api-key > /tmp/key   # NEVER inline the read in $()
//   bun ping-models.mjs /tmp/key https://openrouter.ai/api/v1 "qwen/qwen3.8-max" "openai/gpt-5.6"
// Prints one line per model: id -> first content chars, or HTTP status / error message.
// HTTP 200 with empty content at tiny max_tokens is usually fine (reasoning tokens);
// only an error body means the id is broken.
import { readFileSync } from "node:fs";

const [keyFile, baseUrl, ...models] = process.argv.slice(2);
if (!keyFile || !baseUrl || models.length === 0) {
  console.error("usage: bun ping-models.mjs <key-file> <base-url> <model-id>...");
  process.exit(2);
}

const key = readFileSync(keyFile, "utf8").trim();

for (const model of models) {
  const resp = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: { Authorization: `Bearer <REDACTED> "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: "Reply with the single word: ok" }],
      max_tokens: <REDACTED>
    }),
  });
  const data = await resp.json().catch(() => ({}));
  const out =
    data?.choices?.[0]?.message?.content ??
    data?.error?.message ??
    `HTTP ${resp.status}`;
  console.log(`${model} -> ${JSON.stringify(out).slice(0, 120)}`);
}
