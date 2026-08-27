# Wiring the reviewer into your end-of-turn hooks

The skill ships logic; the hook decides *when* it fires. The wrapper script is `scripts/diff-review-hook.sh` — it's client-agnostic and works with any caller that:

- runs it with cwd inside a git repo
- captures its stdout and either surfaces it to the next agent turn or prints it to the user

Below: snippets for the most common agent runtimes and a few non-agent fallbacks. Pick whichever your daily driver supports.

## Claude Code

`~/.claude/settings.json` (or per-project `.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/git/darkmatter/skills/skills/end-of-turn-review/scripts/diff-review-hook.sh"
          }
        ]
      }
    ]
  }
}
```

The `Stop` event fires when the assistant finishes a turn. Stdout from the hook is appended to the next turn's context, so the model sees the critique on its next invocation.

## opencode

`~/.config/opencode/opencode.json`, top-level `hooks` key. The session-end event name varies by version — check `opencode hook --help` or the docs at https://opencode.ai/docs/hooks/. Wire identically:

```json
{
  "hooks": {
    "session.idle": {
      "command": ["~/git/darkmatter/skills/skills/end-of-turn-review/scripts/diff-review-hook.sh"]
    }
  }
}
```

(Adjust event name to match your opencode version.)

## Cursor

Cursor's `afterTurn` hook in `.cursor/hooks.json` (workspace-level) or via the desktop settings:

```json
{
  "afterTurn": {
    "command": "~/git/darkmatter/skills/skills/end-of-turn-review/scripts/diff-review-hook.sh"
  }
}
```

## Aider

Aider doesn't have a true post-turn hook, but it auto-commits after each successful edit. Pair the reviewer with a git `post-commit` hook in repos you use Aider in:

```bash
# .git/hooks/post-commit
#!/usr/bin/env bash
git diff HEAD~..HEAD | /path/to/skills/end-of-turn-review/scripts/review.sh --kind=diff
```

## Plain git (agent-runtime-independent)

Skip end-of-turn entirely; review at commit boundaries instead. Lower noise, only fires on intentional checkpoints.

```bash
# .git/hooks/pre-commit
#!/usr/bin/env bash
git diff --cached | /path/to/skills/end-of-turn-review/scripts/review.sh --kind=diff
```

Or as a `prepare-commit-msg` hook that drops the critique into the commit message body.

## ACP / generic stdio agent

If your agent speaks ACP (Zed's panel, anything wrapping opencode/Claude Code via JSON-RPC), the host editor decides which hooks fire. There's no portable end-of-turn hook at the ACP layer today — wire it at the underlying runtime (opencode/Claude Code) instead.

## Reviewing plans

The diff hook only handles code. To review a plan, invoke the skill explicitly:

```bash
cat plan.md | /path/to/skills/end-of-turn-review/scripts/review.sh --kind=plan
```

Or instruct your planner agent to end its output with: *"Run end-of-turn-review on this plan before executing."* — the orchestrator picks up the skill and routes the plan through it.

## Why the wrapper is client-agnostic

Everything client-specific lives in the *config snippet* (settings.json, hooks.json, etc.) — that's just a path pointing to the wrapper. The wrapper itself only depends on `git`, `bash`, and `review.sh`. Swapping editors or agent runtimes doesn't require touching the skill.
