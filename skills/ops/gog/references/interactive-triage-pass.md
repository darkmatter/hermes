# Interactive inbox triage pass (Cooper)

When Cooper says "triage my emails" (not the daily cron summarize job), run a **label-applying** multi-account pass. Summarize-only is incomplete.

## Scope defaults

| Account | Role |
|---|---|
| `cooper@darkmatter.io` | Work / primary |
| `me@cm.xyz` | Personal |

- Export **both** before every non-interactive shell (file keyring is forced on this machine):
  ```bash
  export GOG_KEYRING_BACKEND=file
  export GOG_KEYRING_PASSWORD=<REDACTED>
  ```
  `himitsu exec gog/keyring-password -- …` alone is **not** enough — gog looks for the env var name `GOG_KEYRING_PASSWORD`, and without `GOG_KEYRING_BACKEND=file` macOS Keychain may hang waiting for a GUI prompt.
- Always `-a <account>`; never merge query results across accounts without tagging account on every thread ID.
- Prefer `terminal()` (not nested `execute_code`) so keyring env inherits.
- **EXECUTE-SAFE:** label + archive only. No send / delete / pay / domain approve without Cooper.
- Prefer `--gmail-no-send` if only investigating.
- Always use label **names** (`Triage/Needs-Action`, `Muted/Bulk`, …). IDs differ per account (work: Done=`Label_31`, Bulk=`Label_32`, NA=`Label_34`; personal: Done=`Label_42`, Bulk=`Label_43`, NA=`Label_45`). Never pass personal-only helpers (`Action Required`, `Security Alert`) on the work account — Gmail returns `Invalid label: Action Required`.

## Multi-pass procedure (do not stop after first page)

Gmail `gmail list "in:inbox newer_than:Xd" --max 50` returns **one page**. As you archive bulk, **older untriaged threads advance into the next page**. Plan on **2–4 passes** until either:

1. Remaining inbox is mostly `Triage/Needs-Action` / security / financial, **or**
2. You have deliberately left a known long-tail for another session.

### Large bulk long-tails (drain until 0)

Before the general classify loop, exhaust known high-volume noise sources with dedicated paginated drains (batch ≤20–30 IDs, sleep 5–8s between pages; on `403 rateLimitExceeded` sleep ~70s and retry):

```bash
# Work: USPS Informed Delivery + Tracking via CT group
while true; do
  gog -a cooper@darkmatter.io --gmail-no-send gmail list \
    'in:inbox from:1801remodel@darkmatter.io' --max 20 -j > /tmp/usps.json
  n=$(jq '(.threads//[])|length' /tmp/usps.json); [[ "$n" -eq 0 ]] && break
  ids=$(jq -r '(.threads//[])[].id' /tmp/usps.json | tr '\n' ' ')
  gog -a cooper@darkmatter.io --gmail-no-send gmail labels modify $ids \
    --add 'Muted/Bulk' --remove 'INBOX,UNREAD' -y --no-input
  sleep 8
done

# Personal: GoDaddy auctions "Your search results" spam
# same loop with -a me@cm.xyz and 'in:inbox from:auctions@godaddy.com'

# Both: already-muted but still sitting in INBOX (common after partial runs)
# query: in:inbox (label:"Muted/Bulk" OR label:"Muted/Unsubscribe")
# action: --remove 'INBOX,UNREAD' only (do not re-add Bulk)
```

Also drain `in:inbox category:promotions` with a **keep-list** for money/security (Brex transfer restrictions, failed payments, domain renewals). Do **not** treat product marketing that merely contains brand tokens as NA — e.g. Kernel drip `cat@sup.kernel.sh` ("scaling your agent 7/7") is **Muted/Bulk**, while Kernel Stripe `failed-payments+…@stripe.com` is **NA**.

### Parallel subagents (no-input bulk only)

When Cooper asks to keep processing emails that do not need input:

1. Spawn **one leaf subagent per Gmail account** (work / personal). Give each a full self-contained brief: auth exports, safety boundary, mute/done/NA heuristics, verify-with-read-back, stop when remaining is only NA/security/financial/human.
2. Parent may also drain bulk in parallel, but **coordinate rate limits** — two subagents + parent will hit Gmail per-user QPM fast. Prefer parent does long drains while subagents classify, or serialize heavy modifies.
3. Subagent wall-clock is ~600s; design for multi-pass with sleep-on-403, not one giant loop.
4. When no-input-safe mail is gone, **ping Cooper** with ≤5 Critical items (body-based summary + proposed next action). Do not keep grinding ambiguous long-tail without a ping.
5. `hermes kanban` mutations may be blocked inside `delegate_task` child contexts — parent owns Kanban card creates/comments.

Per pass:

```bash
export GOG_KEYRING_BACKEND=file
export GOG_KEYRING_PASSWORD=<REDACTED>

gog -a cooper@darkmatter.io auth doctor --check   # refresh exchange must succeed
gog -a me@cm.xyz auth doctor --check

# Capture + compact TSV
gog -a cooper@darkmatter.io --gmail-no-send gmail list "in:inbox newer_than:3d" --max 50 --json \
  | tee /tmp/work-inbox.json \
  | jq -r '(.threads//[])[] | "\(.id)\t\(.date)\t\(.from)\t\(.subject)\t\((.labels//[])|join(","))"'

gog -a me@cm.xyz --gmail-no-send gmail list "in:inbox newer_than:3d" --max 50 --json \
  | tee /tmp/pers-inbox.json \
  | jq -r '(.threads//[])[] | "\(.id)\t\(.date)\t\(.from)\t\(.subject)\t\((.labels//[])|join(","))"'

# Also surface existing open NA (30d) so backlog is not forgotten
gog -a cooper@darkmatter.io --gmail-no-send gmail list 'label:"Triage/Needs-Action" newer_than:30d' --max 30 --json
gog -a me@cm.xyz --gmail-no-send gmail list 'label:"Triage/Needs-Action" newer_than:30d' --max 30 --json
```

Widen `newer_than` only if inbox is sparse; 3d is the default interactive window; 1d for quick morning morph.

## Classify → batch-label (one modify per bucket)

Read only ambiguous / critical threads (`gmail read <id> --plain`; zigzag to `--json` + base64 when body truncates at ~700 chars).

Bucketing map → labels: `gmail-triage-labels.md`. Shortcut batch shapes:

```bash
# Needs-Action (leave INBOX)
gog -a <account> gmail labels modify <id...> \
  --add "Triage/Needs-Action" -y --no-input
# personal helpers
gog -a me@cm.xyz gmail labels modify <id...> \
  --add "Triage/Needs-Action,Action Required" -y --no-input
gog -a me@cm.xyz gmail labels modify <id...> \
  --add "Triage/Needs-Action,Security Alert" -y --no-input

# Done + archive
gog -a <account> gmail labels modify <id...> \
  --add "Triage/Done" --remove "INBOX,UNREAD" -y --no-input

# Mute noise + archive
gog -a <account> gmail labels modify <id...> \
  --add "Muted/Bulk" --remove "INBOX,UNREAD" -y --no-input
```

When closing a former NA that is now handled, **also remove** the old action labels:

```bash
gog -a me@cm.xyz gmail labels modify <id> \
  --add "Triage/Done" \
  --remove "Triage/Needs-Action,Action Required,INBOX,UNREAD" -y --no-input
```

Batch many IDs per call (gog accepts multiple). Verify after batches:

```bash
gog -a <account> gmail list 'label:"Triage/Needs-Action" newer_than:3d' --max 40 --json
gog -a <account> gmail list "in:inbox newer_than:3d" --max 40 --json \
  | jq '{count:(.threads|length), still_unlabeled:[.threads[]|select((.labels//[]|map(test("Triage/|Muted/")))|length==0)|{from,subject}]}'
```

## Always-flag vs always-mute heuristics (interactive)

**Always `Triage/Needs-Action` (never mute):**

- Brex (debits, support tickets, business-detail KYC, draft bills)
- Gusto / Guideline 401(k) / payroll / QBO mapping todos
- Workers' comp / Hartford / AP Intego withdrawals
- Middesk / registered-agent mail "available"
- Cloudflare **Registrar Action Required** domain moves (Super Admin approve)
- GitHub: org **billing failed**, 2FA recovery codes viewed/download, OAuth you did **not** just authorize, FalconerAI/permission-update requests
- Hetzner/OVH **abuse** reports
- Apple Developer membership / cert expiry
- CoreSite / colocation sales threads Cooper started (Waiting only after Cooper explicitly parked)
- Payment declines: Tesla Insurance cancel notices, Google Fi, Affirm due, Capital One step-required, CDTFA, Saltbox overdue/termination, Vapi wallet auto-reload fail, Anthropic/Anomaly failed charges
- Human calendar invites on work (e.g. nixmac sync)
- Product activations Cooper initiated (PRLeap / Prelint credits low) if still incomplete

**Always mute+archive (`Muted/Bulk`):**

- Marketing: Perplexity, Temporal community, Homebase, Toggl drip, Supermicro, Higgsfield, Forbes drip, Amex/Chase promos, Venmo promo, Glasvin, GoDaddy **auctions search results** + marketing, OKX/Robinhood marketing, Ahrefs onboarding drip, Polar pitches, Alibaba Cloud newsletters, Cision webinars, When I Work / Vast.ai growth pitches, Secretlab/StubHub promos
- Kernel **product drip** (`cat@sup.kernel.sh`, "scaling your agent N/7") — not the same as Kernel **failed Stripe payment**
- USPS Tracking + Informed Delivery (via CT / 1801remodel) — drain until `in:inbox from:1801remodel@darkmatter.io` is 0
- Verda Cloud instance provision/discontinue noise (payment **receipts** → Done)
- Chromatic build status spam
- `vercel[bot]` / `github-actions[bot]` / `renovate[bot]` PR comment floods on personal (unless Cooper is actively reviewing that PR *in this session*)
- CoinTracker "new transactions" digests, Citrindex EOD snapshots
- Google Voice missed-call / voicemail noise (unless Cooper asked to surface calls)
- Already-labeled `Muted/*` threads still carrying `INBOX` → strip INBOX only

**Done + archive (informational / expected self-actions):**

- Payroll **confirmed** notices after Cooper already ran payroll
- BrandPush / PR "order completed" when article-ready sibling remains NA (or reverse—keep only the action twin)
- Expected Google/Vercel "new sign-in" after Cooper just authed
- Expected GitHub OAuth added right after Cooper signed up (prelint)
- PayPal legal agreement changes (no action)
- Receipts (Figma, Ahrefs, Vercel invoices, OakHost invoices, OpenRouter receipts) with no failure
- Expired one-time verification codes / card OTPs once the moment has passed
- Zelle **sent** confirmations and "recipient added" notices (informational); keep **failed** Zelle / fraud as NA
- Cassie/ops "this is paid!" closing a duty thread → Done and strip prior NA labels
- Incogni/Paddle / LegalZoom cancel confirms Cooper already wanted cancelled

## Critical digests shape (user-facing)

Lead with a **Critical (do soon)** table: money/insurance/billing first, then domains/infra, then people/ops. Then short **Cleared this pass** bullet examples. End with gated items not done and 3–5 highest-leverage next moves. Do **not** dump every muted subject.

Optional machine digest (cron/dashboard consumers):

```bash
mkdir -p ~/.hermes/feed/cron-json
# write comms-triage.json with generated_at + accounts + note
```

## Pitfalls

| Pitfall | Fix |
|---|---|
| One `list --max 50` then stop | Re-list after archive; second page is full of untriaged backlog |
| Label Done without removing `Triage/Needs-Action` | Dual-labeled threads stick in NA queries forever |
| Mute Brex / declines / insurance cancel | Financial failure mail is always NA |
| Treat CoreSite / human sales as bulk after Cooper replied | Keep NA or move to Waiting—not Mute |
| `--plain` truncated bodies on ACH amounts | Re-read critical money mail with enough of the thread; prefer reading full multi-message Brex debit threads (amounts differ per message) |
| CF domain move duplicates | Same 5 domains may spawn two ID sets (request + reminder); label both NA; one Super Admin approve clears the set |
| confining queries to `cooper@` only | Always Kemp both accounts; personal holds Tesla, Fi, Vapi, CDTFA |
| Closing session with no evidence | Paste verify counts / sample NA rows; never claim "cleared" from agent assertion alone |
| Keychain hang / empty tokens in agent shells | Force `GOG_KEYRING_BACKEND=file` + `GOG_KEYRING_PASSWORD` from himitsu on **every** gog invocation |
| `unauthorized_client` on refresh while tokens exist | Re-store OAuth client JSON: `himitsu read google/oauth-client-secret-darkmatter-drive.json > /tmp/cs.json && gog auth credentials set /tmp/cs.json -y --no-input && rm /tmp/cs.json`, then `auth doctor --check` |
| `Invalid label: Action Required` on work | Personal-only helper labels; work uses only `Triage/*` + `Muted/*` |
| Broad UNSAFE regex matching brand tokens (`KERNEL`, `payment`) | Prefer sender+subject pairs; Kernel product drip ≠ Kernel Stripe failure |
| Subagents + parent thrash Gmail QPM | Batch ≤20–30 modifies, sleep between pages, 70s backoff on 403; one account per subagent |
| `Muted/*` still in INBOX after "ok" | Drain `in:inbox (label:"Muted/Bulk" OR label:"Muted/Unsubscribe")` with `--remove INBOX,UNREAD` |
| Present huge action queues | ≤5 Critical items per user update; leave the rest labeled NA for the next pass |

## Safety reminder

Label/archive = EXECUTE-SAFE with read-back. Anything that spends money, rotates creds, approves Cloudflare moves, or sends mail = wait for Cooper.
