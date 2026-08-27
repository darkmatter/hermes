# Email Triage Reference

## Gmail Search Query Patterns

### Time ranges
```
newer_than:1d    # last 24 hours
newer_than:7d    # last week
newer_than:30d   # last month
older_than:30d   # older than a month
```

### Inbox + read status
```
in:inbox is:unread                    # unread inbox
in:inbox is:read                      # read but still in inbox
is:unread -in:inbox                   # unread, not in inbox (labels only)
```

### Sender / recipient
```
from:user@example.com                 # specific sender
to:me cc:user@example.com             # CC'd (likely FYI, low urgency)
from:(user1 OR user2)                 # multiple senders
-list:(list1,list2)                   # exclude mailing lists
```

### Category / importance
```
category:primary                      # primary tab
category:promotions                   # promotions tab
category:updates                      # updates tab
category:social                       # social tab
label:IMPORTANT                       # Gmail-marked important
```

### Attachment / size
```
has:attachment                        # has attachment
filename:pdf                          # PDF attachment
larger:5M                             # over 5MB
```

### Combined triage queries
```
# High-signal: unread primary inbox, last 30 days
in:inbox is:unread category:primary newer_than:30d

# Low-signal bulk: promotions + social, older than a week
(category:promotions OR category:social) older_than:7d

# FYI / CC only: not directly addressed
cc:me -to:me newer_than:7d

# Newsletters / subscriptions
from:(newsletter OR digest OR "no-reply") newer_than:30d
```

## Agent Triage Workflow

1. **Fetch inbox overview** — unread primary inbox for the requested time range:
   ```bash
   gog gmail list "in:inbox is:unread category:primary newer_than:30d" -j --max 100
   ```

2. **Group by sender** — after fetching, group messages by `from` address in code to identify volume patterns.

3. **Read high-signal threads** — for senders with multiple messages or known-important contacts:
   ```bash
   gog gmail read <message-id> -j
   gog gmail thread <thread-id> -j
   ```

4. **Summarize** — present grouped digest: sender, subject, count, urgency signal.

5. **Action** — for each group, suggest:
   - Archive / label if handled elsewhere
   - Reply if needed
   - Flag for follow-up

6. **Bulk cleanup** (optional, with user approval):
   ```bash
   gog gmail modify <id> --remove-labels INBOX       # archive
   gog gmail modify <id> --add-labels IMPORTANT      # flag
   gog gmail trash <id>                              # delete
   ```

## Pagination & Fetching Large Inboxes

`--max` caps results per call (default 10, up to ~500). Two ways to get everything:

- **`--all`** — fetch ALL pages automatically. Works for inboxes under ~1000 threads. **WARNING**: on very large inboxes (5000+ threads), the rapid-fire pagination hits Gmail API rate limits (`403 rateLimitExceeded: Quota exceeded for quota metric 'Queries'`). For those inboxes, use manual pagination (below).
- **`--page <token>`** — manual pagination using the `nextPageToken` from a prior JSON response (the flag is `--page`, NOT `--page-token`).

A 30-day darkmatter inbox can be ~850 threads; a 13-month inbox can be 5000+ threads.

### At-scale triage technique (CRITICAL for large inboxes)

When fetching hundreds of threads, the execute_code stdout cap (~20KB) will truncate
JSON mid-stream and break `json.loads`. ALWAYS redirect to a file from the terminal,
then parse the file:

```bash
# Step 1: dump full inbox to a file (terminal, not execute_code stdout)
gog gmail list "in:inbox newer_than:30d" -j --all > /tmp/inbox.json 2>/tmp/inbox_err.txt
wc -c /tmp/inbox.json   # sanity-check size

# Step 2: classify in Python (read the file, never re-print the whole blob)
```

### Manual pagination with rate-limit safety (for 5000+ thread inboxes)

When `--all` hits rate limits, paginate manually from `execute_code` with a 3-second
delay between pages. This was validated on a 5000-thread inbox (50 pages at `--max 100`):

```python
import subprocess, json, time, os

all_threads = []
next_page = None
env = os.environ.copy()
env["GOG_KEYRING_PASSWORD"] = "<from himitsu: gog/keyring-password>"

while True:
    cmd = ["gog", "--gmail-no-send", "gmail", "list", "in:inbox", "-j", "--max", "100"]
    if next_page:
        cmd.extend(["--page", next_page])
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    data = json.loads(result.stdout)
    all_threads.extend(data.get("threads", []))
    next_page = data.get("nextPageToken")
    if not next_page:
        break
    time.sleep(3)  # respect Gmail API per-minute quota

# Reverse for oldest-first triage
all_threads.reverse()
```

Rate-limit recovery: if you still get `403 rateLimitExceeded`, wait 65+ seconds for the
per-minute quota window to reset, then resume from the last successful page token.

Classification heuristics (validated on 5000-thread inbox):
- Parse `from` with `re.search(r'<([^>]+)>', frm)` to extract the bare email.
- Bucket by `CATEGORY_*` label (CATEGORY_PROMOTIONS/UPDATES/PERSONAL/FORUMS/SOCIAL/PRIMARY).
- **Financial action filter**: regex subjects for `(due|overdue|failed|declined|action required|returned|deposited|withdrawal|payroll|wire transfer|\$[\d,]+)` against known finance domains (brex.com, gusto.com, coinbase.com, stripe.com, mercury.com) — this surfaces genuinely time-sensitive items.
- **Human correspondence**: maintain an explicit allowlist of known colleague/vendor addresses; naive `firstname@` regex over-matches automated `team@`/`support@`/`hello@` senders. A noreply regex `(no-?reply|noreply|newsletter|notifications?@|alerts?@|donotreply|mail\.|tm\.)` filters most bulk.
- Single highest-volume sender is often one noisy system (e.g. provisioning/receipt auto-mail) — call it out as the top archive candidate.
- At 5000 threads, 68% are typically safe bulk-archive (automated + promotions + forums + social). Present this as the first approval batch.


## Read-Only Triage Safety

Always use `--gmail-no-send` when doing triage that should not send email:
```bash
gog --gmail-no-send gmail list "in:inbox" -j --max 100
```
