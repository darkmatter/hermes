# Live Chrome CDP — Authenticated Browser Automation

Drive Cooper's existing, authenticated, live Chrome session via CDP (Chrome
DevTools Protocol) instead of spinning up new headless browser profiles.

## When to Use

Use this skill when you need to interact with a site that is heavily
authenticated, relies on hardware passkeys, or aggressively blocks headless
automation (e.g., Banks like Bank of America, Capital One, Amex). It is also
useful for completing CLI OAuth flows (e.g., `gog auth add`) where the user
is already logged into Google in Chrome.

## Why this instead of Camofox / agent-browser?

Cooper's established preference for financial/authenticated automation is to
use his **existing live Chrome profile** because it preserves his passkey and
session state, allowing the agent to inherit a trusted environment without
re-authenticating or fighting anti-bot challenges.

## Setup & Verification

Cooper's live Chrome runs locally on macOS and exposes the CDP port:
- Target endpoint: `127.0.0.1:9222`
- Helper script: `~/.hermes/scripts/live-chrome-cdp.js`

To verify CDP is reachable:
```bash
~/.hermes/scripts/live-chrome-cdp.js targets
# Or directly:
curl -s http://127.0.0.1:9222/json/version
```

## Security & Usage Rules

1. **New Tabs Only:** Always use `newtab <URL>` instead of navigating existing tabs.
   ```bash
   ~/.hermes/scripts/live-chrome-cdp.js newtab "https://secure.bankofamerica.com"
   ```
2. **Do Not Dump Existing Tabs:** Never extract URLs or titles of tabs you did not open unless explicitly authorized by the user.
3. **Read-Only by Default:** You may autonomously investigate and summarize DOM state (e.g. read an alert, extract transaction details).
4. **Writes are Gated:** Any submit, click, or evaluate operation that could move money, answer fraud challenges, change security settings, or perform irreversible writes **must be explicitly authorized by Cooper** in the chat before execution.
5. **Clean Up:** Always close your target tab when the investigation or action is complete.
   ```bash
   ~/.hermes/scripts/live-chrome-cdp.js close "<TARGET_ID>"
   ```

## Completing CLI OAuth Flows

When a CLI tool (e.g., `gog auth add`) needs browser-based OAuth consent,
open the auth URL in live Chrome via CDP. Cooper is typically already logged
into Google, so the consent page appears immediately and the callback
completes automatically:

```bash
~/.hermes/scripts/live-chrome-cdp.js newtab "<OAUTH_URL>"
```

The CLI tool must be running in the background (its local callback server
listening). Clean up the tab after auth completes.

## Executing Custom DOM Interaction

Because the simple helper wrapper only abstracts basic navigation, for complex
multi-step actions (filling forms, polling for elements), write a single-use
node script that imports `chrome-remote-interface` and points it at the known
target ID.

```javascript
const CDP = require('/tmp/cdp-tools/node_modules/chrome-remote-interface');
const target = "YOUR_TARGET_ID";

(async () => {
  const client = await CDP({host:'127.0.0.1', port:9222, target});
  const {Runtime, Page} = client;
  await Runtime.enable(); await Page.enable();

  const res = await Runtime.evaluate({awaitPromise:true, returnByValue:true, expression:`
    (() => {
       const btn = document.querySelector('button.submit');
       if (btn) { btn.click(); return {ok: true}; }
       return {ok: false};
    })()
  `});
  console.log(res);
  await client.close();
})();
```

---

## Fallback: AppleScript When CDP Is Down

When CDP port 9222 is unreachable (Chrome was restarted without
`--remote-debugging-port`, the machine was rebooted, etc.), fall back to
driving Chrome via AppleScript (`osascript`) and `computer_use`. This
preserves the authenticated session but is slower and less reliable than CDP.

### The Multi-Instance Problem

**This is the #1 gotcha when falling back to AppleScript.** Hermes browser
tools (Playwright MCP, Puppeteer) spawn their own Chrome processes with
custom `--user-data-dir` flags. AppleScript's `tell application "Google
Chrome"` and `computer_use app="Google Chrome"` target whichever Chrome
process macOS considers the "main" one — which is often an automation
instance, NOT Cooper's real Chrome with saved bank logins.

**Symptom:** You open a URL via `osascript` or `open`, it loads in a
Playwright/Puppeteer Chrome window with no saved credentials, and the window
title shows plain "Google Chrome" instead of "Google Chrome - Cooper
(darkmatter)".

### Fix: Kill Automation Chrome Instances

Identify and kill the automation Chrome processes so AppleScript targets
Cooper's real Chrome:

```bash
# List all Chrome main processes (not helpers)
ps aux | grep "Google Chrome.app/Contents/MacOS/Google Chrome" | grep -v Helper | grep -v grep

# Identify automation instances by their --user-data-dir flags:
#   Playwright MCP: --user-data-dir=~/Library/Caches/ms-playwright-mcp/...
#   Puppeteer:      --user-data-dir=/var/folders/.../puppeteer_dev_chrome_profile-...
# Cooper's real Chrome: NO --user-data-dir flag (uses default profile)

# Kill the automation instances (PIDs from the ps output above)
kill <PLAYWRIGHT_PID> <PUPPETEER_PID>

# Verify: AppleScript should now target the right Chrome
osascript -e 'tell application "Google Chrome" to get {title, URL} of active tab of every window'
# Look for "Cooper (darkmatter)" in window titles — that's the real profile
```

### Enabling JavaScript from Apple Events

To execute JavaScript in Chrome tabs via AppleScript, "Allow JavaScript from
Apple Events" must be enabled (View → Developer → Allow JavaScript from
Apple Events). This is a one-time setting per Chrome profile.

```bash
# Activate Chrome and try to toggle the menu item
osascript -e '
tell application "Google Chrome" to activate
delay 0.5
tell application "System Events"
    tell process "Google Chrome"
        click menu item "Allow JavaScript from Apple Events" of menu "Developer" of menu item "Developer" of menu "View" of menu bar 1
    end tell
end tell'

# Test that JS execution works
osascript -e '
tell application "Google Chrome"
    set theTab to active tab of front window
    set jsResult to execute theTab javascript "document.URL"
    return jsResult
end tell'
```

> **Pitfall:** The AppleScript `click` on the menu item may silently fail to
> toggle the setting (the command returns success but JS remains disabled).
> If JS execution still fails after clicking, ask Cooper to toggle it
> manually — it's a one-time setup step.

### AppleScript Browser Automation Patterns

Once JS from Apple Events is working:

```bash
# Navigate to a URL
osascript -e 'tell application "Google Chrome" to open location "https://www.bankofamerica.com/"'

# Execute JavaScript in the active tab
osascript -e '
tell application "Google Chrome"
    set theTab to active tab of front window
    set jsResult to execute theTab javascript "document.querySelector(\"body\").innerText.substring(0, 500)"
    return jsResult
end tell'

# Check all open tabs across all windows
osascript -e 'tell application "Google Chrome" to get {title, URL} of active tab of every window'
```

### When AppleScript JS Is Unavailable

If "Allow JavaScript from Apple Events" cannot be enabled, fall back to
`computer_use` for visual interaction (clicks, typing). Note that
`computer_use` also suffers from the multi-instance problem — use the same
kill-automation-instances fix above, then capture with `app="Google Chrome"`
to verify you're driving the right window.

> **Pitfall:** `defaults write com.google.Chrome AllowJavascriptFromAppleEvents -bool true` alone is **not** enough — Chrome still errors until View → Developer → Allow JavaScript from Apple Events is actually on (relaunch + test `execute … javascript "document.title"`).

### Studio Chrome / remote desktop (drive Mac Studio, not Pro browser)

When Cooper wants Studio:

1. **Chrome MCP** on Studio `127.0.0.1:12306/mcp` (SSH `-L` from Pro). Sticky **one client** — if "Already connected… Call close()", free the session or restart bridge/extension; plug DOM tools when free.
2. **CDP on Studio**: launch with debugging; under zsh quote origins: `--remote-allow-origins='*'` (unquoted `*` expands and drops the flag). Require `curl …:9222/json/version` / `DevToolsActivePort` — flags in `ps` without a LISTEN means pick another path, don't thrash relaunches.
3. **Pro `computer_use` → Screen Sharing** window `Coopers-Mac-Studio`. Open URLs via SSH `open -a "Google Chrome" "URL"` on host; Screen Sharing sends pixel clicks/keys only (no nested Chrome AX). Fine for simple steps; bad for dense forms.
4. SSH osascript on Studio for tab URL/title; JS needs Apple Events enabled **there**.

Payment submit stays gated. Airline rebook online after Vapi thrash: see `vapi-call-ops` `references/airline-rebook-lessons.md`.

### AXPress for SPA Buttons (JS .click() Fails)

Some SPA pages (BofA Zelle, React apps, etc.) attach click handlers via
JavaScript event listeners, not native `onclick` attributes. On these pages,
`execute javascript "element.click()"` via AppleScript **silently fails** —
the call returns `missing value` and nothing happens. `form.submit()` also
fails if the button has no parent `<form>`.

**Fix:** Use AppleScript Accessibility to press the button natively, which
triggers the SPA's event listener correctly:

```applescript
tell application "System Events"
    tell process "Google Chrome"
        repeat with w in every window
            if (title of w) contains "<WINDOW_TITLE_FRAGMENT>" then
                set allElements to entire contents of w
                repeat with el in allElements
                    try
                        if (title of el) is "<BUTTON_TEXT>" and (role of el) is "AXButton" then
                            perform action "AXPress" of el
                            return "pressed"
                        end if
                    end try
                end repeat
            end if
        end repeat
    end tell
end tell
```

> **Trade-off:** `entire contents of w` traverses the entire AX tree and can
> take 10-15s on dense pages (1000+ elements). Use it only for one-shot
> confirm/submit actions, not for repeated interactions. The `try` block is
> required because not all AX elements support `title`/`role` queries.
