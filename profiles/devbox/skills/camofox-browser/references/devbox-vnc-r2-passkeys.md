# Devbox Camofox: R2 persistence, VNC, clipboard, and passkeys

Use this reference when setting up or troubleshooting a remote Camofox/Camoufox browser on a Linux/NixOS devbox where a human may need to interact with the browser and then let the agent reuse the authenticated session.

## R2-backed persistence

Pattern:
1. Mount Cloudflare R2 with rclone at a stable path, e.g. `~/r2-mount`.
2. Run rclone mount with full VFS cache so it behaves more like a regular directory:
   - `--vfs-cache-mode full`
   - `--vfs-cache-max-size 10G` or larger
   - `--vfs-cache-max-age 168h`
   - `--vfs-write-back 5s`
   - `--dir-cache-time 72h`
   - `--attr-timeout 72h`
   - larger read chunks such as `--vfs-read-chunk-size 128M --vfs-read-chunk-size-limit 512M`
3. Point Camofox persistence at a subdirectory on that mount, e.g. `CAMOFOX_PROFILE_DIR=~/r2-mount/camofox-profiles`.
4. Verify write-through by writing a small file to the mount and checking the R2 remote after the write-back delay.

Notes:
- On newer rclone versions the flag is `--dir-cache-time`, not `--dir-cache-ttl`.
- S3/R2 does not support rclone polling; avoid `--poll-interval`.
- `--allow-other` requires `user_allow_other` in `/etc/fuse.conf`; omit it if not configured.

## NixOS native Camofox

If running Camofox natively on NixOS, missing shared libraries are often fixed by installing GTK/X11/dbus/GL/audio libs via Nix and setting:

```bash
LD_LIBRARY_PATH=~/.nix-profile/lib
```

Prefer native execution when the profile directory is on a FUSE/R2 mount; Docker bind mounts of FUSE paths can be unreliable or inaccessible.

## VNC/noVNC for human login

Camofox's VNC plugin can expose:
- VNC on `5900`
- noVNC/websockify on `6080`

On NixOS, the bundled assumptions may need patching:
- noVNC web root may not be `/usr/share/novnc`; use the actual Nix store path such as `/nix/store/...-novnc-*/share/webapps/novnc`.
- Log paths like `/var/log/x11vnc.log` may fail on immutable systems; use `~/.local/state/x11vnc.log` and `~/.local/state/novnc.log`.
- Set a VNC password if using macOS Screen Sharing; it may not accept blank passwords.
- Direct Tailscale VNC (`vnc://<tailscale-ip>:5900`) is often more reliable than an SSH tunnel if the VNC server is bound on the Tailscale interface.

## Clipboard: bypass VNC client clipboard

VNC/noVNC clipboard sync can be unreliable. A robust workaround is to sync directly between macOS `pbpaste`/`pbcopy` and the X11 selection inside the Camofox Xvfb display using `xsel` or `xclip`.

Mac -> Camofox example:

```bash
pbpaste | ssh devbox 'DISPLAY_NUM=$(pgrep -af "Xvfb :" | sed -n "s/.*Xvfb \(:[0-9][0-9]*\).*/\1/p" | tail -1); DISPLAY=$DISPLAY_NUM xsel --clipboard --input'
```

Camofox -> Mac example:

```bash
ssh devbox 'DISPLAY_NUM=$(pgrep -af "Xvfb :" | sed -n "s/.*Xvfb \(:[0-9][0-9]*\).*/\1/p" | tail -1); DISPLAY=$DISPLAY_NUM xsel --clipboard --output' | pbcopy
```

Use `xsel` for one-shot scripts; `xclip` may stay in the foreground to own the selection and can hang the calling process if used naïvely.

## Passkeys / U2F / Coinbase-style login

Important distinctions:
- A remote devbox browser cannot use the user's Mac Touch ID/iCloud Keychain passkeys directly.
- Generic USB forwarding for U2F is fragile and timing/security sensitive; do not assume VNC/noVNC/RustDesk will solve WebAuthn.
- 1Password CLI (`op`) can fetch secrets but cannot answer browser WebAuthn/passkey challenges.
- The 1Password browser extension inside Camofox may work if the passkey is stored in 1Password and the extension is signed in. For Firefox/Camoufox, download the 1Password Firefox XPI from AMO, extract it, and pass the extracted add-on directory to `camoufox-js` `launchOptions({ addons: [...] })`.
- If a user can connect Hermes browser tools to a local Mac Chromium debug browser, local passkeys may be available there. However WebAuthn often requires a real user gesture; automated CDP clicks may not trigger the native passkey prompt. Ask the human to click the passkey button manually, then continue automation after authentication.

## Chrome -> Camofox session transfer

Chrome profiles are not compatible with Camofox/Firefox profiles. Cookie-only transfer is often insufficient for modern sites because localStorage and IndexedDB may also matter.

If Chrome is the source browser:
1. Export full Cookie Editor JSON for cookies, including HttpOnly cookies.
2. Export localStorage from DevTools console, e.g. `JSON.stringify({ cookies: await cookieStore.getAll(), localStorage: Object.fromEntries(Object.entries(localStorage)) })`.
3. Convert cookies to Playwright storage-state format and include localStorage under `origins: [{ origin: "https://www.example.com", localStorage: [...] }]`.
4. Write the resulting `storage-state.json` into the Camofox persistence user directory before creating the session.

Caveat: high-security sites may invalidate or short-TTL session cookies; a technically correct transfer may still land on a login page.
