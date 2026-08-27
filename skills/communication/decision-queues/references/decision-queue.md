# Decision queue deployment reference

## Contract

- `POST /ask` accepts `{question, type, options, context, timeout_s, meta}`.
- `type=choice` renders arbitrary options; `type=confirm` defaults to Approve/Deny; `type=text` renders a text input.
- `POST /a/<id>/answer` accepts either JSON or `application/x-www-form-urlencoded` and stores the answer.
- `GET /api/asks/<id>` returns the record and status; `/wait?timeout=N` is bounded long-polling.
- State files should be written with temp-file + atomic rename and reloaded on process start.

## First deployment lessons

The existing Vapi HITL service was a blocking webhook on port 8788 with an in-memory `_pending` map and `/reply`. A separate decision queue was deployed on port 8789 with state under `~/.hermes/decide-queue`, launchd supervision, and a named public route. This avoided coupling ordinary web decisions to a phone-call wait path.

The live Cloudflare tunnel initially had two processes using the same tunnel ID: a nix-store launchd config and a hand-edited config. The stale launchd process caused the new hostname to return 404/501/403 inconsistently. The fix was to make one config authoritative, stop the duplicate, restart the tunnel, and verify both the local health endpoint and the public hostname. Persist the ingress change in the source module as well as the live config; a future nix activation should recreate the intended route.

## Verification checklist

1. Local `/health` is 200.
2. Create `choice`, `confirm`, and `text` asks.
3. Confirm HTML contains real submit forms/buttons.
4. Submit an option using form encoding.
5. Read the answer back through JSON and bounded wait.
6. Restart the service and verify records survive.
7. Verify public HTTPS route and tunnel logs.
8. Remove temporary test records.

Do not report the edge as healthy from local success alone. Test the public URL explicitly; 403/501/404 means the edge or tunnel route still needs repair.
