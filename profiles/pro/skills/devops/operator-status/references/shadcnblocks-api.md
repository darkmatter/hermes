# @shadcnblocks Direct API Access (without MCP)

When the shadcn MCP server is not configured (`hermes mcp list` returns empty), access the @shadcnblocks registry directly via HTTP.

## Registry endpoint

```
URL:    https://shadcnblocks.com/r/{name}
Header: x-api-key: <key>
```

Key lives in himitsu: `himitsu read shadcnblocks-api-key`.

Note: The `components.json` registry config uses the `x-api-key` header (NOT `Authorization: Bearer`).

## Discovering blocks by name scanning

There is no search endpoint. Block names follow `<prefix><number>` convention. Scan by iterating:

```bash
KEY=$(himitsu read shadcnblocks-api-key)
for i in $(seq 1 50); do
  STATUS=$(curl -sL -o /dev/null -w "%{http_code}" -H "x-api-key: $KEY" "https://shadcnblocks.com/r/dashboard${i}")
  if [ "$STATUS" = "200" ]; then echo "dashboard${i} -> 200"; fi
done
```

Known prefixes: `dashboard`, `sidebar`, `stats`, `hero`, `navbar`, `footer`, `pricing`, `feature`, `testimonial`, `faq`, `cta`, `login`, `table`, `form`, `chart`.

## Fetching block metadata

```bash
curl -sL -H "x-api-key: $KEY" "https://shadcnblocks.com/r/dashboard9"
```

Returns JSON with: `name`, `title`, `description`, `dependencies` (npm packages), `registryDependencies` (shadcn UI components), `files` (array of `{target, content}`).

## Installing blocks

```bash
cd ~/feed  # wherever components.json lives
bunx --bun shadcn@latest add @shadcnblocks/dashboard9 --overwrite --yes
```

Installs the block AND all registry dependencies in one step. `--overwrite` prevents interactive prompts about existing files. `--yes` skips confirmation prompts.

## Pattern: present options before building

Cooper prefers choosing from a shortlist of 3-4 block candidates before committing. Fetch metadata for all matching blocks, present descriptions via a `clarify` tool call with choices, then install the winner.

```python
import json, subprocess, concurrent.futures

KEY = subprocess.check_output(["himitsu", "read", "shadcnblocks-api-key"], text=True).strip()
blocks = [f"dashboard{i}" for i in range(1, 19)]

def fetch_meta(name):
    try:
        out = subprocess.check_output(
            ["curl", "-sL", "-H", f"x-api-key: {KEY}", f"https://shadcnblocks.com/r/{name}"],
            text=True, timeout=15)
        d = json.loads(out)
        return {"name": d.get("name"), "title": d.get("title"), "description": d.get("description")}
    except:
        return {"name": name, "error": "failed"}

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(fetch_meta, blocks))
```

Note: The `shadcn-registry-first` skill (in the `devbox` profile) describes the MCP-based workflow but does NOT cover this direct API fallback. This reference fills that gap for the default profile.
