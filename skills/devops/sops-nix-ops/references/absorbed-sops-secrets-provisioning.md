---
name: sops-secrets-provisioning
description: Provision new SOPS-encrypted secrets into a repo (himitsu as source, sops encrypt, age recipients) and wire runtime decrypt + AI model providers from them. Use when creating secrets.sops.json / *.sops.yaml files, adding API keys to a repo's encrypted config, setting up .sops.yaml creation rules, building TypeScript secret loaders (alchemy-sops), or pre-configuring AI providers (OpenRouter, LiteLLM) for agents.
---

# SOPS Secrets Provisioning

Creating and wiring encrypted secrets into a repo — the provisioning side. (`sops-secret-access` covers the read/decrypt-for-a-task side.)

## Terminal masking: never read secrets via inline command substitution

The Hermes terminal masks secret-looking content. Inline `KEY=*** read path)` inside a terminal command gets mangled — `syntax error near unexpected token ')'`, or the variable silently empties (e.g. "Missing Authentication header").

**Two-step pattern instead:**
1. Plain redirect to a temp file: `himitsu openrouter/api-key > /tmp/cfg-or-key`
2. Consume the temp file from a bun/node script written via `write_file` (bun also avoids JSON quoting pain for curl bodies). Never re-inline the secret into a shell string.

Clean up temp key files when done.

## Creating a new SOPS file

- **Input path must match a creation rule.** `sops --encrypt` selects `creation_rules` by matching the *input* path against `path_regex`. A plaintext temp named `secrets-plain.XXX.json` against rule `.*\.sops\.json$` fails: `no matching creation rules found`. Name the temp to match (`/tmp/sops-work/secrets.sops.json`) and pass `--config path/to/.sops.yaml` explicitly (config discovery is relative to the input file).
- **Plaintext never sits in the repo.** Build plaintext in a temp file → encrypt → write ciphertext to the repo path. Ciphertext (`*.sops.*`) is commit-safe.
- **Verify round-trip immediately:** `sops -d file | jq 'keys'` (print derived facts only — never decrypted values).

## Recipient design (.sops.yaml)

Darkmatter standard recipients: AWS KMS dev key + tailscale keyservice age + himitsu age (see `sops.dm.sh/.well-known/.sops.yaml`). **Fleet recipients alone usually can't decrypt on the workstation** — if an agent or dev process must decrypt at runtime, add the local age key (`~/.config/sops/age/keys.txt`) as a recipient too.

## Runtime decrypt in TypeScript: alchemy-sops native backend

`runSopsAge` from `alchemy-sops` decrypts age-encrypted SOPS in-process — **no `sops` binary**. Age key auto-discovery: `XDG_CONFIG_HOME/sops/age/keys.txt` (Linux), `~/Library/Application Support/sops/age/keys.txt` (macOS).

```ts
import * as Effect from "effect/Effect";
import { runSopsAge } from "alchemy-sops";

const text = await Effect.runPromise(
  runSopsAge({ path, binary: "sops", inputType: "json", outputType: "json" }),
);
const secrets = JSON.parse(text);
```

Pitfalls:
- alchemy 2.x / alchemy-sops require **effect 4**. Plain `bun add effect` installs v3 and breaks peers — install `effect@4.0.0-beta.x` explicitly.
- Don't spin up `Alchemy.Stack(...)` just to decrypt at runtime — stacks need providers + state-store layers. Call `runSopsAge` (or `SopsFile` with `backend: "sops-age"`) directly.
- `@ai-sdk/openrouter` does **not exist** on npm — OpenRouter is OpenAI-compatible; use `createOpenAI({ baseURL: "https://openrouter.ai/api/v1", ... })` from `@ai-sdk/openai`.

## Verify model ids BEFORE wiring providers

Never hardcode a model id you haven't seen live. Two checks:
1. Catalog: `GET /v1/models` (OpenRouter/LiteLLM) → confirm exact id, context length, input modalities.
2. Live ping: 1-token chat completion per model id. See `scripts/ping-models.mjs`.

A model returning HTTP 200 with empty content at `max_tokens: 5` is fine (some providers spend tokens on reasoning); only an error body means broken.

## Support files

- `references/darkmatter-recipe.md` — himitsu paths, standard recipients, worked example (czxtm/agents secrets.sops.json), provider table.
- `scripts/ping-models.mjs` — live 1-token ping of candidate model ids (bun).
