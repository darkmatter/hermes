#!/usr/bin/env bash
# Scaffold a new skill directory in darkmatter/skills/skills/.
#
# Usage:
#   scripts/scaffold-skill.sh [--manual] <skill-name> "Short description"
#
# Flags:
#   --manual   Scaffold a manual-invocation skill (per ADR-0001). Requires the
#              name to start with run- / kickoff- / setup- / init- / do-, and
#              prepends the manual-invocation opening line to the description
#              so the agent does not auto-trigger.
#
# Creates:
#   skills/<name>/SKILL.md          (with frontmatter pre-filled)
#   skills/<name>/scripts/.gitkeep
#   skills/<name>/reference/.gitkeep
#
# Refuses to overwrite an existing directory. Run from anywhere — the script
# locates the repo root via its own path.

set -euo pipefail

MANUAL=0
if [[ "${1:-}" == "--manual" ]]; then
	MANUAL=1
	shift
fi

if [[ $# -lt 2 ]]; then
	cat >&2 <<-USAGE
		usage: $0 [--manual] <skill-name> "Short description"

		auto skill (default) — name as a noun phrase: funding-screener, codebase-cleanup
		manual skill (--manual) — name with verb prefix: kickoff-design, run-screen, setup-vault
	USAGE
	exit 2
fi

NAME="$1"
DESC="$2"

# Validate name format (lowercase, hyphenated, no underscores or caps)
if [[ ! "$NAME" =~ ^[a-z][a-z0-9-]*$ ]]; then
	echo "error: skill name must be lowercase, hyphenated, alphanumeric (got: $NAME)" >&2
	echo "examples of good names: funding-screener, dm-skill-creator, end-of-turn-review" >&2
	exit 1
fi

# Manual skills must use a known verb prefix (ADR-0001).
if [[ $MANUAL -eq 1 ]]; then
	if [[ ! "$NAME" =~ ^(run|kickoff|setup|init|do)- ]]; then
		echo "error: --manual requires a verb prefix from {run-, kickoff-, setup-, init-, do-} (got: $NAME)" >&2
		echo "see docs/adr/0001-skill-naming-convention.md for rationale" >&2
		exit 1
	fi
fi

# Auto skills should NOT use a verb prefix (warn, don't block — there are edge cases).
if [[ $MANUAL -eq 0 ]] && [[ "$NAME" =~ ^(run|kickoff|setup|init|do)- ]]; then
	echo "warning: name '$NAME' looks like a manual-invocation skill but --manual was not passed." >&2
	echo "         if this skill needs explicit invocation, re-run with --manual." >&2
	echo "         if it should auto-trigger, pick a noun-phrase name." >&2
	echo
fi

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SKILL_DIR="$REPO_ROOT/skills/$NAME"

if [[ -e "$SKILL_DIR" ]]; then
	echo "error: $SKILL_DIR already exists" >&2
	exit 1
fi

mkdir -p "$SKILL_DIR/scripts" "$SKILL_DIR/reference"
touch "$SKILL_DIR/scripts/.gitkeep" "$SKILL_DIR/reference/.gitkeep"

if [[ $MANUAL -eq 1 ]]; then
	FRONTMATTER_DESC="Manual-invocation skill — run only when the user explicitly asks for \"$NAME\" or invokes it as a slash command. Do not auto-trigger on adjacent topics. $DESC"
else
	FRONTMATTER_DESC="$DESC Triggers when the user asks <fill in concrete phrases>. Do NOT trigger for <fill in adjacent-but-different cases>."
fi

cat > "$SKILL_DIR/SKILL.md" <<EOF
---
name: $NAME
description: $FRONTMATTER_DESC
---

# ${NAME//-/ }

> One-paragraph overview: what this skill does and why it exists.

## When to use

- <concrete trigger phrase or situation>
- <another>

## When NOT to use

- <adjacent thing that uses a different tool>
- <case where general knowledge suffices>

## Tools

### \`scripts/<name>.sh\`

> What it does, when to run it.

**Usage:**

\`\`\`bash
scripts/<name>.sh --help
\`\`\`

**Env vars / deps:** <list any, or "none">

## Reference

- \`reference/<topic>.md\` — <when to load this>
EOF

echo "created $SKILL_DIR ($([ $MANUAL -eq 1 ] && echo manual || echo auto))"
echo
echo "next steps:"
echo "  1. edit $SKILL_DIR/SKILL.md"
echo "  2. add code under $SKILL_DIR/scripts/ and reference docs under $SKILL_DIR/reference/"
echo "  3. $REPO_ROOT/scripts/validate-skill.sh $SKILL_DIR"
echo "  4. add a row to $REPO_ROOT/docs/catalog.md"
echo "  5. rebuild ~/darwin to test:"
echo "     cd ~/darwin && darwin-rebuild switch --flake .#\$(hostname -s) \\"
echo "       --override-input darkmatter/darkmatter-skills path:$REPO_ROOT"
