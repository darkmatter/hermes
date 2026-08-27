# Darwin host attrs + rebuild 401

## Flake attr = hostname

| Machine | `~/.config/darwin/host` / rebuild attr |
|---|---|
| Studio | `Coopers-Mac-Studio` |
| Pro | `Coopers-Mac-Pro` |

Host ids like `coopers-mac-studio` / `macpro` are **not** darwinConfigurations keys.

## GitHub 401 on sudo switch

Symptom: user `darwin-rebuild build` OK; `sudo … switch` fails downloading `comin`/github:

`Deprecated authentication method. Create a Personal Access Token…`

Causes:

1. `/run/agenix/github_token` missing until first successful switch (chicken-and-egg).
2. `~/.netrc` `login oauth` + `github_pat_*` password treated as deprecated Basic auth password.

Fixes:

- netrc: `machine github.com` / `login x-access-token` / `password ghp_…`
- `./rebuild.sh` (9469f70+) injects `NIX_CONFIG=access-tokens = github.com=…` under sudo from agenix → user access-tokens.conf → himitsu.
- Manual: `eval "$(./scripts/nix-github-token-env.sh)"` then sudo with `NIX_CONFIG` preserved.

## Nix launchd path quoting

Bare `${cloudflaredBin}` inside `ProgramArguments = [ … ]` splits the store path into list elements. Always `"${cloudflaredBin}"`.
