# iMessage (BB) vs Twilio SMS for agent status

## Twilio from Vapi/Twilio long code
- Common failure to US mobiles: error **30034** (A2P 10DLC / unregistered campaign).
- Voice outbound can work while SMS is blocked.
- Do not treat undelivered SMS as “bad number” until 30034 is ruled out.

## BlueBubbles path (preferred)
- Stable API: `https://bb-api.cm.xyz`
- Webhook/inbox: `https://bb-hook.cm.xyz`
- Auth: BB server password (config DB) + webhook secret file.
- osascript → Messages on Mac Pro is best-effort only when BB API timeouts.

## Pattern for call status
1. Call starts → short iMessage hold update.
2. Material milestone (human on line, payment blocked, cancel/credit) → short update.
3. Never put card PANs in iMessage.
