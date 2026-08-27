# Kernel Managed Auth (site logins)

Source: https://www.kernel.sh/docs/auth/overview (+ profiles / hosted-ui / credentials / FAQ).

## Layers
| Layer | Purpose | Credential |
|---|---|---|
| API key | Agent → Kernel API | `himitsu read kernel-api-key` → `KERNEL_API_KEY` |
| Profile | Cookies + localStorage across browsers | `kernel profiles create/list` |
| Managed Auth connection | Keep a **domain** logged in on a profile | `kernel auth connections *` |

## Flow
1. Ensure profile exists (`cooper-email` for Gmail; `aa-cooper-test` for aa.com cookies).
2. `connections create --profile-name X --domain Y [--login-url …] [--allowed-domain …] [--credential-provider …]`
3. `connections login <id>` → **`hosted_url`** — give Cooper that URL **immediately** (first line of reply).
4. Poll `connections get` until `AUTHENTICATED` (or FAILED/EXPIRED).
5. `browsers create --profile-name X` — site starts logged in.
6. Runtime: health checks + auto re-auth when credentials saved (`save_credentials` default true). OTP not saved.

## Hosted UI vs live browser HITL
| | Hosted UI (`hosted_url`) | Live browser (`browsers view`) |
|---|---|---|
| Google/Gmail | **FAILED** here: `stuck_in_loop` | **Primary** — Cooper drives login |
| Passkeys | Unsupported | May work if password path available |
| Auto re-auth | Best if login + creds succeed once | Cookie jar only until manual refresh |

**Preference:** for Google, create profile browser + share live URL first; offer Hosted UI only as optional alternate.

## 1Password
- CLI: `credential-providers create --provider-type onepassword --name cooper-1p --token "$(himitsu read op-service-account/token)"`
- SA vaults: cm / cooper / dev. No Google Login item visible at setup — auto-match won't fill Gmail until item exists with google/gmail URLs.
- Detail: `references/gmail-profile-and-1p.md`

## CLI map
```
kernel auth connections create|login|get|list|follow|submit|delete|update
kernel auth connections login <id> -o json   # hosted_url — surface immediately
kernel credential-providers create|test|list-items
kernel profiles create|list|get|delete
```

## Gmail profile (this environment)
- Profile: **`cooper-email`** — live-view login persisted (me@cm.xyz + cooper@darkmatter.io).
- Managed Auth connection may still show `NEEDS_AUTH` / FAILED Hosted UI even when profile cookies work.
- Verify: Playwright open mail.google.com → inbox title + SID cookies; then delete browser to confirm profile reload.

## Pitfalls
- **URLs first:** User will ask “what's the url?” if you poll without printing `hosted_url` / live view.
- Profile save requires browser **delete/timeout**, not Playwright close alone.
- Pool browsers: profile read-only; `save_changes` ignored.
- Don't confuse Kernel API OAuth (`kernel login`) with Managed Auth site login.
- Interactive `connections delete` may hang on `[y/N]` — avoid in agent loops.
- Credentials never returned in API responses / not for LLMs.
