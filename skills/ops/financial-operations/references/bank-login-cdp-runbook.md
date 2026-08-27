# Bank Login Workflow via Live Chrome CDP

When managing consumer banks (BoA, Amex), the preferred pattern is to inject an interaction script via live local Chrome CDP (`127.0.0.1:9222`) utilizing existing passkeys and device-trust.

### Typical Runbook:
1. Extract password safely via `himitsu exec op-service-account/token ...`
2. Create JavaScript evaluation node script utilizing `chrome-remote-interface` module.
3. Open target URL.
4. If an OTP is required, click SMS. Send a local python SQLite poll to `~/Library/Messages/chat.db` for the OTP digits.
5. Provide the OTP via CDP.
6. Once logged in, switch to read-only scraping of `innerText` combined with element mapping for visibility.
7. Any financial change, transfer (e.g., Zelle, Wire), or fraud designation must trigger a Clarify or Handoff back to the user. Do not click 'yes' or 'submit' on money movements without user confirmation.
