# Camofox remote login, persistence, clipboard, and passkeys

Use this when a human needs to log into services locally or through a visible Camofox browser, then hand the authenticated state to Hermes.

## Core model

- Camofox/Camoufox is Firefox-based. Firefox profiles and Playwright `storageState` map naturally; Chrome profiles do not.
- Cookie-only transfer is often insufficient for modern apps. Export or preserve:
  - cookies, including HttpOnly cookies when possible
  - localStorage
  - IndexedDB / service-worker state when the site relies on it
  - full browser profile when profile formats are compatible
- For passkey/U2F-only services, a session copied after login may expire quickly. Prefer registering a passkey that the remote browser can actually use (for example a 1Password-backed passkey inside the Camofox browser) over trying to replay old cookies.

## R2-backed persistence pattern

1. Mount shared storage on the devbox with rclone and `--vfs-cache-mode full` so it behaves like a local directory.
2. Point `CAMOFOX_PROFILE_DIR` at the shared mount, e.g. `~/r2-mount/camofox-profiles`.
3. Keep Camofox `userId` stable, e.g. `hermes`, so the persistence plugin reuses the same profile directory.
4. After injecting or changing storage, restart Camofox or create a fresh session so `contextOptions.storageState` is loaded from disk.

Recommended rclone mount traits for browser profiles:

```bash
rclone mount darkmatter-r2:team-drive ~/r2-mount \
  --vfs-cache-mode full \
  --vfs-cache-max-size 10G \
  --vfs-cache-max-age 168h \
  --vfs-write-back 5s \
  --dir-cache-time 72h \
  --attr-timeout 72h \
  --buffer-size 64M \
  --vfs-read-chunk-size 128M \
  --vfs-read-chunk-size-limit 512M
```

Avoid S3 unsupported flags such as polling flags, and avoid `allow_other` unless `/etc/fuse.conf` permits `user_allow_other`.

## Chrome local session export to Playwright storageState

If the human uses Chrome locally:

1. Log in in Chrome.
2. Export full cookies with a cookie extension that can include HttpOnly cookies, preferably JSON not Netscape if possible.
3. In DevTools Console on the target origin, copy localStorage:

```js
copy(JSON.stringify({
  cookies: await cookieStore.getAll(),
  localStorage: Object.fromEntries(Object.entries(localStorage))
}))
```

4. Merge the extension cookie export with localStorage into Playwright format:

```json
{
  "cookies": [
    {
      "name": "cookie-name",
      "value": "cookie-value",
      "domain": ".example.com",
      "path": "/",
      "expires": 1783907686,
      "httpOnly": true,
      "secure": true,
      "sameSite": "Lax"
    }
  ],
  "origins": [
    {
      "origin": "https://www.example.com",
      "localStorage": [
        { "name": "key", "value": "value" }
      ]
    }
  ]
}
```

5. Write it to the Camofox persistence path for the selected user, e.g. `.../camofox-profiles/<hash>/storage-state.json`.
6. Restart Camofox and navigate with the same `userId`.

Important conversion details:

- Chrome cookie expiration may be milliseconds; Playwright expects seconds.
- JS `cookieStore.getAll()` cannot read HttpOnly cookies. Merge in the browser-extension export.
- `sameSite` must be `Strict`, `Lax`, or `None`.
- Host-only cookies can use `www.example.com`; domain cookies usually use `.example.com`.

## 1Password and passkeys

- `op` / 1Password CLI can retrieve secrets, but it cannot answer browser WebAuthn/passkey challenges.
- The 1Password browser extension can act as the passkey provider if installed and signed in inside the remote Camofox browser.
- For Camoufox, download the Firefox extension XPI, extract it, and pass the extracted directory through Camoufox `addons` launch option.
- If the passkey only exists in iCloud Keychain / Touch ID on the Mac, it generally cannot be used by a remote Linux Camofox browser. Register a new 1Password-backed passkey from the remote browser if the service allows it.

## VNC/noVNC limitations and direct clipboard helpers

VNC/noVNC are pixel transports. Treat clipboard and USB/WebAuthn as separate problems:

- VNC/noVNC clipboard sync may be unreliable or unsupported by the client.
- macOS Screen Sharing often dislikes blank VNC passwords; set an x11vnc password.
- USB forwarding is not solved by VNC/noVNC. Network USB forwarding for WebAuthn/U2F is brittle due to authenticator security and timing.

For reliable clipboard, bypass VNC and write directly to the X11 clipboard on the devbox:

```bash
# Mac -> Camofox X11 clipboard
printf '%s' "$TEXT" | ssh devbox 'DISPLAY=$(pgrep -af "Xvfb :" | sed -n "s/.*Xvfb \(:[0-9][0-9]*\).*/\1/p" | tail -1) xsel --clipboard --input'

# Camofox X11 clipboard -> Mac
ssh devbox 'DISPLAY=$(pgrep -af "Xvfb :" | sed -n "s/.*Xvfb \(:[0-9][0-9]*\).*/\1/p" | tail -1) xsel --clipboard --output' | pbcopy
```

A robust helper should set both `CLIPBOARD` and `PRIMARY` selections with `xsel` or `xclip`, and should discover the active `Xvfb :NNN` display dynamically.

## Troubleshooting checks

```bash
# Is Camofox healthy?
curl -s http://localhost:9377/health

# Which display is active?
pgrep -af 'Xvfb|x11vnc'

# Are VNC/noVNC listening?
ss -tlnp | grep -E '5900|6080'

# Does x11vnc have a password?
grep -i 'password' ~/.local/state/x11vnc.log
```

For NixOS native Camofox, browser binaries and X tools may need `LD_LIBRARY_PATH=~/.nix-profile/lib` plus Nix-installed X/GTK libraries. Capture the fix in the environment setup, not as a claim that the tool is broken.
