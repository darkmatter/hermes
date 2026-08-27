#!/usr/bin/env python3
"""Bulk-create Hermes kanban cards from a list of (title, body, priority) tuples.

Designed to be run inside Hermes execute_code (uses hermes_tools.terminal), or
adapt the `run` call to subprocess for standalone use.

Human-action items: leaves --assignee unset so the dispatcher never auto-runs
them. Each card gets --created-by and --json so we can capture the t_<hex> id.

Edit BOARD and CARDS, then run. Prints [exit] id title per card.
"""
import json
import re
import shlex

# --- edit these ---------------------------------------------------------
BOARD = "email-triage"
CREATED_BY = "Cooper Maruyama"
# (title, body, priority)  higher priority = sooner (tiebreaker only)
CARDS = [
    # ("Q2 estimated tax payment — deadline June 15",
    #  "1800Accountant reminders. Deadline June 15. Source: ...", 10),
]
# ------------------------------------------------------------------------

try:
    from hermes_tools import terminal  # type: ignore

    def run(cmd: str) -> tuple[str, int]:
        r = terminal(command=cmd, timeout=30)
        return r.get("output", "").strip(), r.get("exit_code", 1)
except Exception:  # standalone fallback
    import subprocess

    def run(cmd: str) -> tuple[str, int]:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return (p.stdout or p.stderr).strip(), p.returncode


def create_card(title: str, body: str, priority: int) -> tuple[str, int]:
    cmd = (
        f"hermes kanban --board {shlex.quote(BOARD)} create {shlex.quote(title)} "
        f"--body {shlex.quote(body)} --priority {priority} "
        f"--created-by {shlex.quote(CREATED_BY)} --json"
    )
    out, ec = run(cmd)
    tid = ""
    try:
        j = json.loads(out)
        tid = j.get("id") or j.get("task", {}).get("id", "")
    except Exception:
        m = re.search(r"t_[0-9a-f]+", out)
        tid = m.group(0) if m else out[:60]
    return tid, ec


def main() -> None:
    for title, body, prio in CARDS:
        tid, ec = create_card(title, body, prio)
        print(f"[{ec}] {tid:14} {title[:55]}")
    print("\nVerify: hermes kanban --board %s list" % BOARD)


if __name__ == "__main__":
    main()
