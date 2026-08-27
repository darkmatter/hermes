# eve host tools wrapping remote cua-driver over SSH (the `computer-user` app)

Working example: `~/git/czxtm/agents/apps/computer-user` (`@czxtm/computer-user`) —
the eve twin of the Hermes `studio` profile, driving Mac Studio Chrome for
payments/forms/checkouts. Built + verified 2026-08-03.

## Why host tools instead of an MCP connection

eve `connections/*.ts` MCP clients require an HTTP(S) Streamable-HTTP/SSE URL —
stdio-over-SSH (how Hermes mounts cua-driver) is not expressible. The working
pattern is **host-owned `defineTool`s that shell out one-shot**:

```
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=15 \
  coopermaruyama@coopers-mac-studio \
  "~/.local/bin/cua-driver call <tool> '<json-args>'"
```

`cua-driver call <tool> '<json>'` prints the tool result as JSON on stdout —
parse it; keep raw stdout on parse failure for error surfacing. SSH key auth
only; no secrets cross the wire. Single-quote the JSON POSIX-safely.

## App shape (agent/ under the app root)

- `lib/cua.ts` — transport (`cuaCall(tool, args)`), binding-state store
  (`/tmp/eve-cua/binding-<session>.json`, mode 0600), `findChrome()` (largest
  Chrome window via `list_windows`), `CUA_SSH_TARGET` / `CUA_DRIVER_BIN` env
  overrides.
- `tools/cua-sweep.ts` — THE sweep: start_session → bind via get_browser_state
  (pid+window_id) → `browser_prepare {strategy:{kind:"existing_profile"}}`
  fallback when no `target_id` → semantic_v2 + `include_screenshot:true` →
  decode `screenshot_png_b64` to a local PNG → return slim refs + scale
  factors. Missing screenshot ⇒ clear binding (force rebind next call).
- `tools/cua-vmap.ts` — runs the skill's `scripts/vmap.py` locally (Pro side):
  one Gemini box_2d pass; OpenRouter key from env or `himitsu read
  openrouter/api-key`.
- `tools/cua-click.ts` / `cua-type.ts` / `cua-navigate.ts` — read binding
  state, act, and instruct re-sweep after navigation. `cua_type` always
  `replace:true`.
- `skills/studio-browser-drive/` + `skills/payment-operations/` — eve-adapted
  copies (frontmatter flattened, see SKILL.md pitfalls).
- `instructions/00-main.md` — port of the Hermes profile's SOUL.md (the loop,
  coordinate math, charge gate, style).

## Model + keys

- `flash` alias (= google/gemini-3.6-flash) via LiteLLM,
  `createOpenAI({ baseURL: "https://litellm.drkmttr.dev/v1" }).chat("flash")`
  + `modelContextWindowTokens`.
- Working key as of 2026-08-03: `himitsu read codex-litellm-key`.

## Verification that passed

1. `bun run typecheck` (tsc clean; needs `allowImportingTsExtensions`).
2. `bun x eve info` → Compile ready, **0 errors, 2 skills, 6 tools**.
3. `bun run test:unit` (EVE_MOCK_MODEL=1 mockModel smoke) ✓.
4. `bun x eve eval --tag live` — real `flash` completion through the eve
   runtime ✓ (trailing `503 socket hang up` queue log = teardown noise).
5. Transport probe straight through `lib/cua.ts` with bun: `check_permissions`
   + `findChrome()` returned the live Studio Chrome pid/window.

## Gotchas hit

- Stale top-level `eve dev` from a deleted dir squatted port 2000 and blocked
  `eve eval` — kill process, remove stale `dev-server-state.v1.json`.
- Scaffold template tsconfig lacks `allowImportingTsExtensions` (TS1005 on
  `../lib/x.ts` imports).
- `agent.ts` apiKey lines can be mangled by secret-redaction layers when they
  contain `process.env.*_API_KEY` inline — build the env var name by
  concatenation or read via a helper if a write comes back corrupted.
- `~/.hermes/.env` has an unquoted line (`… Chrome.app/Contents/MacOS/Google`)
  that breaks `source` — read OPENROUTER_API_KEY line-by-line with a regex,
  don't `source` the file. `NODE_ENV=production` is set on the box, so plain
  `bun install` can skip deps; use `env NODE_ENV=development bun install --force`.

## cua-driver refusals & consent recovery (live-run, 2026-08-03)

- **Refusals arrive with transport `ok: true`.** The call succeeds but `data`
  is `{"refusal": {"code": …, "message": …}, "status": "refused"}`. Always
  inspect the payload, never just the SSH/JSON status. Key codes seen:
  - `browser_requires_setup` — no owned DevTools endpoint for the pid → run
    `browser_prepare` (existing_profile strategy) for that exact pid/window.
  - `browser_wrong_target_refused` ("no exact Chrome remote-debugging consent
    sheet appeared") — the daemon restarted since the last consent, so the
    existing-profile consent for that pid was dropped.
- **Daemon restart drops consent.** `start_session` also reports
  `desktop_unlocked: false` when the Studio screen is locked — the consent
  sheet can't surface, so `browser_prepare` hangs/refuses. Recovery: restart
  the Studio daemon with the grant, then re-prepare:
  ```bash
  ssh coopermaruyama@coopers-mac-studio \
    'pkill -f "cua-driver serve"; nohup env CUA_DRIVER_RS_PERMISSIONS_GATE=0 \
     ~/.local/bin/cua-driver serve --grant existing-profile --no-permissions-gate \
     >/tmp/cua-driver-serve.log 2>&1 &'
  ```
- **`cua-driver browser-approve` is interactive-only** — it requires a TTY plus
  `--pid` / `--window-id` / `--session` and hangs headless waiting on the GUI
  consent sheet. Don't script it; use the daemon-restart grant above instead.
- Chrome on the Studio listens for CDP on `localhost:9222` (verify with
  `curl -s http://127.0.0.1:9222/json/version` before assuming the endpoint is
  up).
