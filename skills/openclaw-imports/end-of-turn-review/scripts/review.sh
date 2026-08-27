#!/usr/bin/env bash
# end-of-turn review — pipes work-to-review to a strong reviewer model and prints the critique.
#
# Usage:
#   git diff | review.sh --kind=diff
#   cat plan.md | review.sh --kind=plan
#   review.sh --kind=turn < transcript.txt
#
# Env:
#   REVIEW_MODEL       (default: gpt-5.5)
#   LITELLM_BASE_URL   (default: https://litellm.drkmttr.dev/v1)
#   LITELLM_API_KEY    (required; falls back to ~/.config/litellm/key)
#   REVIEW_CONTEXT     (optional path to extra context — user prompt, prior plan, etc.)

set -euo pipefail

KIND=""
for arg in "$@"; do
  case "$arg" in
    --kind=*) KIND="${arg#--kind=}" ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

if [[ -z "$KIND" ]]; then
  echo "missing --kind={diff|plan|turn}" >&2
  exit 2
fi

MODEL="${REVIEW_MODEL:-gpt-5.5}"
BASE_URL="${LITELLM_BASE_URL:-https://litellm.drkmttr.dev/v1}"

if [[ -z "${LITELLM_API_KEY:-}" ]]; then
  if [[ -r "$HOME/.config/litellm/key" ]]; then
    LITELLM_API_KEY=<REDACTED>
  else
    echo "LITELLM_API_KEY unset and ~/.config/litellm/key missing" >&2
    exit 2
  fi
fi

# Locate the skill root regardless of cwd
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYS_PROMPT="$(cat "$SKILL_DIR/reference/system-prompt.md")"

# Read the work-to-review from stdin
WORK="$(cat)"
if [[ -z "$WORK" ]]; then
  echo "stdin was empty — nothing to review" >&2
  exit 2
fi

# Optional caller-supplied context
EXTRA=""
if [[ -n "${REVIEW_CONTEXT:-}" && -r "${REVIEW_CONTEXT}" ]]; then
  EXTRA=$'\n\n## Additional context the reviewer should consider\n\n'"$(cat "$REVIEW_CONTEXT")"
fi

USER_MSG="Input kind: ${KIND}

${EXTRA}

## Work to review

\`\`\`
${WORK}
\`\`\`"

# Build the request body with jq so quoting is correct regardless of input content
BODY="$(jq -n \
  --arg model "$MODEL" \
  --arg sys "$SYS_PROMPT" \
  --arg user "$USER_MSG" \
  '{model: $model, temperature: 0.1, messages: [{role:"system", content:$sys}, {role:"user", content:$user}]}')"

RESP="$(curl -sS -X POST "${BASE_URL}/chat/completions" \
  -H "Authorization: Bearer <REDACTED>" \
  -H "Content-Type: application/json" \
  --data-binary "$BODY")"

# Extract the critique. If the model isn't available, surface the error to stderr.
if ! echo "$RESP" | jq -e '.choices[0].message.content' >/dev/null 2>&1; then
  echo "review failed:" >&2
  echo "$RESP" >&2
  exit 1
fi

echo "$RESP" | jq -r '.choices[0].message.content'
