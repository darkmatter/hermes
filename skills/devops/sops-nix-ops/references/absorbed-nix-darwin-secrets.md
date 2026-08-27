---
name: nix-darwin-secrets
description: Diagnose and safely operate agenix/sops-nix secrets on nix-darwin, including identity-path failures, LaunchDaemon activation, generated secret paths, and verification without exposing secret contents.
---

# nix-darwin secrets operations

Use this class-level skill when a nix-darwin rebuild succeeds but agenix/sops secrets are absent, `org.nixos.activate-agenix` exits nonzero, or a generated service needs safe identity/path diagnosis.

## Safety rules

- Never print, copy, paste, commit, or report decrypted secret values.
- Use decryptability checks that write to `/dev/null`.
- Inspect generated activation scripts and launchd state for paths, status, and errors only.
- Keep unrelated working-tree changes untouched; commit only the intended Nix changes.
- Treat full system build and privileged activation as separate verification stages.

## Workflow

1. **Confirm declarations and encryption material**
   - Verify the host imports the Darwin module aggregator containing `secrets.nix`.
   - Verify the encrypted file exists in `secrets/` and its recipient policy includes an identity available on the host.
   - Do not infer that a missing `/run/agenix/<name>` means the encrypted file is absent.

2. **Separate build from activation**
   - Build the exact Darwin target as the target user.
   - Apply with the required interactive sudo step.
   - A successful Nix build does not prove launchd/agenix activation succeeded.

3. **Diagnose agenix launchd failures**
   ```bash
   launchctl print system/org.nixos.activate-agenix
   launchctl print system/org.nixos.sops-install-secrets
   find /private/var/run/agenix.d -maxdepth 2 -type f -print
   ```
   Inspect the generated `activate-agenix-start` script for identity paths and the first failing operation. On macOS, the RAM-disk setup under `/private/var/run/agenix.d` can succeed while decryption fails before `/run/agenix` is published.

4. **Validate identities without exposing secrets**
   ```bash
   age --decrypt -i "$HOME/.config/age/keys.txt" \
     -o /dev/null ~/darwin/secrets/openrouter-api-key.age
   ```
   Test each permitted identity independently if needed. Keep stdout and stderr limited to status/errors; never write plaintext to a file that persists.

5. **Handle identity-path pitfalls**
   - Do not put an ECDSA SSH private key in `age.identityPaths`; `age` rejects it as an unsupported SSH identity.
   - A filename such as `~/.ssh/id_ed25519` is not proof of Ed25519 type; inspect the actual key type without exposing private material.
   - On macOS, use the actual age-key locations, especially:
     ```nix
     "${user.homeDirectory}/Library/Application Support/sops/age/keys.txt"
     "${user.homeDirectory}/.config/age/keys.txt"
     ```
   - Keep `age.identityPaths` distinct from `sops.age.sshKeyPaths`; inspect the generated consumer because their accepted identity formats differ.
   - A typo omitting `Library` from the macOS Application Support path silently removes a valid fallback identity.

6. **Verify after the fix**
   ```bash
   test -r /run/agenix/openrouter-api-key && echo available || echo missing
   test -r /run/agenix/op-service-account-token && echo available || echo missing
   launchctl print system/org.nixos.activate-agenix | grep -E 'state =|last exit code'
   ```
   Also verify the consuming application’s non-secret status, e.g. provider configuration or MCP connectivity, without printing the secret.

## Focused verification

For a small Nix identity-path edit, use an OS-safe temporary verifier with a `hermes-verify-` prefix under the platform temp directory. Assert the bad identity is absent from the `age.identityPaths` block, the correct paths occur exactly once, and run `nix-instantiate --parse`. Clean the verifier afterward. This is ad-hoc evidence, not a full test-suite result.

## Common mistakes

- Treating `nix build` success as proof that launchd activation and secret publication succeeded.
- Debugging only `/run/agenix`; inspect `/private/var/run/agenix.d` and the launchd exit code.
- Passing an ECDSA SSH key to age because its filename says `id_ed25519`.
- Fixing the encrypted file or recipients when the actual issue is an invalid local identity path.
- Copying a plaintext secret from one machine to another instead of fixing the declarative identity configuration.
- Overwriting unrelated local changes while committing the fix.

## References

- `references/darwin-agenix-identity-validation.md` — concise reproduction and verification notes for macOS agenix identity/path failures.
