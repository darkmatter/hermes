# Eve direct-provider scaffold notes

Session-proven details from `czxtm/agents` (`~/git/agents`) on eve@0.27.x.

## Repo outcome

- Path: `~/git/agents` → remote `github.com/czxtm/agents`
- Legacy clue tree: `_legacy-clue/`
- Live tree under `agent/` only
- Commits (examples):
  - `e0e521b` — initial eve scaffold (Anthropic direct then swapped)
  - `efbbe8a` — LiteLLM `glm-5.2-fp8` + eval suite

## Default model (current): LiteLLM → glm-5.2-fp8

```ts
import { createOpenAI } from "@ai-sdk/openai";
import { defineAgent } from "eve";
import { mockModel } from "eve/evals";

const litellm = createOpenAI({
  name: "litellm",
  apiKey: <REDACTED>
  baseURL: process.env.LITELLM_BASE_URL ?? "https://litellm.drkmttr.dev/v1",
});

const useMock = process.env.EVE_MOCK_MODEL === "1";

export default defineAgent({
  model: useMock
    ? mockModel(/* responder */)
    : litellm.chat(process.env.LITELLM_MODEL ?? "glm-5.2-fp8"),
  modelContextWindowTokens: <REDACTED>
    process.env.LITELLM_CONTEXT_WINDOW_TOKENS ?? 1_000_000,
  ),
});
```

### Why `modelContextWindowTokens`

Build fails without it for custom providers:

```text
Cannot compile agent compaction because the primary compaction trigger model
"litellm/glm-5.2-fp8" does not have known AI Gateway context window metadata.
```

LiteLLM `/v1/models` advertises ~1M input for this alias.

### Creds

- `~/.secrets/litellm-api-key` → project `.env` as `LITELLM_API_KEY=`
- Endpoint confirmed on Cooper’s stack: `https://litellm.drkmttr.dev/v1`
- Known model ids on that gateway include: `glm-5.2-fp8`, `glm-5.1-fp8`, `glm-5.2`, `glm-5.2-hermes`, `glm-5.2-codex`, …

### Smoke against LiteLLM (shell)

```bash
# Prefer curl + JSON file body; some python urllib paths hit CF hard
curl -sS https://litellm.drkmttr.dev/v1/chat/completions \
  -H "Authorization: Bearer <REDACTED>" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.2-fp8","messages":[{"role":"user","content":"hi"}],"max_tokens":128}'
```

GLM-5.2 may return `reasoning_content` with `content: null` when `max_tokens` is tiny — raise budget and loosen eval asserts.

## Older Anthropic-direct verify (still valid pattern)

```ts
import { anthropic } from "@ai-sdk/anthropic";
export default defineAgent({ model: anthropic("claude-sonnet-4-5") });
```

`GET /eve/v1/info` → `routing.kind: "external"`, `provider: "anthropic"`.

## Working channel auth block

```ts
import { eveChannel } from "eve/channels/eve";
import { localDev, placeholderAuth, vercelOidc } from "eve/channels/auth";

export default eveChannel({
  auth: [vercelOidc(), localDev(), placeholderAuth()],
});
```

Empty `eveChannel()` fails: `Cannot read properties of undefined (reading 'uploadPolicy')`.

## Local sandbox

```ts
import { defaultBackend, defineSandbox } from "eve/sandbox";
export default defineSandbox({ backend: defaultBackend() });
```

## Evals that passed (2026-07-27)

```bash
export PATH="/opt/homebrew/opt/node@25/bin:/opt/homebrew/bin:$PATH"
cd ~/git/agents

EVE_MOCK_MODEL=1 eve eval --tag unit
# unit-smoke, unit-ping-tool — 2/2, ~250ms

eve eval smoke-live
# 1/1, ~4s (live glm-5.2-fp8)

eve eval greeting-no-ping ping-tool
# 2/2, ~4s (greeting no tools; ping tool called)
```

Eval files under `evals/`:

| File | Tags | Notes |
| --- | --- | --- |
| `unit-smoke.eval.ts` | unit | mock; avoid word “ping” in prompt if mock routes tools on it |
| `unit-ping-tool.eval.ts` | unit | mock tool loop via `toolCalls` |
| `smoke-live.eval.ts` | live | include `/pong/i` |
| `greeting-no-ping.eval.ts` | live | `notCalledTool("ping")` |
| `ping-tool.eval.ts` | live | `calledTool("ping")` |

Artifacts: `.eve/evals/<timestamp>/summary.json`.

## Health

```bash
eve build && eve start --host 127.0.0.1 --port 4317
curl -sf http://127.0.0.1:4317/eve/v1/health
# {"ok":true,"status":"ready",…}
```

## Cooper machine Node/npm

- eve needs Node ≥ 24
- Prefer `/opt/homebrew/opt/node@25/bin` over `~/.vite-plus/bin/npm` (vp wrapper)
- Omit flaky short `packageManager` fields under vite-plus

## Package set (2026-07)

- `eve@0.27.6`
- `ai@^7.0.34`
- `@ai-sdk/openai@^4.0.20` (LiteLLM path)
- `@ai-sdk/anthropic@^4.0.21` only if using Anthropic direct
- `zod@4.4.3`
- `@vercel/connect@0.4.2` (scaffold default; optional for bare local HTTP)
- `typescript@5.9.3` (editor)

## Official init constraints

- In-place create only allows existing: `.DS_Store`, `.git`, `.gitkeep`, `.hg`
- Manual path better when migrating non-empty git history

## Docs offline

`node_modules/eve/docs/` — agent-config, channels/eve, sandbox, skills, evals/*, self-hosting.
