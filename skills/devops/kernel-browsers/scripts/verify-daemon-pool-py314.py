#!/usr/bin/env python3
"""Probe DaemonThreadPoolExecutor on this interpreter (3.14 needs fixed daemon_pool)."""
from __future__ import annotations

import sys


def main() -> int:
    try:
        from tools.daemon_pool import DaemonThreadPoolExecutor
    except Exception as e:
        print("import_fail", type(e).__name__, e)
        print("hint: PYTHONPATH=$HOME/.local/lib/hermes-py314-fix or rebuilt hermes-agent")
        return 2
    print("module_file", getattr(sys.modules.get("tools.daemon_pool"), "__file__", "?"))
    try:
        with DaemonThreadPoolExecutor(max_workers=1) as ex:
            v =・ex.submit(lambda: 42).result(timeout=2)
        print("ok", v)
        return 0
    except Exception as e:
        print("fail", type(e).__name__, e)
        if "_initializer" in str(e):
            print("cause: CPython 3.14 removed ThreadPoolExecutor._initializer; ship fixed daemon_pool")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
