#!/usr/bin/env bash
# Client-agnostic diff review hook for end-of-turn-review.
#
# Designed to be called from any agent runtime's session-stop / end-of-turn
# event (Claude Code Stop, opencode session-end, Cursor afterTurn, Aider
# auto-commit hook, plain git pre-commit, etc.) — it makes no assumptions
# about the caller beyond:
#
#   - cwd is inside a git repo
#   - stdout from this script is captured and surfaced to the next turn
#     (or simply printed to the human, in pre-commit / standalone use)
#
# Behavior:
#   1. If not in a git repo → exit 0 silently.
#   2. Collect `git diff HEAD` (uncommitted work). If empty → exit 0.
#   3. Skip trivial diffs (≤3 changed lines) → exit 0.
#   4. Pipe the diff through review.sh and print the critique on stdout.
#
# See reference/hook-setup.md for per-client wiring snippets.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Only review when inside a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

DIFF="$(git diff HEAD 2>/dev/null || true)"
if [[ -z "$DIFF" ]]; then
  exit 0
fi

# Skip trivial diffs (≤3 changed lines, ignoring +++/--- headers)
CHANGED=$(echo "$DIFF" | grep -cE '^[+-][^+-]' || true)
if (( CHANGED <= 3 )); then
  exit 0
fi

echo "---"
echo "## End-of-turn review (gpt-5.5)"
echo
echo "$DIFF" | "$SKILL_DIR/scripts/review.sh" --kind=diff || {
  echo "(reviewer unavailable, skipping)"
  exit 0
}
