#!/usr/bin/env bash
# Load Cooper's Vapi private API key (and common IDs) for CLI/curl.
# Source from other scripts:  source "$(dirname "$0")/vapi_env.sh"
# Or run standalone to print export lines:  eval "$(vapi_env.sh)"
set -euo pipefail

resolve_private_key() {
  if [[ -n "${VAPI_API_KEY:-}" ]]; then
    printf '%s' "$VAPI_API_KEY"
    return 0
  fi
  if [[ -n "${VAPI_KEY:-}" ]]; then
    printf '%s' "$VAPI_KEY"
    return 0
  fi

  # 1Password item "vapi" -> credential (PRIVATE key)
  if command -v op >/dev/null 2>&1; then
    local k
    k="$(op item get vapi --fields credential --reveal 2>/dev/null || true)"
    if [[ -n "$k" ]]; then
      printf '%s' "$k"
      return 0
    fi
  fi

  # Official CLI config (~/.vapi-cli.yaml)
  local cfg="${VAPI_CLI_CONFIG:-$HOME/.vapi-cli.yaml}"
  if [[ -f "$cfg" ]]; then
    local k
    k="$(CFG_PATH="$cfg" python3 - <<'PY'
import os, re
text = open(os.environ["CFG_PATH"]).read()
m = re.search(r"(?m)^\s*api_key:\s*[\"']?([^\"'\n#]+)", text)
print(m.group(1).strip() if m else "")
PY
)"
    if [[ -n "$k" ]]; then
      printf '%s' "$k"
      return 0
    fi
  fi

  echo "vapi_env: no private key found. Set VAPI_API_KEY or unlock 1Password (op item get vapi)." >&2
  return 1
}

VAPI_PRIVATE_KEY="$(resolve_private_key)"
export VAPI_KEY=<REDACTED>
export VAPI_API_KEY=<REDACTED>
export VAPI_BASE_URL="${VAPI_BASE_URL:-https://api.vapi.ai}"

# Standing org defaults (overridable)
export VAPI_ASSISTANT_ID="${VAPI_ASSISTANT_ID:-86a092df-2332-4092-bf2d-2cd02c66ac4a}"
export VAPI_PHONE_NUMBER_ID="${VAPI_PHONE_NUMBER_ID:-68092f67-e7eb-4df9-8a39-e930eb99270d}"

# Official CLI on PATH for this shell
if [[ -d "$HOME/.vapi/bin" ]]; then
  case ":$PATH:" in
    *":$HOME/.vapi/bin:"*) ;;
    *) export PATH="$HOME/.vapi/bin:$PATH" ;;
  esac
fi
if [[ -d "$HOME/.local/bin" ]]; then
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
fi

# When executed (not sourced), emit exports for eval
if [[ "${BASH_SOURCE[0]:-$0}" == "$0" ]]; then
  printf 'export VAPI_KEY=%q\n' "$VAPI_KEY"
  printf 'export VAPI_API_KEY=%q\n' "$VAPI_API_KEY"
  printf 'export VAPI_BASE_URL=%q\n' "$VAPI_BASE_URL"
  printf 'export VAPI_ASSISTANT_ID=%q\n' "$VAPI_ASSISTANT_ID"
  printf 'export VAPI_PHONE_NUMBER_ID=%q\n' "$VAPI_PHONE_NUMBER_ID"
  printf 'export PATH=%q\n' "$PATH"
fi
