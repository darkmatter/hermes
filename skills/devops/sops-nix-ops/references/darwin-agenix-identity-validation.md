# Darwin agenix identity/path incident pattern

Observed pattern:

- `nix build` and the Darwin configuration build can succeed.
- `org.nixos.activate-agenix` can still exit 1 before publishing `/run/agenix`.
- `/private/var/run/agenix.d` may be mounted and empty because the first decryption aborted.
- The generated script uses `set -e`; an invalid identity can stop all subsequent secret decryptions.

Durable diagnosis:

1. Inspect `launchctl print system/org.nixos.activate-agenix` and identify `last exit code`.
2. Inspect the generated `activate-agenix-start` script for `age.identityPaths`.
3. Test each identity against an encrypted file with `age --decrypt -o /dev/null`.
4. On macOS, check that the Application Support path includes `Library`.
5. Remove an ECDSA SSH key from `age.identityPaths`; a misleading `id_ed25519` filename does not guarantee Ed25519 key type.
6. Rebuild and apply with interactive sudo, then verify `/run/agenix/<name>` and launchd state.

Do not print or persist decrypted content during diagnosis.
