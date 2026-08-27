# MCP + SSH browser lifecycle

Verified workflow for Pro Hermes reaching Studio Chrome through an SSH-backed stdio MCP server.

## Configure Pro Hermes

The Studio path does not exist on Pro. Add an SSH-backed server instead:

```bash
hermes mcp add cua-driver --command ssh --args -o BatchMode=yes coopermaruyama@<REDACTED> ~/.local/bin/cua-driver mcp
```

Accept the discovered-tool prompt, verify `hermes mcp list`, then run `/reload-mcp` in the live Hermes TUI. A direct `mcp_servers` entry containing `~/...` is only valid when Hermes itself runs on Studio.

## Stabilize the daemon

```bash
cua-driver permissions status --json
cua-driver permissions grant
cua-driver status
```

The permission result must report `accessibility: true` and `screen_recording: true`. The grant command is preferable when System Settings appears correct but the daemon still reports Screen Recording false; it launches the app under its real TCC identity (`com.trycua.driver`). Repeated log lines about waiting for Screen Recording indicate daemon self-restarts, which invalidate browser bindings.

Start/restart with existing-profile authorization when needed:

```bash
cua-driver serve --grant existing-profile
```

## Browser binding sequence

1. Start a named session.
2. Identify Chrome's exact PID and native window ID.
3. `browser_prepare` with `strategy: {"kind":"existing_profile"}`.
4. Immediately call `get_browser_state` to mint the live `target_id` and `tab_id`.
5. Perform one browser action.
6. After navigation, daemon restart, or endpoint error, repeat steps 3–4. Do not reuse old opaque IDs.

A successful navigation can still invalidate the previous binding; this is expected safety behavior, not proof that Chrome lost remote debugging.

## AX fallback

Use `get_window_state` immediately before AX actions; indices/tokens expire. To enumerate a native dropdown, click its `AXPopUpButton`, then capture the tree and read the resulting `AXMenuItem` labels. Use the exact option label. For legal terms/attestations, obtain explicit user confirmation before clicking; for account-request forms, do not submit without explicit approval after reviewing all fields.
