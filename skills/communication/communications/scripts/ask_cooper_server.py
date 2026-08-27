#!/usr/bin/env python3
"""Mid-call HITL for Vapi:
  - ask_cooper: Slack + iMessage wait for Cooper reply (blocking)
  - text_cooper: fire-and-return iMessage to Cooper (or override `to`)

iMessage identity: ALWAYS Studio BlueBubbles account cooperton42391@gmail.com
via https://bb-api.cm.xyz — NEVER local Messages (koutaroum@icloud.com) which
would loop if Cooper's local Mac is the send path.

Endpoints:
  POST /vapi/tools   Vapi tool-calls webhook
  POST /reply        {"id","answer"} for ask_cooper
  POST /imessage     {"to"?,"message"}
  GET  /health
  GET  /pending

Env:
  SLACK_BOT_TOKEN, SLACK_CHANNEL (D0BG4HJ47GE)
  HITL_TIMEOUT (90), HITL_PORT (8788)
  HITL_IMESSAGE_TO (+13109897067 Cooper)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import parse as urlparse
from urllib import request as urlrequest

PORT = int(os.environ.get("HITL_PORT", "8788"))
TIMEOUT = int(os.environ.get("HITL_TIMEOUT", "90"))
CHANNEL = os.environ.get("SLACK_CHANNEL", "D0BG4HJ47GE")
HITL_TOKEN = <REDACTED>
DEFAULT_IMESSAGE_TO = os.environ.get("HITL_IMESSAGE_TO", "+13109897067")
# Comma-separated E.164 numbers allowed to answer via iMessage (inbound via BlueBubbles webhook inbox).
_IMESSAGE_REPLY_FROM = os.environ.get(
    "HITL_IMESSAGE_REPLY_FROM",
    "+13109897067,+12069542027",
)
IMESSAGE_REPLY_FROM = {
    re.sub(r"\D", "", x) for x in _IMESSAGE_REPLY_FROM.split(",") if x.strip()
}
BB_INBOX_URL = os.environ.get("HITL_BB_INBOX_URL", "http://127.0.0.1:8790/messages")
BB_HOOK_SECRET = <REDACTED>
    os.environ.get("BB_HOOK_SECRET")
    or os.environ.get("HITL_BB_HOOK_SECRET")
    or ""
).strip()
if not BB_HOOK_SECRET:
    try:
        BB_HOOK_SECRET = <REDACTED>
    except Exception:
        BB_HOOK_SECRET = <REDACTED>
BB_API_URL = (
    os.environ.get("HITL_BB_API_URL")
    or os.environ.get("BB_API_URL")
    or "https://bb-api.cm.xyz"
).rstrip("/")
# Expected Studio identity — refuse local Pro Messages过程和
BB_EXPECTED_IMESSAGE = os.environ.get("HITL_BB_IMESSAGE_IDENTITY", "cooperton42391@gmail.com").lower()

STATE_DIR = Path(os.environ.get("HITL_STATE_DIR", "/tmp/vapi-hitl"))
STATE_DIR.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()
_pending: dict[str, dict[str, Any]] = {}


def _himitsu(path: str) -> str:
    try:
        return subprocess.check_output(["himitsu", "read", path], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def slack_token() -> str:
    return os.environ.get("SLACK_BOT_TOKEN") or _himitsu("slack/hermes-bot/bot-token")


def slack_api(method: str, payload: dict | None = None, params: dict | None = None) -> dict:
    token = <REDACTED>
    if not token:
        raise RuntimeError("No Slack bot token")
    url = f"https://slack.com/api/{method}"
    if params:
        url += "?" + urlparse.urlencode(params)
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Authorization": f"Bearer <REDACTED>", "Content-Type": "application/json; charset=utf-8"}
    req = urlrequest.Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    with urlrequest.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def normalize_phone(to: str) -> str:
    to = (to or "").strip()
    digits = re.sub(r"\D", "", to)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    if to.startswith("+"):
        return to
    return to


def _bb_password() -> str:
    p = (
        os.environ.get("BB_PASSWORD")
        or os.environ.get("HITL_BB_PASSWORD")
        or _himitsu("bluebubbles-password")
        or _himitsu("hermes/bb-password")
        or ""
    ).strip()
    if p:
        return p
    # Same server password often stored in local BB config DB (shared with Studio)
    db = Path.home() / "Library/Application Support/bluebubbles-server/config.db"
    if db.exists():
        try:
            out = subprocess.check_output(
                ["sqlite3", str(db), "SELECT value FROM config WHERE name='password'"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if out:
                return out
        except Exception:
            pass
    return ""


def bb_server_identity(passw: str) -> dict:
    try:
        url = f"{BB_API_URL}/api/v1/server/info?password={urlparse.quote(passw)}"
        req = urlrequest.Request(url, headers={"User-Agent": "HermesHITL/1.0"})
        with urlrequest.urlopen(req, timeout=20) as resp:
            d = json.loads(resp.read().decode())
        return (d.get("data") or {}) if isinstance(d, dict) else {}
    except Exception as e:
        return {"_error": str(e)}


def send_imessage(to: str, body: str) -> dict:
    """Send via Studio BlueBubbles ONLY (cooperton42391@gmail.com on bb-api.cm.xyz).

    Never use local osascript/Messages on the Mac Pro (koutaroum@icloud.com) —
    that path messages from Cooper's personal Apple ID and can chat with itself.
    """
    to_fmt = normalize_phone(to)
    body = (body or "").strip()
    if not to_fmt or not body:
        return {"ok": False, "error": "to and body required"}

    passw = _bb_password()
    if not passw:
        return {"ok": False, "error": "no BlueBubbles password (env BB_PASSWORD / himitsu / config.db)"}

    # Guard: confirm we're talking to Studio's BB identity
    info = bb_server_identity(passw)
    imsg = str(
        info.get("detected_imessage")
        or info.get("detected_icloud")
        or info.get("iMessage_email")
        or ""
    ).lower()
    computer = str(info.get("computer_id") or "")
    if info.get("_error"):
        return {"ok": False, "error": f"bb-api unreachable: {info['_error']}", "api": BB_API_URL}
    if BB_EXPECTED_IMESSAGE and imsg and BB_EXPECTED_IMESSAGE not in imsg:
        return {
            "ok": False,
            "error": (
                f"refusing send: bb-api identity is {imsg!r}, expected {BB_EXPECTED_IMESSAGE!r}. "
                "HITL must use Studio cooperton42391@gmail.com only."
            ),
            "computer": computer,
            "api": BB_API_URL,
        }

    chat_guid = f"iMessage;-;{to_fmt}"
    # Never send TO the studio's own handle if someone misconfigured destination
    if "cooperton42391" in to_fmt.lower() or to_fmt.lower().endswith("@gmail.com"):
        # destination must be a phone for Cooper, not an email identity confusion
        if "@" in to_fmt:
            return {"ok": False, "error": f"refusing destination {to_fmt} — use Cooper phone E.164"}

    last_err = None
    for method in ("private-api", "apple-script"):
        payload = {
            "chatGuid": chat_guid,
            "message": body,
            "tempGuid": f"tmp-{uuid.uuid4()}",
            "method": method,
        }
        try:
            endpoint = f"{BB_API_URL}/api/v1/message/text?password={urlparse.quote(passw)}"
            req = urlrequest.Request(
                endpoint,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "User-Agent": "HermesHITL/1.0"},
                method="POST",
            )
            with urlrequest.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode() or "{}")
            # BlueBubbles returns status 200 on success wrapper
            status = data.get("status")
            err = data.get("error") or data.get("message")
            if status in (200, "200", None) and not (isinstance(err, str) and "fail" in err.lower()):
                # hard failures often status != 200
                if status and int(status) >= 400:
                    last_err = data
                    continue
                return {
                    "ok": True,
                    "to": to_fmt,
                    "from": imsg or BB_EXPECTED_IMESSAGE,
                    "computer": computer,
                    "method": method,
                    "api": BB_API_URL,
                    "result": data,
                }
            last_err = data
        except Exception as e:
            last_err = {"exception": str(e)}
            continue
    return {
        "ok": False,
        "error": "bb-api send failed after method attempts",
        "last": last_err,
        "to": to_fmt,
        "from_expected": BB_EXPECTED_IMESSAGE,
        "api": BB_API_URL,
    }


def post_question(question: str, context: str, call_id: str, req_id: str) -> dict:
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "Levi needs a decision (mid-call)"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Question:*\n{question}"}},
    ]
    if context:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*Context:*\n{context[:1800]}"}})
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": (
                f"call=`{call_id or '?'}` · id=`{req_id}` · reply in this DM **or via iMessage** within ~{TIMEOUT}s, or:\n"
                f"`curl -sS -X POST localhost:{PORT}/reply -H 'Content-Type: application/json' "
                f"-d '{{\"id\":\"{req_id}\",\"answer\":\"...\"}}'`"
            ),
        }],
    })
    res = slack_api("chat.postMessage", {"channel": CHANNEL, "text": f"Levi mid-call: {question}", "blocks": blocks})
    if not res.get("ok"):
        raise RuntimeError(f"slack post failed: {res}")
    # also iMessage mirror
    try:
        send_imessage(
            DEFAULT_IMESSAGE_TO,
            (
                f"Levi mid-call [{req_id}]: {question}"
                + (f"\nContext: {context[:400]}" if context else "")
                + f"\n\nREPLY TO THIS iMESSAGE with your answer (within ~{TIMEOUT}s)."
                + f"\nOr Slack DM hermes_bot, or: curl -sS localhost:{PORT}/reply -d "
                + "'{\"id\":\"" + req_id + "\",\"answer\":\"...\"}'"
            ),
        )
    except Exception as e:
        print("[hitl] imessage mirror failed", e)
    return res


def poll_slack_reply(channel: str, after_ts: str, timeout: int) -> str | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with _lock:
            for item in _pending.values():
                if item.get("answer") and item.get("slack_ts") == after_ts:
                    return str(item["answer"])
        try:
            res = slack_api(
                "conversations.history",
                params={"channel": channel, "oldest": after_ts, "inclusive": "false", "limit": "10"},
            )
            if res.get("ok"):
                for msg in res.get("messages") or []:
                    if msg.get("bot_id") or msg.get("subtype"):
                        continue
                    text = (msg.get("text") or "").strip()
                    if text:
                        return text
        except Exception:
            pass
        time.sleep(1.5)
    return None



def _digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def poll_imessage_reply(req_id: str, created_ts: float) -> str | None:
    """Accept inbound iMessages from allowed numbers as HITL answers via BB webhook inbox."""
    if not BB_HOOK_SECRET:
        return None
    try:
        url = f"{BB_INBOX_URL}?secret={urlparse.quote(BB_HOOK_SECRET)}&limit=30"
        req = urlrequest.Request(url, method="GET")
        with urlrequest.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode() or "{}")
    except Exception as e:
        print("[hitl] bb inbox poll failed", e)
        return None

    messages = data.get("messages") or data.get("events") or []
    if isinstance(data, list):
        messages = data

    for ev in reversed(list(messages)):  # newest often last or first; check both sides later
        pass

    # Prefer newest first
    try:
        messages = sorted(messages, key=lambda e: float(e.get("ts") or 0), reverse=True)
    except Exception:
        pass

    for ev in messages:
        try:
            ts = float(ev.get("ts") or 0)
        except Exception:
            ts = 0
        if ts and ts + 0.5 < created_ts:
            continue
        if ev.get("isFromMe") is True:
            continue
        etype = str(ev.get("type") or "")
        if etype and etype not in ("new-message", "message", "unknown", ""):
            # still allow if text present
            if not (ev.get("text") or "").strip():
                continue
        handle_d = _digits(str(ev.get("handle") or ""))
        if IMESSAGE_REPLY_FROM and handle_d and handle_d not in IMESSAGE_REPLY_FROM:
            # allow chatGuid containing generous match
            cg = str(ev.get("chatGuid") or "")
            if not any(x[-10:] in cg for x in IMESSAGE_REPLY_FROM if len(x) >= 10):
                continue
        text = (ev.get("text") or "").strip()
        if not text:
            continue
        # Prefer explicit id tag, else accept plain reply if only one open ask or id present
        if req_id in text:
            # strip id tags soft
            cleaned = re.sub(rf"\[?{re.escape(req_id)}\]?:?", "", text).strip()
            return cleaned or text
        # Any non-empty reply from Cooper after
        with _lock:
            open_asks = [k for k, v in _pending.items() if not v.get("done") and not v.get("answer")]
        if len(open_asks) == 1 and open_asks[0] == req_id:
            return text
        # multiple open: require req_id in text (already handled) else skip
    return None


def wait_for_answer(req_id: str, slack_ts: str, timeout: int) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        ans_path = STATE_DIR / f"{req_id}.answer"
        if ans_path.exists():
            return ans_path.read_text().strip()
        with _lock:
            item = _pending.get(req_id) or {}
            if item.get("answer"):
                return str(item["answer"])
        remaining = max(1, int(deadline - time.time()))
        # iMessage replies via BlueBubbles webhook inbox (preferred easy path)
        with _lock:
            created_ts = float((_pending.get(req_id) or {}).get("created") or 0)
        im = poll_imessage_reply(req_id, created_ts or (time.time() - TIMEOUT))
        if im:
            return im
        got = poll_slack_reply(CHANNEL, slack_ts, timeout=min(3, remaining))
        if got:
            return got
    return (
        "NO_REPLY_TIMEOUT: Cooper did not answer in time. Continue with existing guardrails; "
        "do not invent new spend authority. Prefer documenting the request and offering callback "
        "(310) 989-7067 / me@cooperm.com if a decision is blocked."
    )


def extract_tool_calls(body: dict) -> list[dict]:
    calls = []
    msg = body.get("message") if isinstance(body.get("message"), dict) else {}
    for key in ("toolCalls", "toolCallList", "toolWithToolCallList"):
        for src in (msg, body):
            arr = src.get(key) if isinstance(src, dict) else None
            if isinstance(arr, list):
                calls.extend(arr)
    out = []
    for c in calls:
        if isinstance(c, dict) and "toolCall" in c:
            out.append(c["toolCall"])
        else:
            out.append(c)
    return out


def handle_tool_calls(body: dict) -> dict:
    call_obj = body.get("call") or {}
    call_id = call_obj.get("id") or body.get("callId") or ""
    control_url = ((call_obj.get("monitor") or {}) or {}).get("controlUrl") or ""
    results = []

    for tc in extract_tool_calls(body):
        tc_id = tc.get("id") or tc.get("toolCallId") or ""
        fn = tc.get("function") or {}
        name = fn.get("name") or tc.get("name") or ""
        raw_args = fn.get("arguments") or tc.get("arguments") or {}
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args) if raw_args else {}
            except json.JSONDecodeError:
                args = {"question": raw_args, "message": raw_args}
        else:
            args = raw_args or {}

        if name in ("text_cooper", "textCooper", "message_cooper"):
            msg = (args.get("message") or args.get("text") or args.get("body") or "").strip()
            to = (args.get("to") or DEFAULT_IMESSAGE_TO).strip()
            if not msg:
                results.append({"toolCallId": tc_id, "result": "Missing message for text_cooper."})
                continue
            res = send_imessage(to, msg)
            if res.get("ok"):
                results.append({"toolCallId": tc_id, "result": f"iMessage sent to {res.get('to')}."})
            else:
                results.append({"toolCallId": tc_id, "result": f"iMessage FAILED: {res}"})
            continue

        if name not in ("ask_cooper", "askCooper", "ask_human"):
            results.append({"toolCallId": tc_id, "result": f"Unknown tool {name}; ignored by HITL server."})
            continue

        question = (args.get("question") or args.get("q") or "").strip()
        context = (args.get("context") or args.get("details") or "").strip()
        if not question:
            results.append({"toolCallId": tc_id, "result": "Missing question parameter."})
            continue

        req_id = uuid.uuid4().hex[:10]
        with _lock:
            _pending[req_id] = {
                "question": question,
                "context": context,
                "call_id": call_id,
                "control_url": control_url,
                "tool_call_id": tc_id,
                "created": time.time(),
            }
        (STATE_DIR / f"{req_id}.json").write_text(json.dumps(_pending[req_id], indent=2))

        try:
            posted = post_question(question, context, call_id, req_id)
            slack_ts = str(posted.get("ts") or "")
            with _lock:
                _pending[req_id]["slack_ts"] = slack_ts
                _pending[req_id]["slack_channel"] = posted.get("channel") or CHANNEL
        except Exception as e:
            results.append({
                "toolCallId": tc_id,
                "result": f"Failed to reach Cooper ({e}). Proceed with existing guardrails; do not invent authority.",
            })
            continue

        answer = wait_for_answer(req_id, slack_ts=slack_ts, timeout=TIMEOUT)
        with _lock:
            _pending[req_id]["answer"] = answer
            _pending[req_id]["done"] = True
        (STATE_DIR / f"{req_id}.answer").write_text(answer)
        results.append({"toolCallId": tc_id, "result": f"Cooper replied: {answer}"})

    return {"results": results}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[hitl] {self.address_string()} {fmt % args}")

    def _auth_ok(self) -> bool:
        if not HITL_TOKEN:
            return True
        h = self.headers.get("X-HITL-Token") or ""
        qs = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        return h == HITL_TOKEN or (qs.get("token") or [None])[0] == HITL_TOKEN

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode() or "{}") if raw else {}

    def _send(self, code: int, obj: Any) -> None:
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse.urlparse(self.path).path
        if path == "/health":
            return self._send(200, {
                "ok": True,
                "pending": len([p for p in _pending.values() if not p.get("done")]),
                "timeout": TIMEOUT,
                "imessage_to": DEFAULT_IMESSAGE_TO,
                "imessage_from": BB_EXPECTED_IMESSAGE,
                "bb_api": BB_API_URL,
                "slack_channel": CHANNEL,
            })
        if path == "/pending":
            with _lock:
                return self._send(200, _pending)
        return self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse.urlparse(self.path).path
        if not self._auth_ok():
            return self._send(401, {"error": "unauthorized"})
        try:
            body = self._read_json()
        except Exception as e:
            return self._send(400, {"error": f"bad json: {e}"})

        if path in ("/vapi/tools", "/webhook", "/"):
            msg_type = (body.get("message") or {}).get("type") if isinstance(body.get("message"), dict) else body.get("type")
            print(f"[hitl] webhook type={msg_type} keys={list(body.keys())}")
            if msg_type and msg_type not in ("tool-calls", "tool.calls", "function-call", "function.call"):
                if not extract_tool_calls(body):
                    return self._send(200, {"ok": True, "ignored": msg_type})
            try:
                result = handle_tool_calls(body)
                print(f"[hitl] results={result}")
                return self._send(200, result)
            except Exception as e:
                print(f"[hitl] error {e}")
                return self._send(200, {"results": [{"toolCallId": "unknown", "result": f"HITL error: {e}"}]})

        if path == "/imessage":
            to = str(body.get("to") or DEFAULT_IMESSAGE_TO)
            msg = str(body.get("message") or body.get("text") or body.get("body") or "")
            res = send_imessage(to, msg)
            return self._send(200 if res.get("ok") else 500, res)

        if path == "/reply":
            rid = str(body.get("id") or "").strip()
            answer = str(body.get("answer") or body.get("text") or "").strip()
            if not rid or not answer:
                return self._send(400, {"error": "need id and answer"})
            with _lock:
                item = _pending.setdefault(rid, {})
                item["answer"] = answer
            (STATE_DIR / f"{rid}.answer").write_text(answer)
            control = (_pending.get(rid) or {}).get("control_url")
            if control:
                try:
                    req = urlrequest.Request(
                        control,
                        data=json.dumps({
                            "type": "add-message",
                            "message": {"role": "system", "content": f"HUMAN REPLY from Cooper: {answer}"},
                            "triggerResponseEnabled": True,
                        }).encode(),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urlrequest.urlopen(req, timeout=10) as resp:
                        print("[hitl] injected control", resp.status)
                except Exception as e:
                    print("[hitl] control inject failed", e)
            return self._send(200, {"ok": True, "id": rid})

        return self._send(404, {"error": "not found"})


def main() -> None:
    tok = slack_token()
    print(f"[hitl] :{PORT} timeout={TIMEOUT}s slack={CHANNEL} imessage={DEFAULT_IMESSAGE_TO} token={'yes' if tok else 'NO'}")
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
