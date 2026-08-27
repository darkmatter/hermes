# Call outcome discipline (Cooper)

## Rule
| Verdict | When |
|---|---|
| **Success** | OK **early** if hard evidence already exists (digits/ticketed conf/funded call id in live messages). |
| **Failure** | **Not** until `GET /call/<id>` full `messages` / transcript / analysis checked for **every** relevant call id |

## Must not clinch failure
- Watcher summary alone
- bare `endedReason`
- call **DELETE** / kill
- empty mid-call messages
- a **later** VM call that did stay short

## Real miss this session
First 206 interactive call held ticket STT `0012342708964` after kill; later VM summarized “left VM only.” Online AA form proved that spoken number **wrong** — still: never declare **miss** without full GET on the first call id.

## Cross-tool
Same spirit for flying tools: no fail/switch-to-weaker path until log/tool internals checked (see kernel-browsers vision `_initializer` note).
