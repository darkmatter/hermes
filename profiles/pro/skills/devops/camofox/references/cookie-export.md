# Cookie Export from Camofox

Camofox stores cookies in Playwright's `storage_state.json` format. This is NOT compatible with Chrome profiles (which use LevelDB), but the cookies themselves are portable.

## Playwright Cookie Format

Each cookie in `storage-state.json`:

```json
{
  "name": "__cf_bm",
  "value": "abc123...",
  "domain": ".uniswap.org",
  "path": "/",
  "expires": 1736683200,
  "httpOnly": true,
  "secure": true,
  "sameSite": "Lax"
}
```

## Reading Stored Cookies

Profile data lives at `$CAMOFOX_PROFILE_DIR/<profile-hash>/storage-state.json`.

Quick inspect:
```bash
python3 -c "
import json
d = json.load(open('~/r2-mount/camofox-profiles/*/storage-state.json'))
print('cookies:', len(d.get('cookies', [])), '| origins:', len(d.get('origins', [])))
for c in d.get('cookies', [])[:10]:
    print(c['domain'], c['name'])
"
```

## Converting to Netscape Cookie Jar (for Chrome/import)

```python
import json, time

state = json.load(open("storage-state.json"))
with open("cookies.txt", "w") as f:
    f.write("# Netscape HTTP Cookie File\n")
    for c in state.get("cookies", []):
        secure = "TRUE" if c.get("secure") else "FALSE"
        http_only = "TRUE" if c.get("httpOnly") else "FALSE"
        expiry = int(c.get("expires", 0)) or 0
        f.write(f"{c['domain']}\tTRUE\t{c['path']}\t{secure}\t{expiry}\t{c['name']}\t{c['value']}\n")
```

Import into Chrome via extensions like "EditThisCookie" or "Cookie Editor".

## Converting from Netscape Cookie Jar (Chrome -> Camofox)

```python
import json, sys

netscape = sys.stdin.read()
cookies = []
for line in netscape.strip().split("\n"):
    line = line.strip()
    if line.startswith("#") or not line:
        continue
    parts = line.split("\t")
    if len(parts) < 7:
        continue
    domain = parts[0]
    http_only = False
    if domain.startswith("#HttpOnly_"):
        domain = domain[len("#HttpOnly_"):]
        http_only = True
    cookie = {
        "name": parts[5],
        "value": parts[6],
        "domain": domain,
        "path": parts[2],
        "expires": int(parts[4]) if parts[4].isdigit() else -1,
        "httpOnly": http_only,
        "secure": parts[3] == "TRUE",
        "sameSite": "Lax"
    }
    cookies.append(cookie)

storage_state = {"cookies": cookies, "origins": []}
print(json.dumps(storage_state, indent=2))
```

Usage: `python3 convert.py < cookies.txt > storage-state.json`

**Important**: Netscape cookie exports (e.g. from Cookie Editor extension) only contain cookies, not localStorage or IndexedDB. For sites that store auth tokens in localStorage, use the Chrome DevTools `copy(JSON.stringify({...}))` method instead (see SKILL.md "Chrome -> Camofox session transfer").

## Converting from Cookie Editor JSON Export (Chrome -> Camofox)

The Cookie Editor extension can export in JSON format (not just Netscape). This format includes HttpOnly cookies that `cookieStore.getAll()` can't read from JavaScript. Use this as the primary export method.

Cookie Editor JSON format per cookie:
```json
{
  "domain": ".coinbase.com",
  "expirationDate": 1783907736.474,
  "hostOnly": false,
  "httpOnly": true,
  "name": "cb-gssc",
  "path": "/",
  "sameSite": "no_restriction",
  "secure": true,
  "session": false,
  "value": "eyJhbG..."
}
```

Key differences from Playwright format:
- `expirationDate` (float, seconds) vs `expires` (int, seconds)
- `hostOnly` (bool) vs Playwright uses domain prefix (`.domain` for subdomain cookies, bare `domain` for host-only)
- `sameSite` uses `"no_restriction"` vs Playwright uses `"None"`
- `session` field (boolean) vs Playwright uses `expires: -1`
- Includes HttpOnly cookies (unlike JS `cookieStore.getAll()`)

### Conversion script

See `scripts/convert-cookies.py` for the ready-to-run converter. Usage:

```bash
python3 convert-cookies.py /tmp/cb-cookies-full.json /tmp/cb-chrome-export.json > /tmp/storage-state.json
```

Takes two args: Cookie Editor JSON file (cookies), Chrome DevTools export JSON (localStorage). Outputs Playwright `storage-state.json`.

## Chrome DevTools Full Export (cookies + localStorage)

In Chrome DevTools Console on the target site:

```js
copy(JSON.stringify({
  cookies: await cookieStore.getAll(),
  localStorage: Object.fromEntries(Object.entries(localStorage))
}))
```

This copies cookies AND localStorage to your clipboard. Paste to the agent, who will convert to Playwright format and inject into camofox.

**Limitation**: `cookieStore.getAll()` does NOT include HttpOnly cookies. For sites with HttpOnly auth cookies (most exchanges, banks), you MUST also export via Cookie Editor extension in JSON format to get the full cookie set. Merge both exports using `scripts/convert-cookies.py`.

## API Endpoint

If a session is active, `GET /sessions/<userId>/storage_state` returns the same JSON. Requires `Authorization: Bearer <REDACTED> header. Returns 404 if no session exists yet.

## Short-lived JWT Session Tokens

Many sites (Coinbase, exchanges, SaaS apps) use short-lived JWTs as auth cookies (e.g. `cb-gssc` on Coinbase, typically 15min-1hr TTL). Even with a perfect cookie + localStorage transfer, these tokens expire quickly and the session dies.

**For passkey-only accounts**: The best solution is installing the **1Password Firefox extension** in camoufox (see "1Password Extension" section in SKILL.md). This lets the browser act as its own WebAuthn authenticator. After first-time sign-in via VNC, 1Password persists and handles all future passkey challenges automatically.

**Other options for passkey-only sites**:
1. Log in via VNC (requires email/password + TOTP — passkeys don't work through VNC)
2. Use the site's API directly (API keys instead of browser sessions)
3. Set up a Playwright virtual authenticator on the devbox and register a new passkey bound to camofox

For sites that support email/password login, VNC login is the most reliable approach — the persistence plugin captures the full state including all cookies and localStorage.
