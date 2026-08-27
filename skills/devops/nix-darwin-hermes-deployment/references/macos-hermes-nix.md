# macOS Hermes/Nix reference

Official source: https://hermes-agent.nousresearch.com/docs/getting-started/nix-setup

## Platform distinction

The official docs describe `nix run` / `nix profile install` for macOS and other Nix users. The declarative Hermes NixOS module is for NixOS; do not try to apply it as a nix-darwin service module. A nix-darwin repository may still install the official Hermes package and manage `~/.hermes/` through Home Manager.

## Deployment evidence matrix

| Check | Meaning |
|---|---|
| `nix build ...darwinConfigurations.<host>.system` | System generation evaluates/builds; no activation yet |
| `./rebuild.sh` build success | Same as above unless the sudo activation phase also succeeds |
| `readlink ~/.hermes/config.yaml` points to Nix store | Home Manager installed the declarative Hermes config |
| `hermes mcp test cua-driver` connected | Local Hermes can reach local CuaDriver; does not prove model credentials |
| `/run/agenix/<name>` readable | Secret was decrypted/materialized by privileged activation |
| `launchctl print system/org.nixos.activate-agenix` last exit 0 | agenix LaunchDaemon ran successfully |

## Safe secret diagnosis

- Confirm encrypted file presence and recipients from Git/Nix metadata.
- Test `age --decrypt -i <identity> -o /dev/null <file>` only; discard plaintext.
- If decryptability succeeds but `/run/agenix` is empty, investigate launchd/agenix execution rather than changing recipients or copying secrets.
- Never put plaintext keys in the flake, Home Manager source, Git history, or chat output.
