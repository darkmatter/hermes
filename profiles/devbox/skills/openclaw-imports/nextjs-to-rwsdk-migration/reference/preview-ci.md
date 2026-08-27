# Per-PR preview CI

Two workflows that turn every PR into a live, browser-testable preview. Reuses the existing `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN` repo secrets — no new credentials.

---

## `.github/workflows/preview-deploy.yml`

```yaml
name: Preview Deploy

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main

permissions:
  contents: read
  pull-requests: write

concurrency:
  group: preview-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  deploy:
    name: Deploy preview to Cloudflare
    runs-on: ubuntu-latest
    env:
      CI: "true"
      ALCHEMY_PLAIN: "1"
      ALCHEMY_STAGE: pr-${{ github.event.pull_request.number }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID || vars.CLOUDFLARE_ACCOUNT_ID }}
      CLOUDFLARE_API_TOKEN: <REDACTED>
      CF_TEAM_DOMAIN: ${{ secrets.CF_TEAM_DOMAIN || vars.CF_TEAM_DOMAIN }}
      CF_AUD: ${{ secrets.CF_AUD || vars.CF_AUD }}
    steps:
      - uses: actions/checkout@v4

      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: 1.3.10

      - name: Install dependencies
        run: bun install --frozen-lockfile

      - name: Validate Cloudflare credentials
        run: |
          test -n "$CLOUDFLARE_ACCOUNT_ID" || { echo "Missing CLOUDFLARE_ACCOUNT_ID" >&2; exit 1; }
          test -n "$CLOUDFLARE_API_TOKEN" || { echo "Missing CLOUDFLARE_API_TOKEN" >&2; exit 1; }

      - name: Bootstrap Alchemy state store
        run: bun alchemy cloudflare bootstrap

      - name: Generate blog manifest
        run: bun run generate:blog-manifest

      - name: Build with Vite
        run: bun run build

      - name: Deploy with Alchemy
        id: deploy
        run: |
          set -euo pipefail
          bun alchemy deploy ./alchemy.run.ts --stage "$ALCHEMY_STAGE" --yes 2>&1 | tee /tmp/alchemy.log
          url=$(grep -oE 'https://[a-z0-9-]+\.[a-z0-9-]+\.workers\.dev' /tmp/alchemy.log | tail -n1 || true)
          if [ -z "$url" ]; then
            echo "Could not parse preview URL from alchemy output" >&2
            exit 1
          fi
          echo "preview_url=$url" >> "$GITHUB_OUTPUT"
          echo "Preview URL: $url"

      - name: Smoke-test the preview
        env:
          PREVIEW_URL: ${{ steps.deploy.outputs.preview_url }}
        run: |
          set -euo pipefail
          fail=0
          for path in / /blog /posts /products /feed.xml /sitemap.xml ; do
            code=$(curl -sS -o /dev/null -w "%{http_code}" "${PREVIEW_URL}${path}" || echo "000")
            printf "%-20s %s\n" "$path" "$code"
            case "$code" in
              2*|3*) ;;
              *) fail=1 ;;
            esac
          done
          exit "$fail"

      - name: Comment on PR
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: rwsdk-preview
          message: |
            ### 🚀 RedwoodSDK preview deployed

            | Stack | Stage | URL |
            | ----- | ----- | --- |
            | `${{ github.repository }}` | `pr-${{ github.event.pull_request.number }}` | ${{ steps.deploy.outputs.preview_url }} |

            The preview is rebuilt on every push. It's destroyed when the PR closes.

            <sub>Built with Alchemy + RedwoodSDK · ${{ github.sha }}</sub>
```

Key bits:

- `permissions: pull-requests: write` is required for the sticky comment. GitHub silently drops the comment if missing.
- `concurrency: cancel-in-progress` kills the old deploy when a new push lands. Saves runner minutes; avoids race conditions with the state store.
- The URL parser greps for `*.workers.dev` because alchemy's structured output isn't stable yet.
- Smoke test uses curl, not playwright — playwright is for ad-hoc human verification of complex routes.

---

## `.github/workflows/preview-cleanup.yml`

```yaml
name: Preview Cleanup

on:
  pull_request:
    types: [closed]
    branches:
      - main

permissions:
  contents: read
  pull-requests: write

jobs:
  destroy:
    name: Destroy preview stage
    runs-on: ubuntu-latest
    env:
      CI: "true"
      ALCHEMY_PLAIN: "1"
      ALCHEMY_STAGE: pr-${{ github.event.pull_request.number }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID || vars.CLOUDFLARE_ACCOUNT_ID }}
      CLOUDFLARE_API_TOKEN: <REDACTED>
      CF_TEAM_DOMAIN: ${{ secrets.CF_TEAM_DOMAIN || vars.CF_TEAM_DOMAIN }}
      CF_AUD: ${{ secrets.CF_AUD || vars.CF_AUD }}
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: 1.3.10

      - name: Install dependencies
        run: bun install --frozen-lockfile

      - name: Destroy preview
        run: bun alchemy destroy ./alchemy.run.ts --stage "$ALCHEMY_STAGE" --yes

      - name: Comment on PR
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: rwsdk-preview
          message: |
            ### 🧹 RedwoodSDK preview destroyed

            Stage `pr-${{ github.event.pull_request.number }}` removed.
```

Same `header: rwsdk-preview` so the cleanup message replaces the deploy message on the PR (sticky comments are keyed by header).

---

## Trying it locally first

Before opening a draft PR, kick the deploy manually for your dev stage:

```bash
bun run build
bun alchemy deploy ./alchemy.run.ts --stage dev --yes
```

If that succeeds, the CI path will too. The most common cause of CI-only failures is an unrelated env var the workflow doesn't pass — diff the env in the workflow against your local `.<REDACTED>` to find it.

---

## Production deploy stays separate

The merge-to-main production deploy lives in a separate `alchemy-deploy.yml` and runs on `push` to `main`, not on PRs. Don't merge it into the preview workflow — production needs different secrets, different concurrency, and a different stage name.

---

## Cost: ~free

Each PR preview is a single Cloudflare Worker bound to the assets static-deploy. Workers' free tier covers 100k req/day; sticky preview comments live in GitHub. The only real cost is the few cents per minute of runner time per push, and Cloudflare worker upload metadata.
