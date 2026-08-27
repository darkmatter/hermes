# 1P missing items — as-needed vault cm

Cooper chose policy **1**: when SA catalog lacks a needed login/card, ask to move **that one title** into vault **`cm`**. Do not bulk-nag.

## Rules

- Catalog first: `~/.hermes/op-sa-catalog.json` (parent refreshes; children read)
- Only `~/.local/bin/op` + himitsu `op-service-account/token` + `--vault`
- Never biometric / bare brew-nix op / agenix personal token
- After Cooper moves an item: refresh catalog before retrying

Full SA rules: `references/op-service-account.md` (if editable) and skill body §2.
