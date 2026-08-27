# Enterprise registration for Cilicon Mac runners

Companion to `cilicon-mac-runner-fleet`. Captures the 2026-07 path from org-scoped Cilicon → enterprise `darkmatter`.

## Why github provisioner cannot promote runners today

Cilicon 2.4.2 (traderepublic/Cilicon):

- `GithubProvisionerConfig`: `appId`, `organization`, optional `repository`, `privateKeyPath`, `extraLabels`, `runnerGroup`, optional `url`
- `GithubService` installation URLs:
  - `GET /orgs/{org}/installation` or `GET /repos/{org}/{repo}/installation`
  - `POST .../actions/runners/registration-token` under **orgs/** or **repos/** only
- `GithubActionsProvisioner` always:
  - App JWT → installation token → org/repo registration token
  - `config.sh --url <githubConfig.url defaulting to https://github.com/{org}[/repo]>`
  - optional `--runnergroup`
  - always `--ephemeral --unattended --replace`

There is **no** `/enterprises/{slug}/...` path and no PAT auth mode.

GitHub product rule (matches ARC docs in darkmatter/gitops):

> Enterprise-level runner registration requires a classic PAT with `admin:enterprise`. GitHub App credentials cannot register enterprise runners.

## Token / config matrix

| Scope | Registration token | `config.sh --url` | Typical auth |
|---|---|---|---|
| Repo | `POST /repos/{o}/{r}/actions/runners/registration-token` | `https://github.com/{o}/{r}` | App or PAT |
| Org | `POST /orgs/{o}/actions/runners/registration-token` | `https://github.com/{o}` | App (Cilicon default) or PAT |
| Enterprise | `POST /enterprises/{slug}/actions/runners/registration-token` | `https://github.com/enterprises/{slug}` | **PAT `admin:enterprise` only** |

darkmatter enterprise slug: **`darkmatter`** → URL `https://github.com/enterprises/darkmatter`.

## Credentials already in the org

| Use | Store |
|---|---|
| ARC enterprise scale sets | himitsu `github/darkmatter-pat` → gitops KSOPS `arc-enterprise-github-pat` (`github_token`) |
| Cilicon **org** App | appId `3999123`, host `~/github.pem` |
| Do not confuse | himitsu `github/darkmatter-bot` app `3663660` |

For Mac enterprise: install the **same class of PAT** on each Mac host (mode 600 file or agent-accessible secret store). Do not commit; do not bake into Tart OCI image.

`gh` without `admin:enterprise` returns 404-looking failures on enterprise runner APIs — grant scope + SSO before trusting “not found”.

## Groups (observed under org `darkmatter`)

Org-local vs inherited (names collide — use IDs when PATCHing):

| Name | inherited | allows_public_repositories | Notes |
|---|---|---|---|
| Default | false | true | Org default |
| public | false | true | Org public group |
| Default | true | **false** | Enterprise Default at org |
| public | true | true | Enterprise public at org (ARC `arc` scale set uses enterprise `public`) |
| dm-aarch64-darwin | true | false | Natural Mac enterprise target for private work |
| dm-x86_64-linux / dm-aarch64-linux / x86_64-linux | true | false | Linux named groups |
| overlay-eval | true | false | selected visibility |

Policy pick:

- Private / trusted only → enterprise group with `allows_public_repositories: false` (e.g. `dm-aarch64-darwin` or Default)
- Public repos must schedule on Mac → group that allows public (enterprise `public` or dedicated group)

Inherited groups often arrive with `visibility: selected` and empty repository list on member orgs. Symptom: jobs queued forever while runners look idle.

```bash
gh api /orgs/<org>/actions/runner-groups
gh api -X PATCH /orgs/<org>/actions/runner-groups/<org-local-id> -f visibility=all
# re-dispatch workflows; scale-set/runner routing is decided at queue time
```

## Script provisioner sketch (enterprise)

Cilicon still owns Tart/VM; registration becomes a script. Adjust runner download pinning, labels, and group name.

```yaml
source: oci://ghcr.io/darkmatter/nixmac-runner-tahoe:<tag>
consoleDevices:
  - tart-version-2
sshConnectMaxRetries: 30
provisioner:
  type: script
  config:
    run: |
      set -euo pipefail
      PAT="$(cat "${HOME}/github-enterprise.pat")"
      NAME="$(scutil --get ComputerName 2>/dev/null || hostname -s)"
      LABELS="self-hosted,macOS,ARM64,nixmac-mac"
      GROUP="dm-aarch64-darwin"   # or public, etc.

      mkdir -p "${HOME}/actions-runner"
      cd "${HOME}/actions-runner"
      if [[ ! -x ./config.sh ]]; then
        # Pin a known actions/runner release for osx arm64, or use
        # GET /enterprises/darkmatter/actions/runners/downloads with PAT
        echo "install runner binaries first" >&2
        exit 1
      fi

      TOKEN=<REDACTED>
        -X POST \
        -H "Authorization: Bearer <REDACTED>" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "https://api.github.com/enterprises/darkmatter/actions/runners/registration-token" \
        | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])')"

      ./config.sh \
        --url "https://github.com/enterprises/darkmatter" \
        --token "${TOKEN}" \
        --name "${NAME}" \
        --runnergroup "${GROUP}" \
        --labels "${LABELS}" \
        --work "_work" \
        --replace \
        --ephemeral \
        --unattended

      ./run.sh
```

Host prep:

1. Write PAT to `~/github-enterprise.pat` (600), sourced from himitsu
2. Ensure runner tarball present or download step pdf
3. Pre-pull OCI image with Tart + GHCR creds
4. Restart Cilicon from GUI session
5. Confirm runner on **enterprise** list, not only `orgs/darkmatter/actions/runners`
6. Cross-org job smoke, then remove org-registered Cilicon runners

## Cutover checklist

- [ ] Enterprise group chosen + public-repo policy OK
- [ ] Member orgs: inherited group `visibility=all` (or selected repo list correct)
- [ ] PAT on each Mac host; SSO authorized
- [ ] `cilicon.yml` → script (or patched Cilicon) enterprise registration
- [ ] Labels preserved (`nixmac-mac`, etc.)
- [ ] Cilicon restarted from login/GUI
- [ ] `GET /enterprises/darkmatter/actions/runners` shows macOS online
- [ ] Job from non-`darkmatter` enterprise org assigned
- [ ] Second ephemeral cycle re-registers
- [ ] Old org runners drained

## Medium-term fork delta (if re-adding first-class config)

- Config: `enterprise: darkmatter` **or** honor `url: https://github.com/enterprises/darkmatter` for API base selection
- Auth mode: `tokenPath` / PAT env, skip App installation when enterprise
- Service paths: `/enterprises/{slug}/actions/runners/{registration-token,downloads,...}`
- Keep org App path for single-org fleets

Upstream still uses App-only org model as of Cilicon main around 2.4.x docs.

## Related

- gitops: `apps/arc-runners-enterprise.yaml`, `manifests/arc-runners/README.md`
- Image/cutover nuances: Packer + GHCR live under nixmac ops; SSH MAC workarounds for Tahoe belong in image bake, not host one-offs
