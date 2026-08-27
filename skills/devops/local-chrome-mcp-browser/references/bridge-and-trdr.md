# chrome-mcp-bridge + TRDR notes

## Port map (Cooper laptop)

- Chrome extension bridge: often `127.0.0.1:12306`
- Dia extension bridge: often `127.0.0.1:12307` (child of Dia PID)
- Confirm: `lsof -nP -iTCP:12306,12307 -sTCP:LISTEN` and match PPID to Dia vs Chrome

Default in `mcp-chrome-bridge` source is `NATIVE_SERVER_PORT = 12306`; second browser instance increments.

## Streamable HTTP client (one shot)

```python
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://127.0.0.1:12307/mcp"

def text_of(res):
    return "\n".join(getattr(c, "text", None) or str(c) for c in res.content)

async def main():
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as s:
            await s.initialize()
            async def call(name, args=None):
                return text_of(await s.call_tool(name, args or {}))

            tabs = json.loads(await call("get_windows_and_tabs"))
            alltabs = [t for w in tabs.get("windows", []) for t in w.get("tabs", [])]
            def pick(substr):
                return next((t for t in alltabs if substr in (t.get("title") or "")), None)

            for label, sub in [("xmr", "XMR/USDT"), ("hype", "HYPE/USDC")]:
                t = pick(sub)
                if not t:
                    print("missing", label); continue
                await call("chrome_switch_tab", {"tabId": t["tabId"]})
                await asyncio.sleep(2.5)
                print(label, await call("chrome_get_web_content", {"tabId": t["tabId"], "textContent": True}))

asyncio.run(main())
```

## Stuck transport recovery

Error text: `Already connected to a transport...`

```bash
PID=$(lsof -nP -iTCP:12307 -sTCP:LISTEN -t | head -1)
kill "$PID"
for i in $(seq 1 15); do
  lsof -nP -iTCP:12307 -sTCP:LISTEN && break
  sleep 1
done
```

Then open **one** new client and finish all dumps before exit.

## chrome-devtools-mcp vs bridge

| Check | Meaning |
|-------|---------|
| `curl :9222/json/version` → JSON with `webSocketDebuggerUrl` | CDP OK for chrome-devtools-mcp |
| `curl :9222/json/version` → 404 while port listens | Not usable CDP; use chrome-mcp-bridge |
| User pastes `npx chrome-devtools-mcp@latest` but TRDR is in Dia | Bridge on 12307 is usually correct; DevTools MCP only if Dia/Chrome exposes real CDP |

## TRDR tab identity

- Same path `trdr.io/console/<id>/<id>` can back multiple symbol tabs.
- Match **title**: `XMR/USDT … TRDR`, `HYPE/USDC … TRDR`.
- Do not `chrome_navigate` to console URL to "refresh" HYPE — may activate another symbol's tab.
- Shell-only body after switch → wait and `chrome_get_web_content` again; screenshot via tool or Dia `computer_use`.

## HL quick tape (no browser)

`POST https://api.hyperliquid.xyz/info` body `{"type":"metaAndAssetCtxs"}` → universe + mark/oracle/funding/OI/dayNtlVlm/prevDayPx.
