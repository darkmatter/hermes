# Process listing redaction

Avoid returning **unredacted full command lines or environments** from `ps auxww`, `pgrep -af`, or similar. API keys and tokens often appear as argv (`--api-key …`, `sk-…`, Bearer <REDACTED> or in environment-like process strings.

## Prefer constrained fields

```bash
ps -axo pid,user,pcpu,pmem,rss,etime,comm | head -25
```

Inspect full argv only for **selected** PIDs, and redact before chat:

```bash
ps -p <PID> -o command= | sed -E \
  -e 's/(--api-key[= ]+)[^ ]+/\1[REDACTED]/g' \
  -e 's/(Bearer <REDACTED>' \
  -e 's/(sk-[A-Za-z0-9_-]{8})[A-Za-z0-9_-]+/\1…[REDACTED]/g' \
  -e 's/(token[=: ]+)[^ ]+/\1[REDACTED]/gi'
```

Batch redaction if full command lines are unavoidable:

```bash
ps -axo pid,pcpu,pmem,rss,etime,command |
  sed -E \
    -e 's/(--api-key[= ]+)[^ ]+/\1[REDACTED]/g' \
    -e 's/(Bearer <REDACTED>' \
    -e 's/(sk-[A-Za-z0-9_-]{8})[A-Za-z0-9_-]+/\1…[REDACTED]/g' \
    -e 's/(token[=: ]+)[^ ]+/\1[REDACTED]/gi' |
  head -25
```

Prefer avoiding sensitive argv collection entirely over relying only on post-hoc redaction. Never paste raw `ps` lines containing secrets into the user-visible reply.
