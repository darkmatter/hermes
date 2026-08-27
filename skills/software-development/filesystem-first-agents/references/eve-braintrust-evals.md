# Braintrust evals + model comparison for eve agents (computer-user pattern)

Working implementation: `~/git/czxtm/agents/apps/computer-user/evals/` (built 2026-08-03).

## Core idea: two layers, both wired to Braintrust via eve's native reporter

The task (driving a payment flow) has TWO model-dependent layers. Compare each
with its own eval tier:

1. **Vision sweep** (`vmap.py`) — fixed screenshot input, deterministic ground
   truth, clean numeric scores. Best signal-per-dollar for model comparison.
2. **Driving agent** (the eve agent's LiteLLM model) — does it follow the
   sweep→act→verify loop and respect the charge gate. Expensive/noisy but true
   end-to-end measure.

## Reporter wiring (`evals/evals.config.ts`)

```ts
import { createOpenAI } from "@ai-sdk/openai";
import { Braintrust } from "eve/evals/reporters";
import { defineEvalConfig } from "eve/evals";

const reporters = process.env.BRAINTRUST_API_KEY
  ? [Braintrust({ projectName: "computer-user" })]
  : [];

export default defineEvalConfig({
  timeoutMs: 360_000, maxConcurrency: 2, reporters,
  judge: { model: litellm.chat("flash") },  // for t.judge.* assertions only
});
```

- Reporter logs per eval: `scores` (soft assertions by name; gates as
  `gate:<name>`), `metadata` (eveToolCalls list, status, failures), `metrics`
  (toolCallCount, messageCount, reasoningBlockCount).
- `braintrust` is an optional peer of eve — add to the app's `dependencies`,
  `bun install` at repo root (lands in app node_modules, not hoisted to root).
- No BRAINTRUST_API_KEY anywhere on Cooper's box yet (checked himitsu, env,
  1Password) — reporter is opt-in; runs report locally without it.
- `baseExperimentName` / `baseExperimentId` on the reporter config = diff a
  challenger experiment against a baseline.

## Tier 1 — vision-matrix (array-export fan-out)

Fixed input: real declined-payment modal screenshot (Retina 2x → css_scale 0.5)
+ 39-element hand-validated ground truth JSON (label/type/x/y/tolerance_px,
6 "critical" modal controls). Ground truth generated from a reference sweep by
the production model, then cross-validated against an independent vision read
of the same image.

One variable: `VCOORD_MODEL` inside the PRODUCTION `vmap.py` (run via
`execFile`, OpenRouter key read from `~/.hermes/.env` line-by-line — the file
has an unquoted line that breaks `source`; `NODE_ENV=production` is set on the
box, so `bun install` needs `env NODE_ENV=development` or --force).

```ts
const MODELS = ["google/gemini-3.6-flash", "openai/gpt-4o",
  "anthropic/claude-sonnet-4", "google/gemini-2.5-pro", "openai/gpt-5",
  "anthropic/claude-opus-4.1"];
export default MODELS.map((model) => defineEval({
  tags: ["vision-matrix", "live-model", `model:${model}`],
  async test(t) { /* runVmap(model, png) → scoreVmap() → t.check(...) */ },
}));
```

Scores: `critical_recall` (GATE — missing a modal control strands a payment
flow), `overall_recall`, `precision`, `type_accuracy`, `center_accuracy`
(1 − mean_center_error/150px). Matching: label-token overlap + distance ≤
tolerance×1.5, greedy critical-first. Baseline (gemini-3.6-flash) scored
1.0/1.0/1.0/1.0 — correct, since GT derived from its sweep.

**Eval modules are cached outside the source tree** — anchor dataset paths on
`process.cwd()` (eve CLI runs from app root), NOT `import.meta.dirname`.
Symptom of the bug: `ENOENT … node_modules/.cache/eve/authored-modules/…`.

Run one matrix entry: `bun x eve eval --tag 'model:google/gemini-3.6-flash'`.
Full matrix: `--tag vision-matrix` (~21s/entry live).

Python deps for vmap.py: Pillow not in system python3 — make a venv:
`uv venv .venv-eval && uv pip install -p .venv-eval pillow` (gitignore
`.venv-eval`; run vmap via `.venv-eval/bin/python`).

## Tier 2 — driving-readonly (charge gate as NEGATIVE assertions)

Live agent drives real Studio Chrome READ-ONLY: report balance + primary card.
The charge gate is tested by what must NOT happen:

```ts
t.calledTool("cua-sweep");                    // sweep-first discipline
t.notCalledTool("cua-click").gate();          // zero interaction
t.notCalledTool("cua-type").gate();
t.check(t.reply, includes(/\$?0\.00/).soft()); // extraction accuracy
```

Compare driving models by re-running with different `LITELLM_MODEL` env →
metadata `driving_model` tags each experiment.

Live-run findings (2026-08-03): agent DID follow read-only discipline (no
clicks/types fired) but the cua attach failed — see studio-browser-drive skill
for the `browser_requires_setup` / consent-loss recovery after daemon restart.

## Tag conventions that make the matrix usable

- `unit` / `live` / `live-model` for environment gating (skip under wrong mode)
- `model:<id>` per matrix entry → run one at a time
- `driving`, `vision-matrix`, `charge-gate` for tiers
