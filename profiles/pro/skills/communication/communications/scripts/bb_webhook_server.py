#!/usr/bin/env python3
"""BlueBubbles webhook receiver + inbox for Hermes.

Public via Cloudflare Tunnel: https://bb-hook.cm.xyz
Local bind: :8790

Paths:
  POST /bb/webhook?secret=...   BlueBubbles events (register this URL)
  GET  /health
  GET  /inbox?limit=50
  GET  /messages?limit=50
  POST /ack  {"id":"..."}
"""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import parse as urlparse

PORT = int(os.environ.get("BB_HOOK_PORT", "8790"))
SECRET = <REDACTED>
INBOX_DIR = Path(os.environ.get("BB_INBOX_DIR", "/tmp/bb-inbox"))
INBOX_DIR.mkdir(parents=True, exist_ok=True)
MAX_MEM = int(os.environ.get("BB_INBOX_MAX", "500"))

_lock = threading.Lock()
_events: deque[dict[str, Any]] = deque(maxlen=MAX_MEM)


def _load_recent_from_disk(n: int = 100) -> None:
    files = sorted(INBOX_DIR.glob("*.json"), reverse=True)[:n]
    loaded = []
    for f in files:
        try:
            loaded.append(json.loads(f.read_text()))
        except Exception:
            pass
    loaded.sort(key=lambda e: e.get("ts", 0))
    with _lock:
        for e in loaded:
            _events.append(e)


_load_recent_from_disk()


def normalize_event(body: dict) -> dict:
    etype = body.get("type") or body.get("event") or body.get("name") or "unknown"
    data = body.get("data") if isinstance(body.get("data"), (dict, list)) else body
    msg = data if isinstance(data, dict) else {}
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        msg = {**data, **data.get("data")}
    text = msg.get("text") or msg.get("message") or ""
    handle = msg.get("handle") or msg.get("address") or ""
    if isinstance(handle, dict):
        handle = handle.get("address") or handle.get("id") or ""
    chat_guid = msg.get("chats") or msg.get("chatGuid") or msg.get("guid") or ""
    if isinstance(chat_guid, list) and chat_guid:
        c0 = chat_guid[0]
        chat_guid = c0.get("guid") if isinstance(c0, dict) else c0
    return {
        "id": uuid.uuid4().hex[:12],
        "ts": time.time(),
        "type": etype,
        "text": text,
        "handle": handle,
        "isFromMe": msg.get("isFromMe"),
        "chatGuid": chat_guid,
        "raw": body,
        "acked": False,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[bb-hook] {self.address_string()} {fmt % args}")

    def _qs(self) -> dict:
        return urlparse.parse_qs(urlparse.urlparse(self.path).query)

    def _secret_ok(self) -> bool:
        if not SECRET:
            return True
        h = self.headers.get("X-BB-Hook-Secret") or self.headers.get("X-Webhook-Secret") or ""
        qs = self._qs()
        return h == SECRET or (qs.get("secret") or [None])[0] == SECRET

    def _read_json(self) -> Any:
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode())
        except Exception:
            return {"_raw": raw.decode(errors="replace")}

    def _send(self, code: int, obj: Any) -> None:
        data = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if not self._secret_ok():
            return self._send(401, {"error": "unauthorized"})
        path = urlparse.urlparse(self.path).path
        qs = self._qs()
        limit = int((qs.get("limit") or ["50"])[0])
        if path == "/health":
            with _lock:
                n = len(_events)
            return self._send(200, {"ok": True, "events": n, "port": PORT})
        if path in ("/inbox", "/events"):
            with _lock:
                items = list(reversed(list(_events)[-limit:]))
            return self._send(200, {"count": len(items), "events": items})
        if path == "/messages":
            with _lock:
                items = [
                    e for e in _events
                    if e.get("type") in ("new-message", "updated-message") or e.get("text")
                ]
            items = list(reversed(items))[:limit]
            slim = [
                {k: e.get(k) for k in ("id", "ts", "type", "text", "handle", "isFromMe", "chatGuid", "acked")}
                for e in items
            ]
            return self._send(200, {"count": len(slim), "messages": slim})
        return self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse.urlparse(self.path).path
        body = self._read_json()

        if path in ("/bb/webhook", "/webhook", "/"):
            if not self._secret_ok():
                return self._send(401, {"error": "unauthorized"})
            evt = normalize_event(body if isinstance(body, dict) else {"data": body})
            with _lock:
                _events.append(evt)
            try:
                (INBOX_DIR / f"{int(evt['ts'] * 1000)}_{evt['id']}.json").write_text(
                    json.dumps(evt, default=str)[:200000]
                )
            except Exception as e:
                print("[bb-hook] disk write fail", e)
            print(
                f"[bb-hook] {evt.get('type')} from={evt.get('handle')} "
                f"fromMe={evt.get('isFromMe')} text={(evt.get('text') or '')[:120]!r}"
            )
            return self._send(200, {"ok": True, "id": evt["id"]})

        if not self._secret_ok():
            return self._send(401, {"error": "unauthorized"})

        if path == "/ack":
            eid = str((body or {}).get("id") or "")
            with _lock:
                for e in _events:
                    if e.get("id") == eid:
                        e["acked"] = True
                        return self._send(200, {"ok": True})
            return self._send(404, {"error": "not found"})

        return self._send(404, {"error": "not found"})


def main() -> None:
    print(f"[bb-hook] :{PORT} inbox={INBOX_DIR} secret={'yes' if SECRET else 'no'}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
