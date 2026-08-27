#!/usr/bin/env python3
"""Take a screenshot via camofox /snapshot endpoint.

Usage:
  CAMOFOX_API_KEY=<REDACTED>
"""
import urllib.request, json, base64, os, sys, time

API = os.environ.get("CAMOFOX_API_URL", "http://localhost:9377")
KEY = os.environ.get("CAMOFOX_API_KEY", "")
USER = os.environ.get("CAMOFOX_USER_ID", "hermes")
SESSION = os.environ.get("CAMOFOX_SESSION_KEY", "hermes")
HEAD = {"Content-Type": "application/json", "Authorization": "<REDACTED>" + KEY}

url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/screenshot.png"
wait = int(sys.argv[3]) if len(sys.argv) > 3 else 8

# Create tab
data = json.dumps({"url": url, "userId": USER, "sessionKey": SESSION}).encode()
req = urllib.request.Request(API + "/tabs", data=data, headers=HEAD, method="POST")
resp = json.loads(urllib.request.urlopen(req).read())
tab_id = resp["tabId"]
print(f"Tab: {tab_id}")

time.sleep(wait)

# Snapshot with screenshot
snap_url = API + "/tabs/" + tab_id + "/snapshot?includeScreenshot=true&userId=" + USER
snap = json.loads(urllib.request.urlopen(urllib.request.Request(snap_url, headers=HEAD)).read())

ss = snap.get("screenshot")
if ss and isinstance(ss, dict) and "data" in ss:
    with open(out, "wb") as f:
        f.write(base64.b64decode(ss["data"]))
    print(f"Saved: {out} ({os.path.getsize(out)} bytes)")
else:
    print("No screenshot in response")
    sys.exit(1)
