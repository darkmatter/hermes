# Agent-first feed options

## Why

Cooper uses the feed so **he does not research**. Prompts that ask “what did the console show?” invert the product.

## Default MC (action-needed items without curated options)

| Tab label | id | Intent |
|---|---|---|
| Investigate ★ | `investigate_propose` | Readonly investigate → evidence on kanban → propose one next action |
| Do safe work | `execute_safe` | Investigate + finish every EXECUTE-SAFE step; stop at charge/send/security |
| Snooze | `snooze` | Hermes follow-up later — not Cooper homework |
| Skip | `skip` | Agent archive/mute |

Implemented in prod: `~/git/darkmatter/feed/src/components/dashboard.tsx` → `defaultResponseOptions`.

## Recommendation authors must

- Put **agent verbs** in labels/prompts (“Open official SendGrid console and report…”).
- After investigation, leave Cooper **binary gates only** (Pay/Don't-pay, Approve draft/send, MFA identity).
- Never require Cooper to paste console findings into chat.

## Blocked-card fallback (no recommendation actions)

Same agent-first trio: investigate→propose | finish safe work | defer with agent status comment.
