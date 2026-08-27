# Credentialed-source fact checking before email sends

Use this when a proposed Gmail reply quotes prices, sale history, account facts, contract terms, or other consequential evidence from a site that requires login.

## Workflow

1. **Read the complete email thread first.** Identify exactly which factual claims will influence an offer, approval, payment, or negotiation position.
2. **Inspect the named source directly.** Do not substitute search snippets or stale card summaries when the user names an authoritative site.
3. **Resolve credentials without leakage.** Load `himitsu`; when the login is in 1Password, follow `himitsu` → `references/onepassword-bridge.md`. Search item metadata by exact title first, then broader title/domain terms. If the user just moved an item between vaults, refresh `op item list` before concluding it is absent. Service-account item reads must include `--vault`.
4. **Keep secrets in-process.** Never print or persist usernames, passwords, OTPs, OAuth codes, or session cookies. Use a temporary browser profile for interactive sites and delete it after extraction.
5. **Handle bot checks with a real browser.** For a Cloudflare/Turnstile-protected source, an isolated Firefox/Selenium session can be used when direct extraction fails. Wait for the browser check, fill the credential fields from 1Password, and click the site's explicit login button; pressing Enter may not submit JavaScript modals. Extract only the relevant records.
6. **Reconcile discrepancies before sending.** If the authenticated source conflicts with numbers supplied by the user, stop and show both readings. Ask which formulation to use; recommend the directly verified figures. Do not silently preserve or silently “correct” material negotiation facts.
7. **State only what the source proves.** A public sale record proves that a domain sold for an amount on a date/venue; it does not prove the current seller was the buyer unless ownership evidence independently establishes that.
8. **Preview before send.** For offers, financing, contracts, or other material commitments, present the complete draft and wait for an explicit `send` instruction. Phrases such as “tell Chris…” authorize drafting the requested content, not transmission by themselves.
9. **After explicit send approval:** update the existing draft/thread, send once, verify in Sent before retrying, then transition Gmail state/tags and the Kanban card.

## NameBio example

- Pages such as `https://namebio.com/<domain>` may require both Cloudflare verification and member login.
- A successful authenticated page exposes a sentence shaped like `DOMAIN last sold for $PRICE on DATE at VENUE`; quote that record exactly and retain the page URL.
- Membership passwords are not necessarily NameBio API keys. A failed API-key probe does not invalidate the website login; use the member browser flow instead.

## Verification

- [ ] Authoritative page was read while authenticated.
- [ ] Exact price/date/venue were copied from the live record.
- [ ] Claim language does not infer buyer identity from a sale record.
- [ ] User previewed material offer/financing language.
- [ ] Explicit send approval was received after the preview.
- [ ] Sent copy and final Gmail/Kanban state were verified.
