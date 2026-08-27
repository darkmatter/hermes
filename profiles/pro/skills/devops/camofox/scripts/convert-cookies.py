#!/usr/bin/env python3
"""Convert Chrome cookie exports to Playwright storage-state.json for camofox.

Takes two optional inputs:
  1. Cookie Editor JSON export (includes HttpOnly cookies)
  2. Chrome DevTools export (includes localStorage from cookieStore.getAll())

Outputs Playwright storage-state.json to stdout.

Usage:
  # Full: cookies + localStorage
  python3 convert-cookies.py /tmp/cb-cookies-full.json /tmp/cb-chrome-export.json

  # Cookies only (no localStorage)
  python3 convert-cookies.py /tmp/cb-cookies-full.json

  # localStorage only (no HttpOnly cookies)
  python3 convert-cookies.py "" /tmp/cb-chrome-export.json

  # Specify origin for localStorage (default: auto-detected from cookies)
  python3 convert-cookies.py /tmp/cb-cookies-full.json /tmp/cb-chrome-export.json --origin https://www.coinbase.com
"""
import json, sys, argparse


def convert_cookie_editor_cookies(path):
    """Convert Cookie Editor JSON export to Playwright cookie format."""
    if not path:
        return []
    cookies_raw = json.load(open(path))
    pw_cookies = []
    for c in cookies_raw:
        expires = c.get("expirationDate")
        if expires and expires > 0:
            expires = int(expires)
        else:
            expires = -1

        same_site = c.get("sameSite") or "Lax"
        if same_site.lower() == "no_restriction":
            same_site = "None"
        elif same_site.lower() in ("lax", "strict", "none"):
            same_site = same_site.capitalize()
        else:
            same_site = "Lax"

        domain = c.get("domain", "")

        pw_cookie = {
            "name": c["name"],
            "value": c["value"],
            "domain": domain,
            "path": c.get("path", "/"),
            "expires": expires,
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", True),
            "sameSite": same_site,
        }
        pw_cookies.append(pw_cookie)
    return pw_cookies


def infer_origin(cookies):
    """Infer the most likely origin from cookie domains."""
    domains = set()
    for c in cookies:
        d = c.get("domain", "").lstrip(".")
        if d:
            domains.add(d)
    if not domains:
        return None
    # Prefer the most specific domain (longest, no leading dot)
    best = max(domains, key=lambda d: len(d))
    return f"https://{best}"


def convert_devtools_export(path, origin=None):
    """Convert Chrome DevTools export (cookieStore.getAll() + localStorage) to Playwright format.

    Returns (cookies_list, origins_list).
    Note: cookieStore.getAll() does NOT include HttpOnly cookies.
    """
    if not path:
        return [], []
    data = json.load(open(path))

    # Cookies from cookieStore (non-HttpOnly only)
    pw_cookies = []
    for c in data.get("cookies", []):
        domain = c.get("domain") or ""
        expires = c.get("expires")
        if expires and expires > 1e12:
            expires = int(expires / 1000)  # Chrome uses ms sometimes
        elif expires and expires > 0:
            expires = int(expires)
        else:
            expires = -1

        same_site = c.get("sameSite", "Lax") or "Lax"
        if same_site.lower() in ("lax", "strict", "none"):
            same_site = same_site.capitalize()
        else:
            same_site = "Lax"

        pw_cookie = {
            "name": c["name"],
            "value": c["value"],
            "domain": domain,
            "path": c.get("path", "/"),
            "expires": expires,
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", True),
            "sameSite": same_site,
        }
        pw_cookies.append(pw_cookie)

    # localStorage
    ls_items = data.get("localStorage", {})
    origin_entries = []
    if ls_items:
        ls_list = [{"name": k, "value": v} for k, v in ls_items.items()]
        # Use provided origin or infer from cookie domains
        resolved_origin = origin or infer_origin(pw_cookies) or "https://example.com"
        origin_entries.append({
            "origin": resolved_origin,
            "localStorage": ls_list,
        })

    return pw_cookies, origin_entries


def main():
    parser = argparse.ArgumentParser(description="Convert Chrome cookie exports to Playwright storage-state.json")
    parser.add_argument("cookies_path", nargs="?", default="", help="Cookie Editor JSON export file")
    parser.add_argument("ls_path", nargs="?", default="", help="Chrome DevTools export file (localStorage)")
    parser.add_argument("--origin", default=None, help="Origin for localStorage (e.g. https://www.coinbase.com). Auto-detected from cookies if not set.")
    args = parser.parse_args()

    # Get HttpOnly cookies from Cookie Editor export
    ce_cookies = convert_cookie_editor_cookies(args.cookies_path) if args.cookies_path else []

    # Get non-HttpOnly cookies + localStorage from DevTools export
    dt_cookies, dt_origins = convert_devtools_export(args.ls_path, origin=args.origin) if args.ls_path else ([], [])

    # Merge: Cookie Editor cookies take priority (they include HttpOnly)
    # Remove duplicates by name (CE version wins since it has HttpOnly)
    ce_names = {c["name"] for c in ce_cookies}
    merged_cookies = ce_cookies + [c for c in dt_cookies if c["name"] not in ce_names]

    storage_state = {
        "cookies": merged_cookies,
        "origins": dt_origins,
    }

    print(json.dumps(storage_state, indent=2))
    print(f"\n{len(merged_cookies)} cookies, {sum(len(o['localStorage']) for o in dt_origins)} localStorage items", file=sys.stderr)


if __name__ == "__main__":
    main()
