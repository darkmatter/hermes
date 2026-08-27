# BlueBubbles Private API on macOS 26 (Tahoe) — Fix Reference

## Root cause

macOS 26 Tahoe changed two things that break BlueBubbles' Private API helper:

1. **AMFI tightening** — Apple Mobile File Integrity prevents the helper dylib
   from injecting into `Messages.app` even with SIP disabled.
2. **`_newChatItems` API change** — Tahoe returns
   `IMMessageAcknowledgmentChatItem` objects in the chat items array. The
   stock helper calls `[item index]` on every item, but that class inherits
   from `IMChatItem` (not `IMMessagePartChatItem`) and has no `-index`
   selector → crash → "Process was force quit" → helper never connects.

## Symptoms

- Server info shows `"private_api": false`, `"helper_connected": false`
- Logs: `Detected DYLIB crash for App Messages. Error: Process was force quit`
- Messages remain readable (database access works) but advanced features
  (tapbacks, typing indicators, reply threading) are unavailable
- Sending may fall back to AppleScript which is also broken on Tahoe (#777)

## Fix

### Part 1: NVRAM boot-args (required)

```bash
sudo nvram boot-args="amfi_get_out_of_my_way=1 amfi_allow_any_signature=1 -arm64e_preview_abi ipc_control_port_options=0"
# Reboot required
```

What each flag does:
- `amfi_get_out_of_my_way=1` — Disables AMFI entirely
- `amfi_allow_any_signature=1` — Allows unsigned code execution
- `-arm64e_preview_abi` — Uses preview ABI for arm64e architecture
- `ipc_control_port_options=0` — Adjusts IPC control port behavior

### Part 2: Patched dylib (may be required)

Community-built fix by @willsigmon. The patched dylib handles the
`IMMessageAcknowledgmentChatItem` case without crashing.

- **Release:** https://github.com/willsigmon/bluebubbles-helper/releases/tag/v0.0.22-tahoe
- **Upstream PR:** https://github.com/BlueBubblesApp/bluebubbles-helper/pull/53
- **Binary:** Universal (x86_64 + arm64 + arm64e)
- **SHA-256:** `b72486468c03b9e3d5ea9ccda72e71e72b4f08523ad57fa92fa7a7cb27c5d414`

```bash
# Quit BlueBubbles first
cp "/Applications/BlueBubbles.app/Contents/Resources/appResources/private-api/macos11/BlueBubblesHelper.dylib" \
   "/Applications/BlueBubbles.app/Contents/Resources/appResources/private-api/macos11/BlueBubblesHelper.dylib.bak"
cp ~/Downloads/BlueBubblesHelper.dylib \
   "/Applications/BlueBubbles.app/Contents/Resources/appResources/private-api/macos11/BlueBubblesHelper.dylib"
```

### Part 3: Full stack (if Parts 1+2 insufficient)

Some users needed all of these combined:
1. Dylib swap (Part 2)
2. `csrutil disable` (recovery mode)
3. NVRAM boot-args (Part 1)
4. Ad-hoc code-sign the dylib: `codesign -s - "<path-to-dylib>"`

## Known remaining regressions on Tahoe

| Issue | Description | Status |
|-------|-------------|--------|
| [#779](https://github.com/BlueBubblesApp/bluebubbles-server/issues/779) | Inbound iMessages delayed (APNs drops) on Tahoe 26.3.1 | Open |
| [#814](https://github.com/BlueBubblesApp/bluebubbles-server/issues/814) | Reply-threaded sends (`selectedMessageGuid`) stall; plain sends work | Open |
| [#777](https://github.com/BlueBubblesApp/bluebubbles-server/issues/777) | AppleScript `sendMessage` fails with error -1700 (`'any'` service type) | Open |

## Source issues

- [#755](https://github.com/BlueBubblesApp/bluebubbles-server/issues/755) — Original Tahoe breakage report (closed, NVRAM fix confirmed)
- [#776](https://github.com/BlueBubblesApp/bluebubbles-server/issues/776) — Dylib crash root cause + patched dylib
- [#761](https://github.com/BlueBubblesApp/bluebubbles-server/issues/761) — Server crashes on client connect (Tahoe)

## Verification

After applying fixes, verify Private API is connected:

```bash
PASS=$(sqlite3 ~/Library/Application\ Support/bluebubbles-server/config.db "SELECT value FROM config WHERE name='password'")
curl -s "http://127.0.0.1:1234/api/v1/server/info?password=$PASS" | python3 -m json.tool
# Check: "private_api": true, "helper_connected": true
```
