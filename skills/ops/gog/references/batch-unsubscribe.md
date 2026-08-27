# Batch Email Unsubscribe via gog

Technique for mass-unsubscribing from email lists using `List-Unsubscribe` headers extracted from Gmail threads via the `gog` CLI.

## Overview

1. Search Gmail for emails with `unsubscribe:*` to find threads with `List-Unsubscribe` headers
2. Fetch one thread per unique sender to extract the `List-Unsubscribe` header value
3. Categorize senders (marketing vs service vs forwarded) to decide what to nuke
4. Hit unsubscribe URLs using the appropriate method per platform
5. Handle failures via mailto fallback or browser

## Step 1: Search for Threads with Unsubscribe Headers

```bash
# First page (returns 10 threads per page)
gog -a cooper@darkmatter.io gmail search "unsubscribe:*" -j > /tmp/unsub_p1.json

# Paginate using nextPageToken
gog -a cooper@darkmatter.io gmail search "unsubscribe:*" -j --page "<nextPageToken>" > /tmp/unsub_p2.json
```

Thread objects contain: `id`, `date`, `from`, `subject`, `labels`, `messageCount`.

## Step 2: Extract List-Unsubscribe Headers

For each unique sender, fetch one thread and extract the `List-Unsubscribe` header:

```bash
gog -a cooper@darkmatter.io gmail thread get <threadId> -j | python3 -c "
import json, sys, re
d = json.load(sys.stdin)
msgs = d.get('messages', d.get('thread', {}).get('messages', []))
if isinstance(d, list): msgs = d
msg = msgs[0] if msgs else {}
headers = msg.get('payload', {}).get('headers', [])
for h in headers:
    if h.get('name','').lower() == 'list-unsubscribe':
        val = h['value']
        # Extract URL (prefer https over mailto)
        urls = re.findall(r'<(https?://[^>]+)>', val)
        mailtos = re.findall(r'<(mailto:[^>]+)>', val)
        if urls: print(urls[0])
        elif mailtos: print(mailtos[0])
"
```

### Pitfall: Truncated JWTs

Some email providers (e.g., 1stDibs/Loom/WeWork via Clio/Atlassian) **literally truncate** JWT tokens in the `List-Unsubscribe` header with `...` (e.g., `jwt=eyJhbG...E2Ii`). The URL is unusable. In these cases, fall back to the `mailto:` address from the same header (typically `leave-<encoded-id>@leave.<domain>`).

## Step 3: Categorize Senders

Use Gmail labels to categorize:
- `CATEGORY_PROMOTIONS` → marketing, safe to nuke
- `CATEGORY_UPDATES` → mixed; service notifications (Linear, Google Search Console, Depot CI) should be kept
- `CATEGORY_FORUMS` → often forwarded via Google Groups (USPS, PayPal); handle at group level
- Internal `@darkmatter.io` senders → Google Groups forwards; not direct subscriptions

## Step 4: Hit Unsubscribe URLs by Platform

### curl GET (one-click unsubscribe)

Most `List-Unsubscribe` URLs with `List-Unsubscribe-Post: List-Unsubscribe=One-Click` work with a simple GET:

```bash
curl -sL -o /dev/null -w "%{http_code}" \
  -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  --max-time 30 \
  "$UNSUB_URL"
```

Check the response body for keywords: `unsubscri`, `removed`, `success`, `opt.out`, `no longer`, `preferences saved`.

### HubSpot (hubspotemail.net) — POST

HubSpot unsubscribe URLs accept POST and return HTTP 202 (Accepted):

```bash
curl -sL -o /dev/null -w "%{http_code}" \
  -X POST \
  -A "Mozilla/5.0" \
  --max-time 30 \
  "$HUBSPOT_UNSUB_URL"
```

URL pattern: `https://hs-<id>.s.hubspotemail-<region>.net/subscription-preferences/v2/unsubscribe-all?data=<encoded>`

### Loops.so — POST to `/en` endpoint

URLs from `email.mail.cursor.com`, `links-email.neon.tech`, `e.latitude.sh` (Loops.so platform) need a POST to the URL with `/en` appended:

```bash
curl -sL -o /dev/null -w "%{http_code}" \
  -X POST \
  -d "unsubscribe=true" \
  -A "Mozilla/5.0" \
  --max-time 15 \
  "$UNSUB_URL/en"
```

### Mailchimp (list-manage.com) — Browser

Mailchimp requires visiting the page and clicking an "Unsubscribe" button. Use `browser_navigate` then `browser_click`:

```
browser_navigate(url=<mailchimp_unsub_url>)
# Page shows a button "Unsubscribe"
browser_click(ref=<button_ref>)
# Page changes to show "« return to our website" link = success
```

### PostHog (email.posthog.com) — Browser

Same pattern as Mailchimp: navigate, click "Unsubscribe" button, button changes to "Subscribe" = success.

### Morningstar (app.mscomm.morningstar.com) — curl GET

Morningstar's unsubscribe URL works with a simple GET request; the page shows "Your Morningstar unsubscribe selections have been updated."

### customeriomail (Figma) — curl POST

```bash
curl -sL -o /dev/null -w "%{http_code}" -X POST \
  "https://e.customeriomail.com/unsubscribe/<token>" \
  -A "Mozilla/5.0" --max-time 15
```

### Mailto Fallback

When the URL is truncated or returns errors, send an email to the `mailto:` address from the `List-Unsubscribe` header:

```bash
gog -a cooper@darkmatter.io gmail send \
  --to "leave-<encoded-id>@leave.<domain>" \
  --subject "Unsubscribe" \
  --body "Please unsubscribe me from all email lists."
```

Common pattern: `leave-<BASE32_ID>.<number>@leave.<sender-domain>`

## Step 5: Verify

Re-search Gmail a day later to confirm new emails from unsubscribed senders have stopped arriving:

```bash
gog -a cooper@darkmatter.io gmail search "from:<sender-domain> newer_than:1d" -j
```

## Pitfall: gog Keyring in Subprocess

`execute_code` runs Python subprocesses that do NOT inherit `GOG_KEYRING_PASSWORD` from the terminal environment. The keyring file backend requires this env var, and without it gog fails with:

```
read encoded file keyring item: aes.KeyUnwrap(): integrity check failed
```

**Fix:** Always run `gog` commands via `terminal()` (which inherits the shell environment) rather than via `execute_code`'s `subprocess.run()`. If you must use subprocess, first retrieve the password with `subprocess.run(["bash", "-c", "echo $GOG_KEYRING_PASSWORD"])` and pass it explicitly — but note that even this can fail due to AES key unwrapping issues in the subprocess context. The `terminal()` tool is the reliable path.
