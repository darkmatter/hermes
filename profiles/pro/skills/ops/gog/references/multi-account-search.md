# Multi-Account Email Search & Output Handling

## Searching across multiple Gmail accounts

When looking for a specific email and the sender/account is unknown, search
ALL authenticated accounts. `gog auth list --json` shows which accounts
have Gmail scope authorized. An email that's nowhere in account A may be
in account B — users often have separate Gmail addresses for different
contexts (work vs personal vs project-specific).

```bash
export GOG_KEYRING_PASSWORD=<REDACTED>

# Get all accounts with gmail scope
gog auth list --json | jq -r '.accounts[] | select(.scope | test("gmail")) | .email'

# Search each account (example: looking for "lepisov")
for acct in $(gog auth list --json | jq -r '.accounts[] | select(.scope | test("gmail")) | .email'); do
  echo "=== $acct ==="
  gog -a "$acct" gmail list "lepisov" --max 30 --json | \
    jq -r '.threads[] | [.id, .date, .from, .subject] | @tsv'
done
```

### Pitfall: aliases resolving to the same token

`gog auth list` may show multiple emails (e.g. `me@cm.xyz`,
`me@cooperm.com`) that all resolve to the same underlying OAuth token
(`cooper@darkmatter.io`). Running `gog -a me@cm.xyz auth doctor` will
show `token.default.cooper@darkmatter.io` in the output — a sign the
alias doesn't have its own token. In this case `me@cm.xyz` was a
separate Gmail account that needed its own auth: `gog login me@cm.xyz
--services=gmail --gmail-scope=full --force-consent --remote --step 1`.

**Always verify the account has its own token** by checking
`gog -a <email> auth doctor` output for the token line — if it references
a different email, that account is NOT independently authed.

## Output truncation pitfalls

### `gog gmail read --plain` truncates long bodies

The `--plain` output mode truncates email bodies at an internal limit
(~700 chars of body text). For long emails (especially reply chains with
quoted history), the body gets cut off with `[truncated]`.

**Workaround:** Use `--json` and extract the body from the payload parts
manually:

```bash
gog -a <email> gmail read <threadId> --json 2>&1 | python3 -c "
import sys, json, base64, re
data = json.loads(sys.stdin.read())
msg = data['thread']['messages'][0]
for h in msg['payload']['headers']:
    if h['name'] in ['From','To','Subject','Date']:
        print(f'{h[\"name\"]}: {h[\"value\"]}')
for part in msg['payload'].get('parts', []):
    bdata = part.get('body',{}).get('data','')
    if bdata:
        decoded = base64.urlsafe_b64decode(bdata + '==').decode('utf-8', errors='replace')
        text = re.sub(r'<[^>]+>', '', decoded)
        print(text)
"
```

### `gog gmail list --json` can exceed terminal output cap

Large result sets (500+ threads) can produce JSON exceeding the 50KB
terminal output cap. The output gets silently truncated, causing JSON
parse failures in downstream Python.

**Workarounds:**
1. **Pipe through jq** to extract only needed fields as TSV:
   ```bash
   gog -a <email> gmail list "has:attachment after:2026/05/19" --max 500 --json | \
     jq -r '.threads[] | [.id, .date, .from, .subject] | @tsv'
   ```
2. **Reduce `--max`** to a smaller batch and paginate with `nextPageToken`.
3. **Use `execute_code`** with `terminal()` but parse with
   `json_parse()` (built-in, strict=False) which handles control chars
   better than raw `json.loads()`.
