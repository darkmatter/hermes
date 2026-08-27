# Authentik email + MFA (gitops snapshot)

Paths relative to `~/git/darkmatter/gitops`.

## Email delivery path

```
ArgoCD Application apps/authentik.yaml
  source 1: charts.goauthentik.io (server + worker)
    authentik.existingSecret.secretName: <REDACTED>
  source 2: manifests/authentik
    KSOPS secret-generator.yaml → secrets.sops.yaml
      AUTHENTIK_EMAIL__FROM / HOST / PORT / USERNAME / PASSWORD
      AUTHENTIK_EMAIL__USE_SSL / USE_TLS / TIMEOUT
    configMapGenerator → authentik-blueprints
      mounted /blueprints/local/
        notification-transports.yaml
          default-local-transport  (mode: local)
          default-email-transport  (mode: email → SMTP via env)
            email_template: email/event_notification.html
            email_subject_prefix: "darkmatter ///"
```

### Current SMTP (Mailgun)

| Key | Expected |
|---|---|
| HOST | `smtp.mailgun.org` |
| PORT | `587` |
| USE_TLS | `true` |
| USE_SSL | `false` |
| USERNAME / FROM | `mail@mg.darkmatter.io` |
| PASSWORD | Mailgun SMTP password (len ~50); from OP |

- **1Password (drkmttr):** item title `mailgun smtp`, UUID `sknbd7xv5ohn2lzehc7li77hhq`, vault `shared`.
  - Primary: username `mail@mg.darkmatter.io` + password field id `password`.
  - Section `alt server mg.drkmttr.dev`: email `mail@mg.drkmttr.dev` + second password (legacy).
- **Historical:** pre-2026-05 used `authentik@mg.drkmttr.dev` on Mailgun; 2026-05 switched to Resend (`noreply@darkmatter.io` / `smtp.resend.com`); 2026-08 cut back to Mailgun primary mailbox above (`b6cda21` era).
- Blueprint comment in `notification-transports.yaml` should say **Mailgun**, not Resend.
- Recovery brand flow: stock `default-recovery-flow` (`blueprints/branding.yaml`) — same global Django email settings.
- Voytravel twin: same `AUTHENTIK_EMAIL__*` shape in `manifests/voytravel-authentik/secrets.sops.yaml` (may still differ provider — check before assuming).

### SOPS age key for this repo

- `.sops.yaml` recipient: `<REDACTED>`
- Cluster: Secret `sops-age` in `argocd` ns, key `keys.txt`
- OP backup: `sops-k3s` on my.1password.com vault `cm`
- kube context for prod: `default` → `https://hz-ex63-1:6443` (not docker-desktop)

### Broken template anti-pattern

`default-email-transport.email_template` must be event-notification path (`email/event_notification.html`).
`account_confirmation.html` is email-stage-only → `TemplateDoesNotExist` on policy_exception / configuration_error events.

### Cutover / fix sequence (email not sending)

1. Confirm live HOST/USER/FROM/pwlen on **secret + worker + server** (all three).
2. Confirm Django `settings.EMAIL_*` via `ak shell` on worker (source of truth for send path).
3. SMTP or `send_mail` probe to `cooper@darkmatter.io`.
4. If wrong provider: pull OP Mailgun primary → `sops set` each `AUTHENTIK_EMAIL__*` → update blueprint comment → **commit+push only those files**.
5. Apply secret and `kubectl rollout restart deploy/authentik-server deploy/authentik-worker -n authentik` (or wait Argo).
6. Re-verify both pods + Django `send_mail_result=1`.
7. Wipe `/tmp/sops-age-k3s.txt` and any plaintext secret temps.

**Argo pitfall:** auto-sync self-heal reverts Secret to git. Live-only fixes look good for minutes then flip back (or only one Deployment restarts with new env).

### Ad-hoc verify (no suite)

Check: git SOPS non-secret fields; live secret; worker+server env; Django assert + `send_mail`. Do not print password; assert `PWLEN` only.

## MFA / 2FA as of last review

| Object | File | State |
|---|---|---|
| Expression policy `Has secure 2FA` | `blueprints/security-factor-policies.yaml` | WebAuthn check only; **no bindings** |
| Stage `passkey-authentication-validate` | `blueprints/authentication-flows.yaml` | `device_classes: [webauthn]`, **`not_configured_action: skip`** |
| Flow `password-auth-flow` | same | id → login; **no** validate stage |
| Brand default auth | `blueprints/branding.yaml` | `passkey-authentication-flow` |
| Password footer link | `system-settings-job.yaml` | `/if/flow/password-auth-flow/` |

**Conclusion: 2FA not required.**

### Enforce checklist (implement only when requested)

1. Product choice: WebAuthn-only vs any MFA class; keep password path?
2. Validate stage: `not_configured_action` → `configure` or `deny`
3. Optionally expand `device_classes` / policy expression beyond webauthn
4. Bind deny policy on authentication stage bindings (name identifiers, not pk)
5. Add validate stage to `password-auth-flow` before `default-authentication-login`
6. Revisit footer escape hatch if password-without-MFA must die
7. Verify after sync: Admin → Flows bindings + test user with zero authenticators

## Related non-SMTP “email”

- Identification `user_fields` includes `email` (login identifier, not mail send).
- OAuth scope mappings include OpenID `email`.
- Property mappings / GWS SCIM invent `@darkmatter.io` primary emails — directory, not SMTP.
