# Native Dropbox Client as a Hermes Skill Source

Use this reference when Dropbox’s official desktop/Linux client is installed on the Hermes host or on the machine that owns the live skill tree. Prefer the native client over a newly introduced API mount when it already fits the user’s workflow; it removes a second mount daemon and a second long-lived OAuth configuration.

## Detection: binary, daemon, and sync root are separate facts

On Linux, the bootstrap executable is commonly installed at:

```text
~/.dropbox-dist/dropboxd
```

The running process may instead be a versioned `.../dropbox-lnx.<arch>-<version>/dropbox` binary. Neither command has to be on `PATH`. Therefore:

1. Check the known installation directory in addition to `command -v`.
2. Check the actual process owner and executable.
3. Discover the synchronized root from `~/.dropbox/info.json`; do not assume `~/Dropbox`.
4. If `info.json` contains multiple account entries (for example personal and business), select the account explicitly rather than taking the first mapping value.

Treat these as independent checks. An executable can exist without a running daemon, and a running daemon does not prove that a particular remote folder has downloaded.

## Readiness rule

**The target skill directory is the readiness signal.** Do not repoint Hermes merely because `dropboxd` exists or its process is running.

Before cutover, require all of the following:

- The account-specific sync root is known.
- `<sync-root>/Hermes Skills/<skill>/SKILL.md` exists as a regular file.
- Every support directory (`references/`, `templates/`, `scripts/`, `assets/`) expected by the source is present.
- The native file’s digest matches the currently live source or the Dropbox API object.
- The runtime identity can read and write the directory.
- Fresh propagation checks pass in both directions.

A native client may still be indexing, downloading metadata, applying selective-sync rules, or waiting on account linkage after its daemon starts. Keep the existing source live until file-level readiness is proven.

## Migrating from an rclone-backed source

Use a staged handoff so there is never an empty or ambiguous runtime source:

1. **Keep rclone live.** Leave the current registration and mount service unchanged while the native client downloads the subtree.
2. **Discover the native root.** Parse `~/.dropbox/info.json` and choose the intended account.
3. **Wait for complete hydration.** Verify the skill file and all support directories, not just the parent folder.
4. **Compare integrity.** Hash the native `SKILL.md` and the live/rclone or remote object. Resolve any conflict before proceeding.
5. **Verify Dropbox → native host.** Create a uniquely named remote probe through an independent Dropbox API client or another synchronized workstation; observe it under the native root within a bounded timeout.
6. **Verify native host → Dropbox.** Create a uniquely named file under the native root; observe it through the independent API/client. Remove both probes everywhere afterward.
7. **Cut over atomically.** Replace the Hermes registration symlink with one targeting `<native-root>/Hermes Skills/<skill>` using a sibling temporary link plus atomic rename.
8. **Load and verify.** Confirm the resolved path, parse with `skill_view`, and compare hashes again.
9. **Retire the old transport.** Only now stop/disable the rclone mount and remove its declarative service. Keep the rclone credential briefly only if needed for rollback, then remove it through the user’s approved credential lifecycle.
10. **Reload registrations.** Use `/reload-skills`; use a fresh session when already-loaded instructions must be refreshed.

Do not point both the rclone mount and native Dropbox directory at the same Hermes registration. Two synchronized local directories can coexist during migration, but only one may be the registered writable source.

## Verification checklist

- [ ] Native client installation found without relying solely on `PATH`
- [ ] Correct Dropbox account and sync root selected from `info.json`
- [ ] Daemon process owner/executable verified
- [ ] Complete skill directory hydrated under the native root
- [ ] Native/live/remote hashes agree
- [ ] Independent remote → native probe passed
- [ ] Independent native → remote probe passed
- [ ] Registration atomically points to the native directory
- [ ] `skill_view` loads the expected skill
- [ ] Old mount retired only after successful cutover
- [ ] All probes and temporary migration artifacts removed

## Pitfalls

- Treating `dropboxd` on `PATH` as the only installation test.
- Looking only for a process named `dropboxd`; the active binary may be named `dropbox` under a versioned directory.
- Assuming the sync root is always `~/Dropbox` or selecting the wrong account from `info.json`.
- Switching registration before the target skill and support files materialize.
- Stopping the known-good rclone service as soon as the native daemon starts.
- Calling a native folder “synced” without an independent two-way propagation test.
