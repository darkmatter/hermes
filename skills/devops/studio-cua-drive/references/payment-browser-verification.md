# Payment/browser verification notes

Use this as a recovery checklist when a payment task must run through the dedicated Mac Studio.

## Verified route

1. SSH target: `coopermaruyama@<REDACTED>`
2. Studio binary: `~/.local/bin/cua-driver`
3. Read-only checks:
   - `cua-driver permissions status --json` → require Accessibility true. Screen Recording may report false even when browser capture still works via CDP (see recovery) — do not stall on it.
   - `cua-driver status` → require a running daemon and socket.
   - `printf '%s' '{"session":"<stable>","capture_scope":"window"}' | cua-driver call start_session` (also revives an ended session on the same id).
4. Find Chrome with `list_windows`; select the exact PID and native window ID.
5. Run `browser_prepare` with `{strategy:{kind:"existing_profile"}}`, then `get_browser_state`; browser actions require the returned exact `target_id`.

## Verification rule

`effect: "unverifiable"` means input delivery only. It does not prove that a URL loaded, a form changed, or a payment succeeded. Re-capture or read browser state and require the expected page/URL before continuing. The vmap sweep's `value` column (see `studio-cua-vision-drive`) doubles as form read-back.

## Recovery conditions

- `browser_requires_setup`: run `browser_prepare` again for the exact PID/window.
- `authorization_host_failed` / "target bt-… is not a live binding in this session": the daemon restarted and every browser binding died. Re-run `get_browser_state` in bind mode (pid + window_id) to mint a fresh `target_id` + `tabs[]`. Old target/tab ids are dead forever — never reuse them.
- `browser_consent_required`: restart the driver-owned daemon with the existing-profile grant when the Studio is already authorized; do not click macOS permission dialogs from the agent.
- `browser_wrong_target_refused`: the exact Chrome consent/target is not available; do not guess a target or fall back to headless automation.
- `px_capture_unavailable` on `get_window_state` ("screencapture failed … could not create image from window") and bare `screencapture -l<win>` / `-x` also failing: macOS TCC Screen Recording for com.trycua.driver is lost. `cua-driver permissions grant` + daemon restart may still leave `screen_recording: false`. **For browser tabs this does not block the work: `get_browser_state` with `include_screenshot: true` captures the tab viewport as PNG through CDP and bypasses screencapture/TCC entirely** (response key `screenshot_png_b64`). Drive loop: `studio-cua-vision-drive`.
- `session '<id>' has ended; tool call was rejected`: revive with `start_session` on the same id — cheap, not an error state.
- `desktop_unlocked: false`, empty AX tree, AND no CDP screenshot/read-back: stop and report that the Studio cannot currently verify the browser state. Do not claim a website visit succeeded.

## Payment-specific stop

Card entry and saving/adding a payment method are autonomous — they ARE the task when Cooper asked to fix the payment. The ONLY human gate is the charge-triggering click (Pay / Submit payment / Place order / Subscribe / Renew / Confirm charge): report exact service, amount, and card suffix, then get one confirmation for that click only. Passwords, MFA codes, and passkeys stay handoff-only. The payment-operations skill governs the full boundary.
