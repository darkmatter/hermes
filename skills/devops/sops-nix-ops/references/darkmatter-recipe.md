# Darkmatter SOPS provisioning recipe

Worked from czxtm/agents (Aug 2026): added `secrets.sops.json` to `packages/configs` with himitsu-sourced keys + pre-configured AI providers.

## Source paths

| Secret | Source |
|---|---|
| OpenRouter key | `himitsu openrouter/api-key` |
| LiteLLM key | `~/.secrets/litellm-api-key` (also `himitsu litellm-api-key`) |
| Local age key | `~/.config/sops/age/keys.txt` (also mirrored in `~/Library/Application Support/sops/age/keys.txt`) |

## Standard darkmatter .sops.yaml recipients

From `sops.dm.sh/.well-known/.sops.yaml` (curl it for the canonical copy):

- AWS KMS "sops-dev": `arn:aws:kms:us-west-2:950224716579:key/71e3cd26-ace6-41a0-8ab1-ed51a941443a` (all devs via darkmatter-dev role)
- Tailscale keyservice age: `<REDACTED>` (decrypt via `SOPS_KEYSERVICE=tcp://<REDACTED>:5000 sops decrypt <file>`)
- himitsu age: `<REDACTED>`

**Critical lesson:** these fleet recipients could NOT decrypt on Cooper's workstation alone (`sops -d` failed with "Failed to get the data key"). Adding the local age key as a recipient fixed runtime decrypt. Any repo whose secrets must decrypt in local dev/agents needs the local age recipient.

## Encrypt flow (what worked)

```bash
himitsu openrouter/api-key > /tmp/cfg-or-key
cp -f ~/.secrets/litellm-api-key /tmp/cfg-ll-key

mkdir -p /tmp/sops-work
# temp file NAME must match creation_rules path_regex (.*\.sops\.json$)
jq -n --rawfile or /tmp/cfg-or-key --rawfile ll /tmp/cfg-ll-key '{
  openrouter_api_key: <REDACTED>
  litellm_api_key: <REDACTED>
  litellm_base_url: "https://litellm.drkmttr.dev/v1"
}' > /tmp/sops-work/secrets.sops.json

cd "$REPO"
sops --config "$REPO/.sops.yaml" --encrypt /tmp/sops-work/secrets.sops.json \
  > packages/configs/secrets.sops.json

# verify round-trip (derived facts only)
sops -d packages/configs/secrets.sops.json | jq '{keys: keys}'
```

## alchemy-sops loader + providers (czxtm/agents shape)

Deps in the configs package: `alchemy@2.0.0-beta.57 alchemy-sops@0.5.0 effect@4.0.0-beta.x @ai-sdk/openai ai`. Effect 4 is mandatory for alchemy 2.x.

```ts
// secrets.ts — native decrypt, no sops binary
import * as Effect from "effect/Effect";
import { runSopsAge } from "alchemy-sops";

const path = new URL("../secrets.sops.json", import.meta.url).pathname;
const text = await Effect.runPromise(
  runSopsAge({ path, binary: "sops", inputType: "json", outputType: "json" }),
);

// providers.ts — OpenRouter is OpenAI-compatible; no @ai-sdk/openrouter exists
import { createOpenAI } from "@ai-sdk/openai";
const openrouter = createOpenAI({
  name: "openrouter",
  apiKey: <REDACTED>
  baseURL: "https://openrouter.ai/api/v1",
});
const litellm = createOpenAI({
  name: "litellm",
  apiKey: <REDACTED>
  baseURL: "https://litellm.drkmttr.dev/v1",
});
// openrouter.chat("qwen/qwen3.8-max") etc.
```

## Model ids verified live on OpenRouter (Aug 2026)

| Purpose | id | ctx | modalities |
|---|---|---|---|
| Default/fast | `qwen/qwen3.8-max` | 1M | text,image,video |
| General | `openai/gpt-5.6` (bare id resolves; `-luna/-terra/-sol` variants exist) | 1.05M | text,image |
| Vision/general | `moonshotai/kimi-k3` | 1M | text,image |
| Vision | `google/gemini-3.6-flash` | 1M | text,image,video,file,audio |
| Gateway | `glm-5.2-fp8` via LiteLLM | 1M | — |
