# Himalaya Configuration Reference

Configuration file location: `~/.config/himalaya/config.toml`

## Minimal IMAP + SMTP Setup

```toml
[accounts.default]
email = "user@example.com"
display-name = "Your Name"
default = true

# IMAP backend for reading emails
backend.type = "imap"
backend.host = "imap.example.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "user@example.com"
backend.auth.type = "password"
backend.auth.raw = "your-password"

# SMTP backend for sending emails
message.send.backend.type = "smtp"
message.send.backend.host = "smtp.example.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "user@example.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.raw = "your-password"

# Folder aliases
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
folder.aliases.drafts = "Drafts"
folder.aliases.trash = "Trash"
```

## Password Options

### Password from command (recommended)
```toml
backend.auth.cmd = "pass show email/imap"
```

### System keyring
```toml
backend.auth.keyring = "imap-example"
```

## Gmail Configuration

```toml
[accounts.gmail]
email = "you@gmail.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@gmail.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show google/app-password"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@gmail.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show google/app-password"

# Gmail folder mapping — CRITICAL: without these, save-to-Sent fails
# after SMTP delivery succeeds, causing duplicate emails on retry.
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "[Gmail]/Sent Mail"
folder.aliases.drafts = "[Gmail]/Drafts"
folder.aliases.trash = "[Gmail]/Trash"
```

**Note:** Gmail requires an App Password if 2FA is enabled.

## Folder Aliases — Critical Pitfall

Use the v1.2.0 `folder.aliases.X` syntax (plural, dotted keys):

```toml
[accounts.default]
folder.aliases.inbox = "INBOX"
folder.aliases.sent = "Sent"
```

> **Don't use the singular `alias` form.** Pre-v1.2.0 docs showed
> `[accounts.NAME.folder.alias]` (singular). v1.2.0 silently ignores it —
> TOML parses without error, but the alias resolver never reads it. On Gmail
> this means save-to-Sent fails *after* SMTP delivery succeeds, and
> `himalaya message send` exits non-zero. Any caller that retries on that
> exit code will re-run the entire send — including SMTP — producing
> duplicate emails to recipients.

## iCloud Configuration

```toml
[accounts.icloud]
email = "you@icloud.com"
display-name = "Your Name"

backend.type = "imap"
backend.host = "imap.mail.me.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "you@icloud.com"
backend.auth.type = "password"
backend.auth.cmd = "pass show icloud/app-password"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.mail.me.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "you@icloud.com"
message.send.backend.auth.type = "password"
message.send.backend.auth.cmd = "pass show icloud/app-password"
```

## OAuth2 Authentication

```toml
backend.auth.type = "oauth2"
backend.auth.client-id = "your-client-id"
backend.auth.client-secret.cmd = <REDACTED>
backend.auth.access-token.cmd = <REDACTED>
backend.auth.refresh-token.cmd = <REDACTED>
backend.auth.auth-url = "https://provider.com/oauth/authorize"
backend.auth.token-url = <REDACTED>
```

## Multiple Accounts

```toml
[accounts.personal]
email = "personal@example.com"
default = true

[accounts.work]
email = "work@company.com"
```

Switch with `--account`:
```bash
himalaya --account work envelope list
```

## Notmuch Backend (local mail)

```toml
[<REDACTED>]
email = "user@example.com"
backend.type = "notmuch"
backend.db-path = "~/.mail/.notmuch"
```
