# Studio CUA transport for eve/flue computer-user agents

## Correct transport (2026-08-03)

```
agent (Pro) ──ssh BatchMode──> cua-driver mcp (stdio JSON-RPC) on Studio ──CDP──> Chrome
```

- Spawn: `ssh -o BatchMode=yes coopermaruyama@coopers-mac-studio ~/.local/bin/cua-driver mcp`
- Protocol: initialize → notifications/initialized → tools/call
- Screenshots arrive as MCP **image content blocks** (`content[].type=image`), not top-level `screenshot_png_b64`
- Metadata/refs in `result.structuredContent`

## Why not one-shot `cua-driver call`

Existing-profile attach is granted only through the **MCP host approval flow**.
Raw CLI forever returns `browser_requires_setup` / consent dead-ends.
Daemon help: "MCP hosts use their destructive-tool approval flow instead."

## Why not framework native MCP clients

| Runtime | API | Transports |
|---|---|---|
| Eve | `defineMcpClientConnection` | HTTP / SSE only |
| Flue 2.0.1 | `defineMcpConnection` / `useMcpConnection` | `streamable-http` \| `sse` only |

Studio daemon has **no TCP MCP listener** — only stdio. Hand-roll the client in
framework-free `agent/lib/cua.ts` and keep it portable across eve/flue.

## Bind pitfalls

1. Prefer largest Chrome window (width>800, height>500).
2. Prefer ACTIVE http(s) tab; skip `chrome-extension://` (MetaMask onboarding often tabs[0]).
3. After daemon restart: `browser_wrong_target_refused` / lost DevTools consent —
   human re-approve or restart daemon with `--grant existing-profile`.
4. Google passkey challenge → stop; handoff to Cooper (never automate passkeys).

## Tool naming

- **Eve:** runtime name = filename slug. Use `cua_sweep.ts` (underscore) so
  evals/instructions match; `cua-sweep.ts` becomes `cua-sweep` and breaks gates.
- **Flue:** explicit `defineTool({ name: "cua_sweep" })` — filename free.

## Paths under eve snapshots

`import.meta.url` for `vmap.py` breaks under eve eval compile cache. Resolve via
`process.cwd()/agent/skills/.../vmap.py` (+ Hermes skill fallback). Prefer
`.venv-eval/bin/python3` (Pillow) over system python3.
