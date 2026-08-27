# BofA Zelle Transfer via AppleScript JS Execution

When CDP port 9222 is down and you've fallen back to AppleScript (see
`references/live-chrome-cdp.md` for setup), this reference covers the complete
flow for logging into BofA and sending a Zelle transfer by executing
JavaScript in Chrome tabs via `osascript`.

## Prerequisites

1. Kill automation Chrome instances (Playwright MCP, Puppeteer) so AppleScript
   targets Cooper's real Chrome — see `references/live-chrome-cdp.md` § "The
   Multi-Instance Problem".
2. "Allow JavaScript from Apple Events" enabled (View → Developer → Allow
   JavaScript from Apple Events). If AppleScript `click` silently fails to
   toggle it, ask Cooper to do it manually — it's a one-time setting.
3. BofA credentials in 1Password.

## AppleScript JS Execution Pattern

Complex JS with quotes/braces fails in `osascript -e` due to escaping layers.
Use Python `subprocess` to build and run the osascript command — this avoids
shell quoting hell entirely:

```python
import subprocess

def chrome_js(js_code, win=1, tab=1):
    """Execute JS in a specific Chrome tab by window/tab number (1-indexed)."""
    escaped = js_code.replace('\\', '\\\\').replace('"', '\\"')
    script = f'''tell application "Google Chrome"
    set theTab to tab {tab} of window {win}
    set jsResult to execute theTab javascript "{escaped}"
    return jsResult
end tell'''
    result = subprocess.run(['osascript', '-e', script],
                          capture_output=True, text=True, timeout=30)
    return result.stdout.strip()
```

> **Pitfall:** `osascript -e` with heredocs containing `&` triggers Hermes
> terminal's backgrounding guard. Use `execute_code` with Python subprocess
> instead.

## Step 1: Log Into BofA

Navigate to BofA and fill the login form. The key field selectors:

```javascript
// User ID
var oid = document.getElementById('oid');
oid.value = 'koutaroum';

// Password
var pass = document.getElementById('pass');
pass.value = '<PASSWORD>';

// Submit — use #secure-signin-submit, NOT #appChoiceSubmit (wrong button)
document.getElementById('secure-signin-submit').click();
```

> **Pitfall:** BofA's homepage has multiple submit buttons. `appChoiceSubmit`
> is for the "Get the app" form, not login. Always use `#secure-signin-submit`.

## Step 2: Get 1Password Credentials

```bash
# Find the BofA item
op item list --categories Login | grep -i "bank\|america\|boa"

# Get username and password
op item get <ITEM_ID> --fields username
op item get <ITEM_ID> --fields password --reveal  # --reveal is required for passwords
```

## Step 3: Navigate to Zelle

BofA's SPA uses a `fsdgoto()` JS function for navigation, but it's defined in
a closure/iframe and is **not accessible** from `execute javascript` context.

**Workaround:** Find the Zelle link element and click it, or check if a Zelle
tab is already open:

```python
# Enumerate all tabs to find an existing Zelle session
script = '''tell application "Google Chrome"
    repeat with w in every window
        repeat with t in every tab of w
            if (URL of t) contains "peerpay" then
                return "Found Zelle tab"
            end if
        end repeat
    end repeat
end tell'''
```

If no Zelle tab exists, navigate from the accounts overview page by finding
and clicking the "Send money with Zelle" link:

```javascript
var links = document.querySelectorAll('a');
for (var i = 0; i < links.length; i++) {
    if (links[i].innerText.trim().indexOf('Send money with Zelle') !== -1) {
        links[i].click();
        break;
    }
}
```

The Zelle URL pattern is: `https://secure.bankofamerica.com/paytransfer-peerpay~

## Step 4: Select Recipient

The Zelle Send Money page lists recipients as `button.recipient-item` elements.
Find and click by name:

```javascript
var buttons = document.querySelectorAll('button.recipient-item');
for (var i = 0; i < buttons.length; i++) {
    if (buttons[i].innerText.toUpperCase().indexOf('NUBIA') !== -1) {
        buttons[i].click();
        break;
    }
}
```

## Step 5: Enter Amount

The amount field is `input[name="payment_amount"]` (placeholder `0.00`):

```javascript
var amountInput = document.querySelector('input[name="payment_amount"]');
amountInput.focus();
amountInput.value = '';
amountInput.dispatchEvent(new Event('input', {bubbles: true}));
amountInput.value = '280';
amountInput.dispatchEvent(new Event('input', {bubbles: true}));
amountInput.dispatchEvent(new Event('change', {bubbles: true}));
amountInput.dispatchEvent(new Event('blur', {bubbles: true}));
```

Then click the **Next** button (type=submit, text="Next", not disabled).

## Step 6: Select Payment Date

The date field is `input[name="payment_date"]` (jQuery datepicker). Set
today's date in MM/DD/YYYY format using the same focus → input → change →
blur pattern as the amount field.

Then click **Next** again.

## Step 7: Review and Confirm

The review page shows: To, From, Amount, Date. Present the details to Cooper
for confirmation before clicking **Pay** — this is a GATED ACTION per the
financial-operations security boundaries.

> **CRITICAL PITFALL — JS `.click()` does NOT work on the Pay button.**
> The Pay button (`#Pay-review-btn`) is a SPA/AJAX button with no parent
> `<form>`. Calling `.click()` via `execute javascript` silently fails (returns
> `missing value`, no navigation, no error). `form.submit()` also fails
> because there is no form. `form.requestSubmit()` fails for the same reason.
> A JS `.click()` may also trigger a partial submission that results in a
> BofA error page ("Your request can't be completed. An error occurred while
> processing your request.").
>
> **Fix:** Use AppleScript Accessibility `perform action "AXPress"` to press
> the button natively. This triggers the SPA's event handler correctly.

### The AXPress Pattern for SPA Buttons

```applescript
tell application "System Events"
    tell process "Google Chrome"
        repeat with w in every window
            if (title of w) contains "Send Money" then
                set allElements to entire contents of w
                repeat with el in allElements
                    try
                        if (title of el) is "Pay" and (role of el) is "AXButton" then
                            perform action "AXPress" of el
                            return "pressed Pay"
                        end if
                    end try
                end repeat
            end if
        end repeat
    end tell
end tell
```

> **Note:** `entire contents of w` can be slow (10-15s on a page with 1000+
> AX elements). This is acceptable for a one-time confirm action. The `try`
> block is needed because not all AX elements support `title` or `role`
> queries.

After pressing, wait 5-8 seconds for the SPA to process and navigate. Check
for a success page containing "Your payment is sent" and a confirmation
number. If you see an error instead, check the account balance to verify
the payment didn't go through before retrying.

## Multi-Tab Targeting

When Cooper has many Chrome windows/tabs open (common — 40+ tabs), you must
target the specific window/tab. Enumerate first:

```python
script = '''tell application "Google Chrome"
    repeat with w in every window
        set winIdx to 0
        repeat with t in every tab of w
            set winIdx to winIdx + 1
            if (URL of t) contains "secure.bankofamerica" then
                -- found it, note the window index and tab index
            end if
        end repeat
    end repeat
end tell'''
```

Then use `tab N of window M` in subsequent `execute javascript` calls.

## Key Selectors Summary

| Element | Selector |
|---------|----------|
| Login User ID | `#oid` |
| Login Password | `#pass` |
| Login Submit | `#secure-signin-submit` |
| Recipient button | `button.recipient-item` |
| Amount input | `input[name="payment_amount"]` |
| Date input | `input[name="payment_date"]` |
| Next button | `button[type=submit]` with text "Next" |
| Pay button (review) | `#Pay-review-btn` — **AXPress required**, JS `.click()` fails (SPA, no form) |
